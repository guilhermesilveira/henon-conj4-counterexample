#!/usr/bin/env python3
"""
EXP-001g var c: Strengthening — analyze ALL period-6 and period-8 c values found.
Check for deeper structure connecting different families.
Also: prove the denominator-preservation property for q=2,3,4.
"""
from common import run_experiment
import os, json
from fractions import Fraction

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', '..', 'output', 'exp001g-parametric-family')
os.makedirs(OUTPUT_DIR, exist_ok=True)

state = {}


def henon_orbit(x0, x1, c, n):
    orbit = [x0, x1]
    xp, xc = x0, x1
    for _ in range(n):
        xn = xc * xc + c + xp
        orbit.append(xn)
        xp, xc = xc, xn
    return orbit


def section_analyze_period6_c33_16():
    """Analyze the second period-6 orbit at c=-33/16."""
    print("  Period-6 orbits at c = -33/16:")
    c = Fraction(-33, 16)
    
    # Find ALL period-6 orbits at this c
    found = []
    for q in range(1, 9):
        for a in range(-10*q, 10*q + 1):
            for b in range(-10*q, 10*q + 1):
                x0 = Fraction(a, q)
                x1 = Fraction(b, q)
                orbit = henon_orbit(x0, x1, c, 8)
                
                if orbit[6] == x0 and orbit[7] == x1:
                    prim = True
                    for d in [1, 2, 3]:
                        if orbit[d] == x0 and orbit[d+1] == x1:
                            prim = False
                    if prim:
                        orb_key = tuple(sorted([str(orbit[i]) for i in range(6)]))
                        if orb_key not in [f['key'] for f in found]:
                            found.append({
                                'x0': str(x0), 'x1': str(x1),
                                'orbit': [str(orbit[i]) for i in range(6)],
                                'key': orb_key,
                            })
    
    print(f"  Found {len(found)} distinct period-6 orbits at c=-33/16:")
    for f in found:
        print(f"    orbit = {f['orbit']}")
        denoms = [Fraction(v).denominator for v in f['orbit']]
        print(f"    denominators: {denoms}")
    
    # Is -33/16 = -33/4²? Yes! q=4
    print(f"\n  -33/16 = -33/4² (q=4)")
    print(f"  Compare: -7/9 = -7/3² (q=3)")
    print(f"  Both are p/q² but with different p")
    
    # For c=-7/9: p=7, q=3, period=6=2q
    # For c=-33/16: p=33, q=4, period=6 ≠ 2q=8
    print(f"\n  c=-7/9: p=7, q=3, period=6=2·3 ✅ matches family")
    print(f"  c=-33/16: p=33, q=4, period=6≠2·4=8 ❌ different family")
    
    state['c33_orbits'] = found
    return {'found': len(found)}


def section_denominator_preservation():
    """Why do denominators stay at q for q=2,3,4?
    
    Key: x_{n+1} = x_n² + c + x_{n-1}
    If x_n = a_n/q and c = p/q², then:
    x_{n+1} = a_n²/q² + p/q² + a_{n-1}/q = (a_n² + p + a_{n-1}·q) / q²
    
    For this to have denominator q (not q²), we need:
    q | (a_n² + p + a_{n-1}·q)  i.e.  q | (a_n² + p)
    
    Since p = -(2q+1), this means:  q | (a_n² - 2q - 1)  i.e.  q | (a_n² - 1)
    i.e. a_n² ≡ 1 (mod q)
    """
    print("  Denominator preservation analysis:")
    print("  If x_n = a_n/q and c = -(2q+1)/q², then:")
    print("  x_{n+1} = (a_n² - 2q - 1 + a_{n-1}·q) / q²")
    print("  Denominator q iff q | (a_n² - 2q - 1)  iff  a_n² ≡ 1 (mod q)")
    print()
    
    for q in [2, 3, 4, 5]:
        c = Fraction(-(2*q+1), q*q)
        x0 = Fraction(-(q+1), q)
        x1 = Fraction(q+1, q)
        
        orbit = henon_orbit(x0, x1, c, max(2*q+2, 12))
        
        print(f"  q={q}, c={c}:")
        numerators = [orbit[i].numerator for i in range(min(2*q+2, len(orbit)))]
        print(f"    numerators (a_n): {numerators}")
        
        # Check a_n² mod q
        for i, a in enumerate(numerators[:min(2*q+2, 12)]):
            r = (a * a) % q
            denom = orbit[i].denominator
            print(f"    a_{i}={a:>4d}, a²≡{r} (mod {q}), denom={denom}", end="")
            if r == 1 % q:
                print(" ← a²≡1 ✅")
            else:
                print(f" ← a²≡{r} ❌ (denom preservation FAILS here)")
    
    return {'done': True}


def section_why_q5_breaks():
    """Explain algebraically why q=5 breaks."""
    print("  Why q=5 breaks:")
    print()
    q = 5
    c = Fraction(-(2*q+1), q*q)
    x0 = Fraction(-(q+1), q)
    x1 = Fraction(q+1, q)
    
    # a₀ = -(q+1) = -6, a₁ = q+1 = 6
    # x₂ = (a₁² + p + a₀·q)/q² where p = -(2q+1) = -11
    # = (36 - 11 + (-6)(5)) / 25 = (36 - 11 - 30)/25 = -5/25 = -1/5
    # a₂ = -1 (numerator of x₂ with denom q)
    
    orbit = henon_orbit(x0, x1, c, 12)
    
    print(f"  Step by step:")
    for i in range(8):
        if i < 2:
            a = orbit[i].numerator
            print(f"  x[{i}] = {orbit[i]}, a={a}, a²%{q} = {a*a%q}")
        else:
            # Compute manually
            xprev = orbit[i-1]
            xprev2 = orbit[i-2]
            xnew = xprev**2 + c + xprev2
            a_num = xnew.numerator
            a_den = xnew.denominator
            a_sq_mod = None
            if a_den == q:
                a_sq_mod = (a_num * a_num) % q
            print(f"  x[{i}] = {orbit[i]}, denom={a_den}", end="")
            if a_den == q:
                print(f", a={a_num}, a²%{q} = {a_sq_mod}", end="")
                if a_sq_mod != 1 % q:
                    print(f" ← BREAKS (need a²≡1 mod {q})")
                else:
                    print(f" ← OK")
            else:
                print(f" ← denom already ≠ {q}!")
    
    print(f"\n  Root cause: a₄ = 0 (x[4]=0), and 0² ≡ 0 (mod 5) ≠ 1")
    print(f"  So x[5] gets denom 25 instead of 5, and from there it cascades")
    
    # What values of q have a²≡1 mod q for ALL orbit elements?
    # For q=2: a²≡1 mod 2 iff a is odd. Orbit: -3,3,-1,1 → all odd ✅
    # For q=3: a²≡1 mod 3 iff a≡±1 mod 3. Orbit: -4,4,-1,2,-2,1 → check
    print(f"\n  Check which q values preserve denominators:")
    for q in [2, 3, 4, 5, 6, 7]:
        # Squares mod q that equal 1
        sq1 = [a for a in range(q) if (a*a) % q == 1 % q]
        print(f"    q={q}: a²≡1 mod {q} for a ∈ {sq1} (mod {q})")
        # Fraction of residues: len(sq1)/q
        print(f"      → {len(sq1)}/{q} = {len(sq1)/q:.2f} of residues work")
    
    return {'done': True}


def section_deeper_pattern():
    """Is there a deeper number-theoretic reason for q ∈ {2,3,4}?"""
    print("  Number theory of the working q values:")
    print()
    
    # For the orbit to maintain denom q for ALL 2q steps:
    # Need a_n² ≡ 1 (mod q) for all n
    # This means a_n ≡ ±1 (mod q) for all n (when q is prime or prime power)
    
    # The recurrence in numerators: a_{n+1} = (a_n² - (2q+1) + a_{n-1}·q) / q
    # Wait, let me be more careful:
    # x_{n+1} = x_n² + c + x_{n-1}
    # a_{n+1}/q = (a_n/q)² + (-(2q+1)/q²) + a_{n-1}/q
    # a_{n+1}/q = (a_n² - (2q+1) + a_{n-1}·q) / q²
    # a_{n+1} = (a_n² - (2q+1) + a_{n-1}·q) / q
    
    # For this to be an integer, need q | (a_n² - (2q+1))
    # i.e. q | (a_n² - 1) since 2q+1 ≡ 1 (mod q)
    # i.e. a_n² ≡ 1 (mod q)
    
    # Then a_{n+1} = (a_n² - 1)/q - 2 + a_{n-1}
    
    print("  Recurrence in numerators:")
    print("  a_{n+1} = (a_n² - 1)/q + a_{n-1} - 2")
    print("  (valid when a_n² ≡ 1 mod q)")
    print()
    
    for q in [2, 3, 4]:
        a = [-(q+1), q+1]  # a₀, a₁
        print(f"  q={q}: a₀={a[0]}, a₁={a[1]}")
        ok = True
        for step in range(2*q):
            an = a[-1]
            an_prev = a[-2]
            if (an*an - 1) % q != 0:
                print(f"    Step {len(a)}: a_n={an}, a_n²-1={an*an-1}, not div by {q}!")
                ok = False
                break
            a_new = (an*an - 1) // q + an_prev - 2
            a.append(a_new)
        
        print(f"    Numerator sequence: {a[:2*q+2]}")
        print(f"    All a²≡1 mod {q}? {ok}")
        
        # Check closure: a[2q] = a[0] and a[2q+1] = a[1]?
        if len(a) > 2*q+1:
            print(f"    Closure: a[{2*q}]={a[2*q]} vs a[0]={a[0]}: {'✅' if a[2*q]==a[0] else '❌'}")
    
    # For q=5:
    print(f"\n  q=5:")
    a = [-6, 6]
    for step in range(12):
        an = a[-1]
        an_prev = a[-2]
        if (an*an - 1) % 5 != 0:
            print(f"    Step {len(a)}: a_n={an}, a_n²={an*an}, a_n²%5={an*an%5} ≠ 1")
            print(f"    → Denominator preservation BREAKS here")
            break
        a_new = (an*an - 1) // 5 + an_prev - 2
        a.append(a_new)
        print(f"    a[{len(a)-1}] = {a[-1]}, a²%5 = {a[-1]**2 % 5}")
    
    return {'done': True}


def section_extended_family_search():
    """Search for OTHER x₀, x₁ at the same c values that give higher periods."""
    print("  Searching for other orbits at the family's c values:")
    
    for q in [2, 3, 4]:
        c = Fraction(-(2*q+1), q*q)
        print(f"\n  c = {c} (q={q}):")
        
        found_periods = {}
        for a in range(-10*q, 10*q + 1):
            for b in range(-10*q, 10*q + 1):
                x0 = Fraction(a, q)
                x1 = Fraction(b, q)
                
                orbit = henon_orbit(x0, x1, c, 14)
                
                for p in range(1, 13):
                    if p+1 < len(orbit) and orbit[p] == x0 and orbit[p+1] == x1:
                        # Check primitive
                        prim = True
                        for d in range(1, p):
                            if d+1 < len(orbit) and orbit[d] == x0 and orbit[d+1] == x1:
                                prim = False
                                break
                        if prim:
                            if p not in found_periods:
                                found_periods[p] = []
                            orb = tuple(str(orbit[i]) for i in range(p))
                            if orb not in [tuple(f) for f in found_periods[p]]:
                                found_periods[p].append(list(orb))
                        break
        
        for p in sorted(found_periods.keys()):
            n = len(found_periods[p])
            print(f"    Period {p}: {n} distinct orbits")
            for orb in found_periods[p][:3]:
                print(f"      {orb}")
    
    return {'done': True}


def section_verdict():
    """Final summary of strengthening."""
    print("\n  ╔══════════════════════════════════════════════════╗")
    print("  ║ EXP-001g var c: STRENGTHENING RESULTS            ║")
    print("  ╚══════════════════════════════════════════════════╝")
    
    print("""
  KEY FINDINGS:
  
  1. DENOMINATOR PRESERVATION THEOREM:
     For the Hénon map f(x,y) = (y, y²+c+x) with c = -(2q+1)/q²
     and x₀ = -(q+1)/q, x₁ = (q+1)/q:
     
     If all orbit numerators a_n satisfy a_n² ≡ 1 (mod q), then
     all orbit elements have denominator exactly q.
     
     The numerator recurrence is: a_{n+1} = (a_n² - 1)/q + a_{n-1} - 2
  
  2. WHY q=5 BREAKS:
     At q=5: a₀=-6, a₁=6, a₂=-1, a₃=4, a₄=0.
     a₄=0 has 0²%5=0≠1, breaking denominator preservation.
     From step 4 onward, denominators cascade to 25, 625, etc.
  
  3. WHY q=2,3,4 WORK:
     For small q, the set {a : a²≡1 mod q} is relatively large:
     - q=2: 1 out of 2 residues (50%)
     - q=3: 2 out of 3 residues (67%)
     - q=4: 2 out of 4 residues (50%)
     - q=5: 2 out of 5 residues (40%)
     Smaller q → easier for ALL orbit elements to land in the "safe" set.
  
  4. The c=-33/16 period-6 orbit is from a DIFFERENT family (not c=-(2q+1)/q²).
     It has c=-33/4² with q=4, but period 6≠2·4=8.
""")
    
    return {'success': True}


run_experiment([
    ("Analyze c=-33/16 period-6 orbit", section_analyze_period6_c33_16),
    ("Denominator preservation analysis", section_denominator_preservation),
    ("Why q=5 breaks", section_why_q5_breaks),
    ("Deeper number-theoretic pattern", section_deeper_pattern),
    ("Extended family search at same c values", section_extended_family_search),
    ("Verdict", section_verdict),
], timeout_sec=300)
