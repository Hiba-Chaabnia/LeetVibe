"""Code execution engine for LeetVibe.

Runs Python solution code against test cases and returns per-case results.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import re
import traceback
from dataclasses import dataclass
from typing import Any


@dataclass
class CaseResult:
    case_num: int
    inputs: list
    output: Any = None
    expected: str = ""
    passed: bool | None = None  # None = no expected to compare against
    error: str = ""
    stdout: str = ""


# ---------------------------------------------------------------------------
# Common imports injected into every exec namespace so solutions that rely on
# standard library modules (collections, heapq, math, etc.) work without
# explicitly importing them.
# ---------------------------------------------------------------------------
_IMPORTS_PRELUDE = (
    "import collections\n"
    "import heapq\n"
    "import math\n"
    "import itertools\n"
    "import functools\n"
    "import bisect\n"
    "import string\n"
    "import re as _re\n"
    "from collections import defaultdict, Counter, deque, OrderedDict\n"
    "from heapq import heappush, heappop, heapify\n"
    "from functools import lru_cache, reduce\n"
    "from itertools import accumulate, product, permutations, combinations, chain\n"
    "from bisect import bisect_left, bisect_right, insort\n"
    "from math import inf, gcd, floor, ceil, sqrt, log2, factorial\n"
)

# ---------------------------------------------------------------------------
# Typing names injected into every exec namespace so LeetCode snippets that
# use List[int], Optional[str], Dict[str, int], etc. compile without error.
# ---------------------------------------------------------------------------
_TYPING_PRELUDE = (
    "from typing import ("
    "Any, Callable, Dict, FrozenSet, Generator, Generic, Iterable, Iterator, "
    "List, Mapping, MutableMapping, MutableSequence, MutableSet, NamedTuple, "
    "Optional, Sequence, Set, SupportsFloat, SupportsInt, Tuple, Type, Union"
    ")\n"
)

# ---------------------------------------------------------------------------
# LeetCode data structure definitions injected so solutions that reuse the
# class name (or that forget to define it) still compile and run correctly.
# The solution's own definition will overwrite these if it re-declares them.
# ---------------------------------------------------------------------------
_DATASTRUCTURE_PRELUDE = """\
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    def __repr__(self):
        return f"TreeNode({self.val})"

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
    def __repr__(self):
        return f"ListNode({self.val})"

class Node:
    def __init__(self, val=0, left=None, right=None, next=None, children=None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next
        self.children = children or []
    def __repr__(self):
        return f"Node({self.val})"
"""


_BLOCK_KEYWORDS = frozenset({
    "if", "elif", "else", "for", "while", "with", "try", "except", "finally",
    "def", "async", "class",
})


def _is_block_opener(line: str) -> bool:
    """Return True only for real Python block-opening lines.

    Rejects comment lines and continuation lines (e.g. a multi-line ``if``
    whose closing ``):`  sits on its own line) so that ``_fill_empty_bodies``
    never inserts a spurious ``pass`` after them.
    """
    stripped = line.lstrip()
    if not stripped.rstrip().endswith(":"):
        return False
    if stripped.startswith("#"):
        return False
    first_word = stripped.split()[0] if stripped.split() else ""
    return first_word in _BLOCK_KEYWORDS


def _fill_empty_bodies(code: str) -> str:
    """Insert `pass` into any empty def/class body so the code compiles.

    LeetCode starter snippets end with trailing whitespace after the colon,
    which Python 3.12 rejects with IndentationError.
    """
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    paren_depth = 0
    for i, raw_line in enumerate(lines):
        out.append(raw_line)
        line = raw_line.rstrip("\r\n")
        depth_at_start = paren_depth
        for ch in line:
            if ch in "([{":
                paren_depth += 1
            elif ch in ")]}":
                paren_depth = max(0, paren_depth - 1)
        # Lines inside an open parenthesised expression are continuations,
        # never block openers — even if they start with a keyword like 'for'.
        if depth_at_start > 0 or not _is_block_opener(line):
            continue
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        current_indent = len(line) - len(line.lstrip())
        if j >= len(lines):
            out.append(" " * (current_indent + 4) + "pass\n")
        else:
            next_indent = len(lines[j]) - len(lines[j].lstrip())
            if next_indent <= current_indent:
                out.append(" " * (current_indent + 4) + "pass\n")
    return "".join(out)


def _find_caller(user_code: str, namespace: dict, func_name: str):
    """Return a callable(*inputs) -> output, or None if nothing matches.

    Uses the user's source AST to discover exactly which class/function names
    were defined, then looks them up in the exec namespace directly — avoiding
    false hits from typing imports or other injected names.

    Search order:
    1. Any class the user defined that has a method named *func_name*.
    2. A standalone function named *func_name* in the user's code.
    3. Fallback: namespace scan (in case AST parse fails).

    A fresh instance is created per call so test cases don't share state.
    """
    class_names: list[str] = []
    top_func_names: list[str] = []
    try:
        tree = ast.parse(user_code)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_names.append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                top_func_names.append(node.name)
    except SyntaxError:
        pass

    def _make_method_caller(cls, fn):
        def _call(*inputs):
            return getattr(cls(), fn)(*inputs)
        return _call

    for cname in class_names:
        obj = namespace.get(cname)
        if obj is not None and callable(getattr(obj, func_name, None)):
            return _make_method_caller(obj, func_name)

    # Prefer exact match for func_name; fall back to first callable
    if func_name in top_func_names:
        obj = namespace.get(func_name)
        if obj is not None and callable(obj):
            return obj
    for fname in top_func_names:
        obj = namespace.get(fname)
        if obj is not None and callable(obj):
            return obj

    for name, obj in namespace.items():
        if name.startswith("_") or getattr(obj, "__module__", "") == "typing":
            continue
        if isinstance(obj, type) and callable(getattr(obj, func_name, None)):
            return _make_method_caller(obj, func_name)

    if func_name in namespace and callable(namespace[func_name]):
        return namespace[func_name]

    return None


def _extract_func_name(snippet: str) -> str:
    """Return the method/function name from a Python snippet.

    Comment lines are stripped first so that commented-out class stubs
    (e.g. '# def __init__(self, ...)' in TreeNode/ListNode definitions)
    are never matched ahead of the real solution method.
    Dunder methods (__init__, etc.) are also skipped, handling snippets
    that wrap class definitions in triple-quoted strings (e.g. N-ary tree).
    """
    stripped = "\n".join(
        line for line in snippet.splitlines()
        if not line.strip().startswith("#")
    )
    for m in re.finditer(r"def (\w+)\(self", stripped):
        if not m.group(1).startswith("__"):
            return m.group(1)
    for m in re.finditer(r"def (\w+)\(", stripped):
        if not m.group(1).startswith("__"):
            return m.group(1)
    return "solve"


def _get_param_names(snippet: str) -> list[str]:
    """Return ordered non-self parameter names from the first def in snippet."""
    # Strip comment lines to avoid matching commented-out helper classes
    # (e.g. # def __init__(self, val=0, left=None, right=None):)
    snippet = "\n".join(
        line for line in snippet.splitlines()
        if not line.strip().startswith("#")
    )
    m = re.search(r"def (?!__)\w+\(self(?:,\s*(.*?))?\s*\)\s*(?:->.*?)?:", snippet, re.DOTALL)
    if m and m.group(1):
        params = []
        for p in m.group(1).split(","):
            name = re.split(r"[=:]", p.strip())[0].strip()
            if name and not name.startswith("*"):
                params.append(name)
        return params
    # Standalone function (no self)
    m2 = re.search(r"def \w+\((.*?)\)\s*(?:->.*?)?:", snippet, re.DOTALL)
    if m2 and m2.group(1):
        params = []
        for p in m2.group(1).split(","):
            name = re.split(r"[=:]", p.strip())[0].strip()
            if name and not name.startswith("*"):
                params.append(name)
        return params
    return []


def _extract_param_types(snippet: str) -> dict[str, str]:
    """Return {param_name: type_hint} from docstring or PEP-484 annotations."""
    types: dict[str, str] = {}
    # Python 2 docstring style:  :type root: Optional[TreeNode]
    for m in re.finditer(r":type\s+(\w+)\s*:\s*(.+)", snippet):
        types[m.group(1)] = m.group(2).strip()
    # Python 3 annotation style: def method(self, root: TreeNode, ...)
    sig_m = re.search(
        r"def \w+\(self(?:,\s*(.*?))?\s*\)\s*(?:->.*?)?:",
        snippet, re.DOTALL
    )
    if sig_m and sig_m.group(1):
        for pm in re.finditer(r"(\w+)\s*:\s*([\w\[\], |.]+)", sig_m.group(1)):
            name = pm.group(1)
            if name not in types:
                types[name] = pm.group(2).strip()
    return types


def _is_inplace(snippet: str) -> bool:
    """Return True if the method is documented as returning None (in-place op)."""
    return bool(re.search(r":rtype:\s*None\b|def\s+\w+\([^)]*\)\s*->\s*None\b", snippet))


def _get_return_type(snippet: str) -> str:
    """Extract the return type hint string from a snippet."""
    m = re.search(r":rtype:\s*(.+)", snippet)
    if m:
        return m.group(1).strip()
    m = re.search(r"def\s+\w+\([^)]*\)\s*->\s*([\w\[\], |.]+)", snippet)
    if m:
        return m.group(1).strip()
    return ""


def _build_tree(vals: list, TreeNodeCls: type) -> Any:
    """Build a TreeNode tree from LeetCode BFS-serialised list."""
    if not vals or vals[0] is None:
        return None
    root = TreeNodeCls(vals[0])
    queue = [root]
    i = 1
    while queue and i < len(vals):
        node = queue.pop(0)
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNodeCls(vals[i])
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNodeCls(vals[i])
            queue.append(node.right)
        i += 1
    return root


def _build_listnode(vals: list, ListNodeCls: type) -> Any:
    """Build a ListNode linked list from a list of values."""
    if not vals:
        return None
    head = ListNodeCls(vals[0])
    cur = head
    for v in vals[1:]:
        cur.next = ListNodeCls(v)
        cur = cur.next
    return head


def _serialize_tree(node: Any) -> list:
    """BFS-serialize a TreeNode/Node to a LeetCode-style list (trailing Nones trimmed)."""
    if node is None:
        return []
    result, queue = [], [node]
    while queue:
        n = queue.pop(0)
        if n is None:
            result.append(None)
        else:
            result.append(n.val)
            queue.append(getattr(n, "left", None))
            queue.append(getattr(n, "right", None))
    while result and result[-1] is None:
        result.pop()
    return result


def _build_nary_tree(vals: list, NodeCls: type) -> Any:
    """Build an N-ary Node tree from LeetCode level-order serialised list.

    Format: [root_val, null, child1, child2, ..., null, grandchildren, ...]
    Each null separates one parent's children from the next parent's children.
    """
    if not vals or vals[0] is None:
        return None
    root = NodeCls(vals[0])
    queue = [root]
    parent_idx = 0
    i = 2  # skip root (index 0) and first null (index 1)
    while parent_idx < len(queue) and i <= len(vals):
        node = queue[parent_idx]
        parent_idx += 1
        while i < len(vals) and vals[i] is not None:
            child = NodeCls(vals[i])
            node.children.append(child)
            queue.append(child)
            i += 1
        i += 1  # skip null separator
    return root


def _build_listnode_with_pos(vals: list, pos: int, ListNodeCls: type) -> Any:
    """Build a ListNode chain, optionally connecting the tail to node at *pos* (cycle)."""
    if not vals:
        return None
    nodes = [ListNodeCls(v) for v in vals]
    for k in range(len(nodes) - 1):
        nodes[k].next = nodes[k + 1]
    if 0 <= pos < len(nodes):
        nodes[-1].next = nodes[pos]
    return nodes[0]


def _serialize_listnode(node: Any) -> list:
    """Traverse a ListNode chain to a list of values (cycle-safe)."""
    result, seen = [], set()
    while node is not None:
        nid = id(node)
        if nid in seen:
            break
        seen.add(nid)
        result.append(node.val)
        node = node.next
    return result


def _normalize_output(output: Any) -> Any:
    """Serialize TreeNode/ListNode outputs to plain lists.

    This ensures the result is picklable for the multiprocessing Queue and
    can be compared directly against LeetCode-style expected strings.
    """
    if output is None or isinstance(output, (bool, int, float, str, list, tuple, dict)):
        return output
    name = type(output).__name__
    if name in ("TreeNode", "Node"):
        return _serialize_tree(output)
    if name == "ListNode":
        return _serialize_listnode(output)
    return output


def _parse_input(raw: str) -> Any:
    """Parse a single raw input string to a Python value."""
    raw = raw.strip()
    raw = re.sub(r"\bnull\b", "None", raw)
    raw = re.sub(r"\btrue\b", "True", raw)
    raw = re.sub(r"\bfalse\b", "False", raw)
    try:
        return ast.literal_eval(raw)
    except Exception:
        return raw


def _convert_inputs(
    inputs: list[Any],
    param_names: list[str],
    param_types: dict[str, str],
    namespace: dict,
) -> list[Any]:
    """Convert list inputs to TreeNode/ListNode/Node where the type hint demands it.

    Special cases:
    - N-ary tree (type hint contains 'Node' but not 'TreeNode'): use Node + N-ary format
    - LinkedList + adjacent int 'pos': build list with cycle
    """
    result = list(inputs)

    # Special case: single ListNode param + extra int → cycle-list (e.g. hasCycle)
    if (len(param_names) == 1
            and len(inputs) == 2
            and isinstance(inputs[0], list)
            and isinstance(inputs[1], int)
            and "ListNode" in param_types.get(param_names[0], "")):
        ListNodeCls = namespace.get("ListNode")
        if ListNodeCls:
            return [_build_listnode_with_pos(inputs[0], inputs[1], ListNodeCls)]

    for j, (val, name) in enumerate(zip(inputs, param_names)):
        if not isinstance(val, list):
            continue
        type_hint = param_types.get(name, "")
        if "TreeNode" in type_hint:
            TreeNodeCls = namespace.get("TreeNode")
            if TreeNodeCls:
                result[j] = _build_tree(val, TreeNodeCls)
        elif "Node" in type_hint and "List" not in type_hint:
            # N-ary tree (type hint: Node or Optional[Node])
            NodeCls = namespace.get("Node")
            if NodeCls:
                result[j] = _build_nary_tree(val, NodeCls)
            else:
                # Fall back to binary tree if Node class not in namespace
                TreeNodeCls = namespace.get("TreeNode")
                if TreeNodeCls:
                    result[j] = _build_tree(val, TreeNodeCls)
        elif "ListNode" in type_hint:
            ListNodeCls = namespace.get("ListNode")
            if ListNodeCls:
                result[j] = _build_listnode(val, ListNodeCls)
    return result


def _to_lists(val: Any) -> Any:
    """Recursively convert tuples to lists so comparisons don't fail on type."""
    if isinstance(val, tuple):
        return [_to_lists(x) for x in val]
    if isinstance(val, list):
        return [_to_lists(x) for x in val]
    return val


def _check_output(output: Any, expected_raw: str) -> bool | None:
    """Compare actual output to expected string. Returns None if no expected."""
    if not expected_raw:
        return None

    # Strip zero-width Unicode characters that sometimes appear in LeetCode data
    effective_expected = re.sub(r"[\u200b-\u200f\ufeff]", "", expected_raw.strip())

    # Some LeetCode problems encode the return value AND the modified array,
    # e.g. "2, nums = [1,2,_]". Extract only the part before the first comma.
    if re.match(r"^-?\d+,\s*\w+\s*=", effective_expected):
        effective_expected = effective_expected.split(",")[0].strip()

    # Normalize tuples to lists before comparison
    output = _to_lists(output)

    # Try exact value comparison
    try:
        parsed = _parse_input(effective_expected)
        if output == parsed:
            return True
        # Strip trailing/leading whitespace from string outputs
        if isinstance(output, str) and isinstance(parsed, str):
            if output.strip() == parsed.strip():
                return True
        # Float comparison with rounding (e.g. 4.777777… vs "4.77778")
        if isinstance(output, float) and isinstance(parsed, (int, float)):
            if round(output, 5) == round(float(parsed), 5):
                return True
        # Unordered list comparison (e.g. [9,4] vs [4,9])
        if isinstance(output, list) and isinstance(parsed, list):
            try:
                if sorted(output) == sorted(parsed):
                    return True
            except TypeError:
                pass
        return False
    except Exception:
        pass

    # Fallback: normalise both to stripped repr strings
    if isinstance(output, str):
        return output.strip() == effective_expected.strip()
    return repr(output) == effective_expected


# ---------------------------------------------------------------------------
# API mock factories for LeetCode problems that rely on injected functions
# ---------------------------------------------------------------------------

def _detect_design_format(raw_inputs: list) -> tuple | None:
    """Return (ops, args) if raw_inputs is in LeetCode design-problem format.

    Design format: two strings where the first parses to a list of operation
    names (strings) and the second to a matching list of argument lists.
    """
    if len(raw_inputs) != 2:
        return None
    try:
        ops = _parse_input(raw_inputs[0])
        args = _parse_input(raw_inputs[1])
        if (isinstance(ops, list) and len(ops) >= 1
                and all(isinstance(o, str) for o in ops)
                and isinstance(args, list) and len(ops) == len(args)
                and all(isinstance(a, list) for a in args)):
            return ops, args
    except Exception:
        pass
    return None


def _run_design_case(namespace: dict, ops: list, args: list) -> list:
    """Execute a design-problem test case.

    ops[0] is the class name (constructor); ops[1:] are method calls.
    Returns a list parallel to ops: None for the constructor, then each method's result.
    """
    cls_name = ops[0]
    cls = namespace.get(cls_name)
    if cls is None:
        raise NameError(f"Class '{cls_name}' not found in namespace")
    obj = cls(*args[0])
    results: list = [None]
    for op, op_args in zip(ops[1:], args[1:]):
        method = getattr(obj, op, None)
        if method is None:
            raise AttributeError(f"Method '{op}' not found on {cls_name}")
        results.append(_normalize_output(method(*op_args)))
    return results


def _make_isBadVersion(bad_version: int):
    """Return an isBadVersion mock where versions >= bad_version are 'bad'."""
    def isBadVersion(version):
        return version >= bad_version
    return isBadVersion


def _make_guess(picked: int):
    """Return a guess mock for the given picked number.

    LeetCode API: -1 when guess is too high (num > picked),
                   1 when guess is too low (num < picked),
                   0 when correct.
    """
    def guess(num):
        if num == picked:
            return 0
        return -1 if num > picked else 1
    return guess


def run_tests(
    code: str,
    snippet: str,
    test_cases: list[list[str]],
    expected_outputs: list[str],
) -> list[CaseResult]:
    """Execute *code* against structured test cases; return per-case results."""
    func_name = _extract_func_name(snippet)

    if not test_cases:
        return [CaseResult(case_num=1, inputs=[], error="No test cases found.")]

    # Patch empty bodies then prepend all preludes
    patched = (
        _IMPORTS_PRELUDE
        + _TYPING_PRELUDE
        + _DATASTRUCTURE_PRELUDE
        + _fill_empty_bodies(code)
    )

    namespace: dict = {}
    try:
        exec(compile(patched, "<editor>", "exec"), namespace)  # noqa: S102
    except SyntaxError as e:
        err = f"SyntaxError: {e.msg} (line {e.lineno})"
        return [CaseResult(case_num=i + 1, inputs=case, error=err)
                for i, case in enumerate(test_cases)]
    except Exception:
        err = traceback.format_exc().strip().splitlines()[-1]
        return [CaseResult(case_num=i + 1, inputs=case, error=err)
                for i, case in enumerate(test_cases)]

    caller = _find_caller(code, namespace, func_name)
    if caller is None:
        err = f"Could not find '{func_name}' in any class or as a standalone function."
        return [CaseResult(case_num=i + 1, inputs=case, error=err)
                for i, case in enumerate(test_cases)]

    # Extract parameter metadata once for tree/listnode conversion
    param_names = _get_param_names(snippet)
    param_types = _extract_param_types(snippet)

    # Detect whether the method modifies its first argument in-place (rtype: None)
    inplace = _is_inplace(snippet)

    # Detect return type for None → [] conversion (empty ListNode/TreeNode)
    return_type = _get_return_type(snippet)
    returns_node = any(t in return_type for t in ("ListNode", "TreeNode", "Node"))

    # Detect API-injection needs from the solution code
    needs_isBadVersion = "isBadVersion" in code
    needs_guess = bool(re.search(r"\bguess\s*\(", code))

    results: list[CaseResult] = []
    for i, raw_inputs in enumerate(test_cases):
        expected = expected_outputs[i] if i < len(expected_outputs) else ""

        # ── Design-problem format: [operations, inputs_list] ──────────────────
        design = _detect_design_format(raw_inputs)
        if design is not None:
            ops, args = design
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    output = _run_design_case(namespace, ops, args)
                results.append(CaseResult(
                    case_num=i + 1,
                    inputs=raw_inputs,
                    output=output,
                    expected=expected,
                    passed=_check_output(output, expected),
                    stdout=buf.getvalue(),
                ))
            except Exception:
                last_line = traceback.format_exc().strip().splitlines()[-1]
                results.append(CaseResult(
                    case_num=i + 1,
                    inputs=raw_inputs,
                    expected=expected,
                    passed=False,
                    error=last_line,
                    stdout=buf.getvalue(),
                ))
            continue

        # ── Normal single-method test case ────────────────────────────────────
        parsed = [_parse_input(v) for v in raw_inputs]
        call_inputs = _convert_inputs(parsed, param_names, param_types, namespace)

        # Truncate excess inputs to the number of declared parameters.
        # Some test cases bundle multiple examples into one entry (e.g. tree
        # problems where 3 different trees are packed into a single inputs list).
        if param_names and len(call_inputs) > len(param_names):
            call_inputs = call_inputs[:len(param_names)]

        # Inject per-test-case API mocks that depend on the expected answer
        if needs_isBadVersion and expected and expected.strip().lstrip("-").isdigit():
            namespace["isBadVersion"] = _make_isBadVersion(int(expected.strip()))
        if needs_guess and expected and expected.strip().lstrip("-").isdigit():
            namespace["guess"] = _make_guess(int(expected.strip()))

        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                output = caller(*call_inputs)

            # In-place methods return None; the result is the mutated first arg
            if inplace and output is None and call_inputs:
                output = call_inputs[0]

            # Empty ListNode/TreeNode returns None; serialize as [] to match LeetCode format
            if output is None and returns_node:
                output = []

            # Serialize tree/linked-list nodes to plain lists so they are
            # picklable (prevents multiprocessing Queue deadlocks on Windows)
            # and can be compared against LeetCode-style expected strings.
            output = _normalize_output(output)

            results.append(CaseResult(
                case_num=i + 1,
                inputs=raw_inputs,   # store original strings — picklable
                output=output,
                expected=expected,
                passed=_check_output(output, expected),
                stdout=buf.getvalue(),
            ))
        except Exception:
            last_line = traceback.format_exc().strip().splitlines()[-1]
            results.append(CaseResult(
                case_num=i + 1,
                inputs=raw_inputs,   # store original strings — picklable
                expected=expected,
                passed=False,
                error=last_line,
                stdout=buf.getvalue(),
            ))

    return results
