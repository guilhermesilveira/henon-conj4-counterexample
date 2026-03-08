#!/usr/bin/env python3
"""
EXP-001f var b: Targeted period-8 search.

Key insight from period 6: c=-7/9, orbit elements have denom 3.
Pattern: c = p/q², orbit elements have denom q.

For period 8: try c = p/q² with q=1..8, orbit x₀,x₁ with denom q.
This drastically reduces search space.
"""
from common import run_experiment
import os, json
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp001f-period8-search')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


def check_p8(x0, x1, cv):
    """Check primitive period 8. Returns orbit or None."""
    orbit = [x0, x1]
    xp, xc = x0, x1
    for n in range(2, 10):
        xn = xc * xc + cv + xp
        if xn.numerator.bit_length() > 1200 or xn.denominator.bit_length() > 1200:
            return None
        orbit.append(xn)
        xp, xc = xc, xn
    
    if orbit[8] != orbit[0] or orbit[9] != orbit[1]:
        return None
    
    for d in [1, 2, 4]:
        if orbit[d] == orbit[0] and orbit[d+1] == orbit[1]:
            return None
    
    return orbit[:8]


def section_denom_pattern():
    """Search with c = p/q², x with denom q."""
    
    all_found = []
    
    for q in range(1, 12):
        q2 = q * q
        
        # c = p/q²
        c_vals = [Fraction(p, q2) for p in range(-300, 301)]
        c_vals = sorted(set(c_vals))
        
        # x with denom q
        x_vals = [Fraction(p, q) for p in range(-20 * q, 20 * q + 1)]
        x_vals = sorted(set(x_vals))
        
        combos = len(c_vals) * len(x_vals) ** 2
        print(f"  q={q}: {len(c_vals)} c × {len(x_vals)}² x = {combos}", flush=True)
        
        found = 0
        for cv in c_vals:
            for x0 in x_vals:
                for x1 in x_vals:
                    orbit = check_p8(x0, x1, cv)
                    if orbit:
                        all_found.append({
                            'q': q, 'c': str(cv),
                            'orbit': [str(v) for v in orbit]
                        })
                        found += 1
                        if found <= 3:
                            print(f"    ✅ PERIOD 8! c={cv}, orbit={orbit[:4]}...", flush=True)
                        if found >= 5:
                            break
                if found >= 5:
                    break
            if found >= 5:
                break
        
        if found:
            print(f"  q={q}: {found} period-8 orbits!")
        
        if all_found:
            break
    
    state['denom'] = all_found
    return {'found': len(all_found)}


def section_mixed_denom():
    """Allow x₀ and x₁ to have DIFFERENT denominators."""
    
    if state.get('denom'):
        print("  Already found period 8 — skip mixed denom")
        state['mixed'] = []
        return {'found': 0}
    
    all_found = []
    
    # c with small denom
    c_vals = set()
    for q in range(1, 25):
        for p in range(-200, 201):
            c_vals.add(Fraction(p, q))
    c_vals = sorted(c_vals)
    
    # x with denominator up to 8
    x_vals = set()
    for q in range(1, 9):
        for p in range(-12, 13):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
    combos = len(c_vals) * len(x_vals) ** 2
    print(f"  {len(c_vals)} c × {len(x_vals)}² x = {combos}", flush=True)
    
    for ci, cv in enumerate(c_vals):
        if ci % 1000 == 0 and ci > 0:
            print(f"  c[{ci}/{len(c_vals)}] found={len(all_found)}", flush=True)
        
        for x0 in x_vals:
            for x1 in x_vals:
                orbit = check_p8(x0, x1, cv)
                if orbit:
                    all_found.append({
                        'c': str(cv),
                        'orbit': [str(v) for v in orbit]
                    })
                    if len(all_found) <= 3:
                        print(f"  ✅ PERIOD 8! c={cv}", flush=True)
                    if len(all_found) >= 5:
                        break
            if len(all_found) >= 5:
                break
        if len(all_found) >= 5:
            break
    
    state['mixed'] = all_found
    return {'found': len(all_found)}


def section_reverse_engineer():
    """
    Reverse approach: pick a period-8 orbit shape and solve for c.
    
    For period 8 with x₀,...,x₇: the recurrence x_{n+1} = x_n² + c + x_{n-1}
    gives 8 equations. All must use the SAME c.
    
    c = x₂ - x₁² - x₀ = x₃ - x₂² - x₁ = ... = x₀ - x₇² - x₆
    
    So x₂ - x₁² - x₀ = x₃ - x₂² - x₁
    → x₃ = x₂ - x₁² - x₀ + x₂² + x₁ = x₂² + x₂ - x₁² + x₁ - x₀
    
    This means once we fix x₀, x₁, x₂, the rest is determined by the recurrence.
    But we also need the orbit to close: x₈ = x₀ and x₉ = x₁.
    
    So fix x₀, x₁ ∈ ℚ and c = x₂ - x₁² - x₀ for each candidate x₂.
    Then iterate and check closure.
    """
    if state.get('denom') or state.get('mixed'):
        print("  Already found period 8 — skip reverse")
        state['reverse'] = []
        return {'found': 0}
    
    print("  Reverse engineering: fix x₀, x₁, vary x₂ (which determines c)...", flush=True)
    
    all_found = []
    
    x_vals = [Fraction(p, q) for q in range(1, 8) for p in range(-15, 16)]
    x_vals = sorted(set(x_vals))
    
    total = 0
    for x0 in x_vals:
        for x1 in x_vals:
            for x2 in x_vals:
                total += 1
                cv = x2 - x1 * x1 - x0
                
                orbit = [x0, x1, x2]
                xp, xc = x1, x2
                ok = True
                for n in range(3, 10):
                    xn = xc * xc + cv + xp
                    if xn.numerator.bit_length() > 1000 or xn.denominator.bit_length() > 1000:
                        ok = False
                        break
                    orbit.append(xn)
                    xp, xc = xc, xn
                
                if not ok:
                    continue
                
                if orbit[8] == x0 and orbit[9] == x1:
                    # Check primitive
                    prim = True
                    for d in [1, 2, 4]:
                        if orbit[d] == x0 and orbit[d+1] == x1:
                            prim = False
                            break
                    if prim:
                        all_found.append({
                            'c': str(cv),
                            'orbit': [str(v) for v in orbit[:8]]
                        })
                        if len(all_found) <= 3:
                            print(f"  ✅ PERIOD 8! c={cv}, x₀={x0}, x₁={x1}, x₂={x2}", flush=True)
        
        if len(all_found) >= 5:
            break
    
    print(f"  Reverse: {total} triples tested, {len(all_found)} found")
    
    state['reverse'] = all_found
    return {'found': len(all_found), 'tested': total}


def section_verdict():
    """Final verdict."""
    all_found = state.get('denom', []) + state.get('mixed', []) + state.get('reverse', [])
    
    # Deduplicate
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
            print(f"  {i+1}. c = {entry['c']}")
            print(f"     orbit = {entry['orbit']}")
        print(f"\n  → CONJECTURE 3 IS SHARP (all periods {1,2,3,4,6,8} verified)!")
    else:
        print(f"  ⚠️ No period-8 rational orbits found in search range")
    
    with open(os.path.join(OUTPUT_DIR, 'results.json'), 'w') as f:
        json.dump({'unique': unique, 'counts': {
            'denom': len(state.get('denom', [])),
            'mixed': len(state.get('mixed', [])),
            'reverse': len(state.get('reverse', []))
        }}, f, indent=2, default=str)
    
    return {'found': len(unique)}


run_experiment([
    ("Denominator-pattern search (c=p/q², x denom q)", section_denom_pattern),
    ("Mixed-denominator search", section_mixed_denom),
    ("Reverse engineering (fix x₀,x₁,x₂, solve for c)", section_reverse_engineer),
    ("Verdict", section_verdict),
], timeout_sec=300)
