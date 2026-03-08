#!/usr/bin/env python3
"""
G16 Creative Method 2: Inverse map verification.

The Hénon map f_{c,b}(x,y) = (y, y^2+c+bx) has inverse
f^{-1}_{c,b}(x,y) = ((y - x^2 - c)/b, x)    [for b ≠ 0]

If (x0,x1) → (x1,x2) → (x2,x0) under f, then
(x2,x0) → (x1,x2) → (x0,x1) under f^{-1}.

This is a DIFFERENT way to verify the orbit: iterate the INVERSE map
and check that the orbit closes in 3 steps.
"""
import signal
signal.alarm(60)

from fractions import Fraction

def henon_forward(x, y, c, b):
    """f_{c,b}(x,y) = (y, y^2 + c + b*x)"""
    return y, y*y + c + b*x

def henon_inverse(x, y, c, b):
    """f^{-1}_{c,b}(x,y) = ((y - x^2 - c)/b, x)"""
    return (y - x*x - c) / b, x

def family_values(b):
    c = Fraction(-(29*b*b + 38*b + 29), 16)
    x0 = Fraction(-(5*b + 7), 4)
    x1 = Fraction(7*b + 5, 4)
    x2 = Fraction(b - 1, 4)
    return c, x0, x1, x2

print("G16 Method 2: Inverse map verification")
print()

# Test 50 rational values of b
test_values = []
for num in range(-20, 21):
    for den in [1, 2, 3, 5, 7]:
        b = Fraction(num, den)
        if b != -1:
            test_values.append(b)

# Deduplicate
test_values = sorted(set(test_values))
print(f"Testing {len(test_values)} values of b")

failures = 0
test_values = [b for b in test_values if b != 0]  # b=0 is non-invertible
for b in test_values:
    c, x0, x1, x2 = family_values(b)
    
    # Forward orbit: P0 → P1 → P2 → P0
    P0 = (x0, x1)
    P1 = henon_forward(*P0, c, b)
    P2 = henon_forward(*P1, c, b)
    P3 = henon_forward(*P2, c, b)
    
    # Check forward orbit closes
    fwd_ok = (P3[0] == P0[0] and P3[1] == P0[1])
    
    # Inverse orbit: P0 → f^{-1}(P0) should be P2 → f^{-1}(P2) should be P1
    Q1 = henon_inverse(*P0, c, b)
    Q2 = henon_inverse(*Q1, c, b)
    Q3 = henon_inverse(*Q2, c, b)
    
    # Check inverse orbit: Q1 = P2, Q2 = P1, Q3 = P0
    inv_ok = (Q1 == (x2, x0) and Q2 == (x1, x2) and Q3 == P0)
    
    if not fwd_ok or not inv_ok:
        print(f"  ❌ b={b}: forward={fwd_ok}, inverse={inv_ok}")
        failures += 1

print()
if failures == 0:
    print(f"✅ PASS: Forward AND inverse orbits verified for {len(test_values)} values of b.")
    print("   The orbit is a genuine period-3 cycle of the dynamical system,")
    print("   verified by BOTH f and f^{-1}.")
else:
    print(f"❌ FAIL: {failures} values had failures!")
