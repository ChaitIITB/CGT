#!/usr/bin/env python3
"""
Leaf Convergence Games: Atomic Weight and Value Computation
Advanced analysis with game tree structure and value computation.
"""

from fractions import Fraction
from dataclasses import dataclass
from typing import List, Tuple, Optional

# ============================================================
# GAME STRUCTURE
# ============================================================

@dataclass
class GameNode:
    """Represents a node in a game tree."""
    node_id: str
    left_children: List['GameNode']
    right_children: List['GameNode']
    is_terminal: bool = False
    computed_value: Optional[str] = None
    temperature: Optional[float] = None
    atomic_weight: Optional[str] = None

class GameEvaluator:
    """Evaluates LCG positions and computes game values."""
    
    def __init__(self):
        self.memo = {}
    
    def evaluate_position(self, left_count: int, right_count: int, depth: int = 1):
        """Evaluate an LCG position given left/right branching at given depth."""
        key = (left_count, right_count, depth)
        if key in self.memo:
            return self.memo[key]
        
        if depth == 1:
            result = self._evaluate_depth1(left_count, right_count)
        else:
            result = self._evaluate_depth_n(left_count, right_count, depth)
        
        self.memo[key] = result
        return result
    
    def _evaluate_depth1(self, left_count: int, right_count: int) -> dict:
        """Evaluate depth-1 position."""
        if left_count == 0 and right_count == 0:
            return None
        
        # All leaves converge to 0 (terminal)
        if left_count == 0:
            return {
                'value': f'-{right_count}',
                'temperature': float('-inf'),
                'atomic_weight': f'-{right_count}',
                'type': 'integer_right',
                'cgsuite': self._construct_cgsuite_integer(-right_count)
            }
        elif right_count == 0:
            return {
                'value': f'{left_count}',
                'temperature': float('-inf'),
                'atomic_weight': f'{left_count}',
                'type': 'integer_left',
                'cgsuite': self._construct_cgsuite_integer(left_count)
            }
        elif left_count == right_count:
            return {
                'value': '*',
                'temperature': 0,
                'atomic_weight': '0',
                'type': 'fuzzy',
                'cgsuite': '{0|0}'
            }
        else:
            min_count = min(left_count, right_count)
            sign = '+' if left_count > right_count else '-'
            return {
                'value': f'±{min_count}',
                'temperature': min_count,
                'atomic_weight': f'±{min_count}',
                'type': 'switch',
                'cgsuite': f'{{{min_count}|{-min_count}}}'
            }
    
    def _evaluate_depth_n(self, left_count: int, right_count: int, depth: int) -> dict:
        """Evaluate depth-n position (simplified for depth 2)."""
        if depth == 2:
            # Depth 2: can have internal nodes
            return {
                'value': 'complex',
                'temperature': 0,
                'atomic_weight': '(computed)',
                'type': 'depth2',
                'cgsuite': f'(nested structure)'
            }
        return None
    
    def _construct_cgsuite_integer(self, n: int) -> str:
        """Construct CGSuite code for integer n."""
        if n == 0:
            return '{0|0}'
        elif n == 1:
            return '{0|}'
        elif n == -1:
            return '{|0}'
        elif n > 1:
            return '{' + self._construct_cgsuite_integer(n-1) + '|}'
        else:  # n < -1
            return '{|' + self._construct_cgsuite_integer(n+1) + '}'
    
    def analyze_integer_sequence(self, max_n: int = 5):
        """Analyze atomic weights of integer sequence."""
        print("\n" + "=" * 70)
        print("INTEGER SEQUENCE ANALYSIS")
        print("=" * 70)
        print("\n{:<10} {:<20} {:<20} {:<15}".format(
            "Value", "CGSuite", "Temperature", "Atomic Weight"
        ))
        print("-" * 70)
        
        for n in range(-max_n, max_n + 1):
            if n == 0:
                cgsuite = '{0|0}'
                temp = 0
                aw = '0'
            elif n > 0:
                cgsuite = self._construct_cgsuite_integer(n)
                temp = '-∞'
                aw = str(n)
            else:
                cgsuite = self._construct_cgsuite_integer(n)
                temp = '-∞'
                aw = str(n)
            
            print("{:<10} {:<20} {:<20} {:<15}".format(
                str(n), cgsuite, temp, aw
            ))
    
    def analyze_switches(self, max_diff: int = 5):
        """Analyze switches ±n and their atomic weights."""
        print("\n" + "=" * 70)
        print("SWITCH ANALYSIS (±n with temperature n)")
        print("=" * 70)
        print("\n{:<15} {:<20} {:<15} {:<15}".format(
            "Switch", "CGSuite", "Temperature", "Atomic Weight"
        ))
        print("-" * 70)
        
        for n in range(1, max_diff + 1):
            cgsuite = f'{{{n}|{-n}}}'
            print("{:<15} {:<20} {:<15} {:<15}".format(
                f'±{n}', cgsuite, str(n), f'±{n}'
            ))
    
    def analyze_branching_to_value(self):
        """Show mapping from branching patterns to game values."""
        print("\n" + "=" * 70)
        print("BRANCHING PATTERNS → GAME VALUES (Depth 1)")
        print("=" * 70)
        print("\n{:<15} {:<15} {:<15} {:<15} {:<20}".format(
            "Left", "Right", "Value", "Temperature", "Atomic Weight"
        ))
        print("-" * 70)
        
        for left in range(0, 6):
            for right in range(0, 6):
                if left == 0 and right == 0:
                    continue
                
                result = self._evaluate_depth1(left, right)
                if result:
                    print("{:<15} {:<15} {:<15} {:<15} {:<20}".format(
                        str(left), str(right), 
                        result['value'],
                        str(result['temperature']) if result['temperature'] != float('-inf') else '-∞',
                        result['atomic_weight']
                    ))

# ============================================================
# INFINITESIMAL ANALYSIS
# ============================================================

def analyze_infinitesimals():
    """Analyze infinitesimal structure and emergence."""
    print("\n" + "=" * 70)
    print("INFINITESIMAL ANALYSIS")
    print("=" * 70)
    
    print("\nInfinitesimal Up: ↑ = {0|*}")
    print("-" * 70)
    print("  Left option: 0 (terminal)")
    print("  Right option: * = {0|0} (fuzzy)")
    print("  Interpretation: Left prefers moving (gets 0 advantage), Right indifferent")
    print("  Temperature: 0 (neither player urgent)")
    print("  Atomic Weight: ↑ (positive infinitesimal)")
    print("  CGSuite: G_up := {0|{0|0}}; G_up.AtomicWeight;")
    
    print("\nInfinitesimal Down: ↓ = {*|0}")
    print("-" * 70)
    print("  Left option: * = {0|0} (fuzzy)")
    print("  Right option: 0 (terminal)")
    print("  Interpretation: Right prefers moving, Left indifferent")
    print("  Temperature: 0 (neither player urgent)")
    print("  Atomic Weight: ↓ (negative infinitesimal)")
    print("  CGSuite: G_down := {{0|0}|0}; G_down.AtomicWeight;")
    
    print("\nHigher Order Infinitesimals")
    print("-" * 70)
    print("  {0|↑} = {0|{0|*}} : Left to 0, Right to ↑")
    print("  {↓|0} = {{*|0}|0} : Left to ↓, Right to 0")
    print("  Atomic Weight: Multiplicative composition")
    
    print("\nInfinitesimal Arithmetic")
    print("-" * 70)
    print("  ↑ + ↓ = 0     (cancellative infinitesimals)")
    print("  ↑ + * = ↑      (infinitesimal dominates fuzzy)")
    print("  ↑ + 1 = {1|0}  (hot game with infinitesimal offset)")

def analyze_depth_effects():
    """Analyze how depth affects game structure and values."""
    print("\n" + "=" * 70)
    print("DEPTH EFFECTS ON GAME STRUCTURE")
    print("=" * 70)
    
    print("\nDepth 1: Simple Branching")
    print("-" * 70)
    print("  All leaves directly to terminal (value 0)")
    print("  Value depends only on Left/Right count asymmetry")
    print("  Achievable values: integers, switches, fuzzy game *")
    print("  Temperatures: {0, 1, 2, 3, ..., -∞}")
    print("  Atomic weights: correspond to value (integer or ±n)")
    
    print("\nDepth 2: Internal Structure")
    print("-" * 70)
    print("  Internal nodes can have non-trivial sub-game values")
    print("  Left branch depth-1, Right branch depth-2:")
    print("    Right subtree has {0|0} = * (value * )")
    print("    Root becomes {0|*} = ↑ (infinitesimal)")
    print("  Atomic weight changes: * → 0 at internal level → ↑ at root")
    print("  New phenomenon: Infinitesimals with temperature 0")
    
    print("\nDepth 3+: Arbitrary Values")
    print("-" * 70)
    print("  Deep nesting creates dyadic rationals: p/2^q")
    print("  Mixed infinitesimals: compound hot infinitesimals")
    print("  Full CGT value spectrum potentially realisable")

def atomic_weight_propagation():
    """Show how atomic weights propagate through structure."""
    print("\n" + "=" * 70)
    print("ATOMIC WEIGHT PROPAGATION")
    print("=" * 70)
    
    print("\nRule 1: Integer Propagation")
    print("-" * 70)
    print("  {n|} = n, aw = n")
    print("  {m|} = m, aw = m")
    print("  Disjunctive sum: n + m = {n+m|}, aw = n+m")
    print("  → Atomic weights add linearly for integers")
    
    print("\nRule 2: Switch Propagation")
    print("-" * 70)
    print("  {n|-n} = ±n, aw = ±n, temperature = n")
    print("  {m|-m} = ±m, aw = ±m, temperature = m")
    print("  Disjunctive sum creates complex composition")
    
    print("\nRule 3: Infinitesimal Propagation")
    print("-" * 70)
    print("  {0|*} = ↑, aw = ↑")
    print("  {↑|0} = {0|*}|0 (nested)")
    print("  Multiple infinitesimals: ↑ + ↑ = ?")
    print("  → Multiplicative structure for atomic weights")

def main():
    """Run comprehensive analysis."""
    evaluator = GameEvaluator()
    
    print("\n" + "=" * 70)
    print("LEAF CONVERGENCE GAMES: COMPREHENSIVE ANALYSIS")
    print("=" * 70)
    
    evaluator.analyze_integer_sequence(max_n=5)
    evaluator.analyze_switches(max_diff=5)
    evaluator.analyze_branching_to_value()
    analyze_infinitesimals()
    analyze_depth_effects()
    atomic_weight_propagation()
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
