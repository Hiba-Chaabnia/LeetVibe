from __future__ import annotations

TOPIC: dict = {
    "title": "Trees",
    "slug": "Tree",
    "recognize": (
        "hierarchical data, BST property, path sum, depth/height,\n"
        "lowest common ancestor, serialise/deserialise tree."
    ),
    "diagram": (
        "           4\n"
        "          / \\\n"
        "         2   6\n"
        "        / \\ / \\\n"
        "       1  3 5  7\n"
        "\n"
        "  DFS inorder   (L→N→R): 1 2 3 4 5 6 7  ← sorted for BST\n"
        "  DFS preorder  (N→L→R): 4 2 1 3 6 5 7\n"
        "  DFS postorder (L→R→N): 1 3 2 5 7 6 4\n"
        "  BFS level-order:       4 2 6 1 3 5 7"
    ),
    "when": (
        "Hierarchical data. Use DFS for path problems and subtree queries;\n"
        "BFS for level-by-level processing or shortest paths."
    ),
    "patterns": [
        {
            "name": "DFS recursive — max depth",
            "code": (
                "def dfs(node):\n"
                "    if not node: return 0\n"
                "    return 1 + max(dfs(node.left), dfs(node.right))\n"
                "\n"
                "# BFS iterative — level order\n"
                "from collections import deque\n"
                "q, res = deque([root]), []\n"
                "while q:\n"
                "    level = []\n"
                "    for _ in range(len(q)):    # snapshot length each level\n"
                "        node = q.popleft()\n"
                "        level.append(node.val)\n"
                "        if node.left:  q.append(node.left)\n"
                "        if node.right: q.append(node.right)\n"
                "    res.append(level)"
            ),
        },
        {
            "name": "Validate BST — pass bounds down the recursion",
            "code": (
                "def valid(node, lo=float('-inf'), hi=float('inf')):\n"
                "    if not node: return True\n"
                "    if not (lo < node.val < hi): return False\n"
                "    return (valid(node.left,  lo, node.val) and\n"
                "            valid(node.right, node.val, hi))\n"
                "\n"
                "# Lowest Common Ancestor — BST (use BST ordering)\n"
                "def lca_bst(node, p, q):\n"
                "    if p.val < node.val and q.val < node.val:\n"
                "        return lca_bst(node.left, p, q)\n"
                "    if p.val > node.val and q.val > node.val:\n"
                "        return lca_bst(node.right, p, q)\n"
                "    return node\n"
                "\n"
                "# Lowest Common Ancestor — General Binary Tree (postorder DFS)\n"
                "# Return p or q if found, None otherwise; LCA is where both sides are non-None\n"
                "def lca_general(root, p, q):\n"
                "    if not root or root is p or root is q:\n"
                "        return root          # found one of the targets (or null)\n"
                "    left  = lca_general(root.left,  p, q)\n"
                "    right = lca_general(root.right, p, q)\n"
                "    if left and right:\n"
                "        return root          # p and q are in different subtrees → LCA here\n"
                "    return left or right     # both in same subtree → propagate upward\n"
                "\n"
                "# Iterative inorder DFS (BST in sorted order, no recursion limit)\n"
                "stack, node, result = [], root, []\n"
                "while stack or node:\n"
                "    while node:                 # go as far left as possible\n"
                "        stack.append(node)\n"
                "        node = node.left\n"
                "    node = stack.pop()          # visit\n"
                "    result.append(node.val)\n"
                "    node = node.right           # move right\n"
                "\n"
                "# Tree DP — post-order: each node returns info to its parent\n"
                "# Pattern: compute (local_answer, value_passed_up) at every node\n"
                "# Example: Binary Tree Maximum Path Sum\n"
                "self.max_sum = float('-inf')\n"
                "\n"
                "def gain(node):\n"
                "    if not node: return 0\n"
                "    left_gain  = max(gain(node.left),  0)  # ignore negative branches\n"
                "    right_gain = max(gain(node.right), 0)\n"
                "    self.max_sum = max(self.max_sum,\n"
                "                      node.val + left_gain + right_gain)\n"
                "    return node.val + max(left_gain, right_gain)\n"
                "\n"
                "gain(root)\n"
                "return self.max_sum\n"
                "# Same skeleton works for: diameter, longest univalue path, rob III"
            ),
        },
    ],
    "pitfalls": (
        "• BST validation: pass lo/hi bounds through recursion, not just checking\n"
        "  the immediate parent — a node's ancestor constraint must hold.\n"
        "• General LCA: the trick is returning root when root is p or q —\n"
        "  this assumes both nodes exist in the tree (guaranteed by problem).\n"
        "• DFS space is O(h); a skewed tree is O(n). Use the iterative inorder\n"
        "  pattern when recursion depth could exceed the call stack.\n"
        "• Level-order: snapshot len(q) at the start of each level iteration.\n"
        "• Python default recursion limit is 1000 — add at top of solution:\n"
        "  import sys; sys.setrecursionlimit(10**5)"
    ),
    "time": "O(n)",
    "space": "O(h)   h = height  (O(n) worst — fully skewed tree)",
    "problems": [
        ("Invert Binary Tree",                    "E"),
        ("Maximum Depth of Binary Tree",           "E"),
        ("Binary Tree Level Order Traversal",      "M"),
        ("Binary Tree Right Side View",            "M"),
        ("Kth Smallest Element in a BST",          "M"),
        ("Construct Binary Tree (Pre+Inorder)",    "M"),
        ("Validate Binary Search Tree",            "M"),
        ("Lowest Common Ancestor of a BST",        "M"),
        ("Lowest Common Ancestor of Binary Tree",  "M"),
        ("Binary Tree Maximum Path Sum",           "H"),
        ("Serialize and Deserialize Binary Tree",  "H"),
    ],
    "related": ["Graphs", "Dynamic Programming", "Tries", "LRU Cache", "Iterator Design Pattern"],
}
