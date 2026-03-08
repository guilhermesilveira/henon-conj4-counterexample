#!/usr/bin/env python3
"""
EXP-002j var b: Convention-aware unified parametric family.

CRITICAL DISCOVERY: exp002i used f(x,y)=(y, y²+c-δx) but exp002h used f(x,y)=(y, y²+c+δx).
These are DIFFERENT conventions!

In exp002i's -δ convention:
  Period-3 family: x₀=-(5k+6)/2, x₁=(7k+6)/2, x₂=k/2, δ=-(2k+1), c=-(29k²+48k+24)/4

In exp002h's +δ convention (the standard one), this corresponds to:
  δ' = -δ = 2k+1 (positive odd) → same orbit coords

So the exp002i family gives period-3 for δ = 2k+1 (all positive odd, and by symmetry all odd)
in the STANDARD +δ convention.

But exp002h found period-3 at ALL integers in +δ convention — including EVEN ones.
The even family is NEW and needs its own parametric proof.

This script:
1. Verifies the sign convention mismatch
2. Translates exp002i to +δ and proves symbolically
3. Searches for a parametric family for even δ in +δ convention
4. Tests if there's a UNIVERSAL family for ALL rational δ
"""
from common import run_experiment
import os, json, math
from fractions import Fraction
from sympy import symbols, expand, Rational, factor, solve, Poly

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp002j-unified-parametric')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


def section_verify_convention():
    """Confirm the sign convention mismatch."""
    print("  Convention check:")
    print("  exp002i: x_{n+1} = x_n² + c - δ·x_{n-1}  (eq in prove_family.py line 15)")
    print("  exp002h: x_{n+1} = x_n² + c + δ·x_{n-1}  (check_periods code)")
    
    # Verify exp002i family at k=1, δ=-(2·1+1)=-3 in MINUS convention
    k_val = 1
    delta_minus = -(2*k_val+1)  # -3
    x0 = Fraction(-(5*k_val+6), 2)  # -11/2
    x1 = Fraction(7*k_val+6, 2)     # 13/2
    x2 = Fraction(k_val, 2)          # 1/2
    c = Fraction(-(29*k_val**2 + 48*k_val + 24), 4)  # -101/4
    
    # Minus convention: x₂ = x₁² + c - δ·x₀
    check_minus = x1**2 + c - delta_minus*x0
    # Plus convention: x₂ = x₁² + c + δ·x₀  
    check_plus = x1**2 + c + delta_minus*x0
    
    print(f"\n  k=1, δ=-3:")
    print(f"  x₀={x0}, x₁={x1}, x₂={x2}, c={c}")
    print(f"  MINUS: x₁²+c-δx₀ = {check_minus} {'= x₂ ✅' if check_minus == x2 else '≠ x₂ ❌'}")
    print(f"  PLUS:  x₁²+c+δx₀ = {check_plus} {'= x₂ ✅' if check_plus == x2 else '≠ x₂ ❌'}")
    
    # In PLUS convention, same orbit works at δ=+3 (negate δ)
    delta_plus = 3  # = -delta_minus
    check_plus3 = x1**2 + c + delta_plus*x0
    print(f"\n  Same orbit with δ=+3 (PLUS convention):")
    print(f"  x₁²+c+3x₀ = {check_plus3} {'= x₂ ✅' if check_plus3 == x2 else '≠ x₂ ❌'}")
    
    return {'minus_works': check_minus == x2, 'plus_needs_negation': check_plus3 == x2}


def section_sympy_prove_translated():
    """Prove the translated family: δ_plus = 2k+1 in + convention."""
    k = symbols('k')
    
    d = 2*k + 1  # δ in PLUS convention
    x0 = -(5*k + 6) / Rational(2)
    x1 = (7*k + 6) / Rational(2)
    x2 = k / Rational(2)
    c = -(29*k**2 + 48*k + 24) / Rational(4)
    
    # Plus convention: x₂ = x₁² + c + δ·x₀
    eq1 = expand(x1**2 + c + d*x0 - x2)
    eq2 = expand(x2**2 + c + d*x1 - x0)
    eq3 = expand(x0**2 + c + d*x2 - x1)
    
    print("  Symbolic proof in PLUS convention (δ = 2k+1):")
    print(f"  eq1 (x₁²+c+δx₀-x₂) = {eq1}")
    print(f"  eq2 (x₂²+c+δx₁-x₀) = {eq2}")
    print(f"  eq3 (x₀²+c+δx₂-x₁) = {eq3}")
    
    all_zero = (eq1 == 0 and eq2 == 0 and eq3 == 0)
    print(f"\n  All zero? {all_zero}")
    
    if all_zero:
        print("  ✅ PROVED: For δ = 2k+1 (all odd integers), period-3 exists in + convention")
    
    # Now for NEGATIVE odd: δ = -(2k+1) in + convention
    d_neg = -(2*k + 1)
    # Need different orbit coords. In - convention with δ=-(2k+1), the same family works.
    # In + convention with δ=-(2k+1), we need to find new coords.
    # Actually, let's try: the - convention family at δ=-(2m+1) translates to 
    # + convention at δ'=2m+1. So for NEGATIVE δ' in + convention, we need m such that
    # δ' = -(2m+1), i.e., we need a different parametrization.
    
    # But we can also try: in - convention, there might be families for positive δ too.
    # Actually the exp002i code also proved a "positive odd" family. Let me check.
    
    # For now: the key result is that period-3 exists for all POSITIVE odd δ in + convention.
    # For negative odd and even, we need separate families.
    
    state['odd_positive_proved'] = all_zero
    return {'odd_positive_proved': all_zero}


def section_find_even_family():
    """Find parametric family for even δ in + convention."""
    print("  Finding even-δ family in + convention:")
    
    # Collect (δ, x₀, x₁, x₂, c) for even δ using discriminant method
    data = []
    for d in range(-20, 21, 2):
        delta = Fraction(d)
        # Use discriminant method from exp002h
        x_vals = set()
        for q in range(1, 5):
            for p in range(-40*q, 40*q+1):
                x_vals.add(Fraction(p, q))
        x_vals = sorted(x_vals)
        
        found = False
        for x0 in x_vals:
            if found:
                break
            for x1 in x_vals:
                if x0 == x1:
                    continue
                inner = x0 * (1 + delta) + x1 * (x1 - delta)
                D = 1 + 4 * inner
                if D < 0:
                    continue
                num = D.numerator
                den = D.denominator
                if num < 0:
                    continue
                sn = math.isqrt(num)
                sd = math.isqrt(den)
                if sn * sn != num or sd * sd != den:
                    continue
                sqrt_D = Fraction(sn, sd)
                for sign in [1, -1]:
                    x2 = (-1 + sign * sqrt_D) / 2
                    c = x2 - x1*x1 - delta*x0
                    x3 = x2*x2 + c + delta*x1
                    if x3 != x0:
                        continue
                    x4 = x0*x0 + c + delta*x2
                    if x4 != x1:
                        continue
                    if x0 == x1 == x2:
                        continue
                    data.append((d, x0, x1, x2, c))
                    found = True
                    break
    
    print(f"\n  {'δ':>4s} {'4x₀':>8s} {'4x₁':>8s} {'4x₂':>8s} {'16c':>10s}")
    for d, x0, x1, x2, c in data:
        print(f"  {d:4d} {int(4*x0):8d} {int(4*x1):8d} {int(4*x2):8d} {int(16*c):10d}")
    
    # Try to fit polynomial: 4x₀ = a·δ² + b·δ + c₀
    # Need at least 3 points for quadratic
    # Focus on data that seems "smooth" (same branch)
    
    # For negative even: -2,-4,-6,-8: 4x₀ = -9,-27,-37,-51
    # Differences: -18, -10, -14 — NOT polynomial!
    
    # Multiple branches! Let me collect ALL orbits for a few δ values
    print("\n  Multiple orbits at δ=-2 (+ convention):")
    delta = Fraction(-2)
    count = 0
    x_vals = set()
    for q in range(1, 6):
        for p in range(-50*q, 50*q+1):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
    seen = set()
    for x0 in x_vals:
        for x1 in x_vals:
            if x0 == x1:
                continue
            inner = x0 * (1 + delta) + x1 * (x1 - delta)
            D = 1 + 4 * inner
            if D < 0:
                continue
            num = D.numerator
            den = D.denominator
            if num < 0:
                continue
            sn = math.isqrt(num)
            sd = math.isqrt(den)
            if sn * sn != num or sd * sd != den:
                continue
            sqrt_D = Fraction(sn, sd)
            for sign in [1, -1]:
                x2 = (-1 + sign * sqrt_D) / 2
                c = x2 - x1*x1 - delta*x0
                x3 = x2*x2 + c + delta*x1
                if x3 != x0:
                    continue
                x4 = x0*x0 + c + delta*x2
                if x4 != x1:
                    continue
                if x0 == x1 == x2:
                    continue
                orbit = frozenset([(x0,x1),(x1,x2),(x2,x0)])
                if orbit not in seen:
                    seen.add(orbit)
                    count += 1
                    s = x0+x1+x2
                    print(f"    #{count}: x₀={x0}, x₁={x1}, x₂={x2}, c={c}, Σ={s}")
                    if count >= 10:
                        break
            if count >= 10:
                break
        if count >= 10:
            break
    
    state['even_data'] = data
    return {'count': len(data)}


def section_general_parametric():
    """Try general approach: solve period-3 with x₀ as free parameter."""
    from sympy import symbols, solve, expand, factor, Rational
    
    x0, x1, d, c_sym = symbols('x0 x1 d c')
    
    print("  General period-3 in + convention:")
    print("  eq1: x₂ = x₁² + c + δx₀")
    print("  eq2: x₀ = x₂² + c + δx₁")
    print("  eq3: x₁ = x₀² + c + δx₂")
    
    # From eq1: x₂ = x₁² + c + δx₀
    x2 = x1**2 + c_sym + d*x0
    
    # From eq2: x₀ = x₂² + c + δx₁
    eq2 = expand(x2**2 + c_sym + d*x1 - x0)
    
    # From eq3: x₁ = x₀² + c + δx₂
    eq3 = expand(x0**2 + c_sym + d*x2 - x1)
    
    # Solve eq3 for c:
    c_from_eq3 = solve(eq3, c_sym)
    print(f"\n  From eq3: c = {c_from_eq3}")
    
    if c_from_eq3:
        c_val = c_from_eq3[0]
        print(f"  c = {factor(c_val)}")
        
        # Substitute into eq2
        eq2_sub = expand(eq2.subs(c_sym, c_val))
        print(f"\n  eq2 after substituting c: degree in x1 = {Poly(eq2_sub, x1).degree()}")
        eq2_factored = factor(eq2_sub)
        print(f"  Factored: {eq2_factored}")
        
        # This gives us a relation between x0, x1, δ
        # If it factors nicely, we can parametrize one branch
    
    return {'done': True}


def section_prove_all_rational():
    """Prove period-3 exists for ALL rational δ using resultant approach."""
    from sympy import symbols, expand, factor, Rational, resultant
    
    d = symbols('d')
    
    # Strategy: parameterize x₁ as a function of x₀ and δ, then show
    # there's always a rational solution.
    
    # From the general approach: we have c and two equations.
    # The period-3 curve Φ₃(x₀, x₁; c, δ) = 0 has genus.
    # If genus 0, it's parametrizable → rational points for all δ.
    
    # Alternative: we know the exp002i family gives ONE rational point on Φ₃
    # for each odd δ. Can we extend?
    
    # Actually, let's try a DIRECT approach. The exp002i family in -convention
    # works for all δ (not just integers!). In + convention:
    # Replace δ → -δ: the family gives period-3 at δ_plus = -δ_minus for all δ_minus.
    # Since δ_minus ranges over all odd integers, δ_plus ranges over all odd integers too.
    # But it's the SAME set!
    
    # Wait — the original family parameter is k, with δ_minus = -(2k+1).
    # In + convention: δ_plus = 2k+1.
    # As k ranges over integers, δ_plus = ..., -3, -1, 1, 3, 5, ...
    # So we get ALL odd integers in + convention.
    
    # For EVEN integers in + convention, we need a different family.
    # Let's see if we can find one using SymPy.
    
    # Ansatz for even δ: x₀ = (αδ+β)/4, x₁ = (γδ+ε)/4, x₂ = (ζδ+η)/4
    a, b, g, e, z, h = symbols('a b g e z h', integer=True)
    
    x0 = (a*d + b) / Rational(4)
    x1 = (g*d + e) / Rational(4)
    x2 = (z*d + h) / Rational(4)
    c_sym = x2 - x1**2 - d*x0  # from eq1
    
    eq2_raw = expand(x2**2 + c_sym + d*x1 - x0)
    eq3_raw = expand(x0**2 + c_sym + d*x2 - x1)
    
    # These are quadratics in d. For them to vanish for all d, 
    # coefficients of d², d¹, d⁰ must all be zero.
    from sympy import Poly
    
    p2 = Poly(eq2_raw, d)
    p3 = Poly(eq3_raw, d)
    
    print("  Linear ansatz xᵢ = (αᵢδ+βᵢ)/4:")
    print(f"  eq2 as polynomial in δ: coeffs = {p2.all_coeffs()}")
    print(f"  eq3 as polynomial in δ: coeffs = {p3.all_coeffs()}")
    
    # Solve the system of coefficient equations
    coeffs2 = p2.all_coeffs()
    coeffs3 = p3.all_coeffs()
    
    all_coeffs = coeffs2 + coeffs3
    print(f"\n  {len(all_coeffs)} equations in 6 unknowns (a,b,g,e,z,h)")
    
    solutions = solve(all_coeffs, [a, b, g, e, z, h])
    print(f"  Solutions: {solutions}")
    
    if solutions:
        for sol in solutions[:5]:
            print(f"    {sol}")
    
    return {'done': True}


def section_verdict():
    """Summary."""
    odd_proved = state.get('odd_positive_proved', False)
    
    print("\n  ╔══════════════════════════════════════════════════╗")
    print("  ║ EXP-002j: UNIFIED PARAMETRIC FAMILY               ║")
    print("  ╚══════════════════════════════════════════════════╝")
    
    print(f"\n  SIGN CONVENTION: exp002i used f(x,y)=(y,y²+c-δx)")
    print(f"                   exp002h used f(x,y)=(y,y²+c+δx)")
    
    print(f"\n  In STANDARD (+δ) convention:")
    print(f"  • Odd δ: period-3 PROVED (exp002i family with sign flip)")
    print(f"  • Even δ: period-3 FOUND computationally, no parametric proof yet")
    
    with open(os.path.join(OUTPUT_DIR, 'results_b.json'), 'w') as f:
        json.dump({
            'convention_mismatch': True,
            'odd_proved_plus': odd_proved,
            'even_needs_family': True,
        }, f, indent=2)
    
    return {'odd_proved': odd_proved}


run_experiment([
    ("Verify convention mismatch", section_verify_convention),
    ("SymPy prove translated family (odd)", section_sympy_prove_translated),
    ("Find even-δ family", section_find_even_family),
    ("General parametric approach", section_general_parametric),
    ("Prove for all rational δ", section_prove_all_rational),
    ("Verdict", section_verdict),
], timeout_sec=300)
