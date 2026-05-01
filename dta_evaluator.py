#!/usr/bin/env python3
"""
Directed Tree Ascent (DTA / GDTA) Evaluator
Non-binary version (arbitrary number of L/R children)
Computes game values recursively with memoization
and exports to CGSuite syntax.
"""

from functools import lru_cache
from typing import List, Tuple, Set, Optional

# ------------------------------------------------------------
# Tree Node class (non-binary)
# ------------------------------------------------------------
class Node:
    def __init__(self, l_children: Optional[List['Node']] = None,
                 r_children: Optional[List['Node']] = None):
        self.l_children: List[Node] = l_children or []
        self.r_children: List[Node] = r_children or []

    def is_leaf(self) -> bool:
        return not self.l_children and not self.r_children

    def __repr__(self):
        return f"Node(L:{len(self.l_children)}, R:{len(self.r_children)})"


# ------------------------------------------------------------
# Recursive value computation with memoization
# ------------------------------------------------------------
@lru_cache(maxsize=None)
def game_value(node: Node) -> str:
    """
    Returns the game value in CGSuite syntax, e.g.
    "{0|0}", "{1|}", "{0|*}", etc.
    """
    if node.is_leaf():
        return "0"

    # Get values of all options
    left_opts: List[str] = [game_value(child) for child in node.l_children]
    right_opts: List[str] = [game_value(child) for child in node.r_children]

    # Remove duplicates while preserving order
    left_str = ",".join(sorted(set(left_opts)))
    right_str = ",".join(sorted(set(right_opts)))

    if not left_str and not right_str:
        return "0"
    elif not right_str:
        return f"{{{left_str}|}}"
    elif not left_str:
        return f"{{|{right_str}}}"
    else:
        return f"{{{left_str}|{right_str}}}"


# ------------------------------------------------------------
# Helper functions to build common positions
# ------------------------------------------------------------
def make_path(length: int, player: str) -> Node:
    """Create a monochromatic path of given length (L or R)."""
    if length == 0:
        return Node()
    current = Node()
    for _ in range(length):
        if player == 'L':
            current = Node(l_children=[current])
        else:
            current = Node(r_children=[current])
    return current


def make_switch(k: int) -> Node:
    """Non-binary symmetric switch ±k (root with k L-leaves and k R-leaves)."""
    l_leaves = [Node() for _ in range(k)]
    r_leaves = [Node() for _ in range(k)]
    return Node(l_children=l_leaves, r_children=r_leaves)


def make_up() -> Node:
    """The position ↑ = {0 | *}"""
    star = Node(l_children=[Node()], r_children=[Node()])   # * = {0|0}
    return Node(l_children=[Node()], r_children=[star])


def make_star() -> Node:
    """Simple star * = {0|0}"""
    return Node(l_children=[Node()], r_children=[Node()])


# ------------------------------------------------------------
# Demo / Main
# ------------------------------------------------------------
if __name__ == "__main__":
    print("=== Directed Tree Ascent (GDTA) Evaluator ===\n")

    # Example 1: Monochromatic paths
    print("L^3 path →", game_value(make_path(3, 'L')))          # 3
    print("R^2 path →", game_value(make_path(2, 'R')))          # -2

    # Example 2: Symmetric switches
    print("\n±2 switch (non-binary) →", game_value(make_switch(2)))
    print("±3 switch (non-binary) →", game_value(make_switch(3)))

    # Example 3: Classic infinitesimals
    print("\n*       →", game_value(make_star()))
    print("↑       →", game_value(make_up()))

    # Example 4: A more complex non-binary tree
    # Root with 3 L-leaves and 2 R-children that are themselves stars
    l_leaves = [Node() for _ in range(3)]
    r_stars = [make_star() for _ in range(2)]
    complex_tree = Node(l_children=l_leaves, r_children=r_stars)
    print("\nComplex tree (3L + 2R→*) →", game_value(complex_tree))

    print("\nAll values computed and ready for CGSuite!")
    print("Copy the output strings directly into CGSuite for canonical form / temperature.")