#!/usr/bin/env python3
"""
G16 Creative Method 4: Dynatomic polynomial verification.

The primitive period-3 dynatomic polynomial Φ₃(x₀, c; b) is the polynomial
whose roots are the x-coordinates of primitive period-3 orbits.

We verify that x₀ from the universal family is a root of Φ₃ when c = c(b).
This uses a COMPLETELY DIFFERENT algebraic object (the dynatomic polynomial)
rather than directly checking the recurrence.
"""
import signal
signal.alarm(60)

from sympy import symbols, expand, factor, resultant, Poly, ZZ

b_sym, c_sym, x0, x1, x2 = symbols('b c x0 x1 x2')

print("G16 Method 4: Dynatomic polynomial verification")
print()

# Step 1: Build the period-3 system
print("Step 1: Building period-3 equations...")
eq1 = x1**2 + c_sym + b_sym*x0 - x2   # x2 = x1^2 + c + b*x0
eq2 = x2**2 + c_sym + b_sym*x1 - x0   # x0 = x2^2 + c + b*x1
eq3 = x0**2 + c_sym + b_sym*x2 - x1   # x1 = x0^2 + c + b*x2

# Step 2: Eliminate x2 from eq1 and eq2
print("Step 2: Eliminating x₂...")
# From eq1: x2 = x1^2 + c + b*x0
x2_expr = x1**2 + c_sym + b_sym*x0
eq2_sub = eq2.subs(x2, x2_expr)
eq3_sub = eq3.subs(x2, x2_expr)

# Step 3: Eliminate x1 from eq2_sub and eq3_sub via resultant
print("Step 3: Computing resultant to eliminate x₁...")
R = resultant(expand(eq2_sub), expand(eq3_sub), x1)
R = expand(R)
print(f"  Resultant degree in x₀: {Poly(R, x0).degree()}")
print(f"  Resultant degree in c: {Poly(R, c_sym).degree()}")

# Step 4: Factor out the fixed-point curve c + x0^2 + x0*(b-1)
# Fixed points satisfy x1 = x0, so: x0 = x0^2 + c + b*x0 → c = -x0^2 - x0*(b-1)
# Actually for the Henon map fixed point: f(x,y)=(x,y) means y=x and y^2+c+bx=y
# So x^2 + c + bx = x → c = -x^2 - (b-1)x → c + x^2 + (b-1)x = 0
print("Step 4: Factoring out fixed-point component...")
fp_factor = c_sym + x0**2 + (b_sym - 1)*x0
q, r = Poly(R, c_sym, x0, b_sym).div(Poly(fp_factor, c_sym, x0, b_sym))
r_expr = r.as_expr()
print(f"  Remainder after dividing by fixed-point factor: {expand(r_expr)}")

if expand(r_expr) != 0:
    # Try repeated exact division
    R_current = R
    k = 0
    while True:
        q2, r2 = Poly(R_current, c_sym, x0, b_sym).div(Poly(fp_factor, c_sym, x0, b_sym))
        if expand(r2.as_expr()) == 0:
            k += 1
            R_current = expand(q2.as_expr())
        else:
            break
    print(f"  Fixed-point factor appears with multiplicity {k}")
    Phi3 = R_current
else:
    Phi3 = expand(q.as_expr())

# Step 5: Substitute the universal family
print("Step 5: Substituting universal family into Φ₃...")
c_fam = -(29*b_sym**2 + 38*b_sym + 29) / 16
x0_fam = -(5*b_sym + 7) / 4

val = Phi3.subs([(x0, x0_fam), (c_sym, c_fam)])
val_expanded = expand(val)
print(f"  Φ₃(x₀(b), c(b); b) = {val_expanded}")

if val_expanded == 0:
    print()
    print("✅ PASS: x₀ from the universal family is a root of the dynatomic")
    print("   polynomial Φ₃. This confirms the orbit via a completely different")
    print("   algebraic object than the direct recurrence check.")
else:
    print()
    print(f"❌ FAIL: Φ₃(x₀(b), c(b); b) = {val_expanded} ≠ 0")
