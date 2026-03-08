#!/usr/bin/env python3
"""
EXP-001e: Find ℚ-rational orbits of primitive period 6 for f(x,y)=(y, y²+c+x).

Strategy:
1. Compute R₆(x,c) via resultant (period-6 condition)
2. Compute R₁, R₂, R₃ (sub-period conditions) 
3. Phi₆ = R₆ / (R₁ · R₂ · R₃) — primitive period-6 factor
4. For each x₀ = p/q with small denom, get Phi₆(x₀, c) as poly in c
5. Use rational root theorem to find c ∈ ℚ
6. Verify orbit closes with primitive period 6
"""
from common import run_experiment
import os, json
from fractions import Fraction
from sympy import (symbols, expand, resultant, Poly, factor, Rational,
                   div, ZZ, QQ, factorint, nroots)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp001e-period6-cubic')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}
x, t, c = symbols('x t c')


def build_resultant(N):
    """Build R_N(x,c) = resultant of period-N orbit conditions."""
    xs = [x, t]
    for n in range(1, N):
        xs.append(expand(xs[-1]**2 + c + xs[-2]))
    condA = expand(xs[N] - x)
    condB = expand(x**2 + c + xs[N-1] - t)
    return expand(resultant(condA, condB, t))


def section_compute_phi6():
    """Compute primitive dynatomic polynomial Phi₆."""
    
    print("  Computing resultants R₁..R₆...", flush=True)
    R = {}
    R[1] = expand(c + x**2)
    print("    R₁ done", flush=True)
    
    for N in [2, 3, 6]:
        print(f"    R_{N}...", flush=True, end=" ")
        R[N] = build_resultant(N)
        p = Poly(R[N], x, domain='ZZ[c]')
        print(f"deg_x={p.degree()}", flush=True)
    
    # Phi₆ = R₆ / (R₁ · R₂ · R₃)
    # Actually: R₆ contains R_d for all d | 6: d = 1, 2, 3, 6
    # Phi₆ = R₆ / (R₁ · Phi₂ · Phi₃)
    # Where Phi₂ = R₂/R₁, Phi₃ = R₃/R₁
    
    print("\n  Computing Phi₆ = R₆ / (R₁ · R₂ · R₃)...", flush=True)
    
    # Divide out R₁ first
    num = Poly(R[6], x, c, domain='ZZ')
    for d in [1, 2, 3]:
        divisor = Poly(R[d], x, c, domain='ZZ')
        count = 0
        while True:
            q, r = div(num, divisor, x, c, domain='ZZ')
            if r.is_zero:
                num = q
                count += 1
            else:
                break
        print(f"    Divided by R_{d}: {count} times", flush=True)
    
    phi6 = expand(num.as_expr())
    
    p6 = Poly(phi6, x, domain='ZZ[c]')
    p6c = Poly(phi6, c, domain='ZZ[x]')
    print(f"\n  Phi₆: deg_x = {p6.degree()}, deg_c = {p6c.degree()}")
    
    # Factor Phi₆
    print("  Factoring Phi₆...", flush=True)
    fac = factor(phi6)
    print(f"  Factored Phi₆ = {str(fac)[:500]}")
    
    # Extract irreducible factors
    p6_full = Poly(phi6, x, c, domain='ZZ')
    fac_list = p6_full.factor_list()
    
    print(f"\n  Irreducible factors of Phi₆:")
    factors_info = []
    for fac_poly, mult in fac_list[1]:
        dx = fac_poly.degree(0)  # deg in x
        dc = fac_poly.degree(1)  # deg in c
        td = fac_poly.total_degree()
        expr = fac_poly.as_expr()
        print(f"    deg_x={dx}, deg_c={dc}, total={td}, mult={mult}")
        print(f"      {str(expr)[:200]}")
        factors_info.append({
            'deg_x': dx, 'deg_c': dc, 'total': td, 'mult': mult,
            'expr': expr
        })
    
    state['phi6'] = phi6
    state['factors'] = factors_info
    return {'n_factors': len(factors_info)}


def section_rational_roots():
    """For each factor, find rational points (x₀, c₀) ∈ ℚ²."""
    
    factors = state.get('factors', [])
    
    all_found = []
    
    for fi, finfo in enumerate(factors):
        expr = finfo['expr']
        dc = finfo['deg_c']
        
        print(f"\n  Factor {fi+1}: deg_c={dc}, deg_x={finfo['deg_x']}", flush=True)
        
        found = []
        
        # For each x₀ = p/q
        max_q = 50 if dc <= 3 else 20
        max_p = 80 if dc <= 3 else 30
        
        for qx in range(1, max_q + 1):
            for px in range(-max_p, max_p + 1):
                x0 = Rational(px, qx)
                
                # Evaluate factor at x = x₀
                poly_at_x = expr.subs(x, x0)
                
                if poly_at_x == 0:
                    continue
                
                # Get as polynomial in c
                try:
                    pc = Poly(poly_at_x, c, domain='QQ')
                    coeffs = pc.all_coeffs()
                    
                    if len(coeffs) <= 1:
                        continue
                    
                    # Convert to integer coefficients
                    from math import gcd
                    from functools import reduce
                    
                    denoms = [int(coeff.q) if hasattr(coeff, 'q') else 1 for coeff in coeffs]
                    L = reduce(lambda a, b: a * b // gcd(a, b), denoms)
                    int_coeffs = [int(coeff * L) for coeff in coeffs]
                    
                    a_n = abs(int_coeffs[0])
                    a_0 = abs(int_coeffs[-1])
                    
                    if a_n == 0:
                        continue
                    
                    # c = 0 check
                    if a_0 == 0:
                        val = expr.subs({x: x0, c: Rational(0)})
                        if val == 0:
                            orbit = verify_period6(Fraction(px, qx), Fraction(0))
                            if orbit:
                                found.append({'c': '0', 'x0': str(x0), 'orbit': orbit})
                        continue
                    
                    # Rational root theorem: c = ±p'/q' where p' | a_0, q' | a_n
                    # For efficiency, limit factor enumeration
                    def get_divisors(n, max_div=500):
                        divs = set()
                        for i in range(1, min(n+1, max_div)):
                            if n % i == 0:
                                divs.add(i)
                        return divs
                    
                    p_divs = get_divisors(a_0)
                    q_divs = get_divisors(a_n)
                    
                    for pv in p_divs:
                        for qv in q_divs:
                            for sign in [1, -1]:
                                cv = Rational(sign * pv, qv)
                                val = expr.subs({x: x0, c: cv})
                                if val == 0:
                                    c_frac = Fraction(sign * pv, qv)
                                    orbit = verify_period6(Fraction(px, qx), c_frac)
                                    if orbit:
                                        found.append({
                                            'c': str(cv), 'x0': str(x0),
                                            'orbit': [str(v) for v in orbit]
                                        })
                                        if len(found) <= 3:
                                            print(f"    ✓ c={cv}, x₀={x0}", flush=True)
                except Exception:
                    pass
            
            if len(found) >= 20:
                break
        
        if found:
            print(f"  ✓ Factor {fi+1}: {len(found)} rational period-6 points!")
        else:
            print(f"  ✗ Factor {fi+1}: no rational points found")
        
        all_found.extend(found)
    
    state['found'] = all_found
    return {'total': len(all_found)}


def verify_period6(x0_frac, c_frac):
    """Find x₁ ∈ ℚ that gives primitive period-6 orbit starting at x₀ with param c."""
    MAX_BITS = 800
    
    for qx in range(1, 30):
        for px in range(-50, 51):
            x1 = Fraction(px, qx)
            
            orbit = [x0_frac, x1]
            xprev, xcur = x0_frac, x1
            ok = True
            
            for n in range(2, 8):
                xnext = xcur * xcur + c_frac + xprev
                if (xnext.numerator.bit_length() > MAX_BITS or
                    xnext.denominator.bit_length() > MAX_BITS):
                    ok = False
                    break
                orbit.append(xnext)
                xprev, xcur = xcur, xnext
            
            if not ok:
                continue
            
            # Check period 6
            if orbit[6] == orbit[0] and orbit[7] == orbit[1]:
                # Check primitive (not period 1, 2, or 3)
                is_prim = True
                for d in [1, 2, 3]:
                    if orbit[d] == orbit[0] and orbit[d+1] == orbit[1]:
                        is_prim = False
                        break
                if is_prim:
                    return orbit[:6]
    
    return None


def section_verdict():
    """Summary."""
    found = state.get('found', [])
    
    print(f"\n  ╔══════════════════════════════════════════════════╗")
    print(f"  ║       PERIOD 6 RATIONAL ORBITS — RESULTS        ║")
    print(f"  ╚══════════════════════════════════════════════════╝")
    
    if found:
        print(f"  ✅ Found {len(found)} rational period-6 orbits!")
        for i, entry in enumerate(found[:5]):
            print(f"  {i+1}. c={entry['c']}, orbit={entry['orbit'][:4]}...")
        print(f"\n  → CONJECTURE 3 IS SHARP for period 6")
    else:
        print(f"  ⚠️ No period-6 rational orbits found")
        print(f"     Need: larger x₀ range, or elliptic curve methods")
    
    with open(os.path.join(OUTPUT_DIR, 'results.json'), 'w') as f:
        json.dump(state, f, indent=2, default=lambda o: str(o))
    
    return {'found': len(found)}


run_experiment([
    ("Compute primitive dynatomic Phi₆", section_compute_phi6),
    ("Find rational points on Phi₆ factors", section_rational_roots),
    ("Verdict", section_verdict),
], timeout_sec=300)
