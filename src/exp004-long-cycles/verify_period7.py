#!/usr/bin/env python3
"""Verify the alleged period-7 orbit at c=-9/16, b=-1."""
from common import run_experiment
from fractions import Fraction

state = {}

def section_verify():
    """Find and verify the period-7 orbit."""
    b = Fraction(-1)
    c = Fraction(-9, 16)
    
    x_vals = set()
    for q in range(1, 5):
        for p in range(-15*q, 15*q+1):
            x_vals.add(Fraction(p, q))
    x_vals = sorted(x_vals)
    
    for x0 in x_vals:
        for x1 in x_vals:
            orbit = [x0, x1]
            xp, xc = x0, x1
            ok = True
            for _ in range(10):
                xn = xc * xc + c + b * xp
                if abs(xn.numerator) > 10**12:
                    ok = False
                    break
                orbit.append(xn)
                xp, xc = xc, xn
            
            if not ok:
                continue
            
            # Check period 7 specifically
            if len(orbit) >= 9 and orbit[7] == x0 and orbit[8] == x1:
                # Check not smaller period
                prim = True
                for d in [1]:
                    if orbit[d] == x0 and orbit[d+1] == x1:
                        prim = False
                if prim:
                    print(f"  Alleged period-7: x₀={x0}, x₁={x1}")
                    print(f"  Full orbit: {[str(orbit[i]) for i in range(8)]}")
                    
                    # Verify step by step
                    print(f"\n  Step-by-step verification:")
                    xp, xc = x0, x1
                    for i in range(7):
                        xn = xc*xc + c + b*xp
                        print(f"    step {i+1}: ({xp},{xc}) → ({xc},{xn})")
                        xp, xc = xc, xn
                    
                    print(f"\n  After 7 steps: ({xp},{xc})")
                    print(f"  Original:     ({x0},{x1})")
                    print(f"  Match: {xp == x0 and xc == x1}")
                    
                    # Also check if this is actually period 7 or a sub-period
                    for p in range(1, 7):
                        if 7 % p == 0 or True:  # check all
                            xp2, xc2 = x0, x1
                            for _ in range(p):
                                xn2 = xc2*xc2 + c + b*xp2
                                xp2, xc2 = xc2, xn2
                            if xp2 == x0 and xc2 == x1:
                                print(f"  ⚠️ Also period {p}!")
                    
                    return {'found': True, 'x0': str(x0), 'x1': str(x1)}
    
    print("  No period-7 orbit found in re-scan!")
    return {'found': False}

run_experiment([
    ("Verify period-7 at c=-9/16", section_verify),
], timeout_sec=60)
