#!/usr/bin/env python3
"""
Leaf Convergence Games: Comprehensive Value Enumeration (Depth 1-2)
Enumerates all non-isomorphic LCG positions and generates CGSuite syntax for verification.
"""

from itertools import combinations, product
from fractions import Fraction
from collections import defaultdict

class LCGPosition:
    """Represents an LCG position."""
    def __init__(self, left_count, right_count, depth=1, structure="simple"):
        self.left_count = left_count
        self.right_count = right_count
        self.depth = depth
        self.structure = structure  # "simple", "asymmetric", "ladder", etc.
    
    def __repr__(self):
        return f"LCG({self.left_count}L, {self.right_count}R, d={self.depth}, {self.structure})"
    
    def __hash__(self):
        return hash((self.left_count, self.right_count, self.depth, self.structure))
    
    def __eq__(self, other):
        return (self.left_count == other.left_count and 
                self.right_count == other.right_count and
                self.depth == other.depth and
                self.structure == other.structure)

def evaluate_simple_root(left, right):
    """
    Evaluate simple root with k left-leaves and m right-leaves, all to single terminal.
    Value: {0, 0, ..., 0 | 0, 0, ..., 0} simplifies to ±min(k,m)
    """
    if left == 0 and right == 0:
        return None  # No position
    if left == 0:
        return (-right, 1)  # All right moves → Right advantage
    if right == 0:
        return (left, 1)    # All left moves → Left advantage
    
    min_count = min(left, right)
    if left > right:
        return (min_count, 1)  # Left advantage
    elif right > left:
        return (-min_count, 1)  # Right advantage
    else:
        return (0, 1)  # Symmetric → value 0

def evaluate_depth2_symmetric_branching(left_branches, right_branches):
    """
    Depth 2 with symmetric internal structure.
    Each branch at level 1 has some leaves at depth 2.
    
    Returns multiple position configurations.
    """
    positions = []
    
    # Case 1: All left branches have k leaves each
    for k in range(1, 4):
        for m in range(1, 4):
            # n left branches, each with k leaves → (n*k) total left options
            for n_left_branches in range(1, 3):
                for n_right_branches in range(1, 3):
                    total_left = n_left_branches * k
                    total_right = n_right_branches * m
                    value = evaluate_simple_root(total_left, total_right)
                    if value:
                        positions.append({
                            'config': f"{n_left_branches}×{k}L-leaves, {n_right_branches}×{m}R-leaves",
                            'total_left': total_left,
                            'total_right': total_right,
                            'value': value,
                            'cgsuite': f"{{{','.join(['0']*total_left)} | {','.join(['0']*total_right)}}}",
                            'depth': 2,
                            'structure': 'branched'
                        })
    
    return positions

def evaluate_depth2_mixed(left_at_1, right_at_1, left_at_2, right_at_2):
    """
    Depth 2 mixed: some leaves at depth 1, some at depth 2.
    """
    positions = []
    
    # Simple case: internal right node with (left_at_2, right_at_2) leaves
    internal_value = evaluate_simple_root(left_at_2, right_at_2)
    if internal_value:
        positions.append({
            'config': f"{left_at_1}L depth-1, {right_at_1}R depth-1, internal node {left_at_2}L-{right_at_2}R",
            'value': f"complex mixed",
            'depth': 2,
            'structure': 'mixed'
        })
    
    return positions

def enumerate_all_positions(max_depth=2):
    """Enumerate all LCG positions up to max_depth."""
    all_positions = []
    
    print("=" * 70)
    print("LEAF CONVERGENCE GAMES: VALUE ENUMERATION (Depth 1-2)")
    print("=" * 70)
    
    # DEPTH 1: Simple roots
    print("\n[DEPTH 1] Simple Root Configurations:")
    print("-" * 70)
    
    depth1_values = defaultdict(list)
    
    for left in range(0, 6):
        for right in range(0, 6):
            if left == 0 and right == 0:
                continue
            
            value = evaluate_simple_root(left, right)
            if value:
                num, den = value
                value_str = f"{num}/{den}" if den != 1 else str(num)
                
                # Categorize
                if num == 0:
                    category = "ZERO (symmetric)"
                elif abs(num) > 1:
                    category = f"SWITCH (±{abs(num)})"
                elif num == 1:
                    category = "POSITIVE INTEGER"
                elif num == -1:
                    category = "NEGATIVE INTEGER"
                else:
                    category = "OTHER"
                
                pos_obj = LCGPosition(left, right, depth=1, structure="simple")
                all_positions.append(pos_obj)
                depth1_values[value_str].append((left, right, category))
                
                print(f"  {left}L, {right}R → Value: {value_str:>6} | {category}")
    
    print(f"\nDepth 1 Summary: {len(all_positions)} positions enumerated")
    
    # DEPTH 2: Branched structures
    if max_depth >= 2:
        print("\n[DEPTH 2] Branched Root Configurations:")
        print("-" * 70)
        
        depth2_pos = evaluate_depth2_symmetric_branching(
            left_branches=range(1, 3),
            right_branches=range(1, 3)
        )
        
        # Print unique values
        seen_values = set()
        for pos in depth2_pos:
            value_tuple = pos['value']
            if value_tuple not in seen_values:
                seen_values.add(value_tuple)
                num, den = value_tuple
                value_str = f"±{abs(num)}" if num != 0 else "0"
                print(f"  {pos['config']}")
                print(f"    → Value: {num}/{den} | CGSuite: {pos['cgsuite']}")
                
                all_positions.append(LCGPosition(
                    pos['total_left'], pos['total_right'], 
                    depth=2, structure='branched'
                ))
    
    return all_positions, depth1_values

def generate_cgsuite_script(positions):
    """Generate CGSuite code to verify all positions."""
    script = """// LEAF CONVERGENCE GAMES: CGSuite Verification Script
// Copy-paste each G := ... line into CGSuite to verify

// DEPTH 1 POSITIONS
// ============================================================

// Symmetric positions
G_sym_1 := {0 | 0};
CanonicalForm(G_sym_1);          // Expected: *
Temperature(G_sym_1);             // Expected: 0

G_sym_2 := {0,0 | 0,0};
CanonicalForm(G_sym_2);           // Expected: ±1
Temperature(G_sym_2);             // Expected: 1

G_sym_3 := {0,0,0 | 0,0,0};
CanonicalForm(G_sym_3);           // Expected: ±2
Temperature(G_sym_3);             // Expected: 2

// Asymmetric - Left advantage
G_left_1 := {0};
CanonicalForm(G_left_1);          // Expected: 1

G_left_2 := {0,0};
CanonicalForm(G_left_2);          // Expected: 2

G_left_3 := {0,0,0};
CanonicalForm(G_left_3);          // Expected: 3

// Asymmetric - Right advantage
G_right_1 := { | 0};
CanonicalForm(G_right_1);         // Expected: -1

G_right_2 := { | 0,0};
CanonicalForm(G_right_2);         // Expected: -2

// Mixed asymmetry (Left > Right)
G_3L_1R := {0,0,0 | 0};
CanonicalForm(G_3L_1R);           // Expected: ±1
Temperature(G_3L_1R);             // Expected: 1

G_4L_1R := {0,0,0,0 | 0};
CanonicalForm(G_4L_1R);           // Expected: ±1
Temperature(G_4L_1R);             // Expected: 1

G_5L_1R := {0,0,0,0,0 | 0};
CanonicalForm(G_5L_1R);           // Expected: ±1
Temperature(G_5L_1R);             // Expected: 1

// DEPTH 2 POSITIONS
// ============================================================

// Infinitesimals: {0 | *}
G_up := {0 | {0|0}};
CanonicalForm(G_up);              // Expected: up
Temperature(G_up);                // Expected: 0

// Infinitesimals: {* | 0}
G_down := {{0|0} | 0};
CanonicalForm(G_down);            // Expected: down
Temperature(G_down);              // Expected: 0

// Compound: {0 | up}
G_up_2 := {0 | {0 | {0|0}}};
CanonicalForm(G_up_2);            // Expected: compound

// Compound game
G_compound_1 := {0,0,0 | 0} + {0|0};
Temperature(G_compound_1);

// Temperature analysis
G_temp_1 := {0,0 | 0,0};
Temperature(G_temp_1);            // 1

G_temp_2 := {0,0,0,0 | 0,0};
Temperature(G_temp_2);            // 2

G_temp_3 := {0,0,0,0,0 | 0,0,0};
Temperature(G_temp_3);            // 3
"""
    return script

def main():
    positions, depth1_values = enumerate_all_positions(max_depth=2)
    
    print("\n" + "=" * 70)
    print("VALUE CATEGORIES (Depth 1)")
    print("=" * 70)
    for value_str in sorted(depth1_values.keys(), key=lambda x: float(eval(x))):
        configs = depth1_values[value_str]
        print(f"\nValue {value_str}:")
        for left, right, category in configs:
            print(f"  {left}L × {right}R ({category})")
    
    # Generate CGSuite script
    cgsuite_script = generate_cgsuite_script(positions)
    
    print("\n" + "=" * 70)
    print("CGSuite Script Generated")
    print("=" * 70)
    print(cgsuite_script)
    
    # Save scripts
    with open("lcg_cgsuite_verification.txt", "w", encoding="utf-8") as f:
        f.write(cgsuite_script)
    print("\n✓ Saved to: lcg_cgsuite_verification.txt")

if __name__ == "__main__":
    main()
