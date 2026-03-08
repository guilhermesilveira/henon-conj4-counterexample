#!/usr/bin/env python3
"""
EXP-002j var d: FINAL PROOF — Universal period-3 for ALL δ ∈ ℚ.

DISCOVERY: The exp002i family, when reparametrized as continuous function of δ,
gives a period-3 orbit for EVERY δ ∈ ℚ in the MINUS convention.

And since PLUS convention = MINUS with δ→-δ, this gives period-3 for ALL δ
in BOTH conventions.

The exp002h "failures" at half-integers were FALSE NEGATIVES:
the orbits have denominator 8, beyond the search range denom_max=4-5.
"""
from common import run_experiment
import os, json
from fractions import Fraction
from sympy import symbols, expand, Rational, factor

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp002j-unified-parametric')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}
d = symbols('d')


def section_minus_universal_proof():
    """PROVE: family works for ALL δ in MINUS convention."""
    # Parametrize by δ directly (continuous, not just k∈ℤ)
    x0 = (5*d - 7) / Rational(4)
    x1 = (5 - 7*d) / Rational(4)
    x2 = -(d + 1) / Rational(4)
    c = -(29*d**2 - 38*d + 29) / Rational(16)
    
    # MINUS convention: x_{n+1} = x_n² + c - δ·x_{n-1}
    eq1 = expand(x1**2 + c - d*x0 - x2)
    eq2 = expand(x2**2 + c - d*x1 - x0)
    eq3 = expand(x0**2 + c - d*x2 - x1)
    
    print("  THEOREM: Period-3 for ALL δ ∈ ℚ (MINUS convention)")
    print(f"  f(x,y) = (y, y² + c − δx)")
    print(f"\n  Family (parametrized by δ):")
    print(f"    x₀ = (5δ − 7)/4")
    print(f"    x₁ = (5 − 7δ)/4")
    print(f"    x₂ = −(δ + 1)/4")
    print(f"    c  = −(29δ² − 38δ + 29)/16")
    print(f"\n  Verification:")
    print(f"    x₁² + c − δx₀ − x₂ = {eq1}")
    print(f"    x₂² + c − δx₁ − x₀ = {eq2}")
    print(f"    x₀² + c − δx₂ − x₁ = {eq3}")
    
    ok = (eq1 == 0 and eq2 == 0 and eq3 == 0)
    print(f"\n  {'✅ ALL IDENTICALLY ZERO — QED' if ok else '❌ FAILED'}")
    
    state['minus_universal'] = ok
    return {'proved': ok}


def section_plus_universal_proof():
    """PROVE: translating to PLUS convention via b = -δ."""
    b = symbols('b')
    
    # Standard form: f(x,y) = (y, y² + c + bx) where b = -δ, so δ = -b
    x0 = (5*(-b) - 7) / Rational(4)  # = -(5b+7)/4
    x1 = (5 - 7*(-b)) / Rational(4)  # = (5+7b)/4
    x2 = -((-b) + 1) / Rational(4)   # = (b-1)/4
    c = -(29*(-b)**2 - 38*(-b) + 29) / Rational(16)  # = -(29b²+38b+29)/16
    
    # PLUS (standard) convention: x_{n+1} = x_n² + c + b·x_{n-1}
    eq1 = expand(x1**2 + c + b*x0 - x2)
    eq2 = expand(x2**2 + c + b*x1 - x0)
    eq3 = expand(x0**2 + c + b*x2 - x1)
    
    print("  THEOREM: Period-3 for ALL b ∈ ℚ (STANDARD convention)")
    print(f"  f(x,y) = (y, y² + c + bx)   [Jacobian = b]")
    print(f"\n  Family (parametrized by b):")
    print(f"    x₀ = −(5b + 7)/4")
    print(f"    x₁ = (5 + 7b)/4 = (7b + 5)/4")
    print(f"    x₂ = (b − 1)/4")
    print(f"    c  = −(29b² + 38b + 29)/16")
    print(f"\n  Verification:")
    print(f"    x₁² + c + bx₀ − x₂ = {eq1}")
    print(f"    x₂² + c + bx₁ − x₀ = {eq2}")
    print(f"    x₀² + c + bx₂ − x₁ = {eq3}")
    
    ok = (eq1 == 0 and eq2 == 0 and eq3 == 0)
    print(f"\n  {'✅ ALL IDENTICALLY ZERO — QED' if ok else '❌ FAILED'}")
    
    # Primitivity: when is x₀ = x₁?
    diff = expand(x0 - x1)
    print(f"\n  Primitivity: x₀ − x₁ = {factor(diff)}")
    from sympy import solve
    degen = solve(diff, b)
    print(f"  Degenerate (fixed point) when b = {degen}")
    print(f"  → Period-3 is PRIMITIVE for all b ≠ {degen}")
    
    state['plus_universal'] = ok
    state['degen'] = str(degen)
    return {'proved': ok}


def section_verify_half_integers():
    """Verify the formula at previously-failed half-integers."""
    print("  Verifying at 'failed' half-integers (PLUS convention):")
    
    for b_val in [Fraction(1,2), Fraction(-1,2), Fraction(3,2), Fraction(-3,2),
                  Fraction(5,2), Fraction(-5,2), Fraction(7,2), Fraction(-7,2)]:
        x0 = -(5*b_val + 7) / 4
        x1 = (7*b_val + 5) / 4
        x2 = (b_val - 1) / 4
        c = -(29*b_val**2 + 38*b_val + 29) / 16
        
        # Verify PLUS convention
        check1 = x1**2 + c + b_val*x0
        check2 = x2**2 + c + b_val*x1
        check3 = x0**2 + c + b_val*x2
        
        ok = (check1 == x2 and check2 == x0 and check3 == x1)
        prim = (x0 != x1)
        
        print(f"  b={str(b_val):>5s}: x₀={x0}, x₁={x1}, x₂={x2}, c={c}")
        print(f"          valid={ok}, primitive={prim}, x_denom={x0.denominator}")
    
    return {'done': True}


def section_verify_irrational_extension():
    """Can we extend to irrational δ? The formula is algebraic, so yes!"""
    print("  The formula is POLYNOMIAL in b (= Jacobian parameter):")
    print("  x₀ = -(5b+7)/4,  x₁ = (7b+5)/4,  x₂ = (b-1)/4")
    print("  c = -(29b²+38b+29)/16")
    print()
    print("  This works for ALL b ∈ ℝ (and even ℂ)!")
    print("  The map f(x,y)=(y, y²+c+bx) has a period-3 orbit")
    print("  for EVERY value of b, as long as b ≠ -1 (where it degenerates")
    print("  to a fixed point).")
    print()
    print("  At b = -1 (area-preserving): x₀=x₁=x₂=-1/2, c=-5/4 → FIXED POINT")
    print("  But other period-3 orbits exist at b=-1 (via Φ₃ factorization, e.g. c=-1, orbit (0,-1,0))")
    
    # Double-check at b=-1
    b_val = Fraction(-1)
    x0 = -(5*b_val + 7) / 4
    x1 = (7*b_val + 5) / 4
    x2 = (b_val - 1) / 4
    c = -(29*b_val**2 + 38*b_val + 29) / 16
    
    print(f"\n  b=-1: x₀={x0}, x₁={x1}, x₂={x2}, c={c}")
    print(f"  All equal? {x0==x1==x2}")
    
    # Verify it's a fixed point of the map
    # Fixed point: (p,p) → (p, p²+c+bp) = (p, p) iff p²+c+bp = p
    # p = -1/2, c = -5/4, b = -1:
    # (-1/2)² + (-5/4) + (-1)(-1/2) = 1/4 - 5/4 + 1/2 = -1 + 1/2 = -1/2 = p ✓
    check = x0**2 + c + b_val*x0
    print(f"  x₀²+c+bx₀ = {check} = x₀? {check == x0}")
    
    return {'done': True}


def section_final_theorem():
    """State the final theorem precisely."""
    print("\n  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║           MAIN THEOREM (PROVED ALGEBRAICALLY)                ║")
    print("  ╠══════════════════════════════════════════════════════════════╣")
    print("  ║                                                              ║")
    print("  ║  For every b ∈ ℚ \\ {-1}, the generalized Hénon map          ║")
    print("  ║    f(x,y) = (y, y² + c + bx)                                ║")
    print("  ║  admits a PRIMITIVE period-3 orbit over ℚ.                   ║")
    print("  ║                                                              ║")
    print("  ║  Explicit formulas:                                          ║")
    print("  ║    c  = -(29b² + 38b + 29)/16                               ║")
    print("  ║    x₀ = -(5b + 7)/4                                         ║")
    print("  ║    x₁ = (7b + 5)/4                                          ║")
    print("  ║    x₂ = (b - 1)/4                                           ║")
    print("  ║                                                              ║")
    print("  ║  At b = -1 (area-preserving): degenerates to fixed point,   ║")
    print("  ║  but period-3 orbits exist via Φ₃ factorization.            ║")
    print("  ║                                                              ║")
    print("  ║  CONSEQUENCE: BIRS 2023 Conjecture 4 is FALSE.              ║")
    print("  ║  Period > 2 exists for EVERY b ∈ ℚ, not generically.        ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    
    print("\n  PROOF: Direct algebraic verification in SymPy.")
    print("  All three period-3 equations reduce to 0 as polynomials in b.")
    print("  The orbit is primitive for b ≠ -1 since x₀-x₁ = -3(b+1).")
    
    # Save formal result
    result = {
        'theorem': 'For every b in Q\\{-1}, f(x,y)=(y,y^2+c+bx) has a primitive period-3 orbit over Q',
        'formulas': {
            'c': '-(29b^2 + 38b + 29)/16',
            'x0': '-(5b + 7)/4',
            'x1': '(7b + 5)/4',
            'x2': '(b - 1)/4',
        },
        'degenerate_at': 'b = -1 (fixed point)',
        'proof_method': 'Direct SymPy verification: all 3 equations = 0 identically in b',
        'consequence': 'BIRS 2023 Conjecture 4 is FALSE for ALL b in Q',
        'proved_symbolically': state.get('plus_universal', False),
    }
    
    with open(os.path.join(OUTPUT_DIR, 'THEOREM.json'), 'w') as f:
        json.dump(result, f, indent=2)
    
    return result


run_experiment([
    ("PROVE: MINUS convention universal", section_minus_universal_proof),
    ("PROVE: PLUS (standard) convention universal", section_plus_universal_proof),
    ("Verify at half-integers (previously 'failed')", section_verify_half_integers),
    ("Extension to all reals", section_verify_irrational_extension),
    ("FINAL THEOREM", section_final_theorem),
], timeout_sec=60)
