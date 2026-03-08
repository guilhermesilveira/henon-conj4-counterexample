#!/usr/bin/env python3
"""
ONE-LINE VERIFICATION: Conjecture 4 (Ingram, BIRS 2023) is FALSE.

Conjecture 4 claims: "For all but FINITELY MANY δ ∈ ℚ, rational periodic 
points of f(x,y) = (y, y²+c−δx) have period dividing 2."

COUNTEREXAMPLE: For EVERY odd integer δ = -(2k+1), the map has period 3.

    x₀ = -(5k+6)/2,  x₁ = (7k+6)/2,  x₂ = k/2
    c  = -(29k²+48k+24)/4

Run this script:  python3 verify_one_line.py
"""
from fractions import Fraction

print("Conjecture 4 (Ingram, BIRS 2023): COUNTEREXAMPLE")
print("=" * 55)
print()

for k in range(-10, 11):
    if k == -1:  # degenerate case; δ=1 has its own family
        continue
    
    delta = -(2*k + 1)
    x0 = Fraction(-(5*k + 6), 2)
    x1 = Fraction(7*k + 6, 2)
    x2 = Fraction(k, 2)
    c  = Fraction(-(29*k**2 + 48*k + 24), 4)
    
    # Verify period-3: apply f three times
    # f(x,y) = (y, y² + c - δ·x)
    y0, y1 = x0, x1
    y2 = y1**2 + c - delta * y0   # should = x2
    y3 = y2**2 + c - delta * y1   # should = x0
    y4 = y3**2 + c - delta * y2   # should = x1
    
    assert y2 == x2, f"FAIL at k={k}"
    assert y3 == x0, f"FAIL at k={k}"
    assert y4 == x1, f"FAIL at k={k}"
    assert x0 != x1, f"degenerate at k={k}"
    
    print(f"  δ = {delta:>4}  (k={k:>3})  c = {str(c):>12}  "
          f"orbit = ({x0}, {x1}, {x2})  ✓ period 3")

print()
print(f"All 20 values verified. QED: infinitely many exceptional δ exist.")
print(f"Conjecture 4 is FALSE.")
