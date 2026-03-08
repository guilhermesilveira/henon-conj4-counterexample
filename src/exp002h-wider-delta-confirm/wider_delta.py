#!/usr/bin/env python3
"""
EXP-002h: Wider δ confirmation for corrected Conjecture 4'''.

Now that exp002i PROVED all odd integers δ are exceptional (period-3 orbits exist),
the corrected conjecture is:

  Conj 4''': Period > 2 rational orbits exist ⟺ δ is an odd integer.
  Equivalently: even integer δ and non-integer rational δ have ONLY period 1, 2.

This experiment tests Conj 4''' with a much wider search:
1. Even integers δ = -10, -8, ..., 8, 10 with 100K combos each
2. Non-integer rationals δ = p/q (q ≥ 2) with 100K combos each
3. Near-odd-integer δ (e.g., 2.99, 3.01) to probe the boundary
4. Also test: do even integers have period-3 orbits with LARGER coordinates?
"""
from common import run_experiment
import os, json
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp002h-wider-delta-confirm')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


def check_periods(x0, x1, c, delta, max_period=8):
    """Check for primitive periods up to max_period."""
    orbit = [x0, x1]
    xp, xc = x0, x1
    for _ in range(max_period + 2):
        xn = xc * xc + c + delta * xp
        if abs(xn.numerator) > 10**15 or abs(xn.denominator) > 10**10:
            return None
        orbit.append(xn)
        xp, xc = xc, xn
    
    for p in range(1, max_period + 1):
        if orbit[p] == x0 and orbit[p+1] == x1:
            # Check primitive
            prim = True
            for d in range(1, p):
                if d < len(orbit) - 1 and orbit[d] == x0 and orbit[d+1] == x1:
                    prim = False
                    break
            if prim:
                return p
    return None


def search_delta(delta_val, c_range=200, x_range=15, denom_max=6):
    """Search for period > 2 at given δ. Returns list of (period, c, x0, x1)."""
    delta = Fraction(delta_val)
    found = []
    
    c_vals = set()
    for q in range(1, denom_max + 1):
        for p in range(-c_range, c_range + 1):
            c_vals.add(Fraction(p, q))
    c_vals = sorted(c_vals)
    
    x_vals = set()
    for q in range(1, denom_max + 1):
        for p in range(-x_range * q, x_range * q + 1):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
    for cv in c_vals:
        for x0 in x_vals:
            for x1 in x_vals:
                per = check_periods(x0, x1, cv, delta)
                if per and per > 2:
                    found.append((per, str(cv), str(x0), str(x1)))
                    if len(found) >= 5:
                        return found
    return found


def section_even_integers():
    """Test even integer δ with wide search."""
    print("  Testing even integer δ values:")
    
    results = {}
    for d in range(-10, 11, 2):
        if d == 0:
            continue
        found = search_delta(d, c_range=200, x_range=15, denom_max=4)
        results[d] = found
        status = f"❌ EXCEPTION: {found[:2]}" if found else "✅ only period ≤ 2"
        print(f"    δ={d:4d}: {status}")
    
    state['even'] = results
    exceptions = {k: v for k, v in results.items() if v}
    return {'tested': len(results), 'exceptions': len(exceptions)}


def section_non_integer():
    """Test non-integer rational δ."""
    print("  Testing non-integer rational δ:")
    
    # Select diverse non-integer rationals
    test_deltas = []
    for q in range(2, 8):
        for p in range(-12, 13):
            if p % q != 0:  # truly non-integer
                test_deltas.append(Fraction(p, q))
    
    # Also add near-odd-integer values
    near_odd = [
        Fraction(99, 100), Fraction(101, 100),  # near 1
        Fraction(299, 100), Fraction(301, 100),  # near 3
        Fraction(499, 100), Fraction(501, 100),  # near 5
        Fraction(2, 3), Fraction(4, 3),  # simple non-integers
        Fraction(7, 2), Fraction(9, 2),
    ]
    test_deltas.extend(near_odd)
    test_deltas = sorted(set(test_deltas))
    
    results = {}
    exceptions_count = 0
    
    for delta in test_deltas:
        found = search_delta(delta, c_range=100, x_range=10, denom_max=3)
        results[str(delta)] = found
        if found:
            exceptions_count += 1
            print(f"    δ={str(delta):>8s}: ❌ EXCEPTION period {found[0][0]} at c={found[0][1]}")
        
    print(f"\n  Tested {len(results)} non-integer δ values")
    print(f"  Exceptions: {exceptions_count}")
    
    if exceptions_count == 0:
        print("  ✅ ALL non-integer δ have only period ≤ 2")
    
    state['nonint'] = {'tested': len(results), 'exceptions': exceptions_count}
    return state['nonint']


def section_odd_integers_verify():
    """Verify odd integers DO have period > 2 (positive control)."""
    print("  Positive control: odd integers should have period 3:")
    
    for d in [-9, -7, -5, -3, -1, 1, 3, 5, 7, 9]:
        found = search_delta(d, c_range=200, x_range=15, denom_max=4)
        if found:
            print(f"    δ={d:4d}: ✅ period {found[0][0]} at c={found[0][1]} (positive control OK)")
        else:
            print(f"    δ={d:4d}: ⚠️ NOT FOUND in search range (may need wider)")
    
    return {'done': True}


def section_half_integer_deep():
    """Deep search at half-integer δ (strongest test of boundary)."""
    print("  Deep search at half-integer δ (near odd integers):")
    
    half_ints = [Fraction(p, 2) for p in range(-11, 12) if p % 2 != 0]
    
    results = {}
    for delta in half_ints:
        found = search_delta(delta, c_range=300, x_range=20, denom_max=5)
        results[str(delta)] = found
        if found:
            print(f"    δ={str(delta):>6s}: ❌ period {found[0][0]}")
        else:
            print(f"    δ={str(delta):>6s}: ✅ period ≤ 2 only")
    
    exceptions = {k: v for k, v in results.items() if v}
    print(f"\n  Half-integers tested: {len(results)}, exceptions: {len(exceptions)}")
    
    state['half_int'] = {'tested': len(results), 'exceptions': len(exceptions)}
    return state['half_int']


def section_even_deep():
    """Very deep search at δ=2 (the simplest even integer, most likely to have period>2 if any)."""
    print("  Very deep search at δ=2:")
    
    found = search_delta(2, c_range=500, x_range=25, denom_max=6)
    
    if found:
        print(f"  ❌ FOUND period > 2 at δ=2! {found[0]}")
    else:
        print(f"  ✅ No period > 2 at δ=2 (c∈[-500,500], x∈[-25,25], denom≤6)")
    
    state['delta2_deep'] = found
    return {'found': len(found)}


def section_verdict():
    """Final summary."""
    even = state.get('even', {})
    even_exc = sum(1 for v in even.values() if v)
    nonint = state.get('nonint', {})
    half = state.get('half_int', {})
    d2 = state.get('delta2_deep', [])
    
    print("\n  ╔══════════════════════════════════════════════════╗")
    print("  ║ EXP-002h: CORRECTED CONJECTURE 4''' TEST         ║")
    print("  ╚══════════════════════════════════════════════════╝")
    
    print(f"\n  Conj 4''': period > 2 ⟺ δ is an odd integer")
    print(f"\n  Even integers δ: {len(even)} tested, {even_exc} exceptions")
    print(f"  Non-integer δ: {nonint.get('tested', 0)} tested, {nonint.get('exceptions', 0)} exceptions")
    print(f"  Half-integers δ: {half.get('tested', 0)} tested, {half.get('exceptions', 0)} exceptions")
    print(f"  Deep δ=2 search: {'EXCEPTION' if d2 else 'clean'}")
    
    all_clean = (even_exc == 0 and nonint.get('exceptions', 0) == 0 
                 and half.get('exceptions', 0) == 0 and not d2)
    
    if all_clean:
        print(f"\n  ✅ CONJECTURE 4''' STRONGLY SUPPORTED")
        print(f"     No exceptions found outside odd integers")
    else:
        print(f"\n  ❌ CONJECTURE 4''' HAS COUNTEREXAMPLES")
    
    with open(os.path.join(OUTPUT_DIR, 'results.json'), 'w') as f:
        json.dump({
            'even_exceptions': even_exc,
            'nonint': nonint,
            'half_int': half,
            'delta2_deep': d2,
            'conj4triple_supported': all_clean,
        }, f, indent=2)
    
    return {'supported': all_clean}


run_experiment([
    ("Odd integers positive control", section_odd_integers_verify),
    ("Even integers wide search", section_even_integers),
    ("Non-integer rationals", section_non_integer),
    ("Half-integer deep search", section_half_integer_deep),
    ("Very deep search at δ=2", section_even_deep),
    ("Verdict", section_verdict),
], timeout_sec=600)
