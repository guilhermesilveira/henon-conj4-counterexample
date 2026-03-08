#!/usr/bin/env python3
"""
EXP-001f: Find ℚ-rational orbits of primitive period 8 for f(x,y)=(y, y²+c+x).

R₈ is too large for symbolic computation (degree 256).
Strategy: brute-force with optimized search.

Key insight from period 6: the simplest orbit c=-7/9 has elements with
denominator 3 or 9 (= 3²). Period 8 orbits might have similarly small denominators.

Plan:
A) Wide c sweep with x₀, x₁ having small denominators
B) Focus on c = p/q² patterns (analogous to c = -7/9 = -7/3²)
C) Use period-4 parametric as starting point: find c with period 4,
   then search nearby for period 8
"""
from common import run_experiment
import os, json
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp001f-period8-search')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


def check_prim_period(x0, x1, cv, target=8, max_bits=800):
    """Check if (x₀,x₁) gives primitive period target under f with param c.
    Recurrence: x_{n+1} = x_n² + c + x_{n-1}."""
    orbit = [x0, x1]
    xp, xc = x0, x1
    
    for n in range(2, target + 2):
        xn = xc * xc + cv + xp
        if xn.numerator.bit_length() > max_bits or xn.denominator.bit_length() > max_bits:
            return False
        orbit.append(xn)
        xp, xc = xc, xn
    
    if orbit[target] != orbit[0] or orbit[target + 1] != orbit[1]:
        return False
    
    # Check primitive
    for d in [1, 2, 4]:
        if orbit[d] == orbit[0] and orbit[d + 1] == orbit[1]:
            return False
    
    return orbit[:target]


def section_wide_search():
    """Wide brute-force: many c values, moderate x range, high denominators."""
    
    # c values: focus on fractions with small denominators²
    # Period 6 had c = -7/9 = -7/3². Try q² for q=1..10
    c_vals = set()
    
    # Standard grid
    for q in range(1, 20):
        for p in range(-60 * q, 60 * q + 1):
            c_vals.add(Fraction(p, q))
    
    # Extra: p/q² patterns
    for q in range(1, 15):
        q2 = q * q
        for p in range(-100, 101):
            c_vals.add(Fraction(p, q2))
    
    c_vals = sorted(c_vals)
    
    # x values: up to denominator 10
    x_vals = set()
    for q in range(1, 11):
        for p in range(-15, 16):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
    print(f"  {len(c_vals)} c values × {len(x_vals)}² x values", flush=True)
    
    found8 = []
    total = 0
    
    for ci, cv in enumerate(c_vals):
        if ci % 500 == 0 and ci > 0:
            print(f"  c[{ci}/{len(c_vals)}] found={len(found8)}", flush=True)
        
        for x0 in x_vals:
            for x1 in x_vals:
                total += 1
                orbit = check_prim_period(x0, x1, cv, target=8)
                if orbit:
                    found8.append({
                        'c': str(cv), 'x0': str(x0), 'x1': str(x1),
                        'orbit': [str(v) for v in orbit]
                    })
                    print(f"  ✅ PERIOD 8! c={cv}, orbit={orbit[:4]}...", flush=True)
                    if len(found8) >= 5:
                        break
            if len(found8) >= 5:
                break
        if len(found8) >= 5:
            break
    
    print(f"\n  Wide search: {total} checked, {len(found8)} period-8 orbits found")
    
    state['wide'] = found8
    return {'found': len(found8), 'checked': total}


def section_from_period4():
    """
    Period-4 parametric: c = -(x₀² ± 2x₀ + 2).
    For each such c, search for period-8 orbits with DIFFERENT starting points.
    A period-8 orbit at a period-4 parameter would be especially interesting.
    """
    from sympy import Rational
    
    print("  Searching for period 8 at period-4 parameter values...", flush=True)
    
    found8 = []
    
    # Generate period-4 c values
    c4_vals = set()
    for qx in range(1, 20):
        for px in range(-30, 31):
            x0 = Fraction(px, qx)
            c4_vals.add(-(x0 * x0 + 2 * x0 + 2))
            c4_vals.add(-(x0 * x0 - 2 * x0 + 2))
    c4_vals = sorted(c4_vals)
    
    x_vals = set()
    for q in range(1, 8):
        for p in range(-12, 13):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
    print(f"  {len(c4_vals)} period-4 c values × {len(x_vals)}² x", flush=True)
    
    for ci, cv in enumerate(c4_vals):
        if ci % 200 == 0 and ci > 0:
            print(f"  c4[{ci}/{len(c4_vals)}] found={len(found8)}", flush=True)
        
        for x0 in x_vals:
            for x1 in x_vals:
                orbit = check_prim_period(x0, x1, cv, target=8)
                if orbit:
                    found8.append({
                        'c': str(cv), 'x0': str(x0), 'x1': str(x1),
                        'orbit': [str(v) for v in orbit]
                    })
                    print(f"  ✅ PERIOD 8 at period-4 param! c={cv}", flush=True)
                    if len(found8) >= 5:
                        break
            if len(found8) >= 5:
                break
        if len(found8) >= 5:
            break
    
    print(f"  Period-4 param search: {len(found8)} period-8 orbits")
    
    state['from_p4'] = found8
    return {'found': len(found8)}


def section_high_denom():
    """
    Try higher denominators for x (up to 20) but smaller c range.
    Period 8 orbits might need x with denom 12-20.
    """
    print("  High-denominator search...", flush=True)
    
    c_vals = set()
    for q in range(1, 10):
        for p in range(-30 * q, 30 * q + 1):
            c_vals.add(Fraction(p, q))
    c_vals = sorted(c_vals)
    
    # Higher denominators
    x_vals = set()
    for q in range(1, 16):
        for p in range(-10, 11):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
    print(f"  {len(c_vals)} c × {len(x_vals)}² x ({len(x_vals)} x vals)", flush=True)
    
    found8 = []
    total = 0
    
    for ci, cv in enumerate(c_vals):
        if ci % 200 == 0 and ci > 0:
            print(f"  c[{ci}/{len(c_vals)}] found={len(found8)} total={total}", flush=True)
        
        for x0 in x_vals:
            for x1 in x_vals:
                total += 1
                orbit = check_prim_period(x0, x1, cv, target=8, max_bits=1000)
                if orbit:
                    found8.append({
                        'c': str(cv), 'x0': str(x0), 'x1': str(x1),
                        'orbit': [str(v) for v in orbit]
                    })
                    print(f"  ✅ PERIOD 8! c={cv}", flush=True)
                    if len(found8) >= 5:
                        break
            if len(found8) >= 5:
                break
        if len(found8) >= 5:
            break
    
    print(f"  High-denom: {total} checked, {len(found8)} found")
    
    state['high_denom'] = found8
    return {'found': len(found8), 'checked': total}


def section_verdict():
    """Final summary."""
    all_found = state.get('wide', []) + state.get('from_p4', []) + state.get('high_denom', [])
    
    # Deduplicate by orbit (normalized)
    seen = set()
    unique = []
    for entry in all_found:
        orbit = tuple(entry['orbit'])
        rotations = [orbit[i:] + orbit[:i] for i in range(len(orbit))]
        norm = min(rotations)
        if norm not in seen:
            seen.add(norm)
            unique.append(entry)
    
    print(f"\n  ╔══════════════════════════════════════════════════╗")
    print(f"  ║       PERIOD 8 RATIONAL ORBITS — RESULTS        ║")
    print(f"  ╚══════════════════════════════════════════════════╝")
    
    if unique:
        print(f"  ✅ Found {len(unique)} distinct period-8 rational orbits!")
        for i, entry in enumerate(unique[:5]):
            print(f"  {i+1}. c={entry['c']}")
            print(f"     orbit = {entry['orbit']}")
        print(f"\n  → CONJECTURE 3 IS SHARP for period 8!")
    else:
        print(f"  ⚠️ No period-8 rational orbits found")
        print(f"     Period 8 may require very specific parameters")
        print(f"     or denominators beyond our search range")
    
    with open(os.path.join(OUTPUT_DIR, 'results.json'), 'w') as f:
        json.dump({'all_found': unique, 'counts': {
            'wide': len(state.get('wide', [])),
            'from_p4': len(state.get('from_p4', [])),
            'high_denom': len(state.get('high_denom', []))
        }}, f, indent=2, default=str)
    
    return {'found': len(unique)}


run_experiment([
    ("Wide brute-force search for period 8", section_wide_search),
    ("Search at period-4 parameter values", section_from_period4),
    ("High-denominator search", section_high_denom),
    ("Verdict", section_verdict),
], timeout_sec=360)
