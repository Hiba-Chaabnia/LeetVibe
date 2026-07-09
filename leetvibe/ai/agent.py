"""LeetVibe Vibe Agent — Mistral AI streaming agent with tool-calling loop."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import re
import time
from typing import Generator

from mistralai import Mistral

from ..config import Config
from ..problem_loader import Problem

_CODE_BLOCK_RE = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL)

# Marks the real end of the STEP 1-7 workflow (learn/pair system prompts both
# end with this). Used to tell "the model finished" apart from "the model
# stopped mid-workflow without calling a required tool" — see _run_loop's
# no-tool-calls branch: both look identical (content, no tool_calls) unless
# we check for this line.
_PATTERN_LINE_RE = re.compile(
    r"^[-•\s]*\**pattern\**\s*:?\s*\**\s*`?([\w-]+)`?\**\s*\.?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Module-level cache for deterministic analyze_complexity results (keyed by hash of code).
# Bounded FIFO so long-running sessions with many distinct code variations can't leak
# memory for the lifetime of the process.
_complexity_cache: dict[int, object] = {}
_COMPLEXITY_CACHE_MAX = 200

# ── System prompts ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are LeetVibe AI — an expert competitive programmer and patient teacher.
This is a one-way walkthrough: the user reads your complete session at the end
and can only reply afterwards, in a follow-up chat.

Follow this EXACT workflow for every problem. Never skip a step.

STEP 1 — UNDERSTAND
The full problem statement is already on the user's screen — do not restate it.
Summarise the task in one sentence, then identify:
- The key constraint (what limits n? what are the value ranges?)
- Edge cases (empty input, single element, all duplicates, negatives)

STEP 2 — FIRST PASS
Write the simplest correct solution and explain every line.
Print it in a ```python fenced block in your message — the user must see the
exact code, not just its result.
Keep it feasible for the given constraints — if the naive approach is too slow
to actually execute (e.g. exponential on large inputs), present it, say why
running it is infeasible, and continue without calling run_code().
Otherwise call run_code() to validate the code you just printed. If any test
fails: debug, print the corrected code again, and call run_code() again.

STEP 3 — SPOT THE BOTTLENECK
Call analyze_complexity() on the brute-force code.
State explicitly: "This is O(?) time / O(?) space because …"
Identify the bottleneck — what repeated work makes it slow?

STEP 4 — THE INSIGHT
Name the optimization idea that eliminates the bottleneck. Explain it clearly in plain text.
If the brute force is already optimal for these constraints, say so plainly and
explain why nothing better exists — do not invent a fake improvement.

STEP 5 — OPTIMIZE
Write the optimized solution. Explain every change from the brute-force.
Print it in a ```python fenced block in your message — the user must see the
exact code, not just its result.
Call run_code() to validate the code you just printed. If any test fails:
debug, print the corrected code again, and call run_code() again.

STEP 6 — MEASURE THE GAIN
Call analyze_complexity() on the optimal code.
Compare: "We improved from O(?) → O(?) by eliminating …"

STEP 7 — TAKEAWAY
Without calling any tools, write a single focused paragraph (4–6 sentences) that:
- Names the core insight that makes the optimal solution work.
- Traces the journey: what made the brute force slow and exactly what eliminated that bottleneck.
- States the final time and space complexity and why the problem constraints make further improvement impossible.
Write it as a crisp, memorable takeaway — then end with one short question the
user should try to answer, inviting them to reply in the chat.
After that paragraph, on its own final line, write exactly: Pattern: <slug>
(a short kebab-case name for the core algorithmic pattern, e.g. Pattern: two-pointer).
This line is parsed by the app and never shown to the user — do not reference
it in your prose or mention that you are writing it.

Rules:
- Begin every step with a line of exactly: STEP <number> — <TITLE> (titles as written above).
- Think out loud before every code block. Never write code without explaining the reasoning first.
- Never call run_code() with code you have not shown — every call must be immediately preceded by that exact code in a ```python fence in your message.
- Never skip a step, even for trivial problems (when brute force is already optimal, steps 4–6 shrink to honest one-liners rather than invented improvements).
- If run_code() still fails after 3 attempts, stop retrying — explain honestly what is failing and continue the workflow.
- Never write out tool results yourself — no result JSON, no test-result tables. Call the tool and wait; the app displays the real results.
- analyze_complexity() is an AST heuristic and cannot see recursion — when its estimate is wrong, say so and state the correct complexity yourself.
- Format with markdown only: **bold** for key terms, `backticks` for identifiers, triple-backtick fences for all code. Never use Rich markup tags like [bold] or [dim].\
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

PAIR_PROMPT = """\
You are LeetVibe AI — a patient and encouraging coding coach.
The user has already attempted the problem. Do NOT solve it from scratch.
Your job is to review their attempt, diagnose issues, and walk them to the optimal solution.
This is a one-way walkthrough: the user reads your complete session at the end
and can only reply afterwards, in a follow-up chat — never pose a question and wait.

Follow this EXACT pair programming workflow. Never skip a step.

STEP 1 — RUN YOUR CODE
Call run_code() using the user's code exactly as written.
The results table is displayed automatically — interpret what it means; do not restate the pass/fail counts.

STEP 2 — DIAGNOSE
Examine the user's code carefully. Identify and explain every issue:
- Bugs (incorrect logic, wrong edge case handling, off-by-one errors)
- Inefficiencies (nested loops, redundant passes, unnecessary data structures)
- Code quality (naming, readability, structure)
Be specific — quote the exact code you mean (the user sees no line numbers) and explain why it is problematic.
If the code passes all tests, note that it is correct but focus on efficiency.

STEP 3 — YOUR COMPLEXITY
Call analyze_complexity() on the user's code.
State: "Your solution is O(?) time / O(?) space because …"
Explain whether this is acceptable given the problem's constraints.
Identify the bottleneck — what makes it slow or memory-heavy?

STEP 4 — BRIDGE THE GAP
Narrate the reasoning path from the user's approach to the optimal one — the
chain of hints a coach would give:
- Point at the bottleneck: what work is repeated or unnecessary?
- Pose the unlocking question (e.g. "what structure gives O(1) lookup here?")
  and answer it yourself in the next sentence — the user cannot answer mid-session.
- End with the one concrete idea that transforms their approach into the optimal one.
If their code is already optimal: congratulate them plainly, and use this step
for polish instead — naming, idioms, readability, and one alternative approach worth knowing.

STEP 5 — OPTIMIZE
Reveal the optimal solution with a full line-by-line explanation.
Explain every change from the user's version and why it was made.
Print it in a ```python fenced block in your message — the user must see the
exact code, not just its result.
Call run_code() to validate the code you just printed. If any test fails:
debug, print the corrected code again, and call run_code() again.
If the user's code was already optimal, do not re-present it as "the optimal
solution" — credit their version and show only meaningful refinements.

STEP 6 — COMPARE
Side-by-side comparison of the user's approach vs the optimal:
- What changed and why
- Complexity improvement: O(?) → O(?)
- The single key insight that transforms one into the other

STEP 7 — TAKEAWAY
Without calling any tools, write a single focused paragraph (4–6 sentences) that:
- Names the core insight that makes the optimal solution work.
- Traces the journey: what made the user's original approach slow and exactly what eliminated that bottleneck.
- States the final time and space complexity and why the problem constraints make further improvement impossible.
Write it as a crisp, memorable takeaway — then end with one short question the
user should try to answer, inviting them to reply in the chat.
After that paragraph, on its own final line, write exactly: Pattern: <slug>
(a short kebab-case name for the core algorithmic pattern, e.g. Pattern: two-pointer).
This line is parsed by the app and never shown to the user — do not reference
it in your prose or mention that you are writing it.

Rules:
- Begin every step with a line of exactly: STEP <number> — <TITLE> (titles as written above).
- Always be encouraging — frame issues as learning opportunities, not failures.
- Never call run_code() with new code you have not shown — every call in step 5 must be immediately preceded by that exact code in a ```python fence in your message (step 1 tests the user's own code, already visible in their editor).
- Never skip a step. When the user's code is already optimal, steps 4–6 become polish, refinements, and comparison with alternatives instead of hints and a reveal.
- If run_code() still fails after 3 attempts, stop retrying — explain honestly what is failing and continue the workflow.
- Never write out tool results yourself — no result JSON, no test-result tables. Call the tool and wait; the app displays the real results.
- analyze_complexity() is an AST heuristic and cannot see recursion — when its estimate is wrong, say so and state the correct complexity yourself.
- Format with markdown only: **bold** for key terms, `backticks` for identifiers, triple-backtick fences for all code. Never use Rich markup tags like [bold] or [dim].\
"""


def _prompt_version(prompt: str) -> str:
    """Short fingerprint of a prompt's exact text.

    Saved chat history is only safe to resume if it was built under the
    exact prompt text still in force — any edit (step count, headers,
    tool-call requirements, even wording) can change what the model expects
    next or how the UI parses its output. Deriving the version from a hash
    of the prompt itself means old sessions are automatically invalidated
    whenever SYSTEM_PROMPT/PAIR_PROMPT changes, with no separate constant
    to remember to bump — see upsert_session()/db.py.
    """
    return hashlib.sha256(prompt.encode()).hexdigest()[:12]


SYSTEM_PROMPT_VERSION = _prompt_version(SYSTEM_PROMPT)
PAIR_PROMPT_VERSION = _prompt_version(PAIR_PROMPT)

# Known tools + their transcript icons. Also serves as the allow-list: a
# streamed tool call whose name isn't here is model derailment (e.g. fabricated
# result JSON in the name field) and must never execute, display, or persist.
_TOOL_ICONS = {
    "run_code":           "▶",
    "analyze_complexity": "◈",
}


def _canonical_args(args_str: str) -> str:
    """Normalise a tool-call arguments string for duplicate detection.

    Mistral sometimes streams the same call twice with cosmetic differences
    (whitespace, JSON key order) — canonical JSON makes them compare equal.
    """
    try:
        return json.dumps(json.loads(args_str), sort_keys=True)
    except Exception:
        return args_str


def _collapse(text: str, limit: int) -> str:
    """Flatten whitespace and truncate for single-line display."""
    flat = re.sub(r"\s+", " ", str(text)).strip()
    return (flat[: limit - 1] + "…") if len(flat) > limit else flat


def _tool_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    """Render a compact box-drawing table for tool-result display."""
    widths = [
        max(len(headers[i]), *(len(r[i]) for r in rows)) if rows else len(headers[i])
        for i in range(len(headers))
    ]

    def _row(cells: list[str]) -> str:
        return "│ " + " │ ".join(c.ljust(w) for c, w in zip(cells, widths)) + " │"

    top = "┌" + "┬".join("─" * (w + 2) for w in widths) + "┐"
    mid = "├" + "┼".join("─" * (w + 2) for w in widths) + "┤"
    bot = "└" + "┴".join("─" * (w + 2) for w in widths) + "┘"
    return [top, _row(headers), mid, *[_row(r) for r in rows], bot]


def _format_tool_result(name: str, result_str: str) -> tuple[str, list[str]]:
    """Human display of a tool result: (summary, detail lines).

    The caller renders the summary on the icon header line and each detail
    line indented behind a "│" bar; both render dim in the answer bubble
    """
    try:
        data = json.loads(result_str)
    except Exception:
        data = None
    if isinstance(data, dict):
        if "error" in data:
            return f"error: {_collapse(data['error'], 80)}", []
        if name == "run_code" and "cases" in data:
            cases = data.get("cases") or []
            passed = sum(1 for c in cases if c.get("passed"))
            total = len(cases)
            summary = (
                f"{passed}/{total} tests passed"
                if data.get("all_passed")
                else f"{total - passed}/{total} tests failed"
            )
            # Expected column only when the runner actually compared outputs
            has_expected = any(c.get("expected") for c in cases)
            rows = []
            for c in cases:
                # Failing cases show the error (or stdout) instead of the output
                out = c.get("output", "")
                if c.get("error"):
                    out = c["error"]
                elif not c.get("passed") and c.get("stdout"):
                    out = f"stdout: {c['stdout']}"
                row = [
                    str(c.get("case_num", "?")),
                    _collapse(c.get("input", ""), 40),
                ]
                if has_expected:
                    row.append(_collapse(c.get("expected", ""), 30))
                row += [
                    _collapse(out, 40),
                    "passed" if c.get("passed") else "failed",
                ]
                rows.append(row)
            headers = (
                ["#", "input", "expected output", "actual output", "status"]
                if has_expected
                else ["#", "input", "output", ""]
            )
            return summary, _tool_table(headers, rows)
        if name == "run_code" and "passed" in data and "total" in data:
            # _compress_tool_results() already collapsed the per-case list
            # away to save follow-up token cost — this is what replaying
            # saved history sees. Degraded (totals + first failure only)
            # but honest, instead of the raw "0/0" it used to show.
            passed, total = data["passed"], data["total"]
            summary = (
                f"{passed}/{total} tests passed"
                if passed == total
                else f"{total - passed}/{total} tests failed"
            )
            ff = data.get("first_failure")
            details = (
                _tool_table(
                    ["input", "expected", "actual"],
                    [[
                        _collapse(ff.get("input", ""), 40),
                        _collapse(ff.get("expected", ""), 30),
                        _collapse(ff.get("actual", ""), 40),
                    ]],
                )
                if ff
                else []
            )
            return summary, details
        if name == "analyze_complexity":
            t_val = data.get("time") or data.get("time_complexity") or ""
            s_val = data.get("space") or data.get("space_complexity") or ""
            if t_val or s_val:
                # Explanation format is "Time: <note>  Space: <note>" — split it
                # into per-metric reasons so the table shows the full result.
                explanation = str(data.get("explanation", ""))
                m = re.match(
                    r"\s*Time:\s*(.*?)\s+Space:\s*(.*)", explanation, re.DOTALL
                )
                if m:
                    t_reason, s_reason = m.group(1).strip(), m.group(2).strip()
                else:
                    t_reason, s_reason = explanation.strip(), ""
                rows = [
                    ["time", t_val or "?", _collapse(t_reason, 60)],
                    ["space", s_val or "?", _collapse(s_reason, 60)],
                ]
                # Empty summary: the header shows only the tool name — the
                # table carries the whole result.
                return "", _tool_table(["metric", "result", "reason"], rows)
    return _collapse(result_str, 80) or "done", []


def format_tool_block(name: str, result_str: str) -> str:
    """Build the icon-header + indented-details transcript block for one
    tool call. Shared by the live streaming loop and by history replay
    (session.py), which regenerates this same block from the saved
    (possibly _compress_tool_results()-compacted) tool JSON, since the
    live-formatted text itself is never persisted.
    """
    icon = _TOOL_ICONS.get(name, "⚙")
    summary, details = _format_tool_result(name, result_str)
    header = f"{icon} {name}"
    if summary:
        header += f" — {summary}"
    block = f"\n{header}\n"
    for detail in details:
        block += f"  {detail}\n"
    return block


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
        self._problem: Problem | None = None   # for expected-output injection
        self._last_tool_block: str | None = None  # suppress consecutive dupes
        self._workflow_active: bool = False    # True only during the guided STEP 1-7 run
        self._incomplete_nudges: int = 0       # guards against nudging forever

    # ── Public API ────────────────────────────────────────────────────

    def solve_streaming(
        self,
        problem: Problem,
        mode: str = "learn",
        user_code: str = "",
    ) -> Generator[str, None, None]:
        """Initialise a new session then yield streaming text chunks."""
        self._problem = problem
        if mode == "pair" and user_code.strip():
            system = PAIR_PROMPT
        else:
            system = SYSTEM_PROMPT
        self._messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": self._build_prompt(problem, mode, user_code)},
        ]
        self._start_ts = time.time()
        self._approaches_tried = 0
        self._workflow_active = True
        self._incomplete_nudges = 0
        yield from self._run_loop(tools=_TOOLS)
        self._compress_tool_results()

    def inject_history(self, messages: list[dict], problem: Problem | None = None) -> None:
        """Restore a saved conversation so follow-up questions have full context.

        Call this instead of solve_streaming() when resuming a prior session.
        The caller is responsible for prepending the system message.
        """
        self._messages = messages
        self._start_ts = time.time()
        if problem is not None:
            self._problem = problem

    def chat_streaming(self, user_message: str) -> Generator[str, None, None]:
        """Append a follow-up question and continue the same conversation."""
        if not self._messages:
            yield "[yellow]No active session.[/yellow]\n"
            return
        # Follow-up Q&A is never subject to the STEP 1-7 tool-call enforcement,
        # whether or not the guided workflow actually reached its Pattern line.
        self._workflow_active = False
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
                                # Prose breaks the "consecutive duplicate
                                # tool block" chain — allow re-display
                                self._last_tool_block = None
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

            # Drop stream-accumulation artifacts (missing id/name) and derailed
            # calls whose name isn't a known tool — Mistral occasionally packs
            # model garbage (fabricated result JSON + next-step text) into the
            # streamed function.name field.
            dropped_garbage = any(
                tc["name"] and tc["name"] not in _TOOL_ICONS for tc in tool_calls_acc
            )
            tool_calls_acc = [
                tc for tc in tool_calls_acc
                if tc["id"] and tc["name"] in _TOOL_ICONS
            ]

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

            # No tool calls → agent is either genuinely done, or it silently
            # stopped mid-workflow without making a required run_code/
            # analyze_complexity call (e.g. narrating a result it never
            # produced). Both look identical here (content, no tool_calls),
            # so check for the STEP 7 "Pattern:" line before trusting it.
            if not tool_calls_acc:
                if full_content:
                    self._messages.append({"role": "assistant", "content": full_content})
                    if _PATTERN_LINE_RE.search(full_content):
                        self._workflow_active = False
                if dropped_garbage:
                    # The model derailed mid-call — keep the session alive and
                    # steer it back instead of ending the workflow early.
                    self._messages.append({
                        "role": "user",
                        "content": (
                            "Continue the workflow from where you left off. "
                            "Do not fabricate tool results — call the tool and "
                            "wait for its real output."
                        ),
                    })
                    continue
                if self._workflow_active and self._incomplete_nudges < 2:
                    # Stopped before STEP 7 without calling a tool — nudge it
                    # back rather than silently ending the session with an
                    # unfinished (and possibly fabricated) walkthrough.
                    self._incomplete_nudges += 1
                    self._messages.append({
                        "role": "user",
                        "content": (
                            "You stopped before finishing the workflow (no "
                            "'Pattern: <slug>' line yet) and without calling "
                            "a tool. If you were about to validate code, call "
                            "run_code() or analyze_complexity() now instead of "
                            "describing a result — do not assume or narrate "
                            "what a tool call would return. Otherwise continue "
                            "the workflow from the next step."
                        ),
                    })
                    continue
                if self._workflow_active:
                    # Nudged twice and still no Pattern line — say so plainly
                    # instead of letting the transcript look like a finished
                    # walkthrough when the workflow actually stalled.
                    yield (
                        "\n[yellow]The walkthrough stopped before completing "
                        "all steps. You can ask a follow-up question below.[/yellow]\n"
                    )
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

            # The system prompt requires run_code() to be "immediately preceded"
            # by the exact code in a ```python fence in the same message — but
            # nothing enforced that, so the model could call run_code with code
            # it never printed (the tool call itself still carries real code
            # and returns real results, so it looks fine in the debug log —
            # the user just never sees the solution). Block execution in that
            # case instead of silently running it, so the model is forced to
            # print the code first and the transcript never shows a result
            # with no code above it.
            turn_has_code_fence = bool(_CODE_BLOCK_RE.search(full_content))

            # Execute tools — in parallel when multiple calls arrive in one turn
            def _run_tc(tc: dict) -> str:
                if tc["name"] == "run_code" and not turn_has_code_fence:
                    return json.dumps({
                        "error": (
                            "Rejected: no ```python code block was printed in "
                            "your message before this call. Print the exact "
                            "code in a fenced block first, then call run_code() "
                            "again on that same code."
                        )
                    })
                try:
                    args = json.loads(tc["args_str"]) if tc["args_str"] else {}
                    result = self._execute_tool(tc["name"], args)
                    return json.dumps(result) if not isinstance(result, str) else result
                except Exception as exc:
                    return json.dumps({"error": str(exc)})

            # The model occasionally emits the same call twice in one turn —
            # execute each distinct (name, canonical args) once, reuse the result.
            def _key(tc: dict) -> tuple[str, str]:
                return (tc["name"], _canonical_args(tc["args_str"]))

            distinct: list[dict] = []
            seen: set[tuple[str, str]] = set()
            for tc in tool_calls_acc:
                if _key(tc) not in seen:
                    seen.add(_key(tc))
                    distinct.append(tc)

            if len(distinct) > 1:
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=len(distinct)
                ) as pool:
                    futures = [pool.submit(_run_tc, tc) for tc in distinct]
                    results = [f.result() for f in futures]
            else:
                results = [_run_tc(distinct[0])]
            results_by_key = {_key(tc): r for tc, r in zip(distinct, results)}

            # One human-readable block per distinct call: icon header + details.
            # A block identical to the previous one (model re-ran the same call
            # in its next turn with no prose in between) is executed and
            # answered but not displayed again.
            for tc in distinct:
                if tc["name"] == "run_code":
                    self._approaches_tried += 1
                block = format_tool_block(tc["name"], results_by_key[_key(tc)])
                if block != self._last_tool_block:
                    self._last_tool_block = block
                    yield block

            # Every tool_call id still gets its result message (API requirement)
            for tc in tool_calls_acc:
                self._messages.append(
                    {
                        "role": "tool",
                        "content": results_by_key[_key(tc)],
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
        if mode == "pair" and user_code.strip():
            parts += [
                "## User's Attempt",
                "```python",
                user_code,
                "```",
            ]
        else:
            parts.append("Please solve this problem step by step using the workflow above.")
        return "\n".join(parts)

    def _inject_expected_outputs(self, args: dict) -> None:
        """Attach the problem's expected outputs to a run_code call.

        Only when the model runs the canonical example cases verbatim — a
        custom debug case must not be compared against misaligned answers.
        """
        problem = self._problem
        if problem is None or "expected_outputs" in args:
            return
        expected = getattr(problem, "expected_outputs", None) or []
        if not expected:
            return
        canonical_lines: list[str] = []
        for inputs in problem.test_cases or []:
            canonical_lines.extend(ln.strip() for ln in inputs if ln.strip())
        supplied_lines = [
            ln.strip()
            for ln in str(args.get("example_testcases_raw", "")).splitlines()
            if ln.strip()
        ]
        if supplied_lines and supplied_lines == canonical_lines:
            args["expected_outputs"] = list(expected)

    def _execute_tool(self, name: str, args: dict) -> object:
        """Dispatch tool calls directly to skill module functions."""
        if name == "run_code":
            from .skills.test_runner.server import run_code
            self._inject_expected_outputs(args)
            return run_code(**args)
        elif name == "analyze_complexity":
            from .skills.complexity_analyzer.server import analyze_complexity
            cache_key = hash(args.get("code", ""))
            if cache_key not in _complexity_cache:
                if len(_complexity_cache) >= _COMPLEXITY_CACHE_MAX:
                    _complexity_cache.pop(next(iter(_complexity_cache)))
                _complexity_cache[cache_key] = analyze_complexity(**args)
            return _complexity_cache[cache_key]
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
                # run_code's actual shape is {"cases": [...], "all_passed": bool} —
                # no top-level passed/total/results keys. Reading those (as this
                # used to) always fell back to 0/0, silently corrupting every
                # compacted result to "0/0 tests" regardless of the real outcome.
                cases = data.get("cases") or []
                total = len(cases)
                passed = sum(1 for c in cases if c.get("passed"))
                compact: object = {"passed": passed, "total": total}
                if passed < total:
                    for c in cases:
                        if not c.get("passed"):
                            compact["first_failure"] = {  # type: ignore[index]
                                "input": str(c.get("input", ""))[:80],
                                "expected": str(c.get("expected", ""))[:40],
                                "actual": str(c.get("output", ""))[:40],
                            }
                            break
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


def stream_mistral_chunks(
    client: Mistral, model: str, messages: list[dict]
) -> Generator[str, None, None]:
    """Yield text chunks from a Mistral streaming chat call.

    Shared by every Mistral streaming call site (VibeAgent, ConceptAgent, the
    Playbook's inline chat) so the event-shape handling — delta.content can be
    a plain string or a list of content-part objects — can't silently drift
    between separately-maintained copies. Raises on failure; callers decide
    how to surface/recover from that (inline error text vs. a dedicated error
    bubble, rolling back pending history, ...).
    """
    with client.chat.stream(model=model, messages=messages) as stream:
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
                    yield text


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
            for text in stream_mistral_chunks(self.client, self.model, self._messages):
                full_content += text
                yield text
        except Exception as exc:
            safe = str(exc).replace("[", r"\[").replace("\n", " ")
            yield f"\n[bold red]Agent error: {safe}[/bold red]\n"
            return
        self._messages.append({"role": "assistant", "content": full_content})
