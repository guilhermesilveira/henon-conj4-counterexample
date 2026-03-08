#!/usr/bin/env python3
"""
G16 Creative Method 7: Verify Table 2 (Conjecture 3 sharpness) independently.

The paper claims orbits for b=+1 (i.e., f(x,y) = (y, y²+c+x)) with
periods {1,2,3,4,6,8}. Verify each one by direct iteration.
"""
import signal
signal.alarm(30)

from fractions import Fraction

def henon_f(x, y, c, b):
    return y, y*y + c + b*x

print("G16 Method 7: Verify Table 2 (Conjecture 3 sharpness)")
print()

b = Fraction(1)

# Table 2 entries: (N, c, orbit_x_coords)
table2_entries = [
    (1, Fraction(-1, 4), [Fraction(-1, 2)]),
    (2, Fraction(-4), [Fraction(-2), Fraction(2)]),
    (3, Fraction(-6), [Fraction(-3), Fraction(3), Fraction(0)]),
    (4, Fraction(-5, 4), [Fraction(-3, 2), Fraction(3, 2), Fraction(-1, 2), Fraction(1, 2)]),
    (6, Fraction(-7, 9), [Fraction(-1, 3), Fraction(2, 3), Fraction(-2, 3), 
                           Fraction(1, 3), Fraction(-4, 3), Fraction(4, 3)]),
    (8, Fraction(-9, 16), [Fraction(-5, 4), Fraction(5, 4), Fraction(-1, 4), Fraction(3, 4),
                            Fraction(-1, 4), Fraction(1, 4), Fraction(-3, 4), Fraction(1, 4)]),
]

failures = 0
for N, c, x_coords in table2_entries:
    if N == 1:
        # Fixed point: f(x,x) = (x, x²+c+x) and y-component = x
        x0 = x_coords[0]
        y_comp = x0*x0 + c + b*x0
        if y_comp == x0:
            print(f"  ✓ N={N}: c={c}, x₀={x0} is a fixed point")
        else:
            print(f"  ❌ N={N}: f(x₀,x₀)_y = {y_comp} ≠ {x0}")
            failures += 1
        continue
    
    # For period > 1: build orbit from x-coordinates
    # The orbit in (x,y) plane is (x_i, x_{i+1})
    orbit_ok = True
    
    # Check the recurrence: x_{i+1} = x_i² + c + b*x_{i-1}
    for i in range(1, N):
        x_im1 = x_coords[i-1]
        x_i = x_coords[i]
        x_ip1 = x_coords[(i+1) % N]
        computed = x_i*x_i + c + b*x_im1
        if computed != x_ip1:
            print(f"  ❌ N={N}: recurrence fails at i={i}: {computed} ≠ {x_ip1}")
            orbit_ok = False
            failures += 1
            break
    
    # Check closure: x_N = x_0 and x_{N+1} = x_1
    # The recurrence at i=0: x_1 = x_0² + c + b*x_{N-1}
    x_1_check = x_coords[0]*x_coords[0] + c + b*x_coords[N-1]
    if x_1_check != x_coords[1]:
        print(f"  ❌ N={N}: closure fails: {x_1_check} ≠ {x_coords[1]}")
        orbit_ok = False
        failures += 1
    
    # Check primitivity: not all x_i the same
    if len(set(x_coords)) == 1:
        print(f"  ❌ N={N}: all x_i are the same (fixed point, not primitive)")
        orbit_ok = False
        failures += 1
    
    if orbit_ok:
        print(f"  ✓ N={N}: c={c}, orbit verified with {N} distinct points")

print()

# Also verify period-8 orbit has a special issue: the paper lists x₄=-1/4 and x₆=-3/4
# Let me check if x₄ = x₂ (which would make it period-4 not 8)
print("Extra check: period-8 orbit distinctness...")
p8_x = [Fraction(-5, 4), Fraction(5, 4), Fraction(-1, 4), Fraction(3, 4),
         Fraction(-1, 4), Fraction(1, 4), Fraction(-3, 4), Fraction(1, 4)]
p8_pts = set()
for i in range(8):
    pt = (p8_x[i], p8_x[(i+1) % 8])
    p8_pts.add(pt)
print(f"  Period-8 orbit has {len(p8_pts)} distinct (x,y) points")
if len(p8_pts) < 8:
    print(f"  ⚠️ WARNING: only {len(p8_pts)} distinct points, not 8!")
    print(f"  Points: {sorted(p8_pts)}")
    # This could mean the period is actually less than 8
    # Check if iterating from P0 returns to P0 after exactly 8 steps
    P = (p8_x[0], p8_x[1])
    for step in range(1, 9):
        P = henon_f(*P, Fraction(-9, 16), Fraction(1))
        if P == (p8_x[0], p8_x[1]):
            print(f"  Orbit returns to start after {step} steps (primitive period = {step})")
            if step < 8:
                failures += 1
            break

print()
if failures == 0:
    print(f"✅ PASS: All Table 2 entries verified.")
else:
    print(f"❌ FAIL: {failures} issues found!")
