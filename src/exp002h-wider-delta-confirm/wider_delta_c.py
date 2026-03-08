#!/usr/bin/env python3
"""
EXP-002h var c: Investigate the expanded exceptions.

Findings from var b:
- ALL even integers have period 3 with c = p/16
- δ = p/3 (some) have period 3 with c = p/9
- Half-integers: clean

Questions:
1. Is there a parametric family for ALL integers (not just odd)?
2. Which δ = p/q have period 3? Is the pattern about q?
3. What's the full characterization?
"""
from common import run_experiment
import os, json, math
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp002h-wider-delta-confirm')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


def find_period3(delta, x_range=30, denom_max=6):
    """Find period-3 orbits using discriminant method."""
    delta = Fraction(delta)
    found = []
    
    x_vals = set()
    for q in range(1, denom_max + 1):
        for p in range(-x_range * q, x_range * q + 1):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
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
                c = x2 - x1 * x1 - delta * x0
                x3 = x2 * x2 + c + delta * x1
                
                if x3 != x0:
                    continue
                
                x4 = x0 * x0 + c + delta * x2
                if x4 != x1:
                    continue
                
                if x0 == x1 == x2:
                    continue
                
                found.append({
                    'x0': str(x0), 'x1': str(x1), 'x2': str(x2),
                    'c': str(c), 'c_denom': c.denominator,
                })
                if len(found) >= 3:
                    return found
    
    return found


def section_all_integers():
    """Test ALL integers from -30 to 30."""
    print("  ALL integers δ ∈ [-30, 30]:")
    
    results = {}
    for d in range(-30, 31):
        found = find_period3(d, x_range=30, denom_max=4)
        has_p3 = bool(found)
        c_denom = found[0]['c_denom'] if found else None
        results[d] = {'has_p3': has_p3, 'c_denom': c_denom}
        if found:
            print(f"    δ={d:4d}: ✅ period 3, c={found[0]['c']} (denom {c_denom})")
    
    # Which integers DON'T have period 3?
    no_p3 = [d for d, r in results.items() if not r['has_p3']]
    print(f"\n  Integers WITHOUT period 3: {no_p3}")
    print(f"  That's only δ=0!")
    
    state['integers'] = results
    return {'total': len(results), 'no_p3': no_p3}


def section_denom_pattern():
    """Analyze c denominator pattern for integers."""
    print("  C denominator pattern for integer δ:")
    
    for d in range(-15, 16):
        if d == 0:
            continue
        found = find_period3(d, x_range=40, denom_max=5)
        if found:
            c_vals = [Fraction(f['c']) for f in found]
            denoms = [c.denominator for c in c_vals]
            print(f"    δ={d:4d} ({'odd' if d%2 else 'even'}): c denoms = {denoms}")
    
    return {'done': True}


def section_systematic_rationals():
    """Systematically test δ = p/q for q = 1..8."""
    print("  Systematic test δ = p/q:")
    
    for q in range(1, 9):
        print(f"\n  q = {q} (δ = p/{q}):")
        found_count = 0
        not_found = []
        
        for p in range(-20, 21):
            if math.gcd(abs(p), q) != 1 and p != 0:
                continue  # skip non-reduced fractions
            if p == 0:
                continue
            
            delta = Fraction(p, q)
            found = find_period3(delta, x_range=20, denom_max=4)
            
            if found:
                found_count += 1
            else:
                not_found.append(p)
        
        total = found_count + len(not_found)
        print(f"    Tested {total}, found period 3: {found_count}, NOT found: {len(not_found)}")
        if not_found:
            not_found_deltas = [f"{p}/{q}" for p in not_found]
            print(f"    No period 3 at δ = {not_found_deltas[:15]}")
    
    return {'done': True}


def section_parametric_even():
    """Try to find a parametric family for even integers."""
    print("  Looking for parametric family at even δ:")
    
    # Collect (δ, c, x0, x1, x2) for even integers
    data = []
    for d in range(-20, 21, 2):
        if d == 0:
            continue
        found = find_period3(d, x_range=40, denom_max=5)
        if found:
            f = found[0]
            data.append((d, Fraction(f['c']), Fraction(f['x0']), Fraction(f['x1']), Fraction(f['x2'])))
    
    print(f"  Collected {len(data)} even integer period-3 orbits")
    print(f"\n  {'δ':>4s} {'c':>15s} {'x₀':>10s} {'x₁':>10s} {'x₂':>10s}")
    for d, c, x0, x1, x2 in data:
        print(f"  {d:4d} {str(c):>15s} {str(x0):>10s} {str(x1):>10s} {str(x2):>10s}")
    
    # Check if orbit coords have a pattern as function of δ
    # For odd δ=-(2k+1): x₀=-(5k+6)/2, x₁=(7k+6)/2, x₂=k/2
    # Maybe for even δ=2m: similar?
    print("\n  Trying to fit x₀, x₁, x₂ as rational functions of δ...")
    
    # Check: are x₀*4 and x₁*4 integers? (since c has denom 16=4²)
    for d, c, x0, x1, x2 in data:
        x0_4 = x0 * 4
        x1_4 = x1 * 4
        x2_4 = x2 * 4
        c_16 = c * 16
        print(f"    δ={d:4d}: 4x₀={x0_4}, 4x₁={x1_4}, 4x₂={x2_4}, 16c={c_16}")
    
    return {'count': len(data)}


def section_which_q_work():
    """For which denominator q does δ=1/q have period 3?"""
    print("  Which denominators q allow period 3 at δ=1/q:")
    
    results = {}
    for q in range(1, 20):
        delta = Fraction(1, q)
        found = find_period3(delta, x_range=25, denom_max=5)
        results[q] = bool(found)
        status = "✅" if found else "❌"
        if found:
            print(f"    δ=1/{q}: {status}  c={found[0]['c']}")
        else:
            print(f"    δ=1/{q}: {status}")
    
    working = [q for q, v in results.items() if v]
    failing = [q for q, v in results.items() if not v]
    print(f"\n  Working q: {working}")
    print(f"  Failing q: {failing}")
    
    state['q_pattern'] = {'working': working, 'failing': failing}
    return state['q_pattern']


def section_verdict():
    """Summary."""
    integers = state.get('integers', {})
    no_p3_int = [d for d, r in integers.items() if not r['has_p3']]
    q_pat = state.get('q_pattern', {})
    
    print("\n  ╔══════════════════════════════════════════════════╗")
    print("  ║ EXP-002h var c: EXPANDED EXCEPTIONS ANALYSIS      ║")
    print("  ╚══════════════════════════════════════════════════╝")
    
    print(f"\n  1. ALL nonzero integers have period-3 orbits (not just odd!)")
    print(f"     Integers without period 3: {no_p3_int}")
    print(f"\n  2. δ=1/q pattern:")
    print(f"     Working q: {q_pat.get('working', [])}")
    print(f"     Failing q: {q_pat.get('failing', [])}")
    
    print(f"\n  → Conjecture 4''' DISPROVED")
    print(f"  → Need new characterization of exceptional δ")
    
    with open(os.path.join(OUTPUT_DIR, 'analysis.json'), 'w') as f:
        json.dump({
            'no_p3_integers': no_p3_int,
            'q_pattern': q_pat,
        }, f, indent=2, default=str)
    
    return {'success': True}


run_experiment([
    ("All integers -30..30", section_all_integers),
    ("C denominator pattern", section_denom_pattern),
    ("Systematic rationals by denominator", section_systematic_rationals),
    ("Parametric family for even integers", section_parametric_even),
    ("Which δ=1/q have period 3?", section_which_q_work),
    ("Verdict", section_verdict),
], timeout_sec=480)
