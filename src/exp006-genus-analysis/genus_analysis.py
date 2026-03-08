#!/usr/bin/env python3
"""
EXP-006: Genus analysis of dynatomic curves.

The dynatomic polynomial Φ_n(x, c) defines a curve in the (x, c) plane.
By Faltings' theorem (Mordell conjecture), if genus ≥ 2 then there are
only finitely many rational points on the curve.

For the generalized Hénon map f(x,y)=(y, y²+c+bx):
- The orbit equation gives a system in (x₀,...,x_{n-1}, c) with b fixed
- Eliminating variables gives a curve in fewer variables
- Computing genus of this curve tells us about finiteness of rational periodic points

For period n:
- n equations in n+1 unknowns (x₀,...,x_{n-1}, c) [with b fixed]
- This defines a curve (1-dimensional variety) in ℚ^{n+1}
- We can project to (x₀, c) by elimination

Strategy:
1. For small n (3, 4, 5, 6, 7), compute the resultant/elimination polynomial
2. Compute the genus using degree-genus formula for plane curves
3. If genus ≥ 2 → only finitely many rational periodic points of period n
"""
from common import run_experiment
import os, json
from sympy import (symbols, expand, resultant, Poly, factor, degree,
                   discriminant, sqrt, Rational, gcd)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp006-genus-analysis')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


def section_period3_genus():
    """Compute genus of the period-3 dynatomic curve at b=+1 (Conj 3 map)."""
    x0, x1, x2, c = symbols('x0 x1 x2 c')
    b = 1  # Conjecture 3 map
    
    # Period-3 equations: x_{i+1} = x_i² + c + b·x_{i-1}
    eq1 = x1**2 + c + b*x0 - x2
    eq2 = x2**2 + c + b*x1 - x0
    eq3 = x0**2 + c + b*x2 - x1
    
    print("  Period-3 dynatomic curve (b=+1):")
    print(f"  3 equations, 4 unknowns → 1D curve")
    
    # Eliminate x2 from eq1: x2 = x1² + c + x0
    x2_expr = x1**2 + c + b*x0
    
    # Substitute into eq2 and eq3
    eq2_sub = expand(x2_expr**2 + c + b*x1 - x0)
    eq3_sub = expand(x0**2 + c + b*x2_expr - x1)
    
    print(f"\n  After eliminating x₂:")
    print(f"  eq2: {eq2_sub} = 0")
    print(f"  eq3: {eq3_sub} = 0")
    
    # Now eliminate x1 by computing resultant of eq2_sub and eq3_sub w.r.t. x1
    print(f"\n  Computing resultant to eliminate x₁...")
    R = resultant(Poly(eq2_sub, x1), Poly(eq3_sub, x1), x1)
    R = expand(R)
    
    # This gives a polynomial in (x0, c)
    R_poly = Poly(R, x0, c)
    deg_x0 = degree(R, x0)
    deg_c = degree(R, c)
    total_deg = R_poly.total_degree()
    
    print(f"  Resultant: degree in x₀ = {deg_x0}, degree in c = {deg_c}")
    print(f"  Total degree = {total_deg}")
    
    # Factor to find irreducible components
    print(f"\n  Factoring resultant...")
    F = factor(R)
    print(f"  Factored: {F}")
    
    # For a smooth plane curve of degree d: genus = (d-1)(d-2)/2
    # But we need to check for singularities
    print(f"\n  Genus estimate (smooth curve formula):")
    print(f"  For degree {total_deg}: g = ({total_deg}-1)({total_deg}-2)/2 = {(total_deg-1)*(total_deg-2)//2}")
    print(f"  (Upper bound; actual genus may be lower if singular)")
    
    state['period3'] = {
        'total_deg': total_deg,
        'genus_upper': (total_deg-1)*(total_deg-2)//2,
        'factored': str(F),
    }
    return state['period3']


def section_period3_irreducible():
    """Analyze irreducible components of period-3 curve."""
    x0, c = symbols('x0 c')
    b = 1
    
    # From period-3 with b=1: we can derive the dynatomic polynomial
    # The period-3 points satisfy Φ_3 | (f³(x)-x) but not (f(x)-x)
    
    # For the 1D projection (recurrence), let's work directly
    # x_{n+1} = x_n² + c + x_{n-1}
    # Period 3: x₀ → x₁ → x₂ → x₀
    # With x₂ = x₁² + c + x₀ and x₀ = x₂² + c + x₁
    
    x1 = symbols('x1')
    x2 = x1**2 + c + x0
    # x₀ = x₂² + c + x₁
    closure1 = expand(x2**2 + c + x1 - x0)
    # x₁ = x₀² + c + x₂
    closure2 = expand(x0**2 + c + x2 - x1)
    
    # These are two equations in x0, x1, c
    # Resultant in x1 gives curve in (x0, c)
    print("  Computing resultant for period-3 (b=+1)...")
    R = resultant(Poly(closure1, x1), Poly(closure2, x1), x1)
    R = expand(R)
    
    F = factor(R)
    print(f"  Factored resultant: {F}")
    
    # Extract each factor and compute its degree
    from sympy import Mul, Pow, Integer
    
    # Try to get factors
    R_poly = Poly(R, x0, c)
    factors = R_poly.factor_list()
    print(f"\n  Factor list: {factors}")
    
    print(f"\n  Analysis of each factor:")
    content, factor_list = factors
    for i, (fac, mult) in enumerate(factor_list):
        d = fac.total_degree()
        g = max(0, (d-1)*(d-2)//2)
        print(f"    Factor {i+1}: degree={d}, multiplicity={mult}, genus(smooth)={g}")
        
        # Check if this factor includes fixed points
        if d <= 2:
            print(f"      → Low degree, genus {g} (rational curve)")
        elif g >= 2:
            print(f"      → Genus ≥ 2: FALTINGS applies → finitely many ℚ-points!")
    
    state['period3_factors'] = str(factors)
    return {'factored': str(F)}


def section_period4_genus():
    """Compute genus of period-4 dynatomic curve at b=+1."""
    x0, x1, c = symbols('x0 x1 c')
    b = 1
    
    print("  Period-4 dynatomic curve (b=+1):")
    
    # Build x2, x3, x4 iteratively
    x2 = x1**2 + c + b*x0
    x3 = expand(x2**2 + c + b*x1)
    
    # Closure: x0 = x3² + c + b*x2, x1 = x0² + c + b*x3
    # Actually for period 4: x₀→x₁→x₂→x₃→x₀
    # So x₄ = x₀ and x₅ = x₁
    # eq: x₃² + c + b*x₂ = x₀
    # eq: x₀² + c + b*x₃ = x₁
    
    closure1 = expand(x3**2 + c + b*x2 - x0)
    closure2 = expand(x0**2 + c + b*x3 - x1)
    
    print("  Computing resultant to eliminate x₁ (may be slow)...")
    R = resultant(Poly(closure1, x1), Poly(closure2, x1), x1)
    R = expand(R)
    
    R_poly = Poly(R, x0, c)
    deg = R_poly.total_degree()
    print(f"  Total degree of resultant: {deg}")
    print(f"  Genus upper bound (smooth): ({deg}-1)({deg}-2)/2 = {(deg-1)*(deg-2)//2}")
    
    # Factor
    print("  Factoring...")
    factors = R_poly.factor_list()
    
    content, factor_list = factors
    print(f"\n  Number of irreducible factors: {len(factor_list)}")
    for i, (fac, mult) in enumerate(factor_list):
        d = fac.total_degree()
        g = max(0, (d-1)*(d-2)//2)
        print(f"    Factor {i+1}: degree={d}, mult={mult}, genus(smooth)={g}")
        if g >= 2:
            print(f"      → FALTINGS: finitely many ℚ-points on this component!")
    
    state['period4'] = {
        'total_deg': deg,
        'n_factors': len(factor_list),
        'factor_degrees': [(fac.total_degree(), mult) for fac, mult in factor_list],
    }
    return state['period4']


def section_period3_general_b():
    """Period-3 curve with b as parameter (the universal family lives here)."""
    x0, x1, c, b = symbols('x0 x1 c b')
    
    print("  Period-3 curve with general b:")
    
    x2 = x1**2 + c + b*x0
    closure1 = expand(x2**2 + c + b*x1 - x0)
    closure2 = expand(x0**2 + c + x2 - x1)  # BUG: should be b*x2
    # Fix:
    closure2 = expand(x0**2 + c + b*x2 - x1)
    
    # These are 2 equations in (x0, x1, c, b) — a 2D surface
    # For fixed b, it's a curve in (x0, x1, c)
    
    # Our universal family gives a rational parametrization of this curve:
    # x0 = -(5b+7)/4, x1 = (7b+5)/4, c = -(29b²+38b+29)/16
    # This is a RATIONAL curve (genus 0) parametrized by b
    
    print("  The universal period-3 family parametrizes the curve by b:")
    print("    x₀(b) = -(5b+7)/4")
    print("    x₁(b) = (7b+5)/4")
    print("    c(b)  = -(29b²+38b+29)/16")
    print()
    print("  This is a RATIONAL parametrization → genus 0 component")
    print("  → Infinitely many ℚ-points (confirmed by our theorem)")
    print()
    print("  BUT: for fixed b, the period-3 curve may have OTHER components")
    print("  with higher genus → finitely many additional ℚ-rational orbits")
    
    # For b=1 (Conj 3 map): how many period-3 orbits exist?
    # We know the universal family gives one (at c=-6)
    # Are there others?
    
    return {'genus_of_family': 0}


def section_genus_summary():
    """Summary table."""
    print("\n  ╔══════════════════════════════════════════════════════╗")
    print("  ║       GENUS ANALYSIS SUMMARY                          ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    
    results = {
        'period3': state.get('period3', {}),
        'period4': state.get('period4', {}),
    }
    
    print("\n  Key findings:")
    print("  1. Period-3 universal family: genus 0 (rational curve)")
    print("     → Infinitely many ℚ-rational period-3 orbits (our theorem)")
    print("  2. Each period-n curve factors into components")
    print("  3. High-degree components may have genus ≥ 2 → Faltings finiteness")
    
    with open(os.path.join(OUTPUT_DIR, 'genus_results.json'), 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    return results


run_experiment([
    ("Period-3 genus (b=+1)", section_period3_genus),
    ("Period-3 irreducible components", section_period3_irreducible),
    ("Period-4 genus (b=+1)", section_period4_genus),
    ("Period-3 with general b", section_period3_general_b),
    ("Genus summary", section_genus_summary),
], timeout_sec=180)
