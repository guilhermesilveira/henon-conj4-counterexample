#!/usr/bin/env python3
"""
G16 Creative Method 1: Chinese Remainder Theorem modular verification.

Verify that the period-3 orbit identities hold mod p for 100 distinct primes.
If a polynomial identity holds mod p for enough primes, it must hold over Z
(since a nonzero polynomial of degree d has at most d roots mod p).

The three identities are polynomials of degree ≤ 4 in b, so if they hold
mod p for > 4 primes, they hold over Z[b] (and hence Q[b]).
"""
import signal
signal.alarm(60)

from fractions import Fraction

def henon_map_y(x, y, c, b):
    """Second component of f_{c,b}(x,y) = (y, y^2 + c + bx)"""
    return y*y + c + b*x

def family_values(b):
    """Return (c, x0, x1, x2) from the universal family."""
    c = -(29*b*b + 38*b + 29) * Fraction(1, 16)
    x0 = -(5*b + 7) * Fraction(1, 4)
    x1 = (7*b + 5) * Fraction(1, 4)
    x2 = (b - 1) * Fraction(1, 4)
    return c, x0, x1, x2

def check_mod_p(p):
    """Check all three orbit identities mod p for all b in Z/pZ, b != -1."""
    for b in range(p):
        if (b + 1) % p == 0:
            continue  # skip b = -1
        
        inv16 = pow(16, -1, p)
        c = (-(29*b*b + 38*b + 29) * inv16) % p
        
        inv4 = pow(4, -1, p)
        x0 = (-(5*b + 7) * inv4) % p
        x1 = ((7*b + 5) * inv4) % p
        x2 = ((b - 1) * inv4) % p
        
        # Check eq (3a): x1^2 + c + b*x0 = x2
        lhs1 = (x1*x1 + c + b*x0) % p
        if lhs1 != x2 % p:
            return False, f"Eq 3a fails: b={b}, lhs={lhs1}, rhs={x2 % p}"
        
        # Check eq (3b): x2^2 + c + b*x1 = x0
        lhs2 = (x2*x2 + c + b*x1) % p
        if lhs2 != x0 % p:
            return False, f"Eq 3b fails: b={b}, lhs={lhs2}, rhs={x0 % p}"
        
        # Check eq (3c): x0^2 + c + b*x2 = x1
        lhs3 = (x0*x0 + c + b*x2) % p
        if lhs3 != x1 % p:
            return False, f"Eq 3c fails: b={b}, lhs={lhs3}, rhs={x1 % p}"
    
    return True, "OK"

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

# Get first 100 primes > 2 (need odd primes for invertibility of 4 and 16)
primes = []
n = 3
while len(primes) < 100:
    if is_prime(n):
        primes.append(n)
    n += 2

print("G16 Method 1: CRT modular verification")
print(f"Testing {len(primes)} primes from {primes[0]} to {primes[-1]}")
print()

failures = 0
for i, p in enumerate(primes):
    ok, msg = check_mod_p(p)
    if not ok:
        print(f"  ❌ p={p}: {msg}")
        failures += 1
    elif (i+1) % 20 == 0:
        print(f"  ✓ primes up to {p} ({i+1}/{len(primes)}) all pass")

print()
if failures == 0:
    print(f"✅ PASS: All three orbit identities verified mod p for {len(primes)} primes.")
    print(f"   Since the identities are degree ≤ 4 in b and hold mod p for {len(primes)} primes,")
    print(f"   they hold as polynomial identities over Z (and hence Q).")
else:
    print(f"❌ FAIL: {failures} primes had failures!")
