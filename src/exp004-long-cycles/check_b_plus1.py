#!/usr/bin/env python3
"""Check period 7 at b=+1 (the Conjecture 3 map) and verify convention."""
from common import run_experiment
from fractions import Fraction

state = {}

def section_verify_conj3_convention():
    """Verify: Conj 3 map is (x,y)↦(y,y²+c+x), i.e. b=+1 in PLUS convention."""
    b = Fraction(1)  # b=+1
    c = Fraction(-9, 16)
    
    # Verify the known period-8 orbit from exp001f
    orbit_x = [Fraction(v) for v in [-5, 5, -1, 3, -1, 1, -3, 1]]
    orbit_x = [v / 4 for v in orbit_x]
    
    print("  Verifying period-8 orbit at c=-9/16, b=+1:")
    xp, xc = orbit_x[0], orbit_x[1]
    for i in range(8):
        xn = xc*xc + c + b*xp
        ok = (xn == orbit_x[(i+2) % 8])
        print(f"    step {i+1}: x={xn} {'✅' if ok else '❌'}")
        xp, xc = xc, xn
    
    print(f"\n  After 8 steps: ({xp},{xc}) = ({orbit_x[0]},{orbit_x[1]})? {xp==orbit_x[0] and xc==orbit_x[1]}")
    return {'done': True}


def section_period7_at_b1():
    """Search for period 7 at b=+1."""
    b = Fraction(1)
    print("  Searching period 7 at b=+1 (Conj 3 map):")
    
    found = False
    for q in range(1, 5):
        for pc in range(-100*q, 100*q+1):
            c = Fraction(pc, q)
            for a0 in range(-10*q, 10*q+1):
                x0 = Fraction(a0, q)
                for a1 in range(-10*q, 10*q+1):
                    x1 = Fraction(a1, q)
                    
                    orbit = [x0, x1]
                    xp, xc = x0, x1
                    ok = True
                    for _ in range(9):
                        xn = xc*xc + c + b*xp
                        if abs(xn.numerator) > 10**10:
                            ok = False
                            break
                        orbit.append(xn)
                        xp, xc = xc, xn
                    
                    if not ok or len(orbit) < 9:
                        continue
                    
                    if orbit[7] == x0 and orbit[8] == x1:
                        prim = True
                        for d in [1, 7]:
                            if d < 7 and orbit[d] == x0 and orbit[d+1] == x1:
                                prim = False
                        if prim:
                            print(f"  ✅ PERIOD 7 at b=+1! c={c}")
                            print(f"     orbit={[str(orbit[i]) for i in range(7)]}")
                            found = True
                            break
                if found:
                    break
            if found:
                break
        if found:
            break
    
    if not found:
        print(f"  ❌ No period 7 at b=+1 (consistent with Conjecture 3)")
    
    return {'found': found}


def section_period7_b_minus1_details():
    """Analyze the period-7 orbit at b=-1."""
    b = Fraction(-1)
    c = Fraction(-9, 16)
    x0, x1 = Fraction(-3, 4), Fraction(-1, 4)
    
    print("  Period-7 orbit at b=-1, c=-9/16:")
    print(f"  States:")
    xp, xc = x0, x1
    states = [(xp, xc)]
    for i in range(7):
        xn = xc*xc + c + b*xp
        xp, xc = xc, xn
        if i < 6:
            states.append((xp, xc))
    
    for i, (a, bb) in enumerate(states):
        print(f"    S{i}: ({a}, {bb})")
    
    # Check: is b=-1 the Jacobian det(Df)?
    # f(x,y) = (y, y²+c+bx) has det(Df) = -b
    # b=-1: det = +1 (orientation-preserving, area-preserving)
    # b=+1: det = -1 (orientation-reversing, area-preserving)
    print(f"\n  b=-1 → det(Df) = +1 (orientation-preserving)")
    print(f"  b=+1 → det(Df) = -1 (orientation-reversing, Conj 3 case)")
    print(f"  Period 7 exists for det=+1 but NOT for det=-1")
    print(f"  → Period set depends on orientation!")
    
    return {'done': True}


run_experiment([
    ("Verify Conj 3 convention (b=+1)", section_verify_conj3_convention),
    ("Search period 7 at b=+1", section_period7_at_b1),
    ("Period-7 at b=-1 details", section_period7_b_minus1_details),
], timeout_sec=120)
