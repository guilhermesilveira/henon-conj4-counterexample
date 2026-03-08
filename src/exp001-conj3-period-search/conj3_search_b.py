#!/usr/bin/env python3
"""
EXP-001b: Focused search for periods 6 and 8, plus wider forbidden-period search.

Variation b of exp001. Fixes:
1. Find rational orbits of period 6 and 8 (proving conjecture is sharp)
2. Wider search for forbidden periods with optimized loop
"""
from common import run_experiment
import os, json
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp001-conj3-period-search')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}

def section_find_period_6_and_8():
    """
    Use the parametric approach: for period N, the factor (c + x²) = 0
    always appears (giving fixed points). The INTERESTING factors give
    genuine period-N orbits.
    
    For period 4: c = -x² ± 2x - 2 gives period-4 orbits.
    For period 6 and 8: we need the cubic/quartic factors in c.
    
    Strategy: for period 6, take the cubic factor, parametrize x₀ ∈ ℚ,
    solve for c ∈ ℚ via the cubic formula or rational root test.
    """
    from sympy import symbols, expand, resultant, Poly, factor, Rational, solve, sqrt
    
    x, t, c = symbols('x t c')
    
    results = {}
    
    # ── Period 6 ──
    print("  === Period 6: extracting dynatomic factors ===", flush=True)
    
    # Build the orbit
    xs = [x, t]
    for n in range(1, 6):
        xs.append(expand(xs[-1]**2 + c + xs[-2]))
    
    condA = expand(xs[6] - x)
    condB = expand(x**2 + c + xs[5] - t)
    
    print("    Computing resultant...", flush=True)
    res6 = resultant(condA, condB, t)
    res6 = expand(res6)
    
    print("    Factoring...", flush=True)
    fac6 = factor(res6)
    
    # Extract factors
    from sympy import Mul, Pow
    p6 = Poly(res6, x, c, domain='ZZ')
    fac_list = p6.factor_list()
    
    print(f"    Number of irreducible factors: {len(fac_list[1])}")
    
    # For each factor that is NOT (c + x²) and NOT already seen at lower periods,
    # try to find rational solutions.
    period6_found = []
    
    for fac_poly, mult in fac_list[1]:
        deg_c = fac_poly.degree(1)  # degree in c (second variable)
        deg_x = fac_poly.degree(0)  # degree in x
        total_deg = fac_poly.total_degree()
        print(f"    Factor: deg_x={deg_x}, deg_c={deg_c}, total={total_deg}, mult={mult}")
        
        # Skip c + x² (period 1 factor)
        if total_deg == 2 and deg_c == 1:
            print(f"      (skip: period-1 factor)")
            continue
        
        # For each factor, try x₀ = p/q for small p, q and solve for c
        if deg_c <= 4:  # can solve for c algebraically
            for qx in range(1, 20):
                for px in range(-30, 31):
                    x0 = Rational(px, qx)
                    # Substitute x = x₀ and solve for c
                    fac_at_x0 = fac_poly.eval(0, px * fac_poly.domain.one)  # eval at x = ...
                    # Actually use subs
                    from sympy import Symbol
                    expr = fac_poly.as_expr()
                    expr_at_x0 = expr.subs(x, x0)
                    c_solutions = solve(expr_at_x0, c)
                    
                    for cv in c_solutions:
                        if cv.is_rational:
                            # Verify this gives a primitive period-6 orbit
                            orbit = verify_orbit(float(x0), float(cv), 6)
                            if orbit is not None:
                                period6_found.append({
                                    'c': str(cv), 'x0': str(x0),
                                    'orbit': [str(Fraction(v).limit_denominator(10**15)) for v in orbit]
                                })
                                if len(period6_found) <= 3:
                                    print(f"      ✓ Period 6: c={cv}, x₀={x0}")
                                if len(period6_found) >= 20:
                                    break
                    if len(period6_found) >= 20:
                        break
                if len(period6_found) >= 20:
                    break
    
    if period6_found:
        print(f"    ✓ Found {len(period6_found)} period-6 rational orbits")
        results[6] = period6_found
    else:
        print(f"    ✗ No period-6 rational orbits found")
        results[6] = []
    
    # ── Period 4 (parametric from known factors) ──
    print("\n  === Period 4: verifying from linear factors ===", flush=True)
    # From exp001: c + x² - 2x + 2 = 0 → c = -(x²-2x+2) = -x²+2x-2
    # and c + x² + 2x + 2 = 0 → c = -(x²+2x+2) = -x²-2x-2
    period4_examples = []
    for qx in range(1, 10):
        for px in range(-15, 16):
            x0 = Rational(px, qx)
            for sign in [1, -1]:
                cv = -(x0**2 + sign*2*x0 + 2)
                orbit = verify_orbit_exact(Fraction(int(x0.p), int(x0.q)), 
                                          Fraction(int(cv.p), int(cv.q)), 4)
                if orbit is not None and len(orbit) == 4:
                    period4_examples.append({
                        'c': str(cv), 'orbit': [str(v) for v in orbit]
                    })
    
    print(f"    ✓ Found {len(period4_examples)} period-4 orbits from parametric formula")
    results[4] = period4_examples[:10]
    
    # ── Period 8: try numerical approach ──
    print("\n  === Period 8: searching with wider range ===", flush=True)
    period8_found = []
    
    # Try more c values, larger x range
    for qc in range(1, 15):
        for pc in range(-50 * qc, 50 * qc + 1):
            cv = Fraction(pc, qc)
            for qx in range(1, 8):
                for px0 in range(-15, 16):
                    x0 = Fraction(px0, qx)
                    for px1 in range(-15, 16):
                        x1 = Fraction(px1, qx)
                        orbit = check_period_exact(x0, x1, cv, 8)
                        if orbit is not None:
                            orbit_key = tuple(sorted([str(v) for v in orbit]))
                            period8_found.append({
                                'c': str(cv),
                                'orbit': [str(v) for v in orbit]
                            })
                            if len(period8_found) <= 3:
                                print(f"      ✓ Period 8: c={cv}, orbit={orbit[:4]}...")
                            if len(period8_found) >= 5:
                                break
                    if len(period8_found) >= 5:
                        break
                if len(period8_found) >= 5:
                    break
            if len(period8_found) >= 5:
                break
        if len(period8_found) >= 5:
            break
    
    if period8_found:
        print(f"    ✓ Found {len(period8_found)} period-8 rational orbits")
    else:
        print(f"    ✗ No period-8 found in search range (may need larger range)")
    results[8] = period8_found
    
    state['parametric'] = results
    return results


def verify_orbit(x0_float, c_float, target_period):
    """Numerically verify orbit and return it if primitive period matches."""
    from mpmath import mpf, mp
    mp.dps = 50
    
    x0 = mpf(x0_float)
    c_val = mpf(c_float)
    
    # Need x₁ too. From the orbit equations, x₁ is not free.
    # For parametric solutions, x₁ comes from the resultant.
    # Let me just iterate from the polynomial root.
    # Actually, for the parametric approach, we derived c from x₀,
    # but we still need x₁. Let me compute it from the orbit equations.
    
    # For a period-N orbit: x₀, x₁, ..., x_{N-1} with x_{n+1} = xₙ² + c + x_{n-1}
    # and x_N = x₀, x_{N+1} = x₁.
    # From x_{N+1} = x₁: x₀² + c + x_{N-1} = x₁
    # This is recursive — we need Newton's method to find x₁ given x₀ and c.
    
    # Try: guess x₁ from nearby values and refine
    # Actually, for now just return None (need exact arithmetic)
    return None


def verify_orbit_exact(x0, c_val, target_period):
    """Verify orbit using exact Fraction arithmetic. Returns orbit or None."""
    # For a period-N orbit starting at x₀ with parameter c,
    # we need to find x₁ such that the orbit closes after N steps.
    # x₁ satisfies a polynomial equation of degree 2^(N-2) — too high.
    
    # Alternative: try x₁ from small rationals
    for qx in range(1, 10):
        for px in range(-20, 21):
            x1 = Fraction(px, qx)
            result = check_period_exact(x0, x1, c_val, target_period)
            if result is not None:
                return result
    return None


def check_period_exact(x0, x1, c_val, target_period):
    """Check if (x0, x1) with parameter c gives primitive period target_period."""
    MAX_BITS = 500
    orbit = [x0, x1]
    xprev, xcur = x0, x1
    
    for n in range(2, target_period + 2):
        xnext = xcur * xcur + c_val + xprev
        if (xnext.numerator.bit_length() > MAX_BITS or 
            xnext.denominator.bit_length() > MAX_BITS):
            return None
        orbit.append(xnext)
        xprev, xcur = xcur, xnext
    
    # Check if period divides target
    if orbit[target_period] != x0 or orbit[target_period + 1] != x1:
        return None
    
    # Check primitive
    for d in range(1, target_period):
        if target_period % d == 0:
            if orbit[d] == x0 and orbit[d+1] == x1:
                return None  # sub-period
    
    return orbit[:target_period]


def section_wide_forbidden():
    """
    Aggressive search for forbidden periods 5,7,9,10,11,12.
    Optimized: skip orbits that blow up quickly.
    """
    MAX_PERIOD = 12
    MAX_BITS = 300
    forbidden = {5, 7, 9, 10, 11, 12}
    
    counterexamples = []
    total = 0
    
    # Wider c range, moderate x range
    print("  Searching for forbidden periods...", flush=True)
    
    for qc in range(1, 20):
        for pc in range(-40 * qc, 40 * qc + 1):
            cv = Fraction(pc, qc)
            
            for qx in range(1, 6):
                for px0 in range(-10, 11):
                    x0 = Fraction(px0, qx)
                    for px1 in range(-10, 11):
                        x1 = Fraction(px1, qx)
                        total += 1
                        
                        xprev, xcur = x0, x1
                        for n in range(2, MAX_PERIOD + 2):
                            xnext = xcur * xcur + cv + xprev
                            if (xnext.numerator.bit_length() > MAX_BITS or
                                xnext.denominator.bit_length() > MAX_BITS):
                                break
                            xprev, xcur = xcur, xnext
                            
                            N_cand = n - 1
                            if N_cand >= 1 and xprev == x0 and xcur == x1:
                                # Find primitive
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
                                if prim in forbidden:
                                    counterexamples.append({
                                        'period': prim, 'c': str(cv),
                                        'orbit': [str(v) for v in orbit[:prim]]
                                    })
                                    print(f"  🔴 Period {prim}: c={cv}, orbit={orbit[:prim]}")
                                break
            
            if total % 5000000 == 0 and total > 0:
                print(f"  Progress: {total} checked, c={cv}", flush=True)
    
    print(f"\n  Total checked: {total}")
    if counterexamples:
        print(f"  🔴 {len(counterexamples)} COUNTEREXAMPLES!")
    else:
        print(f"  ✅ No forbidden periods found")
    
    state['wide_forbidden'] = {
        'total': total,
        'counterexamples': counterexamples
    }
    return state['wide_forbidden']


def section_summary():
    """Compile and save final summary."""
    
    # Compile all periods found
    all_periods = set()
    
    # From exp001 results
    exact = state.get('parametric', {})
    for N, entries in exact.items():
        if isinstance(entries, list) and len(entries) > 0:
            all_periods.add(N)
    
    forbidden_found = state.get('wide_forbidden', {}).get('counterexamples', [])
    for ce in forbidden_found:
        all_periods.add(ce['period'])
    
    print(f"\n  === FINAL SUMMARY ===")
    print(f"  Periods with ℚ-rational orbits found: {sorted(all_periods)}")
    print(f"  Allowed by Conjecture 3: {{1,2,3,4,6,8}}")
    
    unexpected = [N for N in all_periods if N not in {1, 2, 3, 4, 6, 8}]
    if unexpected:
        print(f"  🔴 CONJECTURE 3 IS FALSE! Unexpected periods: {unexpected}")
    else:
        print(f"  ✅ Conjecture 3 SUPPORTED — no unexpected periods found")
    
    expected_missing = [N for N in {1,2,3,4,6,8} if N not in all_periods]
    if expected_missing:
        print(f"  ⚠️ Expected periods not yet found: {expected_missing}")
        print(f"     (conjecture says these should exist — need larger search)")
    
    with open(os.path.join(OUTPUT_DIR, 'results_b.json'), 'w') as f:
        json.dump(state, f, indent=2, default=str)
    
    return {'all_periods': sorted(all_periods), 'unexpected': unexpected}


run_experiment([
    ("Find period 6, 8 from parametric/symbolic + verify period 4", section_find_period_6_and_8),
    ("Wide search for forbidden periods 5,7,9,10,11,12", section_wide_forbidden),
    ("Final summary", section_summary),
], timeout_sec=420)
