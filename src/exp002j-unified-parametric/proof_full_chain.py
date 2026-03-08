#!/usr/bin/env python3
"""
FULL LOGICAL CHAIN: zero polynomials ⟹ primitive period-3 orbit.

This script does NOT assume the recurrence — it starts from the MAP DEFINITION
f(x,y) = (y, y² + c + bx) and verifies everything from scratch.

Chain:
  Step 1: Define f as a map ℚ² → ℚ²
  Step 2: Compute f(P₀), f²(P₀), f³(P₀) explicitly
  Step 3: Verify f³(P₀) = P₀  (period divides 3)
  Step 4: Verify f(P₀) ≠ P₀   (not a fixed point)
  Step 5: Since 3 is prime, period divides 3 AND period ≠ 1 ⟹ period = 3 exactly
  Step 6: Verify the 3 orbit points are ALL distinct (bonus)
  Step 7: Numerical spot-check with exact Fraction arithmetic
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run_experiment
from sympy import symbols, expand, factor, Rational
from fractions import Fraction

b = symbols('b')

# The universal family
c_fam  = -(29*b**2 + 38*b + 29) / Rational(16)
x0_fam = -(5*b + 7) / Rational(4)
x1_fam = (7*b + 5) / Rational(4)
x2_fam = (b - 1) / Rational(4)

state = {}


def section_step1_map_definition():
    """Step 1: Define the Hénon map f(x,y) = (y, y² + c + bx)."""
    x, y, c_var, b_var = symbols('x y c b')

    fx = y
    fy = y**2 + c_var + b_var * x

    print("  MAP DEFINITION:")
    print(f"    f: (x, y) ↦ ({fx}, {fy})")
    print(f"    f(x,y) = (y,  y² + c + b·x)")
    print()
    print("  A point P₀ = (x₀, x₁) has period 3 under f if and only if:")
    print("    f(P₀) = P₁,  f(P₁) = P₂,  f(P₂) = P₀")
    print("  where P₀, P₁, P₂ are all DISTINCT points in ℚ².")
    print()
    print("  Equivalently, f³(P₀) = P₀ and f(P₀) ≠ P₀.")
    print("  (Since 3 is prime, period|3 and period≠1 ⟹ period=3.)")
    return {'ok': True}


def section_step2_compute_iterates():
    """Step 2: Compute f(P₀), f²(P₀), f³(P₀) from the MAP, not recurrence."""
    print("  Starting point: P₀ = (x₀, x₁)")
    print(f"    x₀ = -(5b+7)/4")
    print(f"    x₁ = (7b+5)/4")
    print(f"    c  = -(29b²+38b+29)/16")
    print()

    # --- f(P₀) = (x₁, x₁² + c + b·x₀) ---
    f1_x = x1_fam
    f1_y = expand(x1_fam**2 + c_fam + b * x0_fam)

    print("  f(P₀) = (x₁,  x₁² + c + b·x₀)")
    print(f"    1st coord = {f1_x}")
    print(f"    2nd coord = {f1_y}")
    print(f"    2nd coord (simplified) = {factor(f1_y)}")

    # Does f(P₀) second coord = x₂?
    diff_f1 = expand(f1_y - x2_fam)
    print(f"\n    f(P₀)_y - x₂ = {diff_f1}")
    assert diff_f1 == 0, f"FAILED: f(P₀)_y ≠ x₂"
    print(f"    ✅ f(P₀) = (x₁, x₂)  — this is P₁")

    # --- f²(P₀) = f(P₁) = (x₂, x₂² + c + b·x₁) ---
    f2_x = x2_fam
    f2_y = expand(x2_fam**2 + c_fam + b * x1_fam)

    print(f"\n  f²(P₀) = f(P₁) = (x₂,  x₂² + c + b·x₁)")
    print(f"    1st coord = {f2_x}")
    print(f"    2nd coord = {f2_y}")
    print(f"    2nd coord (simplified) = {factor(f2_y)}")

    # Does f²(P₀) second coord = x₀?
    diff_f2 = expand(f2_y - x0_fam)
    print(f"\n    f²(P₀)_y - x₀ = {diff_f2}")
    assert diff_f2 == 0, f"FAILED: f²(P₀)_y ≠ x₀"
    print(f"    ✅ f²(P₀) = (x₂, x₀)  — this is P₂")

    # --- f³(P₀) = f(P₂) = (x₀, x₀² + c + b·x₂) ---
    f3_x = x0_fam
    f3_y = expand(x0_fam**2 + c_fam + b * x2_fam)

    print(f"\n  f³(P₀) = f(P₂) = (x₀,  x₀² + c + b·x₂)")
    print(f"    1st coord = {f3_x}")
    print(f"    2nd coord = {f3_y}")
    print(f"    2nd coord (simplified) = {factor(f3_y)}")

    # Does f³(P₀) second coord = x₁?
    diff_f3 = expand(f3_y - x1_fam)
    print(f"\n    f³(P₀)_y - x₁ = {diff_f3}")
    assert diff_f3 == 0, f"FAILED: f³(P₀)_y ≠ x₁"
    print(f"    ✅ f³(P₀) = (x₀, x₁) = P₀")

    state['f3_equals_P0'] = True
    return {'f3_equals_P0': True}


def section_step3_period_divides_3():
    """Step 3: f³(P₀) = P₀ proved ⟹ period divides 3."""
    print("  From Step 2:")
    print("    f(P₀)  = P₁ = (x₁, x₂)")
    print("    f²(P₀) = P₂ = (x₂, x₀)")
    print("    f³(P₀) = P₀ = (x₀, x₁)  ✅")
    print()
    print("  CONCLUSION: P₀ is a periodic point with period dividing 3.")
    print("  The divisors of 3 are: {1, 3}.")
    print("  So period(P₀) ∈ {1, 3}.")
    return {'period_divides_3': True}


def section_step4_not_fixed_point():
    """Step 4: f(P₀) ≠ P₀ ⟹ not a fixed point ⟹ period ≠ 1."""
    print("  f(P₀) = P₁ = (x₁, x₂)")
    print("  P₀     = (x₀, x₁)")
    print()
    print("  For f(P₀) = P₀, we need BOTH:")
    print("    (a) x₁ = x₀   [first coordinates equal]")
    print("    (b) x₂ = x₁   [second coordinates equal]")
    print()

    # Check (a): x₁ - x₀
    diff_a = expand(x1_fam - x0_fam)
    diff_a_factored = factor(diff_a)
    print(f"  (a) x₁ - x₀ = {diff_a} = {diff_a_factored}")
    print(f"      This is zero iff b = -1.")
    print()

    # Check (b): x₂ - x₁
    diff_b = expand(x2_fam - x1_fam)
    diff_b_factored = factor(diff_b)
    print(f"  (b) x₂ - x₁ = {diff_b} = {diff_b_factored}")
    print(f"      This is zero iff b = 1 (solving -3(2b-1)/4 = 0 → b=1/2... let me check)")

    from sympy import solve
    zeros_a = solve(diff_a, b)
    zeros_b = solve(diff_b, b)
    print(f"\n  x₁ = x₀ when b ∈ {zeros_a}")
    print(f"  x₂ = x₁ when b ∈ {zeros_b}")
    print()

    # For f(P₀) = P₀, need BOTH to hold simultaneously
    common = set(zeros_a) & set(zeros_b)
    print(f"  BOTH hold when b ∈ {common}")

    if common:
        # At those values, verify it's indeed a fixed point
        for b_val in common:
            x0_val = x0_fam.subs(b, b_val)
            x1_val = x1_fam.subs(b, b_val)
            x2_val = x2_fam.subs(b, b_val)
            print(f"\n  At b={b_val}: x₀={x0_val}, x₁={x1_val}, x₂={x2_val}")
            print(f"    All equal? {x0_val == x1_val == x2_val}")

    print(f"\n  For b ≠ -1: x₁ ≠ x₀, so the first coordinate of f(P₀)")
    print(f"  differs from the first coordinate of P₀.")
    print(f"  Therefore f(P₀) ≠ P₀, i.e., P₀ is NOT a fixed point.")
    print(f"\n  ✅ period(P₀) ≠ 1 for all b ∈ ℚ \\ {{-1}}")

    state['not_fixed'] = True
    return {'not_fixed': True, 'degenerate_at': str(common)}


def section_step5_period_exactly_3():
    """Step 5: period|3 AND period≠1 ⟹ period=3 (since 3 is prime)."""
    print("  LOGICAL CHAIN:")
    print()
    print("  (A) f³(P₀) = P₀        [Step 2, verified by SymPy]")
    print("      ⟹ period(P₀) divides 3")
    print("      ⟹ period(P₀) ∈ {1, 3}    [since 3 is prime]")
    print()
    print("  (B) f(P₀) ≠ P₀          [Step 4: x₁ ≠ x₀ for b ≠ -1]")
    print("      ⟹ period(P₀) ≠ 1")
    print()
    print("  (A) ∧ (B) ⟹ period(P₀) = 3  ∎")
    print()
    print("  ═══════════════════════════════════════════════════")
    print("  THEOREM: For every b ∈ ℚ \\ {-1}, the point")
    print("    P₀ = (-(5b+7)/4,  (7b+5)/4)")
    print("  is a PRIMITIVE period-3 point of")
    print("    f(x,y) = (y, y² + c + bx)")
    print("  with c = -(29b² + 38b + 29)/16.")
    print("  ═══════════════════════════════════════════════════")
    return {'period_exactly_3': True}


def section_step6_all_distinct():
    """Step 6 (bonus): Verify all 3 orbit points are distinct."""
    print("  The 3 orbit points in ℚ² are:")
    print(f"    P₀ = (x₀, x₁) = (-(5b+7)/4, (7b+5)/4)")
    print(f"    P₁ = (x₁, x₂) = ((7b+5)/4, (b-1)/4)")
    print(f"    P₂ = (x₂, x₀) = ((b-1)/4, -(5b+7)/4)")
    print()

    # P₀ = P₁ iff x₀=x₁ AND x₁=x₂
    d01_x = factor(expand(x0_fam - x1_fam))
    d01_y = factor(expand(x1_fam - x2_fam))
    print(f"  P₀ = P₁ requires x₀=x₁ [{d01_x}=0] AND x₁=x₂ [{d01_y}=0]")

    from sympy import solve
    sol_01x = solve(expand(x0_fam - x1_fam), b)
    sol_01y = solve(expand(x1_fam - x2_fam), b)
    common_01 = set(sol_01x) & set(sol_01y)
    print(f"    x₀=x₁ at b={sol_01x}, x₁=x₂ at b={sol_01y}")
    print(f"    Both at b ∈ {common_01}")

    # P₁ = P₂ iff x₁=x₂ AND x₂=x₀
    d12_x = factor(expand(x1_fam - x2_fam))
    d12_y = factor(expand(x2_fam - x0_fam))
    sol_12x = solve(expand(x1_fam - x2_fam), b)
    sol_12y = solve(expand(x2_fam - x0_fam), b)
    common_12 = set(sol_12x) & set(sol_12y)
    print(f"\n  P₁ = P₂ requires x₁=x₂ AND x₂=x₀")
    print(f"    x₁=x₂ at b={sol_12x}, x₂=x₀ at b={sol_12y}")
    print(f"    Both at b ∈ {common_12}")

    # P₀ = P₂ iff x₀=x₂ AND x₁=x₀
    d02_x = factor(expand(x0_fam - x2_fam))
    d02_y = factor(expand(x1_fam - x0_fam))
    sol_02x = solve(expand(x0_fam - x2_fam), b)
    sol_02y = solve(expand(x1_fam - x0_fam), b)
    common_02 = set(sol_02x) & set(sol_02y)
    print(f"\n  P₀ = P₂ requires x₀=x₂ AND x₁=x₀")
    print(f"    x₀=x₂ at b={sol_02x}, x₁=x₀ at b={sol_02y}")
    print(f"    Both at b ∈ {common_02}")

    all_degen = common_01 | common_12 | common_02
    print(f"\n  ANY two orbit points coincide only at b ∈ {all_degen}")
    print(f"  For all b ∈ ℚ \\ {all_degen}, the 3 orbit points are ALL DISTINCT. ✅")

    return {'all_distinct_except': str(all_degen)}


def section_step7_numerical():
    """Step 7: Numerical spot-check with exact Fraction arithmetic."""
    print("  Spot-checking with exact rational arithmetic (no floats!):")
    print()

    test_values = [
        Fraction(0), Fraction(1), Fraction(2), Fraction(-2),
        Fraction(1, 2), Fraction(-1, 2), Fraction(3, 7),
        Fraction(-17, 5), Fraction(100), Fraction(-99),
        Fraction(1, 100), Fraction(999, 1000),
    ]

    all_ok = True
    for bv in test_values:
        cv = -(29*bv**2 + 38*bv + 29) / 16
        x0 = -(5*bv + 7) / 4
        x1 = (7*bv + 5) / 4
        x2 = (bv - 1) / 4

        # Apply map f three times, starting from (x0, x1)
        # f(x0, x1) = (x1, x1²+c+b·x0)
        f1_x = x1
        f1_y = x1**2 + cv + bv * x0

        # f²: f(f1_x, f1_y) = (f1_y, f1_y²+c+b·f1_x)
        f2_x = f1_y
        f2_y = f1_y**2 + cv + bv * f1_x

        # f³: f(f2_x, f2_y) = (f2_y, f2_y²+c+b·f2_x)
        f3_x = f2_y
        f3_y = f2_y**2 + cv + bv * f2_x

        # Check f³ = identity
        ok_period = (f3_x == x0 and f3_y == x1)
        # Check not fixed point
        ok_prim = (f1_x != x0 or f1_y != x1)
        # Check all 3 points distinct
        P0 = (x0, x1)
        P1 = (f1_x, f1_y)
        P2 = (f2_x, f2_y)
        ok_distinct = (P0 != P1 and P1 != P2 and P0 != P2)

        status = "✅" if (ok_period and ok_prim and ok_distinct) else "❌"
        if not (ok_period and ok_prim and ok_distinct):
            all_ok = False
        print(f"  b={str(bv):>10s}: f³=P₀? {ok_period}  prim? {ok_prim}  "
              f"3 distinct? {ok_distinct}  {status}")

    print()
    if all_ok:
        print(f"  ✅ All {len(test_values)} spot-checks passed with exact arithmetic.")
    else:
        print(f"  ❌ Some checks FAILED!")

    state['numerical_ok'] = all_ok
    return {'all_ok': all_ok, 'n_tested': len(test_values)}


run_experiment([
    ("Step 1: Map definition", section_step1_map_definition),
    ("Step 2: Compute f, f², f³ from MAP definition", section_step2_compute_iterates),
    ("Step 3: f³(P₀) = P₀ ⟹ period divides 3", section_step3_period_divides_3),
    ("Step 4: f(P₀) ≠ P₀ ⟹ not fixed point", section_step4_not_fixed_point),
    ("Step 5: period|3 ∧ period≠1 ⟹ period=3 (QED)", section_step5_period_exactly_3),
    ("Step 6: All 3 orbit points are distinct (bonus)", section_step6_all_distinct),
    ("Step 7: Numerical spot-check with exact Fractions", section_step7_numerical),
], timeout_sec=30)
