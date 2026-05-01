#!/usr/bin/env python3
"""
Leaf Convergence Games: Analysis and Atomic Weight Computation
Computes LCG values, temperatures, and atomic weights for systematic study.
"""

from fractions import Fraction
from collections import defaultdict

# ============================================================
# GAME VALUE REPRESENTATION
# ============================================================

class GameValue:
    """Represents a partizan game value."""
    
    def __init__(self, name, left_opts=None, right_opts=None, temperature=None, atomic_weight=None):
        self.name = name
        self.left_opts = left_opts or []
        self.right_opts = right_opts or []
        self.temperature = temperature
        self.atomic_weight = atomic_weight
    
    def __repr__(self):
        return f"Game({self.name}, t={self.temperature}, aw={self.atomic_weight})"
    
    def __str__(self):
        return self.name

# ============================================================
# PREDEFINED GAME VALUES
# ============================================================

ZERO = GameValue("0", left_opts=[], right_opts=[], temperature=0, atomic_weight=0)
STAR = GameValue("*", left_opts=[ZERO], right_opts=[ZERO], temperature=0, atomic_weight=0)
UP = GameValue("↑", temperature=0, atomic_weight="↑")
DOWN = GameValue("↓", temperature=0, atomic_weight="↓")

def integer_value(n):
    """Create integer game value n."""
    if n == 0:
        return ZERO
    elif n == 1:
        return GameValue("1", left_opts=[ZERO], right_opts=[], temperature=float('-inf'), atomic_weight=1)
    elif n == -1:
        return GameValue("-1", left_opts=[], right_opts=[ZERO], temperature=float('-inf'), atomic_weight=-1)
    elif n > 1:
        return GameValue(str(n), left_opts=[integer_value(n-1)], right_opts=[], 
                        temperature=float('-inf'), atomic_weight=n)
    else:  # n < -1
        return GameValue(str(n), left_opts=[], right_opts=[integer_value(n+1)], 
                        temperature=float('-inf'), atomic_weight=n)

def switch_value(n):
    """Create switch game ±n with temperature n."""
    return GameValue(f"±{n}", left_opts=[integer_value(n)], right_opts=[integer_value(-n)], 
                    temperature=n, atomic_weight=f"±{n}")

# ============================================================
# LCG POSITION ANALYSIS
# ============================================================

class LCGPosition:
    """Represents an LCG configuration."""
    
    def __init__(self, left_count, right_count, depth=1, structure="simple"):
        self.left_count = left_count
        self.right_count = right_count
        self.depth = depth
        self.structure = structure
    
    def __repr__(self):
        return f"LCG({self.left_count}L, {self.right_count}R, d={self.depth}, {self.structure})"

def evaluate_depth1(left_count, right_count):
    """Evaluate depth-1 position: k left-leaves, m right-leaves, all converge to terminal 0."""
    if left_count == 0 and right_count == 0:
        return None
    
    if left_count == 0:
        return integer_value(-right_count)
    elif right_count == 0:
        return integer_value(left_count)
    elif left_count == right_count:
        return STAR
    else:
        min_count = min(left_count, right_count)
        if left_count > right_count:
            return switch_value(min_count)
        else:
            return switch_value(-min_count)

# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def analyze_depth1_spectrum():
    """Enumerate all depth-1 values and categorize by type."""
    print("=" * 70)
    print("DEPTH 1 ANALYSIS: All Branching Configurations")
    print("=" * 70)
    
    values_by_type = defaultdict(list)
    all_games = {}
    
    for left in range(0, 6):
        for right in range(0, 6):
            if left == 0 and right == 0:
                continue
            
            game = evaluate_depth1(left, right)
            if game:
                all_games[(left, right)] = game
                
                # Categorize
                if game.name == "*":
                    category = "FUZZY"
                elif game.temperature == 0:
                    category = "COLD (t=0)"
                elif game.temperature == float('-inf'):
                    category = "FROZEN (t=-∞)"
                elif game.temperature > 0:
                    category = f"HOT (t={game.temperature})"
                else:
                    category = "OTHER"
                
                values_by_type[category].append((left, right, game))
    
    # Print by category
    for category in sorted(values_by_type.keys()):
        print(f"\n{category}")
        print("-" * 70)
        configs = values_by_type[category]
        for left, right, game in configs:
            aw = game.atomic_weight if game.atomic_weight else "N/A"
            print(f"  {left}L × {right}R → {game.name:>6} | aw={aw}")
    
    print(f"\n{'=' * 70}")
    print(f"Total depth-1 positions: {len(all_games)}")
    print(f"{'=' * 70}\n")
    
    return all_games

def analyze_temperature_spectrum():
    """Show which temperatures are achievable at depth 1."""
    print("=" * 70)
    print("TEMPERATURE SPECTRUM (Depth 1)")
    print("=" * 70)
    
    temps = defaultdict(list)
    
    for left in range(0, 8):
        for right in range(0, 8):
            if left == 0 and right == 0:
                continue
            
            game = evaluate_depth1(left, right)
            if game and game.temperature is not None:
                temps[game.temperature].append((left, right))
    
    for temp in sorted(temps.keys(), key=lambda x: (x == float('-inf'), x)):
        configs = temps[temp]
        temp_str = "-∞" if temp == float('-inf') else str(temp)
        print(f"\nTemperature t = {temp_str}")
        print(f"  Configurations ({len(configs)} total):")
        for left, right in sorted(configs)[:10]:  # Show first 10
            print(f"    {left}L × {right}R")
        if len(configs) > 10:
            print(f"    ... and {len(configs)-10} more")

def analyze_branching_patterns():
    """Analyze how different branching patterns affect game value."""
    print("\n" + "=" * 70)
    print("BRANCHING PATTERN ANALYSIS")
    print("=" * 70)
    
    print("\n1. SYMMETRIC PATTERNS (Left = Right)")
    print("-" * 70)
    for n in range(1, 6):
        game = evaluate_depth1(n, n)
        print(f"  {n}L × {n}R → {game.name} | Temperature: {game.temperature}")
    
    print("\n2. LEFT-DOMINANT PATTERNS (Left > Right)")
    print("-" * 70)
    for left in range(2, 6):
        for right in range(1, left):
            game = evaluate_depth1(left, right)
            print(f"  {left}L × {right}R → {game.name:>6} | Temperature: {game.temperature:>3}")
    
    print("\n3. PURE ASYMMETRY (One player only)")
    print("-" * 70)
    for k in range(1, 6):
        left_only = evaluate_depth1(k, 0)
        right_only = evaluate_depth1(0, k)
        print(f"  {k}L × 0R → {left_only.name:>3} | 0L × {k}R → {right_only.name:>3}")

def analyze_atomic_weights():
    """Compute and display atomic weights for various game structures."""
    print("\n" + "=" * 70)
    print("ATOMIC WEIGHT ANALYSIS")
    print("=" * 70)
    
    print("\nInteger Atomic Weights (n)")
    print("-" * 70)
    for n in range(-5, 6):
        if n != 0:
            game = integer_value(n)
            print(f"  {n:>3} | aw = {game.atomic_weight}")
    
    print("\nSwitch Atomic Weights (±n, temperature n)")
    print("-" * 70)
    for n in range(1, 6):
        game = switch_value(n)
        print(f"  ±{n} (t={n}) | aw = {game.atomic_weight}")
    
    print("\nInfinitesimal Atomic Weights")
    print("-" * 70)
    print(f"  ↑ (up)     | Temperature: 0 | aw = ↑")
    print(f"  ↓ (down)   | Temperature: 0 | aw = ↓")
    print(f"  * (fuzzy)  | Temperature: 0 | aw = 0")

def relationship_analysis():
    """Analyze relationships between branching and game values."""
    print("\n" + "=" * 70)
    print("BRANCHING → VALUE RELATIONSHIPS")
    print("=" * 70)
    
    print("\nRule 1: Symmetric → Fuzzy")
    print("-" * 70)
    print("Observation: If k_L = k_R, then position = *")
    print("Reasoning: Both players move to identical sub-game value (0)")
    print("Intuition: No player advantage → fuzzy game, temperature 0\n")
    
    print("Rule 2: Asymmetric → Switch or Integer")
    print("-" * 70)
    print("Observation: If k_L ≠ k_R:")
    print("  - Value = ±min(k_L, k_R)")
    print("  - Temperature = min(k_L, k_R)")
    print("  - Atomic Weight = ±min(k_L, k_R)")
    print("Intuition: Minority player limits both sides' incentive\n")
    
    print("Rule 3: Pure Advantage → Integer with t = -∞")
    print("-" * 70)
    print("Observation: If only one player has moves:")
    print("  - k_L > 0, k_R = 0 → value = k_L")
    print("  - k_L = 0, k_R > 0 → value = -k_R")
    print("Intuition: One player wins by force (frozen game)\n")

def depth2_infinitesimal_analysis():
    """Analyze how depth-2 structures create infinitesimals."""
    print("\n" + "=" * 70)
    print("DEPTH 2: INFINITESIMAL GENERATION")
    print("=" * 70)
    
    print("\nStructure: Left leaf (depth 1) vs. Right subtree (depth 2)")
    print("-" * 70)
    print("Left option: single terminal (value 0)")
    print("Right option: {0|0} = * (value * )")
    print("Resulting game: {0|*} = ↑ (infinitesimal up)\n")
    print("Key insight: Asymmetric depths create infinitesimals")
    print("  - {0|*} = ↑  (Right has no advantage in sub-game)")
    print("  - {*|0} = ↓  (Left has no advantage in sub-game)")
    print("  - Temperature = 0 (neither player urgent at 0-temperature)")
    print("  - Atomic weight propagates the infinitesimal nature\n")

def summary_table():
    """Print comprehensive summary table."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE VALUE TABLE (Depth 1-2)")
    print("=" * 70)
    print("\n{:<20} {:<15} {:<15} {:<20}".format(
        "Configuration", "Value", "Temperature", "Atomic Weight"
    ))
    print("-" * 70)
    
    configs = [
        ("1L, 0R", integer_value(1), float('-inf'), 1),
        ("2L, 0R", integer_value(2), float('-inf'), 2),
        ("0L, 1R", integer_value(-1), float('-inf'), -1),
        ("1L, 1R", STAR, 0, 0),
        ("2L, 2R", STAR, 0, 0),
        ("2L, 1R", switch_value(1), 1, "±1"),
        ("3L, 1R", switch_value(1), 1, "±1"),
        ("2L, 3R", switch_value(-2), 2, "±2"),
        ("Depth2: {0|*}", UP, 0, "↑"),
        ("Depth2: {*|0}", DOWN, 0, "↓"),
    ]
    
    for config, value, temp, aw in configs:
        temp_str = "-∞" if temp == float('-inf') else str(temp)
        aw_str = str(aw) if isinstance(aw, str) else str(aw)
        print("{:<20} {:<15} {:<15} {:<20}".format(
            config, value.name, temp_str, aw_str
        ))

def main():
    """Run all analyses."""
    print("\n")
    analyze_depth1_spectrum()
    analyze_temperature_spectrum()
    analyze_branching_patterns()
    analyze_atomic_weights()
    relationship_analysis()
    depth2_infinitesimal_analysis()
    summary_table()
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
