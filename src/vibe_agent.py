"""LeetVibe Vibe Agent — Mistral AI streaming agent with tool-calling loop."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Generator

# Ensure project root is on sys.path so `skills.*` imports resolve
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from mistralai import Mistral

from .config import Config
from .challenge_loader import Challenge

# ── System prompts ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are LeetVibe AI — an expert competitive programmer and patient teacher.

Follow this EXACT workflow for every problem. Never skip a step.

[bold]STEP 1 — UNDERSTAND[/bold]
Restate the problem in your own words. Identify:
- The key constraint (what limits n? what are the value ranges?)
- Edge cases (empty input, single element, all duplicates, negatives)
- The likely algorithm family (two-pointer, DP, graph, hash-map, etc.)

[bold]STEP 2 — BRUTE FORCE[/bold]
Write the simplest correct solution and explain every line.
Call run_code() to validate it. If any test fails: debug, fix, and call run_code() again until all pass.

[bold]STEP 3 — ANALYSE BRUTE FORCE[/bold]
Call analyze_complexity() on the brute-force code.
State explicitly: "This is O(?) time / O(?) space because …"
Identify the bottleneck — what repeated work makes it slow?

[bold]STEP 4 — KEY INSIGHT[/bold]
Name the optimization idea that eliminates the bottleneck. Explain it clearly in plain text.

[bold]STEP 5 — OPTIMAL SOLUTION[/bold]
Write the optimized solution. Explain every change from the brute-force.
Call run_code() to validate it. If any test fails: debug, fix, and call run_code() again.

[bold]STEP 6 — ANALYSE OPTIMAL[/bold]
Call analyze_complexity() on the optimal code.
Compare: "We improved from O(?) → O(?) by eliminating …"

[bold]STEP 7 — EXPLAIN APPROACH[/bold]
Call explain_approach() with approach="optimal" to generate a structured walkthrough.

[bold]STEP 8 — LOG[/bold]
Call log_session() to record the session.

Rules:
- Think out loud before every code block. Never write code without explaining the reasoning first.
- Never skip a step, even for trivial problems.
- If run_code() returns failures, fix the code before proceeding to the next step.
- Use Rich markup: [bold] for key terms, [dim] for secondary info, triple backticks for all code.\
"""

INTERVIEW_PROMPT = """\
You are a senior software engineer conducting a 30-minute mock technical interview.

YOUR ROLE:
- On your FIRST message only: greet the candidate warmly, introduce yourself by first name, state the problem title and difficulty, then ask them to walk through their approach before coding.
- On all subsequent messages: skip any greeting or re-introduction. React directly to what the candidate just said.
- Respond with short, realistic interviewer reactions (2–4 sentences max).
- Probe with follow-ups like: "What's the time complexity?" / "Any edge cases?" / "Can you do better?"
- Do NOT write code. Do NOT reveal the optimal solution unless they've already found it.
- If they are stuck, give one small hint then wait for their next message.
- When they present a working solution, give brief feedback on correctness, complexity, and one thing to improve.
- Close the session with: "Thanks, that wraps up our session."

RULES:
- Every response must be 2–4 sentences. Real interviewers are concise.
- No markdown, no bullet lists, no code blocks. Speak naturally as if talking out loud.
- Never re-introduce yourself after the first message.
- Never call tools.\
"""

COACH_PROMPT = """\
You are LeetVibe AI — a patient and encouraging coding coach.
The user has already attempted the problem. Do NOT solve it from scratch.
Your job is to review their attempt, diagnose issues, and guide them to the optimal solution.

Follow this EXACT coaching workflow. Never skip a step.

[bold]STEP 1 — TEST USER'S CODE[/bold]
Call run_code() using the user's code exactly as written.
Report clearly: "Your code passes X/Y test cases."

[bold]STEP 2 — DIAGNOSE[/bold]
Examine the user's code carefully. Identify and explain every issue:
- Bugs (incorrect logic, wrong edge case handling, off-by-one errors)
- Inefficiencies (nested loops, redundant passes, unnecessary data structures)
- Code quality (naming, readability, structure)
Be specific — point to exact lines and explain why each is problematic.
If the code passes all tests, note that it is correct but focus on efficiency.

[bold]STEP 3 — ANALYSE USER'S COMPLEXITY[/bold]
Call analyze_complexity() on the user's code.
State: "Your solution is O(?) time / O(?) space because …"
Explain whether this is acceptable given the problem's constraints.
Identify the bottleneck — what makes it slow or memory-heavy?

[bold]STEP 4 — GUIDED HINTS[/bold]
Do NOT reveal the optimal solution yet. Guide the user toward it with questions and nudges:
- Point to the bottleneck: "Notice that this part repeats work — what's redundant?"
- Suggest a direction: "What data structure would let you look this up in O(1)?"
- Give one concrete hint that bridges their approach to the optimal one.

[bold]STEP 5 — OPTIMAL SOLUTION[/bold]
Now reveal the optimal solution with a full line-by-line explanation.
Explain every change from the user's version and why it was made.
Call run_code() to validate it. If any test fails: debug, fix, and call run_code() again.

[bold]STEP 6 — COMPARE[/bold]
Side-by-side comparison of the user's approach vs the optimal:
- What changed and why
- Complexity improvement: O(?) → O(?)
- The single key insight that transforms one into the other

[bold]STEP 7 — EXPLAIN APPROACH[/bold]
Call explain_approach() with approach="optimal" to generate a structured walkthrough.

[bold]STEP 8 — LOG[/bold]
Call log_session() to record the session.

Rules:
- Always be encouraging — frame issues as learning opportunities, not failures.
- Never skip a step, even if the user's code is already optimal.
- If run_code() returns failures in step 5, fix the code before proceeding.
- Use Rich markup: [bold] for key terms, [dim] for secondary info, triple backticks for all code.\
"""

# ── Tool schemas (Mistral / OpenAI format) ────────────────────────────────────

_TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "run_code",
            "description": "Execute Python code against test cases. Returns pass/fail per case.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute",
                    },
                    "snippet": {
                        "type": "string",
                        "description": "Original function/class snippet (used for caller resolution)",
                    },
                    "example_testcases_raw": {
                        "type": "string",
                        "description": (
                            "Newline-separated raw input values — one value per line, "
                            "grouped by parameter count. NO variable names. "
                            "Example for f(nums, k) with 2 cases: '[1,2,3]\\n2\\n[4,5]\\n1'"
                        ),
                    },
                    "test_cases": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Structured test case list",
                    },
                },
                "required": ["code", "snippet"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_complexity",
            "description": "Analyse time and space complexity of Python code via AST inspection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to analyse"},
                    "function_name": {
                        "type": "string",
                        "description": "Name of the main function (optional)",
                    },
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_approach",
            "description": "Return a structured step-by-step explanation of the algorithm approach.",
            "parameters": {
                "type": "object",
                "properties": {
                    "problem_title": {"type": "string"},
                    "approach": {
                        "type": "string",
                        "enum": ["brute_force", "optimal"],
                    },
                    "algorithm_pattern": {
                        "type": "string",
                        "description": "e.g. two-pointer, dp, hash-map, sliding-window",
                    },
                    "code": {
                        "type": "string",
                        "description": "Code to include in the walkthrough (optional)",
                    },
                },
                "required": ["problem_title", "approach", "algorithm_pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_session",
            "description": "Log a completed learning session to Weights & Biases.",
            "parameters": {
                "type": "object",
                "properties": {
                    "problem_id": {"type": "string"},
                    "problem_title": {"type": "string"},
                    "difficulty": {"type": "string"},
                    "solved": {"type": "boolean"},
                    "time_seconds": {"type": "integer"},
                    "approaches_tried": {"type": "integer"},
                    "final_complexity": {"type": "string"},
                    "hints_used": {"type": "boolean"},
                },
                "required": [
                    "problem_id",
                    "problem_title",
                    "difficulty",
                    "solved",
                    "time_seconds",
                    "approaches_tried",
                    "final_complexity",
                    "hints_used",
                ],
            },
        },
    },
]


# ── Agent ─────────────────────────────────────────────────────────────────────


class VibeAgent:
    """Mistral AI agent with a streaming tool-calling loop."""

    def __init__(self, config: Config) -> None:
        self.client = Mistral(api_key=config.mistral_api_key)
        self.model = config.mistral_model
        self._messages: list[dict] = []        # persisted conversation history
        self._start_ts: float = 0.0
        self._approaches_tried: int = 0
        self._interview_mode: bool = False

    # ── Public API ────────────────────────────────────────────────────

    def solve_streaming(
        self,
        challenge: Challenge,
        mode: str = "learn",
        user_code: str = "",
    ) -> Generator[str, None, None]:
        """Initialise a new session then yield streaming text chunks."""
        self._interview_mode = mode == "interview"
        if self._interview_mode:
            system = INTERVIEW_PROMPT
        elif mode == "coach" and user_code.strip():
            system = COACH_PROMPT
        else:
            system = SYSTEM_PROMPT
        self._messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": self._build_prompt(challenge, mode, user_code)},
        ]
        self._start_ts = time.time()
        self._approaches_tried = 0
        tools = [] if self._interview_mode else _TOOLS
        yield from self._run_loop(tools=tools)
        if not self._interview_mode:
            elapsed = int(time.time() - self._start_ts)
            yield f"\n[dim]Session complete — {elapsed}s elapsed[/dim]\n"

    def inject_history(self, messages: list[dict]) -> None:
        """Restore a saved conversation so follow-up questions have full context.

        Call this instead of solve_streaming() when resuming a prior session.
        The caller is responsible for prepending the system message.
        """
        self._messages = messages
        self._start_ts = time.time()

    def chat_streaming(self, user_message: str) -> Generator[str, None, None]:
        """Append a follow-up question and continue the same conversation."""
        if not self._messages:
            yield "[yellow]No active session.[/yellow]\n"
            return
        self._messages.append({"role": "user", "content": user_message})
        tools = [] if self._interview_mode else _TOOLS
        yield from self._run_loop(tools=tools)

    # ── Private loop ──────────────────────────────────────────────────

    def _run_loop(self, tools: list[dict] | None = None) -> Generator[str, None, None]:
        """Core tool-calling loop. Reads/writes self._messages."""
        if tools is None:
            tools = _TOOLS
        max_turns = 20  # safety cap
        empty_turns = 0  # consecutive turns with no content and no tool calls

        for _ in range(max_turns):
            full_content = ""
            tool_calls_acc: list[dict] = []

            try:
                with self.client.chat.stream(
                    model=self.model,
                    messages=self._messages,
                    tools=tools or None,
                ) as stream:
                    for event in stream:
                        try:
                            choice = event.data.choices[0]
                        except (AttributeError, IndexError):
                            continue

                        delta = choice.delta

                        if delta.content:
                            # content can be str or List[ContentChunk]
                            raw = delta.content
                            text = (
                                raw
                                if isinstance(raw, str)
                                else "".join(
                                    getattr(c, "text", "") for c in raw
                                )
                            )
                            if text:
                                full_content += text
                                yield text

                        if delta.tool_calls:
                            for tc_delta in delta.tool_calls:
                                tc_id = getattr(tc_delta, "id", None) or ""
                                fn = getattr(tc_delta, "function", None)
                                fn_name = getattr(fn, "name", None) if fn else None
                                fn_args = getattr(fn, "arguments", None) if fn else None

                                # Look up existing entry by id, then by index fallback
                                entry = None
                                if tc_id:
                                    for e in tool_calls_acc:
                                        if e["id"] == tc_id:
                                            entry = e
                                            break
                                if entry is None:
                                    idx = getattr(tc_delta, "index", None)
                                    if idx is None:
                                        idx = len(tool_calls_acc)
                                    while len(tool_calls_acc) <= idx:
                                        tool_calls_acc.append(
                                            {"id": "", "name": "", "args_str": ""}
                                        )
                                    entry = tool_calls_acc[idx]

                                if tc_id and not entry["id"]:
                                    entry["id"] = tc_id
                                if fn_name:
                                    # Names arrive complete in one chunk (unlike args).
                                    # Using += caused corruption when Mistral re-sent the
                                    # name on every delta, producing "narratenarrateerror".
                                    if not entry["name"]:
                                        entry["name"] = fn_name
                                if fn_args is not None:
                                    # arguments can be a pre-parsed dict or a partial str
                                    if isinstance(fn_args, dict):
                                        entry["args_str"] = json.dumps(fn_args)
                                    else:
                                        entry["args_str"] += fn_args

            except Exception as exc:
                safe = str(exc).replace("[", r"\[").replace("\n", " ")
                yield f"\n[bold red]Agent error: {safe}[/bold red]\n"
                break

            # Empty response — model returned nothing; retry with a nudge
            if not full_content and not tool_calls_acc:
                empty_turns += 1
                if empty_turns >= 3:
                    yield (
                        "\n[yellow]Model did not respond after 3 attempts. "
                        "Please restart the session.[/yellow]\n"
                    )
                    break
                yield "\n[dim]No response received, retrying…[/dim]\n"
                self._messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Please begin solving the problem following the "
                            "workflow in the system prompt."
                        ),
                    }
                )
                continue

            empty_turns = 0  # reset on any non-empty turn

            # No tool calls → agent is done
            if not tool_calls_acc:
                break

            # Append assistant turn (with tool calls)
            self._messages.append(
                {
                    "role": "assistant",
                    "content": full_content or "",
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": tc["args_str"],
                            },
                        }
                        for tc in tool_calls_acc
                    ],
                }
            )

            # Execute tools and append results
            for tc in tool_calls_acc:
                name = tc["name"]
                yield f"\n[dim]⚙  Calling {name}…[/dim]\n"
                try:
                    args = json.loads(tc["args_str"]) if tc["args_str"] else {}
                    result = self._execute_tool(name, args)
                    if name == "run_code":
                        self._approaches_tried += 1
                    result_str = (
                        json.dumps(result) if not isinstance(result, str) else result
                    )
                except Exception as exc:
                    result_str = json.dumps({"error": str(exc)})

                # Show a compact preview of the result (collapse newlines so
                # the line-buffered RichLog never receives a half-open markup tag)
                preview = result_str[:300].replace("\n", " ") + (
                    "…" if len(result_str) > 300 else ""
                )
                yield f"[dim]   → {preview}[/dim]\n\n"

                self._messages.append(
                    {
                        "role": "tool",
                        "content": result_str,
                        "tool_call_id": tc["id"],
                        "name": name,
                    }
                )

    # ── Helpers ───────────────────────────────────────────────────────

    def last_code_block(self) -> str:
        """Return the last Python code block from the conversation, or ''.

        Searches assistant messages in reverse so follow-up answers take
        priority over the original session code.
        """
        import re

        pattern = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL)
        for msg in reversed(self._messages):
            if msg.get("role") == "assistant":
                content = msg.get("content") or ""
                blocks = pattern.findall(content)
                if blocks:
                    return blocks[-1].strip()
        return ""

    def _build_prompt(
        self, challenge: Challenge, mode: str, user_code: str
    ) -> str:
        if mode == "interview":
            desc = (challenge.description or "")[:600]
            return (
                f"Problem: {challenge.title} ({challenge.difficulty}).\n\n"
                f"{desc}\n\n"
                "Begin the interview now. Greet the candidate, state the problem title "
                "and difficulty, then ask them to walk you through their initial approach. "
                "Keep it to 3 sentences."
            )
        parts = [
            f"# Problem: {challenge.title}",
            f"**Difficulty:** {challenge.difficulty}",
            f"**Topics:** {', '.join(challenge.topics or [])}",
            "",
            "## Description",
            challenge.description or "(no description available)",
            "",
        ]
        if challenge.python_snippet:
            parts += ["## Starter Code", "```python", challenge.python_snippet, "```", ""]
        if challenge.test_cases:
            case_lines = []
            raw_lines = []
            for i, (inputs, expected) in enumerate(
                zip(challenge.test_cases, challenge.expected_outputs or []), 1
            ):
                case_lines.append(f"Case {i}: {', '.join(inputs)} → {expected}")
                raw_lines.extend(inputs)
            raw_block = "\n".join(raw_lines)
            parts += [
                "## Example Test Cases",
                "\n".join(case_lines),
                "",
                f"When calling run_code(), use example_testcases_raw exactly as:\n```\n{raw_block}\n```",
                "",
            ]
        if mode == "coach" and user_code.strip():
            parts += [
                "## User's Attempt",
                "```python",
                user_code,
                "```",
            ]
        else:
            parts.append("Please solve this problem step by step using the workflow above.")
        return "\n".join(parts)

    def _execute_tool(self, name: str, args: dict) -> object:
        """Dispatch tool calls directly to skill module functions."""
        if name == "run_code":
            from skills.test_runner.server import run_code
            return run_code(**args)
        elif name == "narrate":
            from skills.voice_narrator.server import narrate
            return narrate(**args)
        elif name == "analyze_complexity":
            from skills.complexity_analyzer.server import analyze_complexity
            return analyze_complexity(**args)
        elif name == "explain_approach":
            from skills.teaching_mode.server import explain_approach
            return explain_approach(**args)
        else:
            return {"error": f"Unknown tool: {name}"}
