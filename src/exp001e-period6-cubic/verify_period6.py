#!/usr/bin/env python3
"""
Quick verification: does c=-7/9, x₀=-1/3 give a period-6 orbit?
Also check c=-33/16, x₀=-3/4.
"""
from common import run_experiment
import os, json
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp001e-period6-cubic')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


def section_verify():
    """
    For each candidate (c, x₀) on the Phi₆ curve, find x₁ that closes
    the orbit with primitive period 6.
    
    The Phi₆ curve says: the FULL period-6 orbit condition is satisfied
    for this (x₀, c). But we still need x₁.
    
    For the recurrence x_{n+1} = x_n² + c + x_{n-1}, a period-6 orbit
    starting at x₀ requires x₁ such that x₆ = x₀ and x₇ = x₁.
    
    Given x₀ and c, x₁ satisfies a degree-2^4 = 16 polynomial.
    But from the Phi₆ factorization, the cubic factor gives us constraints.
    
    Strategy: just try x₁ = p/q for reasonable denominators.
    """
    candidates = [
        (Fraction(-1, 3), Fraction(-7, 9)),
        (Fraction(1, 3), Fraction(-7, 9)),
        (Fraction(-3, 4), Fraction(-33, 16)),
    ]
    
    found = []
    
    for x0, cv in candidates:
        print(f"\n  Testing x₀={x0}, c={cv}:", flush=True)
        
        # Try x₁ with larger range and higher denominators
        for qx in range(1, 100):
            for px in range(-100 * qx // max(qx, 1), 100 * qx // max(qx, 1) + 1):
                x1 = Fraction(px, qx)
                
                orbit = [x0, x1]
                xprev, xcur = x0, x1
                ok = True
                
                for n in range(2, 8):
                    xnext = xcur * xcur + cv + xprev
                    if (xnext.numerator.bit_length() > 1000 or
                        xnext.denominator.bit_length() > 1000):
                        ok = False
                        break
                    orbit.append(xnext)
                    xprev, xcur = xcur, xnext
                
                if not ok:
                    continue
                
                if orbit[6] == orbit[0] and orbit[7] == orbit[1]:
                    # Check primitive
                    is_prim = True
                    for d in [1, 2, 3]:
                        if orbit[d] == orbit[0] and orbit[d+1] == orbit[1]:
                            is_prim = False
                            break
                    if is_prim:
                        found.append({
                            'c': str(cv), 'x0': str(x0), 'x1': str(x1),
                            'orbit': [str(v) for v in orbit[:6]]
                        })
                        print(f"    ✅ PERIOD 6! x₁={x1}")
                        print(f"       orbit = {orbit[:6]}")
                        break
            else:
                continue
            break
        else:
            print(f"    ✗ No x₁ found for denominators up to 99")
    
    state['found'] = found
    return found


def section_additional_search():
    """
    Also try: Factor 1 (which showed no results) might need larger x₀.
    Factor 1: c³ + 3c²x² + 4c² + 3cx⁴ + 4cx² - 11c + x⁶ - 3x² + 6 = 0
    This IS the period-3 dynatomic! (from exp001). So it gives period 3, not 6.
    
    The TRUE period-6 factors are 2, 3, 4, and the degree-18 one.
    
    Also do a brute force search: just iterate orbits with wider range.
    """
    from sympy import Rational as R
    
    # Factor 2: c³ + 3c²x² + 8c² + 3cx⁴ + 12cx² + 13c + x⁶ + 4x⁴ + 5x² + 6 = 0
    # This is our period-6 factor. Let's find MORE rational points on it.
    
    from sympy import symbols, Poly
    x_s, c_s = symbols('x c')
    F2 = (c_s**3 + 3*c_s**2*x_s**2 + 8*c_s**2 + 3*c_s*x_s**4 + 12*c_s*x_s**2 + 
          13*c_s + x_s**6 + 4*x_s**4 + 5*x_s**2 + 6)
    
    print("\n  Searching for more rational points on Factor 2...", flush=True)
    
    factor2_pts = []
    
    for qx in range(1, 80):
        for px in range(-120, 121):
            x0 = R(px, qx)
            # Evaluate F2 at x = x₀, get cubic in c
            f2_at_x = F2.subs(x_s, x0)
            pc = Poly(f2_at_x, c_s, domain='QQ')
            coeffs = pc.all_coeffs()
            
            # Convert to integer coeffs
            from math import gcd
            from functools import reduce
            denoms = [int(coeff.q) if hasattr(coeff, 'q') else 1 for coeff in coeffs]
            L = reduce(lambda a, b: a * b // gcd(a, b), denoms)
            int_coeffs = [int(coeff * L) for coeff in coeffs]
            
            a3 = abs(int_coeffs[0])
            a0 = abs(int_coeffs[-1])
            
            if a3 == 0 or a0 == 0:
                continue
            
            # Rational root theorem
            def divisors(n, mx=1000):
                return [i for i in range(1, min(n+1, mx)) if n % i == 0]
            
            for pv in divisors(a0):
                for qv in divisors(a3):
                    for sign in [1, -1]:
                        cv = R(sign * pv, qv)
                        val = F2.subs({x_s: x0, c_s: cv})
                        if val == 0:
                            factor2_pts.append({'x0': str(x0), 'c': str(cv)})
                            if len(factor2_pts) <= 10:
                                print(f"    (x₀, c) = ({x0}, {cv})", flush=True)
        
        if len(factor2_pts) >= 50:
            break
    
    print(f"\n  Found {len(factor2_pts)} rational points on Factor 2")
    
    # Factor 3 and 4 (the other cubics)
    F3 = (c_s**3 + 3*c_s**2*x_s**2 - 4*c_s**2*x_s + 2*c_s**2 + 3*c_s*x_s**4 - 
          8*c_s*x_s**3 + 8*c_s*x_s**2 - 2*c_s*x_s + 2*c_s + x_s**6 - 4*x_s**5 + 
          6*x_s**4 - 2*x_s**3 - 2*x_s**2 + 3)
    
    print("\n  Searching for rational points on Factor 3...", flush=True)
    factor3_pts = []
    
    for qx in range(1, 60):
        for px in range(-80, 81):
            x0 = R(px, qx)
            f3_at_x = F3.subs(x_s, x0)
            pc = Poly(f3_at_x, c_s, domain='QQ')
            coeffs = pc.all_coeffs()
            
            denoms = [int(coeff.q) if hasattr(coeff, 'q') else 1 for coeff in coeffs]
            L = reduce(lambda a, b: a * b // gcd(a, b), denoms)
            int_coeffs = [int(coeff * L) for coeff in coeffs]
            
            a3 = abs(int_coeffs[0])
            a0 = abs(int_coeffs[-1])
            
            if a3 == 0 or a0 == 0:
                continue
            
            def divisors(n, mx=500):
                return [i for i in range(1, min(n+1, mx)) if n % i == 0]
            
            for pv in divisors(a0):
                for qv in divisors(a3):
                    for sign in [1, -1]:
                        cv = R(sign * pv, qv)
                        val = F3.subs({x_s: x0, c_s: cv})
                        if val == 0:
                            factor3_pts.append({'x0': str(x0), 'c': str(cv)})
                            if len(factor3_pts) <= 10:
                                print(f"    (x₀, c) = ({x0}, {cv})", flush=True)
        
        if len(factor3_pts) >= 30:
            break
    
    print(f"\n  Found {len(factor3_pts)} rational points on Factor 3")
    
    state['factor2_pts'] = factor2_pts
    state['factor3_pts'] = factor3_pts
    return {'f2': len(factor2_pts), 'f3': len(factor3_pts)}


def section_final():
    """Final summary."""
    found = state.get('found', [])
    f2 = state.get('factor2_pts', [])
    f3 = state.get('factor3_pts', [])
    
    print(f"\n  ╔══════════════════════════════════════════════════╗")
    print(f"  ║       PERIOD 6 — FINAL RESULTS                   ║")
    print(f"  ╚══════════════════════════════════════════════════╝")
    
    if found:
        print(f"\n  ✅ FOUND {len(found)} VERIFIED period-6 rational orbits!")
        for entry in found:
            print(f"    c = {entry['c']}")
            print(f"    orbit = {entry['orbit']}")
        print(f"\n  → Conjecture 3 is SHARP for period 6")
    else:
        print(f"\n  ⚠️ Found curve points but couldn't verify orbits")
        print(f"     {len(f2)} points on Factor 2, {len(f3)} points on Factor 3")
        print(f"     These points (x₀, c) satisfy Phi₆ = 0")
        print(f"     But we couldn't find x₁ ∈ ℚ with small denominators")
    
    with open(os.path.join(OUTPUT_DIR, 'results_e.json'), 'w') as f:
        json.dump(state, f, indent=2, default=str)
    
    return {'verified': len(found), 'curve_pts_f2': len(f2), 'curve_pts_f3': len(f3)}


run_experiment([
    ("Verify period-6 candidates from Phi₆", section_verify),
    ("Search for more rational points on Phi₆ factors", section_additional_search),
    ("Final results", section_final),
], timeout_sec=300)
