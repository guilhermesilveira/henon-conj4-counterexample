#!/usr/bin/env python3
"""
G16 Creative Method 6: Verify Table 1 entries independently.

The paper has a Table 1 with 11 specific orbits. Verify each one by:
1. Computing the orbit from the family formula
2. Actually iterating the Hénon map and checking it returns to start
3. Checking primitivity (not a fixed point)
4. Verifying the table entries match the formulas exactly
"""
import signal
signal.alarm(30)

from fractions import Fraction

def henon_f(x, y, c, b):
    return y, y*y + c + b*x

def family(b):
    c = Fraction(-(29*b*b + 38*b + 29), 16)
    x0 = Fraction(-(5*b + 7), 4)
    x1 = Fraction(7*b + 5, 4)
    x2 = Fraction(b - 1, 4)
    return c, x0, x1, x2

# Table 1 entries from the paper
# (b, c, x0, x1, x2, note)
table_entries = [
    (Fraction(-10), Fraction(-2549, 16), Fraction(43, 4), Fraction(-65, 4), Fraction(-11, 4), "b=-10"),
    (Fraction(-5), Fraction(-141, 4), Fraction(9, 2), Fraction(-15, 2), Fraction(-3, 2), "b=-5"),
    (Fraction(-2), Fraction(-69, 16), Fraction(3, 4), Fraction(-9, 4), Fraction(-3, 4), "b=-2"),
    (Fraction(0), Fraction(-29, 16), Fraction(-7, 4), Fraction(5, 4), Fraction(-1, 4), "b=0"),
    (Fraction(1), Fraction(-6), Fraction(-3), Fraction(3), Fraction(0), "b=1"),
    (Fraction(2), Fraction(-221, 16), Fraction(-17, 4), Fraction(19, 4), Fraction(1, 4), "b=2"),
    (Fraction(5), Fraction(-59), Fraction(-8), Fraction(10), Fraction(1), "b=5"),
    (Fraction(10), Fraction(-3309, 16), Fraction(-57, 4), Fraction(75, 4), Fraction(9, 4), "b=10"),
    (Fraction(1, 2), Fraction(-221, 64), Fraction(-19, 8), Fraction(17, 8), Fraction(-1, 8), "b=1/2"),
    (Fraction(3, 7), Fraction(-155, 49), Fraction(-16, 7), Fraction(2), Fraction(-1, 7), "b=3/7"),
    (Fraction(-17, 5), Fraction(-1469, 100), Fraction(5, 2), Fraction(-47, 10), Fraction(-11, 10), "b=-17/5"),
]

print("G16 Method 6: Verify Table 1 entries")
print()

failures = 0
for b, c_tab, x0_tab, x1_tab, x2_tab, note in table_entries:
    # 1. Compute from formula
    c_form, x0_form, x1_form, x2_form = family(b)
    
    # 2. Check formula matches table
    formula_ok = (c_form == c_tab and x0_form == x0_tab and 
                  x1_form == x1_tab and x2_form == x2_tab)
    
    # 3. Iterate map
    P0 = (x0_tab, x1_tab)
    P1 = henon_f(*P0, c_tab, b)
    P2 = henon_f(*P1, c_tab, b)
    P3 = henon_f(*P2, c_tab, b)
    
    orbit_ok = (P3 == P0)
    prim_ok = (P1 != P0)  # not a fixed point
    
    # 4. Check orbit points match table
    points_ok = (P1 == (x1_tab, x2_tab) and P2 == (x2_tab, x0_tab))
    
    if formula_ok and orbit_ok and prim_ok and points_ok:
        print(f"  ✓ {note}: formula={formula_ok}, orbit={orbit_ok}, primitive={prim_ok}")
    else:
        print(f"  ❌ {note}: formula={formula_ok}, orbit={orbit_ok}, primitive={prim_ok}, points={points_ok}")
        if not formula_ok:
            print(f"    Table: c={c_tab}, x0={x0_tab}, x1={x1_tab}, x2={x2_tab}")
            print(f"    Formula: c={c_form}, x0={x0_form}, x1={x1_form}, x2={x2_form}")
        failures += 1

print()
if failures == 0:
    print(f"✅ PASS: All {len(table_entries)} Table 1 entries verified:")
    print("   - Formula matches table values exactly")
    print("   - Orbit closes after 3 iterations")
    print("   - Orbit is primitive (not a fixed point)")
    print("   - Intermediate orbit points match")
else:
    print(f"❌ FAIL: {failures} table entries had problems!")
