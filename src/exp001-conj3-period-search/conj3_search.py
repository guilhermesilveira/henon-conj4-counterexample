#!/usr/bin/env python3
"""
EXP-001: Search for ℚ-rational periodic points of f(x,y) = (y, y²+c+x).
Tests Ingram's Conjecture 3 (BIRS 2023): no period N outside {1,2,3,4,6,8}.

Strategy: for each period N, parametrize orbits as (x₀, x₁, c) with the
recurrence x_{n+1} = xₙ² + c + x_{n-1} and closure x_N = x₀, x_{N+1} = x₁.
Use exact rational arithmetic throughout.

Deterministic: no random numbers used.
"""
from common import run_experiment
import os, json
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp001-conj3-period-search')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}

# ═══════════════════════════════════════════════════════
# SECTION A: Exact rational orbit search
# ═══════════════════════════════════════════════════════

def section_exact_search():
    """
    For rational (x₀, x₁), compute c from periodicity and check if orbit closes.
    Uses exact Fraction arithmetic — no floating point at all.
    """
    # For fixed x₀, x₁ ∈ ℚ, the orbit is determined:
    #   x₂ = x₁² + c + x₀
    #   x₃ = x₂² + c + x₁
    #   ...
    # For period-N: x_N = x₀ and x_{N+1} = x₁.
    #
    # Key trick: from c = x₂ - x₁² - x₀, all subsequent xₙ are polynomials in x₂.
    # Periodicity gives polynomial equations in x₂.
    #
    # BUT: we have 3 unknowns (x₀, x₁, c) and 2 equations from N-periodicity.
    # So it's a 1-parameter family. Let's parametrize by x₀ and derive (x₁, c).
    #
    # Alternative: fix c ∈ ℚ and x₀ ∈ ℚ, then x₁ is determined by x_{N+1} = x₁.
    # This gives a polynomial in x₁ of degree 2^(N-1). Too expensive.
    #
    # Most efficient: fix (x₀, x₁) ∈ ℚ², iterate, check closure.
    # The iteration is deterministic and exact in ℚ. c doesn't need to be fixed!
    #
    # Wait — we need c. From the orbit (x₀, x₁, ...), the value c appears in
    # x₂ = x₁² + c + x₀. But c is free. For a period-N orbit to exist,
    # we need x_N(c) = x₀ and x_{N+1}(c) = x₁. These are polynomial equations in c.
    #
    # Strategy: Fix x₀, x₁ ∈ ℚ. Build orbit x₂(c), x₃(c), ... as polynomials in c.
    # Solve x_N(c) = x₀ for c ∈ ℚ. Then check x_{N+1}(c) = x₁.
    #
    # Degrees: x₂ is degree 1 in c. x₃ = x₂² + c + x₁ is degree 2 in c.
    # x₄ is degree 4, x₅ is degree 8, ... x_N is degree 2^{N-2} for N ≥ 2.
    # For N=12, that's degree 1024 — too much symbolically.
    #
    # Better: just fix (x₀, x₁) and iterate directly with specific c values.
    #
    # BEST approach: Sweep over (x₀, x₁, c) all rational with small denominators.
    # Then just iterate and check.
    
    MAX_PERIOD = 12
    MAX_Q = 6  # denominator bound
    MAX_P = 20  # numerator bound
    MAX_BITS = 500  # kill if numbers get too big
    
    period_found = {}  # N -> set of (c, orbit_tuple)
    
    # Generate rational c values
    c_vals = set()
    for q in range(1, MAX_Q + 1):
        for p in range(-MAX_P * q, MAX_P * q + 1):
            c_vals.add(Fraction(p, q))
    c_vals = sorted(c_vals)
    
    print(f"  Scanning {len(c_vals)} rational c values", flush=True)
    print(f"  For each c, trying x₀ ∈ ℚ with |num| ≤ {MAX_P}, denom ≤ {MAX_Q}", flush=True)
    
    # For each c, try starting points
    x_vals = set()
    for q in range(1, MAX_Q + 1):
        for p in range(-MAX_P, MAX_P + 1):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
    total_checked = 0
    
    for ci, cv in enumerate(c_vals):
        if ci % 200 == 0 and ci > 0:
            print(f"  Progress: {ci}/{len(c_vals)} c values, {total_checked} orbits checked, "
                  f"periods found: {sorted(period_found.keys())}", flush=True)
        
        for x0 in x_vals:
            for x1 in x_vals:
                total_checked += 1
                
                # Iterate orbit with exact arithmetic
                xprev, xcur = x0, x1
                found_period = 0
                
                for n in range(2, MAX_PERIOD + 2):
                    xnext = xcur * xcur + cv + xprev
                    
                    # Check bit size
                    if (xnext.numerator.bit_length() > MAX_BITS or 
                        xnext.denominator.bit_length() > MAX_BITS):
                        break
                    
                    xprev, xcur = xcur, xnext
                    
                    # Check if we've returned: need x_{n-1} = x₀ AND x_n = x₁
                    # At this point: xprev = x_{n-1}, xcur = x_n
                    N_candidate = n - 1  # because x_{n-1} should be x₀
                    if N_candidate >= 1 and xprev == x0 and xcur == x1:
                        found_period = N_candidate
                        break
                
                if found_period > 0:
                    # Check primitive period
                    N = found_period
                    
                    # Rebuild orbit to find primitive period
                    orbit = [x0, x1]
                    xp, xc = x0, x1
                    for step in range(2, N + 2):
                        xn = xc * xc + cv + xp
                        orbit.append(xn)
                        xp, xc = xc, xn
                    
                    # Find smallest d | N with orbit[d] = x₀ and orbit[d+1] = x₁
                    prim = N
                    for d in range(1, N):
                        if N % d == 0 and orbit[d] == x0 and orbit[d+1] == x1:
                            prim = d
                            break
                    
                    N = prim
                    orbit_tuple = tuple(orbit[:N])
                    
                    # Normalize orbit (start from lexicographically smallest)
                    rotations = [orbit_tuple[i:] + orbit_tuple[:i] for i in range(N)]
                    orbit_norm = min(rotations)
                    
                    key = (str(cv), orbit_norm)
                    if N not in period_found:
                        period_found[N] = set()
                    
                    # Use a hashable representation
                    orbit_key = (str(cv), tuple(str(x) for x in orbit_norm))
                    if orbit_key not in period_found[N]:
                        period_found[N].add(orbit_key)
                        
                        if N not in {1, 2, 3, 4, 6, 8}:
                            print(f"\n  🔴 COUNTEREXAMPLE! Period {N} at c={cv}:", flush=True)
                            print(f"     orbit: {orbit[:N]}", flush=True)
    
    # Summary
    print(f"\n  === Exact Search Summary ===")
    print(f"  Total orbits checked: {total_checked}")
    
    summary = {}
    for N in sorted(period_found.keys()):
        count = len(period_found[N])
        marker = "✓" if N in {1, 2, 3, 4, 6, 8} else "🔴"
        print(f"  {marker} Period {N}: {count} distinct rational orbit(s)")
        
        # Show a few examples
        examples = list(period_found[N])[:5]
        for ex_c, ex_orbit in examples:
            print(f"      c={ex_c}, orbit={list(ex_orbit)[:4]}...")
        
        summary[N] = {
            'count': count,
            'examples': [{'c': ex_c, 'orbit': list(ex_orbit)} 
                        for ex_c, ex_orbit in list(period_found[N])[:10]]
        }
    
    unexpected = [N for N in period_found if N not in {1, 2, 3, 4, 6, 8}]
    expected_missing = [N for N in {3, 4, 6, 8} if N not in period_found]
    
    if unexpected:
        print(f"\n  🔴 UNEXPECTED PERIODS: {unexpected}")
    else:
        print(f"\n  ✅ All found periods are in {{1,2,3,4,6,8}}")
    
    if expected_missing:
        print(f"  ⚠️ Expected periods NOT found in search: {expected_missing}")
        print(f"     (may need larger search range)")
    
    state['exact_search'] = {
        'total_checked': total_checked,
        'num_c': len(c_vals),
        'num_x': len(x_vals),
        'summary': summary,
        'unexpected_periods': unexpected,
        'expected_missing': expected_missing
    }
    
    return state['exact_search']


# ═══════════════════════════════════════════════════════
# SECTION B: Symbolic parametric (small N)
# ═══════════════════════════════════════════════════════

def section_symbolic():
    """
    For periods N=1..8, build the resultant polynomial and factor over ℚ.
    This gives the COMPLETE picture: which curves in (x₀, c) space give period-N orbits.
    """
    from sympy import symbols, expand, resultant, Poly, factor, Rational, ZZ
    
    x, t, c = symbols('x t c')
    
    results = {}
    
    for N in range(1, 9):
        print(f"\n  Period N={N}:", flush=True)
        
        if N == 1:
            # x₁ = x₀, x₁²+c+x₀ = x₁ → x₀²+c = 0
            poly_str = "c + x^2"
            results[1] = {'poly': poly_str, 'factors': ['c + x^2'], 
                         'rational_family': True, 'description': 'c = -x₀², any x₀'}
            print(f"    Polynomial: {poly_str}")
            print(f"    ✓ Rational family: c = -x₀²")
            continue
        
        if N == 2:
            # Already derived: c = -x₀² = -x₁², x₁ = ±x₀
            poly_str = "c + x^2 (same as period 1, period-2 orbit: x₁=-x₀)"
            results[2] = {'poly': poly_str, 'factors': ['c + x^2'],
                         'rational_family': True, 'description': 'c = -x₀², x₁=-x₀'}
            print(f"    ✓ Rational family: c = -x0^2, orbit (x0,-x0)")
            continue
        
        # Build orbit: x₀ = x, x₁ = t, x₂ = t² + c + x, ...
        xs = [x, t]
        for n in range(1, N):
            xnp1 = expand(xs[n]**2 + c + xs[n-1])
            xs.append(xnp1)
        
        # Periodicity: x_N = x₀ and x_{N+1} = x₁
        condA = expand(xs[N] - x)
        condB = expand(x**2 + c + xs[N-1] - t)
        
        # Eliminate t via resultant
        print(f"    Computing resultant (eliminating x₁)...", flush=True)
        try:
            res = resultant(condA, condB, t)
            res = expand(res)
        except Exception as e:
            print(f"    ✗ Resultant failed: {e}")
            results[N] = {'error': str(e)}
            continue
        
        # Factor
        print(f"    Factoring...", flush=True)
        try:
            fac = factor(res)
            fac_str = str(fac)
        except Exception as e:
            fac_str = f"(factoring failed: {e})"
        
        # Get degree info
        try:
            p = Poly(res, x, c, domain='ZZ')
            deg_x = Poly(res, x, domain='ZZ[c]').degree()
            deg_c = Poly(res, c, domain='ZZ[x]').degree()
        except:
            deg_x = deg_c = '?'
        
        print(f"    Result: deg_x={deg_x}, deg_c={deg_c}")
        print(f"    Factored: {fac_str[:300]}")
        
        # Check if any factor is linear in c (giving c = rational function of x)
        # which would provide a rational family
        has_linear_c = False
        try:
            for fac_item, mult in Poly(res, x, c, domain='ZZ').factor_list()[1]:
                dc = fac_item.degree(1)  # degree in c
                if dc == 1:
                    has_linear_c = True
                    print(f"    ✓ Has factor linear in c: {fac_item}")
        except Exception as e:
            pass
        
        results[N] = {
            'deg_x': deg_x,
            'deg_c': deg_c,
            'factored': fac_str[:500],
            'has_linear_c_factor': has_linear_c
        }
    
    state['symbolic'] = results
    return results


# ═══════════════════════════════════════════════════════
# SECTION C: Wider search with higher denominators
# ═══════════════════════════════════════════════════════

def section_wider_search():
    """
    Focused search for periods 5,7,9,10,11,12 (the ones Conj 3 says DON'T exist).
    Use larger c range but targeted starting points.
    """
    MAX_PERIOD = 12
    MAX_BITS = 800
    
    # For each c, try to find period-N orbits for N ∉ {1,2,3,4,6,8}
    forbidden_periods = {5, 7, 9, 10, 11, 12}
    
    # More c values, fewer x values per c (since we only care about forbidden periods)
    c_vals = set()
    for q in range(1, 12):
        for p in range(-60 * q, 60 * q + 1):
            c_vals.add(Fraction(p, q))
    c_vals = sorted(c_vals)
    
    x_vals = set()
    for q in range(1, 8):
        for p in range(-12, 13):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
    print(f"  Wider search: {len(c_vals)} c values × {len(x_vals)} starting x₀ × {len(x_vals)} x₁")
    print(f"  Targeting periods {sorted(forbidden_periods)}", flush=True)
    
    counterexamples = []
    total = 0
    
    for ci, cv in enumerate(c_vals):
        if ci % 500 == 0 and ci > 0:
            print(f"  Progress: {ci}/{len(c_vals)}, {total} checked", flush=True)
        
        for x0 in x_vals:
            for x1 in x_vals:
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
                        # Find primitive period
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
                        
                        if prim in forbidden_periods:
                            counterexamples.append({
                                'period': prim,
                                'c': str(cv),
                                'orbit': [str(x) for x in orbit[:prim]]
                            })
                            print(f"\n  🔴 COUNTEREXAMPLE! Period {prim} at c={cv}!", flush=True)
                            print(f"     orbit: {orbit[:prim]}", flush=True)
                        break
    
    print(f"\n  === Wider Search Summary ===")
    print(f"  Total checked: {total}")
    
    if counterexamples:
        print(f"  🔴 {len(counterexamples)} COUNTEREXAMPLES found!")
        for ce in counterexamples[:10]:
            print(f"    Period {ce['period']}: c={ce['c']}")
    else:
        print(f"  ✅ No forbidden periods found — Conjecture 3 supported")
    
    state['wider_search'] = {
        'total_checked': total,
        'num_c': len(c_vals),
        'counterexamples': counterexamples
    }
    
    return state['wider_search']


# ═══════════════════════════════════════════════════════
# SECTION D: Save all results
# ═══════════════════════════════════════════════════════

def section_save():
    """Save combined results."""
    with open(os.path.join(OUTPUT_DIR, 'results.json'), 'w') as f:
        json.dump(state, f, indent=2, default=str)
    print(f"  Results saved to {OUTPUT_DIR}/results.json")
    return {'saved': True}


run_experiment([
    ("Exact rational orbit search (small denominators)", section_exact_search),
    ("Symbolic parametric for periods 1-8", section_symbolic),
    ("Wider search for forbidden periods 5,7,9,10,11,12", section_wider_search),
    ("Save results", section_save),
], timeout_sec=480)
