#!/usr/bin/env python3
"""
EXP-002h var b: Optimized wider δ confirmation.
Use the reverse-engineering approach: fix x₀, x₁, compute c from period-3 condition.
For period 3: x₂ = x₁² + c + δx₀, x₃ = x₂² + c + δx₁, x₃ must equal x₀.
So: c = (x₀ - x₂² - δx₁) and also c = (x₂ - x₁² - δx₀).
Equating: x₀ - x₂² - δx₁ = x₂ - x₁² - δx₀  →  x₂ = f(x₀, x₁, δ).
Then check if c from both equations agrees and x₃=x₀.
"""
from common import run_experiment
import os, json
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp002h-wider-delta-confirm')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


def find_period3_algebraic(delta_val, x_range=30, denom_max=6):
    """Find period-3 orbits algebraically.
    
    For period 3 with f(x,y)=(y, y²+c+δx):
    x₀ → x₁ → x₂ → x₀
    
    c = x₂ - x₁² - δx₀  (from x₂ = x₁² + c + δx₀)
    Also: x₀ = x₂² + c + δx₁  (closure)
    
    Substituting c: x₀ = x₂² + x₂ - x₁² - δx₀ + δx₁
    And: x₂ = x₁² + c + δx₀, x₁ = x₀² + c + δx₂ (wait, we need x₁ from x₀)
    
    Actually the map is (x,y) → (y, y²+c+δx).
    If we label orbit as (x₀,x₁), (x₁,x₂), (x₂,x₀):
    x₂ = x₁² + c + δx₀
    x₀ = x₂² + c + δx₁  (closure after 3 steps: x₃=x₀, and x₃ comes from x₂²+c+δx₁... wait)
    
    Let me be careful. State is (a,b). Map: (a,b) → (b, b²+c+δa).
    Period-3: (x₀,x₁) → (x₁,x₂) → (x₂,x₃) → must equal (x₀,x₁).
    So x₃ = x₀ and we need x₄ = x₁ (implied by x₃=x₀ if truly periodic).
    
    x₂ = x₁² + c + δx₀
    x₃ = x₂² + c + δx₁ = x₀  (closure condition 1)
    x₄ = x₀² + c + δx₂ = x₁  (closure condition 2, redundant if condition 1 + map structure)
    
    From x₂ = x₁² + c + δx₀: c = x₂ - x₁² - δx₀
    From x₃ = x₀: x₂² + c + δx₁ = x₀
    Substituting c: x₂² + x₂ - x₁² - δx₀ + δx₁ = x₀
    → x₂² + x₂ = x₀ + x₁² + δx₀ - δx₁ = x₀(1+δ) + x₁² - δx₁ = x₀(1+δ) + x₁(x₁-δ)
    → x₂² + x₂ - x₀(1+δ) - x₁(x₁-δ) = 0
    
    This is a QUADRATIC in x₂! Given x₀, x₁, δ, solve for x₂:
    x₂ = (-1 ± √(1 + 4[x₀(1+δ) + x₁(x₁-δ)])) / 2
    
    For x₂ ∈ ℚ, the discriminant must be a perfect square (rational).
    """
    delta = Fraction(delta_val)
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
            
            # Discriminant D = 1 + 4[x₀(1+δ) + x₁(x₁-δ)]
            inner = x0 * (1 + delta) + x1 * (x1 - delta)
            D = 1 + 4 * inner
            
            if D < 0:
                continue
            
            # Check if D is a perfect square of a rational
            # D = p/q, need p*q to be a perfect square... actually D = a/b in lowest terms
            # √(a/b) is rational iff a*b is a perfect square? No: iff a and b are both perfect squares.
            num = D.numerator
            den = D.denominator
            
            if num < 0:
                continue
            
            # Check if num and den are perfect squares
            import math
            sn = math.isqrt(num)
            sd = math.isqrt(den)
            
            if sn * sn != num or sd * sd != den:
                continue
            
            # x₂ = (-1 ± sn/sd) / 2
            sqrt_D = Fraction(sn, sd)
            
            for sign in [1, -1]:
                x2 = (-1 + sign * sqrt_D) / 2
                
                c = x2 - x1 * x1 - delta * x0
                
                # Verify full period-3
                x3 = x2 * x2 + c + delta * x1
                if x3 != x0:
                    continue
                
                x4 = x0 * x0 + c + delta * x2
                if x4 != x1:
                    continue
                
                # Check primitive (not fixed point or period-2)
                if x0 == x1 == x2:
                    continue
                if x0 == x2 and x1 == x0:
                    continue
                
                found.append({
                    'x0': str(x0), 'x1': str(x1), 'x2': str(x2),
                    'c': str(c), 'delta': str(delta),
                })
                if len(found) >= 3:
                    return found
    
    return found


def section_odd_control():
    """Positive control: odd integers should find period-3."""
    print("  Positive control (odd integers):")
    for d in [-7, -5, -3, -1, 1, 3, 5, 7]:
        found = find_period3_algebraic(d, x_range=20, denom_max=3)
        if found:
            f = found[0]
            print(f"    δ={d:3d}: ✅ period 3: x₀={f['x0']}, x₁={f['x1']}, c={f['c']}")
        else:
            print(f"    δ={d:3d}: ⚠️ not found in range")
    return {'done': True}


def section_even_integers():
    """Test even integers."""
    print("  Even integers (expect NO period 3):")
    results = {}
    for d in range(-20, 21, 2):
        if d == 0:
            continue
        found = find_period3_algebraic(d, x_range=25, denom_max=4)
        results[d] = bool(found)
        if found:
            f = found[0]
            print(f"    δ={d:4d}: ❌ EXCEPTION! period 3: c={f['c']}")
    
    exceptions = [k for k, v in results.items() if v]
    if not exceptions:
        print(f"  ✅ All {len(results)} even integers: NO period 3 found")
    else:
        print(f"  ❌ Exceptions at: {exceptions}")
    
    state['even_exc'] = exceptions
    return {'tested': len(results), 'exceptions': len(exceptions)}


def section_non_integer():
    """Test non-integer rationals."""
    print("  Non-integer rationals (expect NO period 3):")
    
    test_deltas = set()
    for q in range(2, 10):
        for p in range(-15, 16):
            if p % q != 0:
                test_deltas.add(Fraction(p, q))
    
    # Add near-odd values
    for odd in range(-5, 6, 2):
        for eps_q in [10, 100]:
            for eps_p in [-1, 1]:
                test_deltas.add(Fraction(odd * eps_q + eps_p, eps_q))
    
    test_deltas = sorted(test_deltas)
    
    exceptions = []
    for delta in test_deltas:
        found = find_period3_algebraic(delta, x_range=15, denom_max=3)
        if found:
            exceptions.append((str(delta), found[0]))
            print(f"    δ={str(delta):>8s}: ❌ EXCEPTION! c={found[0]['c']}")
    
    if not exceptions:
        print(f"  ✅ All {len(test_deltas)} non-integer δ: NO period 3")
    else:
        print(f"  ❌ {len(exceptions)} exceptions found!")
        for e in exceptions[:5]:
            print(f"    δ={e[0]}: c={e[1]['c']}")
    
    state['nonint_exc'] = exceptions
    return {'tested': len(test_deltas), 'exceptions': len(exceptions)}


def section_half_integers():
    """Deep test at half-integers."""
    print("  Half-integer δ (deep search):")
    
    half_ints = [Fraction(p, 2) for p in range(-21, 22) if p % 2 != 0]
    
    exceptions = []
    for delta in half_ints:
        found = find_period3_algebraic(delta, x_range=30, denom_max=5)
        if found:
            exceptions.append((str(delta), found[0]))
            print(f"    δ={str(delta):>6s}: ❌ period 3 at c={found[0]['c']}")
    
    if not exceptions:
        print(f"  ✅ All {len(half_ints)} half-integers: NO period 3")
    
    state['half_exc'] = exceptions
    return {'tested': len(half_ints), 'exceptions': len(exceptions)}


def section_period4_even():
    """Also check period 4 at even integers (maybe period 3 fails but 4 exists?)."""
    print("  Period-4 check at even integers:")
    
    for d in [-4, -2, 2, 4, 6]:
        delta = Fraction(d)
        found_any = False
        
        # Brute force period-4 check with moderate range
        for q in range(1, 4):
            for p_c in range(-50, 51):
                c = Fraction(p_c, q)
                for a in range(-8, 9):
                    for b in range(-8, 9):
                        x0, x1 = Fraction(a), Fraction(b)
                        orbit = [x0, x1]
                        xp, xc = x0, x1
                        ok = True
                        for _ in range(6):
                            xn = xc * xc + c + delta * xp
                            if abs(xn.numerator) > 10**12:
                                ok = False
                                break
                            orbit.append(xn)
                            xp, xc = xc, xn
                        
                        if not ok:
                            continue
                        
                        if orbit[4] == x0 and orbit[5] == x1:
                            # Check primitive
                            prim = True
                            for dd in [1, 2]:
                                if orbit[dd] == x0 and orbit[dd+1] == x1:
                                    prim = False
                            if prim:
                                print(f"    δ={d}: ❌ PERIOD 4! c={c}, orbit={[str(orbit[i]) for i in range(4)]}")
                                found_any = True
                                break
                    if found_any:
                        break
                if found_any:
                    break
            if found_any:
                break
        
        if not found_any:
            print(f"    δ={d}: ✅ no period 4 found")
    
    return {'done': True}


def section_verdict():
    """Final verdict."""
    even = state.get('even_exc', [])
    nonint = state.get('nonint_exc', [])
    half = state.get('half_exc', [])
    
    print("\n  ╔══════════════════════════════════════════════════╗")
    print("  ║ EXP-002h: CORRECTED CONJECTURE 4''' TEST         ║")
    print("  ╚══════════════════════════════════════════════════╝")
    
    print(f"\n  Even integers: {len(even)} exceptions")
    print(f"  Non-integer rationals: {len(nonint)} exceptions")
    print(f"  Half-integers: {len(half)} exceptions")
    
    all_clean = len(even) == 0 and len(nonint) == 0 and len(half) == 0
    
    if all_clean:
        print(f"\n  ✅ CONJECTURE 4''' STRONGLY SUPPORTED:")
        print(f"     Period > 2 ⟺ δ is an odd integer")
    else:
        print(f"\n  ❌ CONJECTURE 4''' HAS ISSUES")
    
    with open(os.path.join(OUTPUT_DIR, 'results.json'), 'w') as f:
        json.dump({
            'even_exc': even,
            'nonint_exc': [str(e) for e in nonint],
            'half_exc': [str(e) for e in half],
            'supported': all_clean,
        }, f, indent=2, default=str)
    
    return {'supported': all_clean}


run_experiment([
    ("Odd integer positive control", section_odd_control),
    ("Even integers", section_even_integers),
    ("Non-integer rationals", section_non_integer),
    ("Half-integers deep", section_half_integers),
    ("Period 4 at even integers", section_period4_even),
    ("Verdict", section_verdict),
], timeout_sec=480)
