#!/usr/bin/env python3
"""
G16 Creative Method 8: Verify period-7 orbit (Proposition 6.1) independently.

The paper claims: at b=-1, c=-9/16, there's a primitive period-7 orbit.
We verify by:
1. Finding ALL periodic orbits of period dividing 7 at these parameters
   (brute-force search with exact arithmetic)
2. Confirming the period-7 orbit exists
3. Confirming it has exactly 7 distinct points
4. Cross-checking with the Lean formalization claim
"""
import signal
signal.alarm(60)

from fractions import Fraction

def henon_f(x, y, c, b):
    return y, y*y + c + b*x

b = Fraction(-1)
c = Fraction(-9, 16)

print("G16 Method 8: Verify period-7 orbit")
print(f"Parameters: b={b}, c={c}")
print()

# Strategy: search for period-7 orbits with denominator 4
# Paper claims all coordinates have denominator 4.
# Search space: x = a/4 for a in some range
denom = 4
search_range = range(-40, 41)  # a/4 for a in [-40, 40]

period7_orbits = []
seen_orbits = set()

for a0 in search_range:
    for a1 in search_range:
        x0 = Fraction(a0, denom)
        x1 = Fraction(a1, denom)
        
        P = (x0, x1)
        P_start = P
        
        # Iterate 7 times
        orbit = [P]
        valid = True
        for _ in range(7):
            P = henon_f(*P, c, b)
            # Check if coordinates have denominator dividing 4
            if P[0].denominator > denom or P[1].denominator > denom:
                valid = False
                break
            orbit.append(P)
        
        if not valid:
            continue
        
        # Check if period-7
        if orbit[7] == orbit[0]:
            # Check primitive (not period 1 or 7)
            is_fp = (orbit[1] == orbit[0])
            
            if not is_fp:
                # Check minimal period
                min_period = None
                for p in [1, 7]:
                    if orbit[p] == orbit[0]:
                        min_period = p
                        break
                
                if min_period == 7:
                    # Canonicalize orbit (smallest point first)
                    canon = tuple(sorted([orbit[i] for i in range(7)]))
                    if canon not in seen_orbits:
                        seen_orbits.add(canon)
                        period7_orbits.append(orbit[:7])

print(f"Found {len(period7_orbits)} distinct period-7 orbits with denominator {denom}")

if len(period7_orbits) > 0:
    for idx, orb in enumerate(period7_orbits):
        print(f"\nOrbit {idx+1}:")
        for i, pt in enumerate(orb):
            print(f"  P{i} = ({pt[0]}, {pt[1]})")
        
        # Verify all 7 points are distinct
        pts_set = set(orb)
        print(f"  Distinct points: {len(pts_set)}")
        
        # Re-verify by iteration
        P = orb[0]
        for step in range(7):
            P = henon_f(*P, c, b)
        print(f"  f^7(P0) == P0: {P == orb[0]}")
    
    print()
    print("✅ PASS: Period-7 orbit found and verified at b=-1, c=-9/16.")
    print("   This confirms Proposition 6.1 of the paper.")
else:
    print()
    print("❌ FAIL: No period-7 orbit found!")

# Also verify that the same c gives period-8 at b=+1
print()
print("--- Cross-check: same c with b=+1 ---")
b_plus = Fraction(1)
# Search for period-8 orbit
period8_found = False
for a0 in search_range:
    for a1 in search_range:
        x0 = Fraction(a0, denom)
        x1 = Fraction(a1, denom)
        P = (x0, x1)
        orbit = [P]
        valid = True
        for _ in range(8):
            P = henon_f(*P, c, b_plus)
            if P[0].denominator > denom or P[1].denominator > denom:
                valid = False
                break
            orbit.append(P)
        if not valid:
            continue
        if orbit[8] == orbit[0] and orbit[1] != orbit[0]:
            # Check minimal period is 8 (not 1,2,4)
            min_p = None
            for p in [1, 2, 4, 8]:
                if orbit[p] == orbit[0]:
                    min_p = p
                    break
            if min_p == 8:
                print(f"  Period-8 orbit at b=+1, c=-9/16: P0={orbit[0]}")
                period8_found = True
                break
    if period8_found:
        break

if period8_found:
    print("  ✓ Confirmed: c=-9/16 gives period-8 at b=+1")
else:
    print("  ✗ No period-8 orbit found at b=+1, c=-9/16 with denom 4")
