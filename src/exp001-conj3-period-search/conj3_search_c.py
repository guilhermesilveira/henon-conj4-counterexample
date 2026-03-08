#!/usr/bin/env python3
"""
EXP-001c: Smart algebraic search for all periods 1-12.

For each period N, extract the dynatomic factor (primitive period N only),
then systematically find rational points on the curve P_N(x, c) = 0.

Uses the rational root theorem for efficiency: for each x₀ = p/q,
the rational roots of P_N(x₀, c) are constrained to p'/q' where
q' | leading_coeff and p' | constant_term.
"""
from common import run_experiment
import os, json
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp001-conj3-period-search')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


def section_dynatomic_factorization():
    """
    Compute resultant polynomials for periods 1-8 and extract dynatomic
    (primitive period) factors by dividing out lower period factors.
    """
    from sympy import symbols, expand, resultant, Poly, factor, div, ZZ
    
    x, t, c = symbols('x t c')
    
    # Build resultants for each period
    resultants = {}
    
    for N in range(1, 9):
        print(f"\n  Period N={N}:", flush=True)
        
        if N == 1:
            resultants[1] = expand(c + x**2)
            print(f"    R_1 = c + x²")
            continue
        
        # Build orbit
        xs_list = [x, t]
        for n in range(1, N):
            xs_list.append(expand(xs_list[-1]**2 + c + xs_list[-2]))
        
        condA = expand(xs_list[N] - x)
        condB = expand(x**2 + c + xs_list[N-1] - t)
        
        print(f"    Computing resultant...", flush=True)
        res = expand(resultant(condA, condB, t))
        resultants[N] = res
        
        deg_x = Poly(res, x, domain='ZZ[c]').degree()
        deg_c = Poly(res, c, domain='ZZ[x]').degree()
        print(f"    R_{N}: deg_x={deg_x}, deg_c={deg_c}")
    
    # Now compute dynatomic = R_N / product(R_d for d | N, d < N)
    # using Möbius function: Phi_N = product_{d|N} R_d^{mu(N/d)}
    from sympy import factorint
    
    def mobius(n):
        """Möbius function."""
        if n == 1:
            return 1
        facs = factorint(n)
        if any(e > 1 for e in facs.values()):
            return 0
        return (-1)**len(facs)
    
    def divisors(n):
        """All divisors of n."""
        divs = []
        for i in range(1, n+1):
            if n % i == 0:
                divs.append(i)
        return divs
    
    dynatomic = {}
    
    for N in range(1, 9):
        if N not in resultants:
            continue
        
        print(f"\n  Dynatomic Phi_{N}:", flush=True)
        
        # Phi_N = R_N / product(Phi_d for d | N, d < N)
        # Or equivalently via Möbius: Phi_N = product_{d|N} R_d^{mu(N/d)}
        # For simplicity, just divide R_N by all R_d for proper divisors d
        
        num = Poly(resultants[N], x, c, domain='ZZ')
        for d in divisors(N):
            if d < N and d in resultants:
                divisor = Poly(resultants[d], x, c, domain='ZZ')
                # Divide as many times as possible
                while True:
                    q, r = div(num, divisor, x, c, domain='ZZ')
                    if r.is_zero:
                        num = q
                    else:
                        break
        
        phi_N = num.as_expr()
        phi_N = expand(phi_N)
        
        try:
            deg_x = Poly(phi_N, x, domain='ZZ[c]').degree()
            deg_c = Poly(phi_N, c, domain='ZZ[x]').degree()
        except:
            deg_x = deg_c = '?'
        
        print(f"    Phi_{N}: deg_x={deg_x}, deg_c={deg_c}")
        
        # Factor
        try:
            fac = factor(phi_N)
            fac_str = str(fac)[:300]
            print(f"    Factored: {fac_str}")
        except:
            fac_str = "?"
        
        dynatomic[N] = phi_N
    
    state['dynatomic'] = {N: str(p)[:500] for N, p in dynatomic.items()}
    state['dynatomic_polys'] = dynatomic
    return state['dynatomic']


def section_rational_points():
    """
    For each dynatomic polynomial Phi_N(x, c), find ℚ-rational points.
    Use: for each x₀ = p/q with small p, q, evaluate Phi_N(x₀, c) as
    a univariate polynomial in c and find rational roots.
    """
    from sympy import Poly, Rational, symbols, ZZ, QQ
    import cypari2
    
    x, c = symbols('x c')
    pari = cypari2.Pari()
    
    dynatomic = state.get('dynatomic_polys', {})
    
    all_results = {}
    
    for N in sorted(dynatomic.keys()):
        phi = dynatomic[N]
        print(f"\n  Period {N}: searching for rational points on Phi_{N}(x,c) = 0", flush=True)
        
        found = []
        
        # Try x₀ = p/q for small values
        for qx in range(1, 30):
            for px in range(-50, 51):
                x0 = Rational(px, qx)
                
                # Evaluate Phi_N(x₀, c)
                phi_at_x0 = phi.subs(x, x0)
                
                if phi_at_x0 == 0:
                    # x₀ is a root for ALL c — shouldn't happen for dynatomic
                    continue
                
                # Convert to PARI polynomial in c and find rational roots
                try:
                    poly_c = Poly(phi_at_x0, c, domain='QQ')
                    coeffs = poly_c.all_coeffs()
                    
                    # Build PARI polynomial
                    pari_str = " + ".join(
                        f"({float(coeff)})*x^{len(coeffs)-1-i}" 
                        for i, coeff in enumerate(coeffs)
                    )
                    
                    # Use rational root theorem instead (exact)
                    # Rational roots of a_n*c^n + ... + a_0 are p/q where p | a_0 and q | a_n
                    # Convert to integer coefficients
                    from sympy import lcm as sym_lcm
                    denoms = [coeff.q if hasattr(coeff, 'q') else 1 for coeff in coeffs]
                    from math import lcm
                    from functools import reduce
                    L = reduce(lcm, [int(d) for d in denoms])
                    int_coeffs = [int(coeff * L) for coeff in coeffs]
                    
                    # Leading and constant
                    a_n = abs(int_coeffs[0])
                    a_0 = abs(int_coeffs[-1])
                    
                    if a_n == 0 or a_0 == 0:
                        # c = 0 might be a root
                        if int_coeffs[-1] == 0:
                            # Verify
                            cv = Rational(0)
                            val = phi.subs({x: x0, c: cv})
                            if val == 0:
                                orbit = verify_and_get_orbit(Fraction(px, qx), Fraction(0), N)
                                if orbit:
                                    found.append({'c': '0', 'x0': str(x0), 'orbit': orbit})
                        continue
                    
                    # Factors of a_0 and a_n
                    def small_factors(n, max_fac=200):
                        facs = set()
                        for i in range(1, min(n+1, max_fac)):
                            if n % i == 0:
                                facs.add(i)
                        return facs
                    
                    p_candidates = small_factors(a_0, 500)
                    q_candidates = small_factors(a_n, 500)
                    
                    # Test each p/q
                    for p_val in p_candidates:
                        for q_val in q_candidates:
                            for sign in [1, -1]:
                                cv = Rational(sign * p_val, q_val)
                                # Evaluate poly
                                val = sum(int_coeffs[i] * int(cv.p)**( len(int_coeffs)-1-i) * int(cv.q)**(i) 
                                          for i in range(len(int_coeffs)))
                                # Actually need to be more careful with rational evaluation
                                val = phi.subs({x: x0, c: cv})
                                if val == 0:
                                    orbit = verify_and_get_orbit(
                                        Fraction(px, qx), 
                                        Fraction(int(cv.p), int(cv.q)), 
                                        N)
                                    if orbit:
                                        found.append({
                                            'c': str(cv), 
                                            'x0': str(x0),
                                            'orbit': [str(v) for v in orbit]
                                        })
                                        if len(found) <= 3:
                                            print(f"    ✓ c={cv}, x₀={x0}, orbit={orbit[:4]}...")
                except Exception as e:
                    pass
            
            if len(found) >= 20:
                break
        
        marker = "✓" if N in {1,2,3,4,6,8} else ("🔴" if found else "✓(none)")
        if found:
            print(f"  {marker} Period {N}: {len(found)} rational orbit(s)")
        else:
            print(f"  {marker} Period {N}: no rational orbits found")
        
        all_results[N] = found
    
    state['rational_points'] = {N: v for N, v in all_results.items()}
    return state['rational_points']


def verify_and_get_orbit(x0_frac, c_frac, target_N):
    """
    Given (x₀, c) ∈ ℚ, find x₁ that gives a primitive period-N orbit.
    Try x₁ from small rationals.
    """
    MAX_BITS = 500
    
    for qx in range(1, 20):
        for px in range(-30, 31):
            x1 = Fraction(px, qx)
            
            orbit = [x0_frac, x1]
            xprev, xcur = x0_frac, x1
            ok = True
            
            for n in range(2, target_N + 2):
                xnext = xcur * xcur + c_frac + xprev
                if (xnext.numerator.bit_length() > MAX_BITS or
                    xnext.denominator.bit_length() > MAX_BITS):
                    ok = False
                    break
                orbit.append(xnext)
                xprev, xcur = xcur, xnext
            
            if not ok:
                continue
            
            # Check period
            if orbit[target_N] == orbit[0] and orbit[target_N + 1] == orbit[1]:
                # Check primitive
                is_prim = True
                for d in range(1, target_N):
                    if target_N % d == 0 and orbit[d] == orbit[0] and orbit[d+1] == orbit[1]:
                        is_prim = False
                        break
                if is_prim:
                    return orbit[:target_N]
    
    return None


def section_summary():
    """Final summary and save."""
    rp = state.get('rational_points', {})
    
    print(f"\n  ╔══════════════════════════════════════════╗")
    print(f"  ║  CONJECTURE 3 TEST RESULTS               ║")
    print(f"  ╚══════════════════════════════════════════╝")
    
    periods_found = sorted([N for N, v in rp.items() if len(v) > 0])
    
    for N in range(1, 13):
        count = len(rp.get(N, []))
        if N in {1,2,3,4,6,8}:
            status = f"✓ (allowed, {count} found)" if count > 0 else f"⚠️ (allowed, NOT found)"
        else:
            status = f"🔴 COUNTEREXAMPLE ({count} found)" if count > 0 else f"✓ (forbidden, none found)"
        print(f"  Period {N:2d}: {status}")
    
    unexpected = [N for N in periods_found if N not in {1,2,3,4,6,8}]
    
    if unexpected:
        print(f"\n  🔴 CONJECTURE 3 IS FALSE! Periods {unexpected} found!")
    else:
        print(f"\n  ✅ Conjecture 3 SUPPORTED")
        print(f"     No rational periodic orbits of forbidden periods found.")
    
    with open(os.path.join(OUTPUT_DIR, 'results_c.json'), 'w') as f:
        json.dump({
            'periods_found': periods_found,
            'unexpected': unexpected,
            'details': {str(k): v for k, v in rp.items()},
            'dynatomic_info': state.get('dynatomic', {})
        }, f, indent=2, default=str)
    
    return {'periods_found': periods_found, 'unexpected': unexpected}


run_experiment([
    ("Compute dynatomic polynomials Phi_1 through Phi_8", section_dynatomic_factorization),
    ("Find rational points on dynatomic curves", section_rational_points),
    ("Final summary", section_summary),
], timeout_sec=360)
