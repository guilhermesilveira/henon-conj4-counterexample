#!/usr/bin/env python3
"""
EXP-001d: Final combined search. Focus on:
1. Finding periods 6, 8 (proving sharpness)
2. Confirming no forbidden periods exist
Uses exact Fraction arithmetic only. No SymPy needed.
"""
from common import run_experiment
import os, json
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp001-conj3-period-search')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}

def check_orbit(x0, x1, cv, max_period=12, max_bits=800):
    """Check what primitive period (x₀,x₁) has under f with parameter c.
    Returns (primitive_period, orbit) or (0, None) if no period ≤ max_period."""
    orbit = [x0, x1]
    xprev, xcur = x0, x1
    
    for n in range(2, max_period + 2):
        xnext = xcur * xcur + cv + xprev
        if (xnext.numerator.bit_length() > max_bits or
            xnext.denominator.bit_length() > max_bits):
            return (0, None)
        orbit.append(xnext)
        xprev, xcur = xcur, xnext
        
        N = n - 1
        if N >= 1 and xprev == x0 and xcur == x1:
            # Find primitive period
            prim = N
            for d in range(1, N):
                if N % d == 0 and orbit[d] == x0 and orbit[d+1] == x1:
                    prim = d
                    break
            return (prim, orbit[:prim])
    
    return (0, None)


def section_comprehensive():
    """
    Comprehensive search with optimized loop.
    Key optimization: skip (x₀, x₁) if x₂ is already too large.
    """
    MAX_P_C = 50
    MAX_Q_C = 10
    MAX_P_X = 12
    MAX_Q_X = 6
    
    # Build c values
    c_vals = set()
    for q in range(1, MAX_Q_C + 1):
        for p in range(-MAX_P_C * q, MAX_P_C * q + 1):
            c_vals.add(Fraction(p, q))
    c_vals = sorted(c_vals)
    
    # Build x values
    x_vals = set()
    for q in range(1, MAX_Q_X + 1):
        for p in range(-MAX_P_X, MAX_P_X + 1):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
    print(f"  {len(c_vals)} c values × {len(x_vals)}² x values = ~{len(c_vals)*len(x_vals)**2/1e6:.1f}M combos")
    
    period_data = {}  # N -> list of (c, orbit)
    total = 0
    
    for ci, cv in enumerate(c_vals):
        if ci % 100 == 0 and ci > 0:
            periods_so_far = sorted(period_data.keys())
            counts = {N: len(v) for N, v in period_data.items()}
            print(f"  c[{ci}/{len(c_vals)}] periods={periods_so_far} counts={counts}", flush=True)
        
        for x0 in x_vals:
            for x1 in x_vals:
                total += 1
                prim, orbit = check_orbit(x0, x1, cv)
                if prim > 0:
                    if prim not in period_data:
                        period_data[prim] = []
                    
                    # Normalize orbit for dedup
                    rotations = [tuple(orbit[i:] + orbit[:i]) for i in range(prim)]
                    orbit_norm = min(rotations)
                    key = (cv, orbit_norm)
                    
                    # Check if we already have this exact orbit
                    already = any(e['key'] == key for e in period_data[prim])
                    if not already:
                        period_data[prim].append({
                            'c': str(cv),
                            'orbit': [str(v) for v in orbit],
                            'key': key
                        })
                        
                        if prim not in {1, 2, 3, 4, 6, 8}:
                            print(f"\n  🔴 COUNTEREXAMPLE! Period {prim}!")
                            print(f"     c = {cv}")
                            print(f"     orbit = {orbit}")
    
    print(f"\n  === Comprehensive Search Results ===")
    print(f"  Total: {total} starting points checked")
    
    for N in sorted(period_data.keys()):
        count = len(period_data[N])
        marker = "✓" if N in {1,2,3,4,6,8} else "🔴"
        print(f"  {marker} Period {N}: {count} distinct orbits")
        for e in period_data[N][:3]:
            print(f"      c={e['c']}, orbit={e['orbit'][:4]}...")
    
    unexpected = [N for N in period_data if N not in {1,2,3,4,6,8}]
    missing = [N for N in {1,2,3,4,6,8} if N not in period_data]
    
    state['comprehensive'] = {
        'total': total,
        'period_counts': {N: len(v) for N, v in period_data.items()},
        'unexpected': unexpected,
        'missing': missing,
        'examples': {N: [{'c': e['c'], 'orbit': e['orbit']} for e in v[:5]] 
                    for N, v in period_data.items()}
    }
    
    if unexpected:
        print(f"\n  🔴 CONJECTURE 3 VIOLATED: periods {unexpected}")
    else:
        print(f"\n  ✅ No forbidden periods found")
    
    if missing:
        print(f"  ⚠️ Expected periods not found: {missing}")
    
    return state['comprehensive']


def section_targeted_6_8():
    """
    Extra-focused search for periods 6 and 8 with larger denominators.
    Use parametric insight: period-4 orbits exist with c = -(x₀²±2x₀+2).
    Period-6 orbits might exist with similar parametric families.
    """
    print("  Targeted search for period 6 and 8 with larger range...", flush=True)
    
    found6 = []
    found8 = []
    
    # Larger c range, moderate x range, higher denominators for x
    c_vals = set()
    for q in range(1, 6):
        for p in range(-200, 201):
            c_vals.add(Fraction(p, q))
    c_vals = sorted(c_vals)
    
    x_vals = set()
    for q in range(1, 12):
        for p in range(-20, 21):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
    print(f"  {len(c_vals)} c × {len(x_vals)}² x = ~{len(c_vals)*len(x_vals)**2/1e6:.1f}M combos", flush=True)
    
    total = 0
    for ci, cv in enumerate(c_vals):
        if ci % 200 == 0 and ci > 0:
            print(f"  c[{ci}/{len(c_vals)}] p6={len(found6)} p8={len(found8)}", flush=True)
        
        for x0 in x_vals:
            for x1 in x_vals:
                total += 1
                prim, orbit = check_orbit(x0, x1, cv, max_period=8, max_bits=1000)
                
                if prim == 6:
                    found6.append({'c': str(cv), 'orbit': [str(v) for v in orbit]})
                    if len(found6) <= 5:
                        print(f"    ✓ Period 6: c={cv}, orbit={orbit}")
                elif prim == 8:
                    found8.append({'c': str(cv), 'orbit': [str(v) for v in orbit]})
                    if len(found8) <= 5:
                        print(f"    ✓ Period 8: c={cv}, orbit={orbit}")
                
                if len(found6) >= 5 and len(found8) >= 5:
                    break
            if len(found6) >= 5 and len(found8) >= 5:
                break
        if len(found6) >= 5 and len(found8) >= 5:
            break
    
    print(f"\n  Targeted search: {total} checked")
    print(f"  Period 6: {len(found6)} orbits")  
    print(f"  Period 8: {len(found8)} orbits")
    
    state['targeted_6'] = found6
    state['targeted_8'] = found8
    return {'p6': len(found6), 'p8': len(found8)}


def section_save():
    """Save and print final verdict."""
    
    comp = state.get('comprehensive', {})
    
    all_periods = set(comp.get('period_counts', {}).keys())
    if state.get('targeted_6'):
        all_periods.add(6)
    if state.get('targeted_8'):
        all_periods.add(8)
    
    print(f"\n  ╔══════════════════════════════════════════════════╗")
    print(f"  ║       CONJECTURE 3 (INGRAM) — FINAL VERDICT     ║")
    print(f"  ╚══════════════════════════════════════════════════╝")
    print(f"  Periods found with ℚ-rational orbits: {sorted(all_periods)}")
    print(f"  Allowed by Conjecture 3:              {{1,2,3,4,6,8}}")
    
    unexpected = [N for N in all_periods if N not in {1,2,3,4,6,8}]
    
    if unexpected:
        print(f"\n  🔴🔴🔴 CONJECTURE 3 IS FALSE! Unexpected periods: {unexpected}")
    else:
        print(f"\n  ✅ Conjecture 3 SUPPORTED — consistent with all tests")
    
    missing = [N for N in {1,2,3,4,6,8} if N not in all_periods]
    if missing:
        print(f"  ⚠️ Allowed periods not yet found: {missing} (need larger search)")
    
    with open(os.path.join(OUTPUT_DIR, 'final_results.json'), 'w') as f:
        json.dump(state, f, indent=2, default=lambda o: str(o))
    
    return {'periods': sorted(all_periods), 'unexpected': unexpected, 'missing': missing}


run_experiment([
    ("Comprehensive exact search", section_comprehensive),
    ("Targeted search for periods 6, 8", section_targeted_6_8),
    ("Save results and verdict", section_save),
], timeout_sec=360)
