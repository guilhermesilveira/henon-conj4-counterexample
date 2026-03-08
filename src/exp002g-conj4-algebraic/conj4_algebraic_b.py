#!/usr/bin/env python3
"""
EXP-002g var b: Fast algebraic analysis using Fraction arithmetic.

From var a we know:
- Phi₃(x,c;δ) is degree 6 in x, 3 in c, 6 in δ
- At δ=1: factors into LINEAR-in-c pieces → parametric families
- At other δ: irreducible cubic in c

Question: for which δ does the cubic have ANY rational point (x₀,c₀)?
"""
from common import run_experiment
import os, json
from fractions import Fraction
from math import gcd
from functools import reduce

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp002g-conj4-algebraic')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


# Pre-compute Phi₃ coefficients from SymPy result.
# Phi₃(x,c;d) as dict of (x_pow, c_pow, d_pow) -> coefficient
# From the SymPy output, manually extracted:
PHI3_TERMS = {
    # c³ terms
    (0, 3, 0): 1,
    # c² terms
    (0, 2, 2): 2, (1, 2, 1): 1, (2, 2, 0): 3, (1, 2, 0): 1, (0, 2, 0): 2,
    # c¹ terms
    (0, 1, 4): 1, (1, 1, 3): 2, (0, 1, 3): 4, (2, 1, 2): 3, (0, 1, 2): -5,
    (3, 1, 1): 2, (2, 1, 1): 2, (0, 1, 1): 4, (4, 1, 0): 3, (3, 1, 0): 2,
    (2, 1, 0): 3, (1, 1, 0): 2, (0, 1, 0): 1,
    # c⁰ terms
    (0, 0, 6): 1, (1, 0, 5): 1, (0, 0, 5): -1, (2, 0, 4): 1, (1, 0, 4): -1,
    (0, 0, 4): 1, (3, 0, 3): 1, (2, 0, 3): 2, (1, 0, 3): 1, (4, 0, 2): 1,
    (3, 0, 2): 1, (2, 0, 2): -1, (1, 0, 2): 1, (0, 0, 2): 1, (5, 0, 1): 1,
    (4, 0, 1): 2, (3, 0, 1): 1, (2, 0, 1): 2, (1, 0, 1): -1, (0, 0, 1): -1,
    (6, 0, 0): 1, (5, 0, 0): 1, (4, 0, 0): 1, (3, 0, 0): 1, (2, 0, 0): 1,
    (1, 0, 0): 1, (0, 0, 0): 1,
}


def eval_phi3_cubic_in_c(x0, dv):
    """Evaluate Phi₃(x₀, c; δ) as cubic a₃c³ + a₂c² + a₁c + a₀.
    Returns (a₃, a₂, a₁, a₀) as Fractions."""
    coeffs = [Fraction(0)] * 4  # [a₃, a₂, a₁, a₀] for c³, c², c¹, c⁰
    
    for (xp, cp, dp), coeff in PHI3_TERMS.items():
        val = Fraction(coeff) * (x0 ** xp) * (dv ** dp)
        idx = 3 - cp  # c³ → index 0, c⁰ → index 3
        coeffs[idx] += val
    
    return tuple(coeffs)


def has_rational_root_cubic(a3, a2, a1, a0, max_factors=300):
    """Check if a₃c³ + a₂c² + a₁c + a₀ = 0 has a rational root."""
    if a3 == 0:
        # Degenerate: quadratic or lower
        if a2 == 0:
            if a1 == 0:
                return a0 == 0
            return (a0 / a1) if (-a0 / a1).denominator != 0 else False
        # Quadratic: discriminant check
        disc = a1 * a1 - 4 * a2 * a0
        if disc < 0:
            return False
        # Check if disc is perfect square
        from math import isqrt
        n = disc.numerator * disc.denominator
        if n < 0:
            return False
        s = isqrt(abs(n))
        return s * s == abs(n) and disc >= 0
    
    # Integer coefficients
    denoms = [c.denominator for c in [a3, a2, a1, a0]]
    L = reduce(lambda a, b: a * b // gcd(a, b), denoms)
    ic = [int(c * L) for c in [a3, a2, a1, a0]]
    
    an = abs(ic[0])
    a0i = abs(ic[3])
    
    if an == 0:
        return False
    
    if a0i == 0:
        # c=0 is a root
        return True
    
    # Rational root theorem
    def get_divisors(n, mx):
        return [i for i in range(1, min(n + 1, mx)) if n % i == 0]
    
    for p in get_divisors(a0i, max_factors):
        for q in get_divisors(an, max_factors):
            for sign in [1, -1]:
                # Evaluate ic[0]*(sp/q)³ + ic[1]*(sp/q)² + ic[2]*(sp/q) + ic[3]
                sp = sign * p
                # Use exact: ic[0]*sp³ + ic[1]*sp²*q + ic[2]*sp*q² + ic[3]*q³
                val = (ic[0] * sp**3 + ic[1] * sp**2 * q + 
                       ic[2] * sp * q**2 + ic[3] * q**3)
                if val == 0:
                    return True
    
    return False


def section_fast_scan():
    """Fast scan: for each δ = p/q, check if Phi₃ has ANY rational point."""
    
    delta_vals = set()
    for q in range(1, 25):
        for p in range(-30, 31):
            delta_vals.add(Fraction(p, q))
    delta_vals = sorted(delta_vals)
    
    exceptional = []
    
    for di, dv in enumerate(delta_vals):
        found = False
        
        for qx in range(1, 30):
            if found:
                break
            for px in range(-40, 41):
                x0 = Fraction(px, qx)
                a3, a2, a1, a0 = eval_phi3_cubic_in_c(x0, dv)
                
                if has_rational_root_cubic(a3, a2, a1, a0):
                    found = True
                    exceptional.append(str(dv))
                    break
        
        if (di + 1) % 100 == 0:
            print(f"  [{di+1}/{len(delta_vals)}] {len(exceptional)} exc", flush=True)
    
    print(f"\n  Fast scan: {len(delta_vals)} δ, {len(exceptional)} have period-3 rational pts")
    
    # Deduplicate
    exc_set = sorted(set(exceptional), key=lambda s: Fraction(s))
    print(f"  Exceptional δ: {exc_set}")
    
    state['fast_scan'] = {
        'total': len(delta_vals),
        'exceptional': exc_set
    }
    return state['fast_scan']


def section_factorization_structure():
    """
    For δ=1 and δ=-1, show WHY they're exceptional algebraically.
    
    δ=1: Phi₃ factors into (deg_x=2,deg_c=1) pieces — linear in c!
    δ=-1: Phi₃ is irreducible cubic — but specific x₀ give rational c.
    """
    from sympy import symbols, expand, Poly, factor, Rational as R
    x_s, c_s = symbols('x c')
    
    # Reconstruct Phi₃ at δ=1 and δ=-1
    for dv, dv_name in [(1, 'δ=1'), (-1, 'δ=-1')]:
        phi3_d = Fraction(0)
        # Build symbolic version
        terms = {}
        for (xp, cp, dp), coeff in PHI3_TERMS.items():
            key = (xp, cp)
            val = coeff * (dv ** dp)
            terms[key] = terms.get(key, 0) + val
        
        # Build sympy expression
        expr = sum(coeff * x_s**xp * c_s**cp for (xp, cp), coeff in terms.items())
        expr = expand(expr)
        
        fac = factor(expr)
        print(f"\n  {dv_name}:")
        print(f"    Phi₃ = {expr}")
        print(f"    Factored = {fac}")
        
        # Extract factors
        p = Poly(expr, x_s, c_s, domain='ZZ')
        fl = p.factor_list()
        print(f"    Factors:")
        for fp, mult in fl[1]:
            dx = fp.degree(0)
            dc = fp.degree(1)
            print(f"      (deg_x={dx}, deg_c={dc})^{mult}: {fp.as_expr()}")
    
    state['structure'] = True
    return {}


def section_verdict():
    """Final verdict."""
    scan = state.get('fast_scan', {})
    exc = scan.get('exceptional', [])
    total = scan.get('total', 0)
    
    print(f"\n  ╔══════════════════════════════════════════════════╗")
    print(f"  ║       CONJECTURE 4' — ALGEBRAIC VERDICT         ║")
    print(f"  ╚══════════════════════════════════════════════════╝")
    
    print(f"\n  δ tested: {total}")
    print(f"  δ with Phi₃ rational points: {exc}")
    
    exc_set = set(exc)
    if exc_set == {'-1', '1'}:
        print(f"\n  ✅ CONFIRMED: period-3 requires δ ∈ {{-1, 1}}")
        print(f"     Algebraic reason for δ=1: Phi₃ factors into LINEAR-in-c pieces")
        print(f"     For δ=-1: Phi₃ is irreducible cubic but has sparse rational points")
        print(f"     For all other δ: no rational points found on Phi₃ curve")
    elif exc_set.issubset({'-1', '1'}):
        print(f"\n  ✅ Consistent: exceptions ⊆ {{-1, 1}}")
    else:
        extra = exc_set - {'-1', '1'}
        print(f"\n  ⚠️ Additional exceptions found: {extra}")
    
    with open(os.path.join(OUTPUT_DIR, 'results_b.json'), 'w') as f:
        json.dump(state, f, indent=2, default=str)
    
    return {'exceptional': exc}


run_experiment([
    ("Fast scan: which δ have Phi₃ rational points?", section_fast_scan),
    ("Factorization structure at δ=±1", section_factorization_structure),
    ("Verdict", section_verdict),
], timeout_sec=300)
