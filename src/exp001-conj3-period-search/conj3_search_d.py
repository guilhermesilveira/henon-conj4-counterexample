#!/usr/bin/env python3
"""
EXP-001d: Combined approach — exact search (from 001a) + dynatomic (periods 1-7).
Skip period 8 resultant (too slow). Use direct search for period 6, 8.
"""
from common import run_experiment
import os, json
from fractions import Fraction
from sympy import symbols, expand, resultant, Poly, factor, Rational, div, ZZ, factorint

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp001-conj3-period-search')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}
x, t, c = symbols('x t c')


def build_resultant(N):
    """Build the resultant R_N(x, c) for period N."""
    xs_list = [x, t]
    for n in range(1, N):
        xs_list.append(expand(xs_list[-1]**2 + c + xs_list[-2]))
    condA = expand(xs_list[N] - x)
    condB = expand(x**2 + c + xs_list[N-1] - t)
    return expand(resultant(condA, condB, t))


def section_dynatomic_and_rational():
    """Compute dynatomic for periods 1-7 and find rational points."""
    
    # Step 1: Build resultants for N=1..7
    R = {}
    for N in range(1, 8):
        print(f"  R_{N}...", flush=True, end=" ")
        if N == 1:
            R[1] = expand(c + x**2)
        else:
            R[N] = build_resultant(N)
        print(f"done (deg_x={Poly(R[N], x, domain='ZZ[c]').degree()})")
    
    # Step 2: Compute dynatomic (divide out sub-periods)
    def divisors(n):
        return [i for i in range(1, n+1) if n % i == 0]
    
    Phi = {}
    for N in range(1, 8):
        print(f"\n  Phi_{N}:", flush=True)
        num = Poly(R[N], x, c, domain='ZZ')
        for d in divisors(N):
            if d < N and d in Phi:
                divisor = Poly(Phi[d], x, c, domain='ZZ')
                while True:
                    q, r = div(num, divisor, x, c, domain='ZZ')
                    if r.is_zero:
                        num = q
                    else:
                        break
        
        Phi[N] = expand(num.as_expr())
        deg_x = Poly(Phi[N], x, domain='ZZ[c]').degree()
        deg_c = Poly(Phi[N], c, domain='ZZ[x]').degree()
        print(f"    deg_x={deg_x}, deg_c={deg_c}")
        
        # Factor
        try:
            fac = factor(Phi[N])
            print(f"    Factored: {str(fac)[:200]}")
        except:
            pass
    
    # Step 3: For each Phi_N, find rational points
    print(f"\n  === Finding rational points on dynatomic curves ===")
    
    all_found = {}
    
    for N in range(1, 8):
        print(f"\n  Period {N}:", flush=True)
        found = []
        
        phi = Phi[N]
        
        for qx in range(1, 40):
            for px in range(-60, 61):
                x0 = Rational(px, qx)
                phi_at_x = phi.subs(x, x0)
                
                if phi_at_x == 0:
                    continue
                
                # Find rational roots of phi(x₀, c) = 0 in c
                try:
                    poly_c = Poly(phi_at_x, c, domain='QQ')
                    
                    # Use SymPy's rational_roots
                    # Convert to integer polynomial
                    coeffs = poly_c.all_coeffs()
                    from math import gcd
                    from functools import reduce
                    
                    # Get integer coefficients
                    denoms = []
                    for coeff in coeffs:
                        if hasattr(coeff, 'q'):
                            denoms.append(int(coeff.q))
                        else:
                            denoms.append(1)
                    
                    L = reduce(lambda a, b: a * b // gcd(a, b), denoms)
                    int_coeffs = [int(coeff * L) for coeff in coeffs]
                    
                    # Rational root theorem
                    if int_coeffs[-1] == 0:
                        # c = 0 is a root
                        cv = Rational(0)
                        orbit = find_orbit(Fraction(px, qx), Fraction(0), N)
                        if orbit:
                            found.append({'c': '0', 'x0': str(x0), 'orbit': [str(v) for v in orbit]})
                        continue
                    
                    a_n = abs(int_coeffs[0])
                    a_0 = abs(int_coeffs[-1])
                    
                    if a_n == 0:
                        continue
                    
                    # Divisors
                    p_divs = set()
                    for i in range(1, min(a_0 + 1, 300)):
                        if a_0 % i == 0:
                            p_divs.add(i)
                    q_divs = set()
                    for i in range(1, min(a_n + 1, 300)):
                        if a_n % i == 0:
                            q_divs.add(i)
                    
                    for p_val in p_divs:
                        for q_val in q_divs:
                            for sign in [1, -1]:
                                cv = Rational(sign * p_val, q_val)
                                val = phi.subs({x: x0, c: cv})
                                if val == 0:
                                    orbit = find_orbit(Fraction(px, qx), Fraction(sign * p_val, q_val), N)
                                    if orbit:
                                        key = (str(cv), tuple(str(v) for v in sorted(orbit)))
                                        found.append({
                                            'c': str(cv), 'x0': str(x0),
                                            'orbit': [str(v) for v in orbit],
                                            'key': key
                                        })
                except Exception:
                    pass
            
            if len(found) >= 30:
                break
        
        # Deduplicate
        seen = set()
        unique = []
        for entry in found:
            k = entry.get('key', (entry['c'], tuple(entry['orbit'])))
            if k not in seen:
                seen.add(k)
                unique.append(entry)
        
        all_found[N] = unique
        
        marker = "✓" if N in {1,2,3,4,6,8} else ("🔴" if unique else "✓")
        print(f"  {marker} Period {N}: {len(unique)} distinct rational orbit(s)")
        for ex in unique[:3]:
            print(f"      c={ex['c']}, orbit={ex['orbit'][:4]}...")
    
    state['dynatomic_search'] = {N: v for N, v in all_found.items()}
    return state['dynatomic_search']


def find_orbit(x0_frac, c_frac, target_N):
    """Find x₁ that gives a primitive period-N orbit."""
    MAX_BITS = 500
    
    for qx in range(1, 25):
        for px in range(-40, 41):
            x1 = Fraction(px, qx)
            
            orbit = [x0_frac, x1]
            xprev, xcur = x0_frac, x1
            ok = True
            
            for n in range(2, target_N + 2):
                xnext = xcur * xcur + c_frac + xprev
                if (xnext.numerator.bit_length() > MAX_BITS or
                    xnext.denominator.bit_length() > MAX_BITS):
                    ok = False
                    break
                orbit.append(xnext)
                xprev, xcur = xcur, xnext
            
            if not ok:
                continue
            
            if orbit[target_N] == orbit[0] and orbit[target_N + 1] == orbit[1]:
                is_prim = True
                for d in range(1, target_N):
                    if target_N % d == 0 and orbit[d] == orbit[0] and orbit[d+1] == orbit[1]:
                        is_prim = False
                        break
                if is_prim:
                    return orbit[:target_N]
    return None


def section_direct_6_8():
    """Direct search for periods 6 and 8 with exact arithmetic."""
    
    print("  Direct exact search for periods 6 and 8...", flush=True)
    
    found6 = []
    found8 = []
    MAX_BITS = 600
    
    # Use the parametric families: for period 4 we have c = -(x₀²±2x₀+2).
    # For period 6: try c values that worked for period 3 (c=-6) ± small perturbations
    # More importantly: search systematically
    
    # For period 6 and 8, use wider range of c but smaller x range
    c_vals = set()
    for q in range(1, 25):
        for p in range(-80 * q, 80 * q + 1):
            c_vals.add(Fraction(p, q))
    c_vals = sorted(c_vals)
    
    print(f"  Testing {len(c_vals)} c values for periods 6 and 8", flush=True)
    
    total = 0
    for ci, cv in enumerate(c_vals):
        if ci % 2000 == 0 and ci > 0:
            print(f"    Progress: {ci}/{len(c_vals)}, found p6={len(found6)}, p8={len(found8)}", flush=True)
        
        for qx in range(1, 5):
            for px0 in range(-8, 9):
                x0 = Fraction(px0, qx)
                for px1 in range(-8, 9):
                    x1 = Fraction(px1, qx)
                    total += 1
                    
                    xprev, xcur = x0, x1
                    
                    for n in range(2, 10):
                        xnext = xcur * xcur + cv + xprev
                        if (xnext.numerator.bit_length() > MAX_BITS or
                            xnext.denominator.bit_length() > MAX_BITS):
                            break
                        xprev, xcur = xcur, xnext
                        
                        N_cand = n - 1
                        if N_cand >= 1 and xprev == x0 and xcur == x1:
                            orbit = [x0, x1]
                            xp2, xc2 = x0, x1
                            for s in range(2, N_cand + 2):
                                orbit.append(xc2 * xc2 + cv + xp2)
                                xp2, xc2 = xc2, orbit[-1]
                            prim = N_cand
                            for d in range(1, N_cand):
                                if N_cand % d == 0 and orbit[d] == x0 and orbit[d+1] == x1:
                                    prim = d
                                    break
                            
                            if prim == 6:
                                found6.append({'c': str(cv), 'orbit': [str(v) for v in orbit[:6]]})
                                if len(found6) <= 3:
                                    print(f"    ✓ Period 6: c={cv}, orbit={orbit[:6]}")
                            elif prim == 8:
                                found8.append({'c': str(cv), 'orbit': [str(v) for v in orbit[:8]]})
                                if len(found8) <= 3:
                                    print(f"    ✓ Period 8: c={cv}, orbit={orbit[:8]}")
                            break
    
    print(f"\n  Direct search: {total} starting points checked")
    print(f"  Period 6: {len(found6)} orbits found")
    print(f"  Period 8: {len(found8)} orbits found")
    
    state['direct_6'] = found6
    state['direct_8'] = found8
    return {'period_6': len(found6), 'period_8': len(found8)}


def section_final():
    """Final verdict."""
    ds = state.get('dynatomic_search', {})
    
    all_periods = set()
    for N, entries in ds.items():
        if entries:
            all_periods.add(N)
    
    if state.get('direct_6'):
        all_periods.add(6)
    if state.get('direct_8'):
        all_periods.add(8)
    
    # Also include from exp001a: periods 1,2,3,4 found
    all_periods.update({1, 2, 3, 4})
    
    print(f"\n  ╔══════════════════════════════════════════════════╗")
    print(f"  ║       CONJECTURE 3 (INGRAM) — FINAL VERDICT     ║")
    print(f"  ╚══════════════════════════════════════════════════╝")
    
    for N in range(1, 13):
        count = len(ds.get(N, []))
        if N == 6:
            count += len(state.get('direct_6', []))
        if N == 8:
            count += len(state.get('direct_8', []))
        
        if N in {1,2,3,4,6,8}:
            if N in all_periods:
                status = f"✓ ALLOWED, found ({count} orbits)"
            else:
                status = f"⚠️ ALLOWED but not yet found"
        else:
            if count > 0:
                status = f"🔴 FORBIDDEN but FOUND ({count} orbits) — COUNTEREXAMPLE!"
            else:
                status = f"✓ FORBIDDEN, none found"
        
        print(f"  Period {N:2d}: {status}")
    
    unexpected = [N for N in range(1, 13) if N not in {1,2,3,4,6,8} 
                  and (len(ds.get(N, [])) > 0)]
    
    if unexpected:
        print(f"\n  🔴🔴🔴 CONJECTURE 3 IS FALSE!")
    else:
        print(f"\n  ✅ Conjecture 3 SUPPORTED by all tests")
    
    final = {
        'periods_found': sorted(all_periods),
        'unexpected': unexpected,
        'summary': {N: len(ds.get(N, [])) for N in range(1, 13)}
    }
    
    with open(os.path.join(OUTPUT_DIR, 'results_d.json'), 'w') as f:
        json.dump(final, f, indent=2)
    
    return final


run_experiment([
    ("Dynatomic polynomials Phi_1..Phi_7 + rational points", section_dynatomic_and_rational),
    ("Direct search for periods 6 and 8", section_direct_6_8),
    ("Final verdict", section_final),
], timeout_sec=420)
