"""LeetVibe Vibe Agent — Mistral AI streaming agent with tool-calling loop."""

from __future__ import annotations

import concurrent.futures
import json
import re
import time
from typing import Generator

from mistralai import Mistral

from ..config import Config
from ..problem_loader import Problem

_CODE_BLOCK_RE = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL)

# Module-level cache for deterministic analyze_complexity results (keyed by hash of code)
_complexity_cache: dict[int, object] = {}

# ── System prompts ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are LeetVibe AI — an expert competitive programmer and patient teacher.

Follow this EXACT workflow for every problem. Never skip a step.

STEP 1 — UNDERSTAND
Restate the problem in your own words. Identify:
- The key constraint (what limits n? what are the value ranges?)
- Edge cases (empty input, single element, all duplicates, negatives)
- The likely algorithm family (two-pointer, DP, graph, hash-map, etc.)

STEP 2 — BRUTE FORCE
Write the simplest correct solution and explain every line.
Call run_code() to validate it. If any test fails: debug, fix, and call run_code() again until all pass.

STEP 3 — ANALYSE BRUTE FORCE
Call analyze_complexity() on the brute-force code.
State explicitly: "This is O(?) time / O(?) space because …"
Identify the bottleneck — what repeated work makes it slow?

STEP 4 — KEY INSIGHT
Name the optimization idea that eliminates the bottleneck. Explain it clearly in plain text.

STEP 5 — OPTIMAL SOLUTION
Write the optimized solution. Explain every change from the brute-force.
Call run_code() to validate it. If any test fails: debug, fix, and call run_code() again.

STEP 6 — ANALYSE OPTIMAL
Call analyze_complexity() on the optimal code.
Compare: "We improved from O(?) → O(?) by eliminating …"

STEP 7 — EXPLAIN APPROACH
Call explain_approach() with approach="optimal" to generate a structured walkthrough.

STEP 8 — SYNTHESIS
Without calling any tools, write a single focused paragraph (4–6 sentences) that:
- Names the core insight that makes the optimal solution work.
- Traces the journey: what made the brute force slow and exactly what eliminated that bottleneck.
- States the final time and space complexity and why the problem constraints make further improvement impossible.
Write it as a crisp, memorable takeaway — the one paragraph a developer should carry away from this session.

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

STEP 1 — TEST USER'S CODE
Call run_code() using the user's code exactly as written.
Report clearly: "Your code passes X/Y test cases."

STEP 2 — DIAGNOSE
Examine the user's code carefully. Identify and explain every issue:
- Bugs (incorrect logic, wrong edge case handling, off-by-one errors)
- Inefficiencies (nested loops, redundant passes, unnecessary data structures)
- Code quality (naming, readability, structure)
Be specific — point to exact lines and explain why each is problematic.
If the code passes all tests, note that it is correct but focus on efficiency.

STEP 3 — ANALYSE USER'S COMPLEXITY
Call analyze_complexity() on the user's code.
State: "Your solution is O(?) time / O(?) space because …"
Explain whether this is acceptable given the problem's constraints.
Identify the bottleneck — what makes it slow or memory-heavy?

STEP 4 — GUIDED HINTS
Do NOT reveal the optimal solution yet. Guide the user toward it with questions and nudges:
- Point to the bottleneck: "Notice that this part repeats work — what's redundant?"
- Suggest a direction: "What data structure would let you look this up in O(1)?"
- Give one concrete hint that bridges their approach to the optimal one.

STEP 5 — OPTIMAL SOLUTION
Now reveal the optimal solution with a full line-by-line explanation.
Explain every change from the user's version and why it was made.
Call run_code() to validate it. If any test fails: debug, fix, and call run_code() again.

STEP 6 — COMPARE
Side-by-side comparison of the user's approach vs the optimal:
- What changed and why
- Complexity improvement: O(?) → O(?)
- The single key insight that transforms one into the other

STEP 7 — EXPLAIN APPROACH
Call explain_approach() with approach="optimal" to generate a structured walkthrough.

STEP 8 — SYNTHESIS
Without calling any tools, write a single focused paragraph (4–6 sentences) that:
- Names the core insight that makes the optimal solution work.
- Traces the journey: what made the user's original approach slow and exactly what eliminated that bottleneck.
- States the final time and space complexity and why the problem constraints make further improvement impossible.
Write it as a crisp, memorable takeaway — the one paragraph the user should carry away from this coaching session.

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

    # ── Public API ────────────────────────────────────────────────────

    def solve_streaming(
        self,
        problem: Problem,
        mode: str = "learn",
        user_code: str = "",
    ) -> Generator[str, None, None]:
        """Initialise a new session then yield streaming text chunks."""
        if mode == "coach" and user_code.strip():
            system = COACH_PROMPT
        else:
            system = SYSTEM_PROMPT
        self._messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": self._build_prompt(problem, mode, user_code)},
        ]
        self._start_ts = time.time()
        self._approaches_tried = 0
        yield from self._run_loop(tools=_TOOLS)
        self._compress_tool_results()
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
        yield from self._run_loop(tools=_TOOLS)
        self._compress_tool_results()

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

            # No tool calls → agent is done; save the response to history
            if not tool_calls_acc:
                if full_content:
                    self._messages.append({"role": "assistant", "content": full_content})
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

            # Execute tools — in parallel when multiple calls arrive in one turn
            _TOOL_ICONS = {
                "run_code":           "▶",
                "analyze_complexity": "◈",
                "explain_approach":   "✎",
            }

            # Announce all tool calls upfront (ordered)
            for tc in tool_calls_acc:
                icon = _TOOL_ICONS.get(tc["name"], "⚙")
                yield f"\n[dim]│ Tool call:[/dim] [bold dim]{icon} {tc['name']}[/bold dim]\n"

            # Execute — parallel when more than one tool call in this turn
            def _run_tc(tc: dict) -> str:
                try:
                    args = json.loads(tc["args_str"]) if tc["args_str"] else {}
                    result = self._execute_tool(tc["name"], args)
                    return json.dumps(result) if not isinstance(result, str) else result
                except Exception as exc:
                    return json.dumps({"error": str(exc)})

            if len(tool_calls_acc) > 1:
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=len(tool_calls_acc)
                ) as pool:
                    futures = [pool.submit(_run_tc, tc) for tc in tool_calls_acc]
                    tc_results = [f.result() for f in futures]
            else:
                tc_results = [_run_tc(tool_calls_acc[0])]

            # Yield result previews and append tool messages (ordered)
            for tc, result_str in zip(tool_calls_acc, tc_results):
                if tc["name"] == "run_code":
                    self._approaches_tried += 1
                # Show a compact preview (collapse newlines, strip markdown markers)
                preview = result_str[:300].replace("\n", " ") + (
                    "…" if len(result_str) > 300 else ""
                )
                preview = re.sub(r"#{1,3}\s+", "", preview)
                preview = re.sub(r"\*\*(.+?)\*\*", r"\1", preview)
                yield f"[dim]│  → {preview}[/dim]\n\n"

                self._messages.append(
                    {
                        "role": "tool",
                        "content": result_str,
                        "tool_call_id": tc["id"],
                        "name": tc["name"],
                    }
                )

    # ── Helpers ───────────────────────────────────────────────────────

    def last_code_block(self) -> str:
        """Return the last Python code block from the conversation, or ''.

        Searches assistant messages in reverse so follow-up answers take
        priority over the original session code.
        """
        for msg in reversed(self._messages):
            if msg.get("role") == "assistant":
                content = msg.get("content") or ""
                blocks = _CODE_BLOCK_RE.findall(content)
                if blocks:
                    return blocks[-1].strip()
        return ""

    def _build_prompt(
        self, problem: Problem, mode: str, user_code: str
    ) -> str:
        parts = [
            f"# Problem: {problem.title}",
            f"**Difficulty:** {problem.difficulty}",
            f"**Topics:** {', '.join(problem.topics or [])}",
            "",
            "## Description",
            problem.description or "(no description available)",
            "",
        ]
        if problem.python_snippet:
            parts += ["## Starter Code", "```python", problem.python_snippet, "```", ""]
        if problem.test_cases:
            case_lines = []
            raw_lines = []
            for i, (inputs, expected) in enumerate(
                zip(problem.test_cases, problem.expected_outputs or []), 1
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
            from .skills.test_runner.server import run_code
            return run_code(**args)
        elif name == "analyze_complexity":
            from .skills.complexity_analyzer.server import analyze_complexity
            cache_key = hash(args.get("code", ""))
            if cache_key not in _complexity_cache:
                _complexity_cache[cache_key] = analyze_complexity(**args)
            return _complexity_cache[cache_key]
        elif name == "explain_approach":
            from .skills.teaching_mode.server import explain_approach
            return explain_approach(**args)
        else:
            return {"error": f"Unknown tool: {name}"}

    def _compress_tool_results(self) -> None:
        """Replace verbose tool result payloads with compact summaries in-place.

        Called after _run_loop completes so the model has already consumed the
        full results. Reduces token cost for any follow-up chat_streaming calls.
        """
        # Build call_id → tool_name lookup from assistant messages
        call_id_to_name: dict[str, str] = {}
        for msg in self._messages:
            if msg.get("role") == "assistant":
                for tc in msg.get("tool_calls") or []:
                    tc_id = tc.get("id", "")
                    name = (tc.get("function") or {}).get("name", "")
                    if tc_id and name:
                        call_id_to_name[tc_id] = name

        for i, msg in enumerate(self._messages):
            if msg.get("role") != "tool":
                continue
            content = msg.get("content", "")
            if not isinstance(content, str) or len(content) <= 300:
                continue

            tool_name = call_id_to_name.get(msg.get("tool_call_id", ""), "")
            try:
                data = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                self._messages[i] = {**msg, "content": content[:300]}
                continue

            if tool_name == "run_code":
                compact: object = {
                    "passed": data.get("passed", 0),
                    "total": data.get("total", 0),
                }
                if data.get("passed", 0) < data.get("total", 0):
                    for r in data.get("results", []):
                        if not r.get("passed"):
                            compact["first_failure"] = {  # type: ignore[index]
                                "input": str(r.get("input", ""))[:80],
                                "expected": str(r.get("expected", ""))[:40],
                                "actual": str(r.get("actual", ""))[:40],
                            }
                            break
            elif tool_name == "explain_approach":
                compact = str(data)[:300]
            else:
                compact = str(data)[:300]

            self._messages[i] = {
                **msg,
                "content": json.dumps(compact) if isinstance(compact, dict) else compact,
            }


# ── InterviewAgent ────────────────────────────────────────────────────────────


class InterviewAgent:
    """Dedicated interview agent — no tool calls, sliding-window context."""

    _WINDOW = 10

    def __init__(self, config: Config) -> None:
        self.client = Mistral(api_key=config.mistral_api_key)
        self.model = config.mistral_model
        self._messages: list[dict] = []

    def start_streaming(self, problem: Problem) -> Generator[str, None, None]:
        self._messages = [
            {"role": "system", "content": INTERVIEW_PROMPT},
            {"role": "user", "content": self._build_prompt(problem)},
        ]
        yield from self._stream()

    def chat_streaming(self, user_message: str) -> Generator[str, None, None]:
        self._messages.append({"role": "user", "content": user_message})
        yield from self._stream()

    def last_code_block(self) -> str:
        return ""

    def _build_prompt(self, problem: Problem) -> str:
        desc = (problem.description or "")[:600]
        return (
            f"Problem: {problem.title} ({problem.difficulty}).\n\n"
            f"{desc}\n\n"
            "Begin the interview now. Greet the candidate, state the problem title "
            "and difficulty, then ask them to walk you through their initial approach. "
            "Keep it to 3 sentences."
        )

    def _stream(self) -> Generator[str, None, None]:
        api_messages = (
            [self._messages[0]]
            + self._messages[max(1, len(self._messages) - self._WINDOW):]
        )
        full_content = ""
        try:
            with self.client.chat.stream(
                model=self.model,
                messages=api_messages,
            ) as stream:
                for event in stream:
                    try:
                        choice = event.data.choices[0]
                    except (AttributeError, IndexError):
                        continue
                    delta = choice.delta
                    if delta.content:
                        raw = delta.content
                        text = (
                            raw
                            if isinstance(raw, str)
                            else "".join(getattr(c, "text", "") for c in raw)
                        )
                        if text:
                            full_content += text
                            yield text
        except Exception as exc:
            safe = str(exc).replace("[", r"\[").replace("\n", " ")
            yield f"\n[bold red]Agent error: {safe}[/bold red]\n"
            return
        self._messages.append({"role": "assistant", "content": full_content})


# ── ConceptAgent ──────────────────────────────────────────────────────────────

_CONCEPT_SYSTEM = """\
You are LeetVibe AI — a focused algorithm educator and DS&A mentor.
Answer questions about data structures, algorithms, and patterns clearly and concisely.
Explain concepts with concrete examples. Use plain language first, then formalize.
When relevant, connect explanations back to the problem the user just worked on.
Use Rich markup: [bold] for key terms, [dim] for secondary info, triple backticks for code.\
"""


class ConceptAgent:
    """Lightweight concept Q&A agent using mistral_qa_model."""

    def __init__(self, config: Config, session_summary: dict) -> None:
        self.client = Mistral(api_key=config.mistral_api_key)
        self.model = config.mistral_qa_model
        self._messages: list[dict] = [
            {"role": "system", "content": self._build_system(session_summary)}
        ]

    @staticmethod
    def _build_system(summary: dict) -> str:
        parts = [_CONCEPT_SYSTEM]
        if summary:
            parts.append("\nSession context:")
            if summary.get("title"):
                parts.append(f"- Problem: {summary['title']} ({summary.get('difficulty', '')})")
            if summary.get("topics"):
                parts.append(f"- Topics: {', '.join(summary['topics'])}")
            if summary.get("algorithm_pattern"):
                parts.append(f"- Algorithm pattern: {summary['algorithm_pattern']}")
            if summary.get("complexity"):
                parts.append(f"- Complexity: {summary['complexity']}")
            if summary.get("synthesis"):
                parts.append(f"- Synthesis: {summary['synthesis']}")
        return "\n".join(parts)

    def chat_streaming(self, user_message: str) -> Generator[str, None, None]:
        self._messages.append({"role": "user", "content": user_message})
        full_content = ""
        try:
            with self.client.chat.stream(
                model=self.model,
                messages=self._messages,
            ) as stream:
                for event in stream:
                    try:
                        choice = event.data.choices[0]
                    except (AttributeError, IndexError):
                        continue
                    delta = choice.delta
                    if delta.content:
                        raw = delta.content
                        text = (
                            raw
                            if isinstance(raw, str)
                            else "".join(getattr(c, "text", "") for c in raw)
                        )
                        if text:
                            full_content += text
                            yield text
        except Exception as exc:
            safe = str(exc).replace("[", r"\[").replace("\n", " ")
            yield f"\n[bold red]Agent error: {safe}[/bold red]\n"
            return
        self._messages.append({"role": "assistant", "content": full_content})
