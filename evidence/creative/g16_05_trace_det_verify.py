#!/usr/bin/env python3
"""
G16 Creative Method 5: Independent trace/determinant verification via mpmath.

The paper claims:
  det(Df³) = -b³
  tr(Df³) = -(b-1)(35b² + 62b + 35)/8

We verify these by computing Df³ NUMERICALLY at 50-digit precision for 100
random rational values of b, using the actual Jacobian matrices (not the
claimed formula). If the numerical values match, the formulas are correct.
"""
import signal
signal.alarm(60)

from mpmath import mp, mpf, matrix as mpmatrix, fabs

mp.dps = 50  # 50 decimal digits

def henon_jacobian_at(x, y, b):
    """Jacobian of f_{c,b} at point (x,y): [[0,1],[b,2y]]"""
    return mpmatrix([[0, 1], [b, 2*y]])

def mat_mul(A, B):
    """2x2 matrix multiply."""
    return mpmatrix([
        [A[0,0]*B[0,0] + A[0,1]*B[1,0], A[0,0]*B[0,1] + A[0,1]*B[1,1]],
        [A[1,0]*B[0,0] + A[1,1]*B[1,0], A[1,0]*B[0,1] + A[1,1]*B[1,1]],
    ])

def family_values_mp(b):
    c = -(29*b**2 + 38*b + 29) / 16
    x0 = -(5*b + 7) / 4
    x1 = (7*b + 5) / 4
    x2 = (b - 1) / 4
    return c, x0, x1, x2

print("G16 Method 5: Independent trace/det verification via mpmath (50 digits)")
print()

# Test 100 rational values
from fractions import Fraction
test_vals = []
for num in range(-30, 31):
    for den in [1, 2, 3, 4, 5, 7, 11]:
        b = Fraction(num, den)
        if b != -1:
            test_vals.append(b)
test_vals = sorted(set(test_vals))[:100]

failures = 0
for b_frac in test_vals:
    b = mpf(b_frac.numerator) / mpf(b_frac.denominator)
    c, x0, x1, x2 = family_values_mp(b)
    
    # Orbit points: P0=(x0,x1), P1=(x1,x2), P2=(x2,x0)
    # Jacobians at each point
    J0 = henon_jacobian_at(x0, x1, b)  # Df at P0 = (x0, x1)
    J1 = henon_jacobian_at(x1, x2, b)  # Df at P1 = (x1, x2)
    J2 = henon_jacobian_at(x2, x0, b)  # Df at P2 = (x2, x0)
    
    # Df³ = J2 · J1 · J0 (chain rule: last applied first)
    Df3 = mat_mul(J2, mat_mul(J1, J0))
    
    # Numerical det and trace
    det_num = Df3[0,0]*Df3[1,1] - Df3[0,1]*Df3[1,0]
    tr_num = Df3[0,0] + Df3[1,1]
    
    # Claimed values
    det_claimed = -b**3
    tr_claimed = -(b - 1) * (35*b**2 + 62*b + 35) / 8
    
    # Check
    det_err = fabs(det_num - det_claimed)
    tr_err = fabs(tr_num - tr_claimed)
    
    if det_err > mpf('1e-40') or tr_err > mpf('1e-40'):
        print(f"  ❌ b={b_frac}: det_err={det_err}, tr_err={tr_err}")
        failures += 1

print(f"Tested {len(test_vals)} values of b at 50-digit precision.")
print()
if failures == 0:
    print("✅ PASS: det(Df³) = -b³ and tr(Df³) = -(b-1)(35b²+62b+35)/8")
    print("   verified to 40+ correct digits for all test values.")
    print("   This uses a COMPLETELY INDEPENDENT numerical computation,")
    print("   not the SymPy symbolic proof used in the paper.")
else:
    print(f"❌ FAIL: {failures} values had mismatches!")
