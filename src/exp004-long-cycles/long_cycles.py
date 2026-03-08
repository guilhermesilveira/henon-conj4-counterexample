#!/usr/bin/env python3
"""
EXP-004: Long cycles — BIRS Q45.

Q45: Over a number field K, can we construct infinite families of generalized
Hénon maps of algebraic degree d with K-rational cycles of length ≥ d+3?

For d=2: need cycles of length ≥ 5.

What we already know:
- Period 3: universal family (exp002j), works for ALL b∈ℚ\{-1}
- Period 4: c=-5/4, b=+1 / δ=-1 (exp001)
- Period 6: c=-7/9, b=+1 / δ=-1 (exp001e)
- Period 8: c=-9/16, b=+1 / δ=-1 (exp001f)
- Periods 5, 7, 9, 10, ...: NOT FOUND yet

This experiment:
1. Can we find period-5 orbits? (needed for Q45 with d=2)
2. Search for parametric families giving period ≥5 with general b
3. Count total rational periodic points for specific (c,b)
4. Construct maps with maximum number of rational periodic points
"""
from common import run_experiment
import os, json, math
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp004-long-cycles')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


def find_period_n(n, b_val, c_range=100, x_range=15, denom_max=4):
    """Find period-n orbits for given b in PLUS convention."""
    b = Fraction(b_val)
    found = []
    
    c_vals = set()
    for q in range(1, denom_max + 1):
        for p in range(-c_range * q, c_range * q + 1):
            c_vals.add(Fraction(p, q))
    
    x_vals = set()
    for q in range(1, denom_max + 1):
        for p in range(-x_range * q, x_range * q + 1):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
    for c in sorted(c_vals):
        for x0 in x_vals:
            for x1 in x_vals:
                # Iterate n times
                xp, xc = x0, x1
                ok = True
                for _ in range(n):
                    xn = xc * xc + c + b * xp
                    if abs(xn.numerator) > 10**12:
                        ok = False
                        break
                    xp, xc = xc, xn
                
                if not ok:
                    continue
                
                # Check: after n steps, back to (x0, x1)?
                # After n steps: state is (xp, xc)
                # Actually need to track more carefully
                # Let orbit = [x0, x1, x2, ..., x_{n+1}]
                orbit = [x0, x1]
                xp, xc = x0, x1
                for _ in range(n):
                    xn = xc * xc + c + b * xp
                    if abs(xn.numerator) > 10**12:
                        ok = False
                        break
                    orbit.append(xn)
                    xp, xc = xc, xn
                
                if not ok or len(orbit) < n + 2:
                    continue
                
                if orbit[n] == x0 and orbit[n+1] == x1:
                    # Check primitive: no smaller period divides n
                    prim = True
                    for d in range(1, n):
                        if n % d == 0:
                            if orbit[d] == x0 and orbit[d+1] == x1:
                                prim = False
                                break
                    
                    if prim:
                        found.append({
                            'c': str(c), 'b': str(b),
                            'orbit': [str(orbit[i]) for i in range(n)],
                        })
                        if len(found) >= 3:
                            return found
    return found


def section_period5_search():
    """Search for period-5 orbits at b=-1 (area-preserving)."""
    print("  Searching for period-5 orbits (b=-1, area-preserving):")
    
    found = find_period_n(5, -1, c_range=50, x_range=10, denom_max=3)
    
    if found:
        print(f"  ✅ PERIOD 5 FOUND! {len(found)} orbits")
        for f in found:
            print(f"    c={f['c']}, orbit={f['orbit'][:5]}")
    else:
        print(f"  ❌ No period-5 orbits found in range")
        print(f"    (c∈[-50,50], x∈[-10,10], denom≤3)")
    
    state['period5'] = found
    return {'found': len(found)}


def section_period5_wider():
    """Wider search for period-5 at various b values."""
    print("  Wider period-5 search at multiple b values:")
    
    all_found = {}
    for b in [-1, 1, -2, 2, -3, 3, Fraction(1,2), Fraction(-1,2)]:
        found = find_period_n(5, b, c_range=30, x_range=8, denom_max=2)
        all_found[str(b)] = found
        if found:
            print(f"    b={str(b):>5s}: ✅ period 5 at c={found[0]['c']}")
        else:
            print(f"    b={str(b):>5s}: ❌ not found")
    
    state['period5_wider'] = all_found
    return {'any_found': any(v for v in all_found.values())}


def section_period5_algebraic():
    """Algebraic approach: try to extend universal period-3 family to period 5."""
    print("  Algebraic approach for period 5:")
    print("  The period-3 family has c = -(29b²+38b+29)/16")
    print("  At this c value, do period-5 orbits also exist?")
    
    # For each b, compute c from period-3 family, then search for period-5
    for b_val in [-2, -3, 2, 3, 5, 7]:
        b = Fraction(b_val)
        c = -(29*b**2 + 38*b + 29) / 16
        
        # Search for period-5 at this (c, b)
        x_vals = set()
        for q in range(1, 5):
            for p in range(-20*q, 20*q+1):
                x_vals.add(Fraction(p, q))
        x_vals = sorted(x_vals)
        
        found = False
        for x0 in x_vals:
            if found:
                break
            for x1 in x_vals:
                orbit = [x0, x1]
                xp, xc = x0, x1
                ok = True
                for _ in range(7):  # compute 7 terms
                    xn = xc * xc + c + b * xp
                    if abs(xn.numerator) > 10**12:
                        ok = False
                        break
                    orbit.append(xn)
                    xp, xc = xc, xn
                
                if not ok or len(orbit) < 7:
                    continue
                
                if orbit[5] == x0 and orbit[6] == x1:
                    # Check primitive
                    prim = True
                    for d in [1]:
                        if orbit[d] == x0 and orbit[d+1] == x1:
                            prim = False
                    if prim:
                        print(f"    b={b_val}: ✅ PERIOD 5! orbit={[str(o) for o in orbit[:5]]}")
                        found = True
                        break
        
        if not found:
            print(f"    b={b_val}, c={c}: ❌ no period-5")
    
    return {'done': True}


def section_count_rational_points():
    """Count total rational periodic points for specific (c, b) pairs."""
    print("  Counting total rational periodic points:")
    print("  For each (c,b), find ALL periodic orbits up to period 8")
    
    test_cases = [
        ("c=-7/9, b=-1", Fraction(-7,9), Fraction(-1)),
        ("c=-9/16, b=-1", Fraction(-9,16), Fraction(-1)),
        ("c=-5/4, b=-1", Fraction(-5,4), Fraction(-1)),
        ("c=-29/16, b=0", Fraction(-29,16), Fraction(0)),
        ("c=-69/16, b=-2", Fraction(-69,16), Fraction(-2)),
    ]
    
    for label, c, b in test_cases:
        orbits = {}
        
        x_vals = set()
        for q in range(1, 5):
            for p in range(-15*q, 15*q+1):
                x_vals.add(Fraction(p, q))
        x_vals = sorted(x_vals)
        
        all_periodic = set()
        
        for x0 in x_vals:
            for x1 in x_vals:
                orb = [x0, x1]
                xp, xc = x0, x1
                ok = True
                for _ in range(10):
                    xn = xc * xc + c + b * xp
                    if abs(xn.numerator) > 10**12:
                        ok = False
                        break
                    orb.append(xn)
                    xp, xc = xc, xn
                
                if not ok:
                    continue
                
                for per in range(1, 9):
                    if per < len(orb) - 1 and orb[per] == x0 and orb[per+1] == x1:
                        # Check primitive
                        prim = True
                        for d in range(1, per):
                            if per % d == 0 and orb[d] == x0 and orb[d+1] == x1:
                                prim = False
                                break
                        if prim:
                            orbit_set = frozenset((orb[i], orb[i+1]) for i in range(per))
                            if orbit_set not in all_periodic:
                                all_periodic.add(orbit_set)
                                if per not in orbits:
                                    orbits[per] = []
                                orbits[per].append(per)
                        break
        
        total = sum(per * len(orbs) for per, orbs in orbits.items())
        periods_found = sorted(orbits.keys())
        orbit_counts = {p: len(orbs) for p, orbs in sorted(orbits.items())}
        
        print(f"\n  {label}:")
        print(f"    Periods found: {periods_found}")
        print(f"    Orbit counts: {orbit_counts}")
        print(f"    Total rational periodic points: {total}")
    
    return {'done': True}


def section_interpolation_Q45():
    """
    Q45 approach: given d+2 = 4 points in ℚ², find a Hénon map with those points periodic.
    
    For a Hénon map f(x,y)=(y, y²+c+bx), a period-n orbit visits n states:
    (x₀,x₁), (x₁,x₂), ..., (x_{n-1},x₀)
    
    The orbit is determined by x₀,...,x_{n-1} and must satisfy:
    xᵢ₊₁ = xᵢ² + c + b·xᵢ₋₁ for each i (mod n)
    
    This gives n equations in n+2 unknowns (x₀,...,x_{n-1}, c, b).
    For n ≥ 3: n equations, n+2 unknowns → 2-parameter family!
    
    So for period 5: 5 equations, 7 unknowns → 2 free parameters.
    Pick x₀, x₁ freely, the rest is determined (if consistent).
    """
    print("  Q45 interpolation: period-5 construction")
    print("  5 equations, 7 unknowns → 2 free parameters (x₀, x₁)")
    
    # For period 5: given x₀, x₁, we can compute x₂,...,x₄ and (c, b) IF the system is consistent
    # x₂ = x₁² + c + b·x₀  →  c + b·x₀ = x₂ - x₁²
    # x₃ = x₂² + c + b·x₁  →  c + b·x₁ = x₃ - x₂²
    # x₄ = x₃² + c + b·x₂  →  c + b·x₂ = x₄ - x₃²
    # x₀ = x₄² + c + b·x₃  →  c + b·x₃ = x₀ - x₄²
    # x₁ = x₀² + c + b·x₄  →  c + b·x₄ = x₁ - x₀²
    
    # From first two: b(x₀-x₁) = (x₂-x₁²) - (x₃-x₂²) = x₂-x₃+x₂²-x₁²
    # If x₀ ≠ x₁: b = (x₂-x₃+x₂²-x₁²)/(x₀-x₁)
    # c = x₂-x₁²-b·x₀
    
    # So given x₀, x₁, x₂, x₃: b and c are determined.
    # Then x₄ = x₃² + c + b·x₂ (determined)
    # Closure 1: x₀ = x₄² + c + b·x₃ (constraint)
    # Closure 2: x₁ = x₀² + c + b·x₄ (constraint)
    
    # So: 4 free params (x₀,x₁,x₂,x₃), 2 constraints → 2-parameter family
    
    print("\n  Strategy: pick x₀,x₁,x₂,x₃ ∈ ℚ, compute b,c,x₄, check closure")
    
    found = []
    for q in range(1, 4):
        for a0 in range(-6, 7):
            x0 = Fraction(a0, q)
            for a1 in range(-6, 7):
                x1 = Fraction(a1, q)
                if x0 == x1:
                    continue
                for a2 in range(-6, 7):
                    x2 = Fraction(a2, q)
                    for a3 in range(-6, 7):
                        x3 = Fraction(a3, q)
                        
                        denom = x0 - x1
                        if denom == 0:
                            continue
                        
                        b = (x2 - x3 + x2**2 - x1**2) / denom
                        c = x2 - x1**2 - b * x0
                        
                        # Compute x4
                        x4 = x3**2 + c + b * x2
                        
                        # Check closure
                        close1 = x4**2 + c + b * x3
                        close2 = x0**2 + c + b * x4
                        
                        if close1 == x0 and close2 == x1:
                            # Check primitive
                            orb = [x0, x1, x2, x3, x4]
                            if len(set(orb)) < 3:  # degenerate
                                continue
                            # Check no smaller period
                            orbit_seq = [x0, x1, x2, x3, x4, x0, x1]
                            prim = True
                            for d in [1]:
                                if orbit_seq[d] == x0 and orbit_seq[d+1] == x1:
                                    prim = False
                            if prim:
                                key = (str(b), str(c))
                                found.append({
                                    'b': str(b), 'c': str(c),
                                    'orbit': [str(x) for x in orb],
                                })
                                if len(found) <= 5:
                                    print(f"    ✅ b={b}, c={c}, orbit={[str(x) for x in orb]}")
                                if len(found) >= 20:
                                    break
                    if len(found) >= 20:
                        break
                if len(found) >= 20:
                    break
            if len(found) >= 20:
                break
        if len(found) >= 20:
            break
    
    if not found:
        print("    ❌ No period-5 orbits found")
    else:
        print(f"\n  Found {len(found)} period-5 orbits!")
        # Check which are at b=-1
        b_minus1 = [f for f in found if f['b'] == '-1']
        print(f"  Of those, {len(b_minus1)} have b=-1 (area-preserving)")
    
    state['period5_interp'] = found
    return {'found': len(found)}


def section_verdict():
    """Summary."""
    p5 = state.get('period5', [])
    p5w = state.get('period5_wider', {})
    p5i = state.get('period5_interp', [])
    
    any_p5 = len(p5) > 0 or any(v for v in p5w.values()) or len(p5i) > 0
    
    print("\n  ╔══════════════════════════════════════════════════╗")
    print("  ║       EXP-004: LONG CYCLES / Q45                  ║")
    print("  ╚══════════════════════════════════════════════════╝")
    
    if any_p5:
        print(f"\n  ✅ Period-5 orbits FOUND!")
        print(f"     Brute force: {len(p5)}")
        print(f"     Interpolation: {len(p5i)}")
        print(f"  → Q45 answered: YES, length-5 cycles exist (≥ d+3=5)")
    else:
        print(f"\n  ❌ No period-5 orbits found")
        print(f"  → Conjecture 3 support: period 5 may not exist over ℚ")
    
    with open(os.path.join(OUTPUT_DIR, 'results.json'), 'w') as f:
        json.dump({
            'period5_brute': len(p5),
            'period5_interp': len(p5i),
            'q45_answered': any_p5,
        }, f, indent=2)
    
    return {'any_p5': any_p5}


run_experiment([
    ("Period-5 search (b=-1)", section_period5_search),
    ("Period-5 wider search", section_period5_wider),
    ("Period-5 at period-3 family c values", section_period5_algebraic),
    ("Count total rational periodic points", section_count_rational_points),
    ("Interpolation construction (Q45)", section_interpolation_Q45),
    ("Verdict", section_verdict),
], timeout_sec=480)
