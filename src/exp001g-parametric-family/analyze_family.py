#!/usr/bin/env python3
"""
EXP-001g: Algebraic analysis of the parametric family c = -(2q+1)/q².

Key discovery from exp001f: the family c = -(2q+1)/q², x₀ = -(q+1)/q, x₁ = (q+1)/q
produces primitive period 2q orbits for q = 2, 3, 4 but FAILS for q = 5, 6.

Questions:
1. What is the algebraic structure? Why does it work for q ∈ {2,3,4}?
2. What goes wrong at q = 5?
3. Is there a deeper family that includes these as special cases?
4. Are there OTHER parametric families giving period 6, 8?
"""
from common import run_experiment
import os, json, sys
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp001g-parametric-family')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


def henon_iterate(x0, x1, c, n):
    """Iterate f(x,y) = (y, y² + c + x) n times from (x0, x1). Return orbit."""
    orbit = [x0, x1]
    xp, xc = x0, x1
    for _ in range(n):
        xn = xc * xc + c + xp
        orbit.append(xn)
        xp, xc = xc, xn
    return orbit


def section_verify_family():
    """Verify the family c = -(2q+1)/q² for q = 1..10."""
    print("  Testing family c = -(2q+1)/q², x₀ = -(q+1)/q, x₁ = (q+1)/q:")
    
    results = []
    for q in range(1, 11):
        c = Fraction(-(2*q+1), q*q)
        x0 = Fraction(-(q+1), q)
        x1 = Fraction(q+1, q)
        
        # Iterate up to 2q + 4 steps
        target = 2*q
        orbit = henon_iterate(x0, x1, c, target + 4)
        
        # Check closure at period 2q
        closes_2q = (orbit[target] == x0 and orbit[target+1] == x1)
        
        # Check all possible periods
        actual_period = None
        for p in range(1, target + 5):
            if p + 1 < len(orbit) and orbit[p] == x0 and orbit[p+1] == x1:
                actual_period = p
                break
        
        # Check if orbit elements stay bounded (denominator growth)
        max_denom = max(abs(orbit[i].denominator) for i in range(min(len(orbit), target+2)))
        max_num = max(abs(orbit[i].numerator) for i in range(min(len(orbit), target+2)))
        
        result = {
            'q': q, 'target_period': target, 'c': str(c),
            'x0': str(x0), 'x1': str(x1),
            'closes_at_target': closes_2q,
            'actual_period': actual_period,
            'max_denom': int(max_denom),
            'max_num': int(max_num),
        }
        results.append(result)
        
        status = "✅" if closes_2q else "❌"
        period_str = f"period={actual_period}" if actual_period else "no period found"
        print(f"    q={q:2d}: c={str(c):>12s}  target=period {target:2d}  {status}  ({period_str}, max_denom={max_denom})")
    
    state['family_results'] = results
    return {'results': results}


def section_orbit_structure():
    """Analyze orbit structure for q=2,3,4 (the working cases)."""
    print("  Orbit structure analysis:")
    
    for q in [2, 3, 4]:
        c = Fraction(-(2*q+1), q*q)
        x0 = Fraction(-(q+1), q)
        x1 = Fraction(q+1, q)
        
        orbit = henon_iterate(x0, x1, c, 2*q)
        period = 2*q
        
        print(f"\n    q={q}, c={c}, period={period}:")
        print(f"    orbit: {[str(orbit[i]) for i in range(period)]}")
        
        # Analyze: are orbit elements symmetric? What are the denominators?
        denoms = [orbit[i].denominator for i in range(period)]
        nums = [orbit[i].numerator for i in range(period)]
        print(f"    denoms: {denoms}")
        print(f"    nums:   {nums}")
        
        # Check symmetry: does orbit[i] + orbit[i + period/2] = something?
        half = period // 2
        sums = [orbit[i] + orbit[i + half] for i in range(half)]
        diffs = [orbit[i] - orbit[i + half] for i in range(half)]
        print(f"    orbit[i] + orbit[i+{half}]: {[str(s) for s in sums]}")
        print(f"    orbit[i] - orbit[i+{half}]: {[str(d) for d in diffs]}")
    
    return {'done': True}


def section_what_happens_q5():
    """Analyze what happens at q=5: where does the orbit go?"""
    print("  What happens at q=5 (target period 10):")
    
    q = 5
    c = Fraction(-(2*q+1), q*q)
    x0 = Fraction(-(q+1), q)
    x1 = Fraction(q+1, q)
    
    # Iterate many steps and track
    orbit = [x0, x1]
    xp, xc = x0, x1
    for step in range(30):
        xn = xc * xc + c + xp
        orbit.append(xn)
        xp, xc = xc, xn
        
        # Check if we returned to start
        if xn == x1 and orbit[-2] == x0:
            print(f"    Orbit closes at step {step+2}!")
    
    print(f"    First 12 orbit elements:")
    for i in range(min(12, len(orbit))):
        print(f"      x[{i}] = {orbit[i]} = {float(orbit[i]):.6f}")
    
    # Deviation from closure at step 10
    dev0 = orbit[10] - x0
    dev1 = orbit[11] - x1
    print(f"\n    Closure deviation at step 10:")
    print(f"      orbit[10] - x₀ = {dev0} = {float(dev0):.6f}")
    print(f"      orbit[11] - x₁ = {dev1} = {float(dev1):.6f}")
    
    # Check denominator growth
    print(f"\n    Denominator growth:")
    for i in range(min(20, len(orbit))):
        print(f"      x[{i}]: denom = {orbit[i].denominator}")
    
    state['q5_orbit'] = [str(v) for v in orbit[:20]]
    state['q5_dev'] = (str(dev0), str(dev1))
    return {'deviation': (str(dev0), str(dev1))}


def section_symbolic_closure():
    """Use SymPy to derive the closure condition symbolically."""
    print("  Symbolic closure analysis with SymPy...")
    
    from sympy import symbols, Rational, expand, factor, simplify, Poly
    
    q_sym = symbols('q', positive=True, integer=True)
    
    # For small concrete q, compute the closure residual
    for q in range(2, 8):
        c = Rational(-(2*q+1), q**2)
        x0 = Rational(-(q+1), q)
        x1 = Rational(q+1, q)
        
        # Iterate 2q steps
        orbit = [x0, x1]
        xp, xc = x0, x1
        for _ in range(2*q):
            xn = expand(xc**2 + c + xp)
            orbit.append(xn)
            xp, xc = xc, xn
        
        residual0 = orbit[2*q] - x0
        residual1 = orbit[2*q + 1] - x1
        
        closes = (residual0 == 0 and residual1 == 0)
        status = "✅ CLOSES" if closes else f"❌ residual = ({residual0}, {residual1})"
        print(f"    q={q}: period {2*q} → {status}")
    
    return {'done': True}


def section_generalized_family_search():
    """Search for other parametric families with period 2q."""
    print("  Searching for other parametric families giving period 6, 8...")
    
    # For period 6: we know c=-7/9 works. Are there other simple c values?
    period6_hits = []
    period8_hits = []
    
    # Search c = p/q² for small p, q
    for q in range(1, 20):
        for p in range(-50*q, 50*q + 1):
            c = Fraction(p, q*q)
            
            # Try x₀, x₁ with denominator q
            for a in range(-10*q, 10*q + 1):
                for b in range(-10*q, 10*q + 1):
                    x0 = Fraction(a, q)
                    x1 = Fraction(b, q)
                    
                    # Quick period-6 check
                    orbit = [x0, x1]
                    xp, xc = x0, x1
                    ok = True
                    for _ in range(8):
                        xn = xc * xc + c + xp
                        if abs(xn.numerator) > 10**8:
                            ok = False
                            break
                        orbit.append(xn)
                        xp, xc = xc, xn
                    
                    if not ok:
                        continue
                    
                    # Check period 6
                    if len(orbit) >= 8 and orbit[6] == x0 and orbit[7] == x1:
                        # Check primitive
                        prim = True
                        for d in [1, 2, 3]:
                            if orbit[d] == x0 and orbit[d+1] == x1:
                                prim = False
                                break
                        if prim and str(c) not in [h['c'] for h in period6_hits]:
                            period6_hits.append({'c': str(c), 'x0': str(x0), 'x1': str(x1),
                                                'orbit': [str(orbit[i]) for i in range(6)]})
                            if len(period6_hits) <= 10:
                                print(f"    Period 6: c={c}, x₀={x0}, x₁={x1}")
                    
                    # Check period 8
                    if len(orbit) >= 10 and orbit[8] == x0 and orbit[9] == x1:
                        prim = True
                        for d in [1, 2, 4]:
                            if orbit[d] == x0 and orbit[d+1] == x1:
                                prim = False
                                break
                        if prim and str(c) not in [h['c'] for h in period8_hits]:
                            period8_hits.append({'c': str(c), 'x0': str(x0), 'x1': str(x1),
                                                'orbit': [str(orbit[i]) for i in range(8)]})
                            if len(period8_hits) <= 10:
                                print(f"    Period 8: c={c}, x₀={x0}, x₁={x1}")
        
        # Early exit if we have enough
        if len(period6_hits) >= 15 and len(period8_hits) >= 10:
            break
    
    print(f"\n  Summary: {len(period6_hits)} distinct period-6 c values, {len(period8_hits)} period-8")
    
    # Analyze the c values found
    if period6_hits:
        print("  Period-6 c values:")
        for h in period6_hits[:10]:
            cv = Fraction(h['c'])
            print(f"    c = {cv} = {float(cv):.6f}")
    
    if period8_hits:
        print("  Period-8 c values:")
        for h in period8_hits[:10]:
            cv = Fraction(h['c'])
            print(f"    c = {cv} = {float(cv):.6f}")
    
    state['period6_hits'] = period6_hits
    state['period8_hits'] = period8_hits
    
    with open(os.path.join(OUTPUT_DIR, 'families.json'), 'w') as f:
        json.dump({'period6': period6_hits, 'period8': period8_hits}, f, indent=2)
    
    return {'period6_count': len(period6_hits), 'period8_count': len(period8_hits)}


def section_period10_obstruction():
    """Analyze the algebraic obstruction preventing period 10.
    
    For any c, x₀, x₁ ∈ ℚ with period 10:
    - Phi₁₀ = R₁₀ / (R₁ · R₂ · R₅) must have rational roots
    - R₁₀ has degree 2^10 = 1024... too big for SymPy
    
    Instead, test: is there ANY rational period-10 orbit with small coords?
    """
    print("  Searching for ANY period-10 rational orbit (wider search)...")
    
    count = 0
    found = 0
    
    # Extended search: c with denominator up to 50
    for denom in range(1, 30):
        for p in range(-200, 201):
            c = Fraction(p, denom)
            
            for a in range(-15, 16):
                for b in range(-15, 16):
                    x0 = Fraction(a, 1)
                    x1 = Fraction(b, 1)
                    count += 1
                    
                    orbit = [x0, x1]
                    xp, xc = x0, x1
                    ok = True
                    for _ in range(10):
                        xn = xc * xc + c + xp
                        if abs(xn.numerator) > 10**12:
                            ok = False
                            break
                        orbit.append(xn)
                        xp, xc = xc, xn
                    
                    if not ok:
                        continue
                    
                    if orbit[10] == x0 and orbit[11] == x1:
                        # Check primitive (not period 1, 2, 5)
                        prim = True
                        for d in [1, 2, 5]:
                            if orbit[d] == x0 and orbit[d+1] == x1:
                                prim = False
                                break
                        if prim:
                            found += 1
                            print(f"    ✅ PERIOD 10 FOUND! c={c}, orbit={[str(orbit[i]) for i in range(10)]}")
    
    print(f"  Tested {count} combinations, found {found} period-10 orbits")
    
    if found == 0:
        print("  → No period-10 orbits found. Consistent with Conjecture 3.")
    
    state['period10_found'] = found
    return {'tested': count, 'found': found}


def section_dynatomic_analysis():
    """Compute Phi_N factorization structure for N ∈ {4,6,8} to understand the pattern."""
    print("  Dynatomic polynomial structure analysis...")
    
    from sympy import symbols, resultant, factor, Poly, ZZ, degree
    
    x, c = symbols('x c')
    
    # For the map f(x,y) = (y, y²+c+x), a period-N orbit satisfies:
    # x_{n+1} = x_n² + c + x_{n-1}
    # 
    # For a 1-parameter family with δ=1:
    # R_N(x, c) = resultant of the period-N condition
    # We already computed Phi_N for N ≤ 7 in exp001.
    #
    # Here: analyze the factor structure
    
    # Phi₄ = (c + x² - 2x + 2)(c + x² + 2x + 2) → two linear-in-c factors
    phi4_f1 = c + x**2 - 2*x + 2  # c = -(x²-2x+2) = -(x-1)²-1
    phi4_f2 = c + x**2 + 2*x + 2  # c = -(x²+2x+2) = -(x+1)²-1
    
    print("  Period 4 (Phi₄):")
    print(f"    Factor 1: c = -(x-1)² - 1 → LINEAR in c")
    print(f"    Factor 2: c = -(x+1)² - 1 → LINEAR in c")
    print(f"    → Every x₀ ∈ ℚ gives c ∈ ℚ → infinitely many rational period-4 orbits")
    
    # For each working q, verify that x₀=-(q+1)/q is on one of these factors
    for q in [2, 3, 4]:
        x0_val = Fraction(-(q+1), q)
        c_val = Fraction(-(2*q+1), q*q)
        # Check: c + x₀² - 2x₀ + 2 = 0?
        test1 = c_val + x0_val**2 - 2*x0_val + 2
        test2 = c_val + x0_val**2 + 2*x0_val + 2
        print(f"    q={q}: x₀={x0_val}, c={c_val}")
        print(f"      Factor 1 eval: {test1}")
        print(f"      Factor 2 eval: {test2}")
    
    # Key insight: the family c = -(2q+1)/q² with x₀ = -(q+1)/q
    # c + x₀² + 2x₀ + 2 = -(2q+1)/q² + (q+1)²/q² - 2(q+1)/q + 2
    #   = [-(2q+1) + (q+1)²]/q² - 2(q+1)/q + 2
    #   = [-(2q+1) + q² + 2q + 1]/q² - 2(q+1)/q + 2
    #   = q²/q² - 2(q+1)/q + 2
    #   = 1 - 2(q+1)/q + 2 = 3 - 2 - 2/q = 1 - 2/q
    # So: c + x₀² + 2x₀ + 2 = 1 - 2/q = (q-2)/q
    # This is ZERO only when q = 2!
    
    print("\n  KEY ALGEBRAIC INSIGHT:")
    print("  c + x₀² + 2x₀ + 2 = (q-2)/q")
    print("  → Factor 2 of Phi₄ is satisfied ONLY at q=2")
    print("  → For q=3,4: the (x₀,c) pair is NOT on a Phi₄ factor!")
    print("  → The period-6 at q=3 and period-8 at q=4 come from HIGHER dynatomic polys")
    
    return {'insight': 'family lies on Phi_4 only at q=2, on higher Phi_N for q>2'}


def section_closure_residual_polynomial():
    """Compute the closure residual as a polynomial in q."""
    print("  Computing closure residual as function of q...")
    
    from sympy import symbols, Rational, expand, factor, cancel, simplify, together
    
    q = symbols('q')
    
    # c = -(2q+1)/q²
    c_expr = -(2*q + 1) / q**2
    # x₀ = -(q+1)/q, x₁ = (q+1)/q
    x0 = -(q + 1) / q
    x1 = (q + 1) / q
    
    # Iterate the Hénon recurrence x_{n+1} = x_n² + c + x_{n-1}
    orbit = [x0, x1]
    xp, xc = x0, x1
    
    MAX_STEPS = 12  # Up to period 12
    print(f"  Computing orbit symbolically for {MAX_STEPS} steps...")
    
    for step in range(MAX_STEPS):
        xn = xc**2 + c_expr + xp
        xn = cancel(xn)  # Simplify rational function of q
        orbit.append(xn)
        xp, xc = xc, xn
        
        # Check closure: does orbit[step+2] = x0 and orbit[step+3] = x1?
        # We need two consecutive matching
        if step >= 1:
            period = step + 2
            res0 = cancel(orbit[period] - x0)
            res1 = cancel(orbit[period + 1] - x1) if period + 1 < len(orbit) else None
            
            if res0 == 0:
                if res1 is not None and res1 == 0:
                    print(f"    Step {period}: orbit[{period}] = x₀ AND orbit[{period+1}] = x₁ → CLOSES!")
                else:
                    print(f"    Step {period}: orbit[{period}] = x₀ but orbit[{period+1}] ≠ x₁")
            else:
                # Factor the residual
                try:
                    res0_factored = factor(res0)
                    print(f"    Step {period}: residual = {res0_factored}")
                except:
                    print(f"    Step {period}: residual = {res0} (unfactored)")
    
    # Specifically check periods 4, 6, 8, 10
    print("\n  Closure check at specific periods:")
    for target in [4, 6, 8, 10]:
        if target < len(orbit):
            res = cancel(orbit[target] - x0)
            try:
                res_f = factor(res)
            except:
                res_f = res
            print(f"    Period {target}: orbit[{target}] - x₀ = {res_f}")
    
    return {'done': True}


def section_verdict():
    """Summarize findings."""
    print("\n  ╔══════════════════════════════════════════════════╗")
    print("  ║     EXP-001g: PARAMETRIC FAMILY ANALYSIS         ║")
    print("  ╚══════════════════════════════════════════════════╝")
    
    p6 = state.get('period6_hits', [])
    p8 = state.get('period8_hits', [])
    p10 = state.get('period10_found', 0)
    
    print(f"\n  1. Family c=-(2q+1)/q² verification:")
    for r in state.get('family_results', []):
        status = "✅" if r['closes_at_target'] else "❌"
        print(f"     q={r['q']}: period {r['target_period']} → {status}")
    
    print(f"\n  2. Other families found:")
    print(f"     Period-6 c values: {len(p6)}")
    print(f"     Period-8 c values: {len(p8)}")
    
    print(f"\n  3. Period 10 search: {'FOUND!' if p10 > 0 else 'NOT FOUND (Conj 3 supported)'}")
    
    # Save all results
    with open(os.path.join(OUTPUT_DIR, 'summary.json'), 'w') as f:
        json.dump({
            'family_results': state.get('family_results', []),
            'period6_count': len(p6),
            'period8_count': len(p8),
            'period10_found': p10,
        }, f, indent=2)
    
    return {'success': True}


run_experiment([
    ("Verify family c=-(2q+1)/q² for q=1..10", section_verify_family),
    ("Orbit structure for working cases q=2,3,4", section_orbit_structure),
    ("What happens at q=5?", section_what_happens_q5),
    ("Symbolic closure residual as polynomial in q", section_closure_residual_polynomial),
    ("Dynatomic polynomial analysis", section_dynatomic_analysis),
    ("Search for other period-6, period-8 families", section_generalized_family_search),
    ("Period-10 obstruction test (wider search)", section_period10_obstruction),
    ("Verdict", section_verdict),
], timeout_sec=600)
