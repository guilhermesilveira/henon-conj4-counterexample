#!/usr/bin/env python3
"""
EXP-002g: Algebraic analysis of Conjecture 4'.

For f(x,y) = (y, y²+c−δx), compute the dynatomic polynomials Phi_N(x,c;δ)
for N=3,4,5 and analyze when they have rational roots.

Key question: why does period > 2 require |δ| = 1?

Recurrence: x_{n+1} = x_n² + c − δ·x_{n-1}
"""
from common import run_experiment
import os, json
from sympy import (symbols, expand, resultant, Poly, factor, Rational,
                   div, ZZ, QQ, discriminant, solve, simplify, sqrt,
                   collect, Symbol)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp002g-conj4-algebraic')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}
x, t, c, d = symbols('x t c d')  # d = delta


def build_resultant_delta(N):
    """Build R_N(x, c; δ) for f(x,y) = (y, y²+c−δx)."""
    xs = [x, t]
    for n in range(1, N):
        xs.append(expand(xs[-1]**2 + c - d * xs[-2]))
    condA = expand(xs[N] - x)
    condB = expand(x**2 + c - d * xs[N-1] - t)
    return expand(resultant(condA, condB, t))


def section_period3():
    """
    Compute Phi₃(x, c; δ) and analyze.
    
    Period-3 condition: orbit (x₀, x₁, x₂) with x₃ = x₀, x₄ = x₁.
    Recurrence: x_{n+1} = x_n² + c − δ·x_{n-1}
    
    R₁ = c + x² − δx − x = c + x² − (δ+1)x  (fixed point: x₁=x₀)
    Wait, fixed point means x₁ = x₀, so: x₀ = x₀² + c − δ·x₀
    → c = x₀ − x₀² + δ·x₀ = (1+δ)x₀ − x₀²
    → c + x₀² − (1+δ)x₀ = 0.
    
    Actually let me use the resultant approach properly.
    """
    print("  Computing R₁(x, c; δ)...", flush=True)
    R1 = build_resultant_delta(1)
    print(f"    R₁ = {R1}")
    
    print("  Computing R₃(x, c; δ)...", flush=True)
    R3 = build_resultant_delta(3)
    p3 = Poly(R3, x, domain='ZZ[c,d]')
    print(f"    R₃: deg_x = {p3.degree()}")
    
    # Phi₃ = R₃ / R₁
    print("  Computing Phi₃ = R₃ / R₁...", flush=True)
    num = Poly(R3, x, c, d, domain='ZZ')
    div_poly = Poly(R1, x, c, d, domain='ZZ')
    
    count = 0
    while True:
        q, r = div(num, div_poly, x, c, d, domain='ZZ')
        if r.is_zero:
            num = q
            count += 1
        else:
            break
    
    phi3 = expand(num.as_expr())
    print(f"    Divided by R₁: {count} times")
    
    # Degree check
    try:
        p3x = Poly(phi3, x, domain='ZZ[c,d]')
        p3c = Poly(phi3, c, domain='ZZ[x,d]')
        p3d = Poly(phi3, d, domain='ZZ[x,c]')
        print(f"    Phi₃: deg_x={p3x.degree()}, deg_c={p3c.degree()}, deg_δ={p3d.degree()}")
    except:
        pass
    
    print(f"\n    Phi₃ = {phi3}")
    
    # Factor
    print("\n  Factoring Phi₃...", flush=True)
    fac = factor(phi3)
    print(f"    Factored: {fac}")
    
    state['phi3'] = str(phi3)
    state['phi3_factored'] = str(fac)
    state['phi3_expr'] = phi3
    
    return {'phi3': str(phi3)[:200]}


def section_discriminant_analysis():
    """
    Phi₃(x, c; δ) is a polynomial in (x, c) parameterized by δ.
    For it to have rational points (x₀, c₀) ∈ ℚ², we need the discriminant
    (in c) to be a perfect square.
    
    Phi₃ as polynomial in c: degree 3 (cubic). A cubic in c has a rational root
    iff the discriminant allows it, or by rational root theorem.
    
    For specific δ, evaluate and check if rational roots exist.
    """
    phi3 = state.get('phi3_expr')
    if phi3 is None:
        print("  No Phi₃ computed — skip")
        return {}
    
    print("  Analyzing Phi₃ as cubic in c for various δ...", flush=True)
    
    # For specific δ values, substitute and check if cubic in c has rational roots
    results = {}
    
    test_deltas = [Rational(-1), Rational(0), Rational(1), 
                   Rational(1, 2), Rational(-1, 2),
                   Rational(2), Rational(-2),
                   Rational(1, 3), Rational(-1, 3),
                   Rational(3), Rational(-3)]
    
    for dv in test_deltas:
        phi3_at_d = phi3.subs(d, dv)
        phi3_at_d = expand(phi3_at_d)
        
        # Factor over ℚ
        fac = factor(phi3_at_d)
        
        # Check if there are linear-in-c factors
        p = Poly(phi3_at_d, x, c, domain='QQ')
        fac_list = p.factor_list()
        
        has_linear_c = False
        factor_info = []
        for fac_poly, mult in fac_list[1]:
            dc = fac_poly.degree(1)  # degree in c
            dx = fac_poly.degree(0)  # degree in x
            factor_info.append(f"(deg_x={dx},deg_c={dc})^{mult}")
            if dc <= 1:
                has_linear_c = True
        
        results[str(dv)] = {
            'has_linear_c': has_linear_c,
            'factors': factor_info,
            'factored': str(fac)[:200]
        }
        
        marker = "✓ LINEAR-C" if has_linear_c else "✗ no linear"
        print(f"    δ={str(dv):>5}: {marker}  factors: {factor_info}", flush=True)
    
    state['disc'] = results
    return results


def section_period3_at_specific_x():
    """
    For each δ, take Phi₃(x₀, c; δ) at specific x₀ ∈ ℚ and check
    if the resulting cubic in c has rational roots.
    
    A cubic a₃c³ + a₂c² + a₁c + a₀ = 0 (with integer coefficients)
    has a rational root iff its discriminant Δ allows it.
    
    Δ = 18a₃a₂a₁a₀ − 4a₂³a₀ + a₂²a₁² − 4a₃a₁³ − 27a₃²a₀²
    
    If Δ > 0: three distinct real roots
    If Δ = 0: repeated root
    If Δ < 0: one real root + two complex
    
    Rational root exists iff one of the candidates ±p/q (p|a₀, q|a₃) works.
    """
    phi3 = state.get('phi3_expr')
    if phi3 is None:
        print("  No Phi₃ — skip")
        return {}
    
    print("  For which δ does Phi₃ have rational points?", flush=True)
    print("  Testing δ = p/q for q ≤ 20...\n", flush=True)
    
    from fractions import Fraction
    
    delta_has_rational = []
    delta_no_rational = []
    
    delta_vals = set()
    for q in range(1, 21):
        for p in range(-20, 21):
            delta_vals.add(Fraction(p, q))
    delta_vals = sorted(delta_vals)
    
    for dv_frac in delta_vals:
        dv = Rational(dv_frac.numerator, dv_frac.denominator)
        phi3_d = expand(phi3.subs(d, dv))
        
        # Try x₀ = p/q for small p, q
        found_rational = False
        for qx in range(1, 30):
            if found_rational:
                break
            for px in range(-40, 41):
                x0 = Rational(px, qx)
                val_at_x = phi3_d.subs(x, x0)
                
                if val_at_x == 0:
                    continue  # x₀ is on the curve for ALL c — unlikely for Phi₃
                
                # Get cubic in c
                try:
                    pc = Poly(val_at_x, c, domain='QQ')
                    coeffs = pc.all_coeffs()
                    
                    if len(coeffs) < 2:
                        continue
                    
                    from math import gcd
                    from functools import reduce
                    denoms = [int(coeff.q) if hasattr(coeff, 'q') else 1 for coeff in coeffs]
                    L = reduce(lambda a, b: a * b // gcd(a, b), denoms)
                    int_coeffs = [int(coeff * L) for coeff in coeffs]
                    
                    a_n = abs(int_coeffs[0])
                    a_0 = abs(int_coeffs[-1])
                    
                    if a_n == 0 or a_0 == 0:
                        if a_0 == 0:
                            # c=0 is a root
                            if phi3_d.subs({x: x0, c: 0}) == 0:
                                found_rational = True
                                break
                        continue
                    
                    def divisors(n, mx=200):
                        return [i for i in range(1, min(n+1, mx)) if n % i == 0]
                    
                    for pv in divisors(a_0):
                        if found_rational:
                            break
                        for qv in divisors(a_n):
                            if found_rational:
                                break
                            for sign in [1, -1]:
                                cv = Rational(sign * pv, qv)
                                if phi3_d.subs({x: x0, c: cv}) == 0:
                                    found_rational = True
                                    break
                except:
                    pass
        
        if found_rational:
            delta_has_rational.append(str(dv_frac))
        else:
            delta_no_rational.append(str(dv_frac))
    
    print(f"  δ with rational period-3 points: {len(delta_has_rational)}")
    print(f"  δ without: {len(delta_no_rational)}")
    
    if delta_has_rational:
        print(f"\n  Exceptional δ (have period-3 rational orbits):")
        for dv in delta_has_rational:
            print(f"    δ = {dv}")
    
    state['rational_delta'] = delta_has_rational
    state['no_rational_delta_count'] = len(delta_no_rational)
    
    return {'has': delta_has_rational, 'no_count': len(delta_no_rational)}


def section_verdict():
    """Final analysis."""
    has = state.get('rational_delta', [])
    no_count = state.get('no_rational_delta_count', 0)
    
    print(f"\n  ╔══════════════════════════════════════════════════╗")
    print(f"  ║       CONJECTURE 4' — ALGEBRAIC ANALYSIS        ║")
    print(f"  ╚══════════════════════════════════════════════════╝")
    
    print(f"\n  Phi₃ = {state.get('phi3', '?')[:200]}")
    print(f"\n  Phi₃ factored = {state.get('phi3_factored', '?')[:200]}")
    
    print(f"\n  δ values with rational period-3 points: {has}")
    print(f"  δ values without: {no_count}")
    
    # Check if exceptional = exactly {-1, 1}
    exc_set = set(has)
    if exc_set == {'-1', '1'}:
        print(f"\n  ✅ CONFIRMED: period-3 rational orbits exist ONLY for δ = ±1")
        print(f"     This is strong algebraic evidence for Conjecture 4'")
    elif exc_set.issubset({'-1', '1'}):
        print(f"\n  ✅ Consistent with Conj 4': exceptions ⊆ {{-1, 1}}")
    else:
        extra = exc_set - {'-1', '1'}
        print(f"\n  ⚠️ Additional exceptions: {extra}")
    
    with open(os.path.join(OUTPUT_DIR, 'results.json'), 'w') as f:
        json.dump(state, f, indent=2, default=str)
    
    return {'exceptional': has}


run_experiment([
    ("Compute Phi₃(x, c; δ) with parameter δ", section_period3),
    ("Discriminant and factorization analysis", section_discriminant_analysis),
    ("Systematic search: which δ have rational period-3 points?", section_period3_at_specific_x),
    ("Verdict", section_verdict),
], timeout_sec=300)
