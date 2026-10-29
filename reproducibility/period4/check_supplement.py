"""Bounded F04 bridges. Exact identities support, but do not replace the article and supplement proofs.
Output is confined to this script directory.
"""
import hashlib
import itertools
import json
import platform
from pathlib import Path
import sympy as s

HERE = Path(__file__).resolve().parent
checks = {}
certificates = {}

def check(name, condition):
    assert condition, name
    checks[name] = True

def zero(name, expression):
    check(name, s.cancel(expression) == 0)

x,y,z,w,c,r,S,U,v,q,n,m = s.symbols('x y z w c r S U v q n m')
# New fixed-map route: universal monic standard basis over Q[c].
variables = [x,y,z,w]
linear = [y-w-c,z-x-c,w-y-c,x-z-c]
equations = [a*a-b for a,b in zip(variables,linear)]
pairs = []
for i,j in itertools.combinations(range(4),2):
    spol = variables[j]**2*equations[i]-variables[i]**2*equations[j]
    rep = linear[j]*equations[i]-linear[i]*equations[j]
    zero(f'fixed_map_standard_representation_{i}_{j}',spol-rep)
    check(f'fixed_map_representation_lower_degree_{i}_{j}',
          s.Poly(linear[j]*equations[i],*variables).total_degree()<4 and
          s.Poly(linear[i]*equations[j],*variables).total_degree()<4)
    pairs.append({'pair':[i,j],'S_polynomial':str(s.expand(spol)),
                  'coefficients':[str(linear[j]),str(-linear[i])]})
certificates['fixed_map']={'variables':list(map(str,variables)),
    'coefficient_ring':'Q[c]; all leading coefficients are 1',
    'equations':list(map(str,equations)), 'standard_representations':pairs,
    'standard_monomials':[str(s.prod(a**e for a,e in zip(variables,exps)))
                          for exps in itertools.product([0,1],repeat=4)],
    'lower_period_quotient_basis':['1','x','y','x*y']}
for i,f in enumerate(equations):
    lower=s.expand(f.subs({z:x,w:y},simultaneous=True))
    zero(f'fixed_map_lower_quotient_{i}',lower-([x*x+c,y*y+c,x*x+c,y*y+c][i]))

# New isolated-C infinitude route: bounded error plus ordered integer sequence.
den=4*r*r*(r*r-1)**2
num=r**8+14*r**4+1
error=2*r**6+13*r**4+1
positive=10*r**6-37*r**4+12*r*r-1
zero('C_order_error_identity',num-r*r*den/4-error)
zero('C_order_upper_bound_identity',3*den-error-positive)
coeffs=s.Poly(positive.subs(r,q+2),q).all_coeffs()
check('C_order_positive_coefficients_for_r_ge_2',all(a>0 for a in coeffs))
zero('C_sequence_separation',(4*m)**2/4-(4*n)**2/4-4*(m-n)*(m+n))
certificates['C_order']={'error_numerator':str(error),
    'positive_shift_r_equals_q_plus_2':str(s.expand(positive.subs(r,q+2))),
    'coefficients':list(map(str,coeffs)),
    'universal_prose_bridge':'q>=0 implies 0<error/den<3; r_n=4n, n>=1; Supplement S6 proves strict separation.'}

# New quotient route: two quadratic involutions and reconstruction tower.
rho=(r+1)/(1-r)
Sr=r-1/r; Ur=r+1/r
zero('quotient_rho_squared',rho.subs(r,rho)+1/r)
zero('quotient_sigma_linear',-1/r-(Sr-r))
zero('quotient_S_under_rho',Sr.subs(r,rho)+4/Sr)
zero('quotient_tau_linear',-4/S-(v-S)-(S*S-v*S-4)/S)
zero('quotient_r_minpoly',r*r-Sr*r-1)
zero('quotient_S_minpoly',S*S-(S-4/S)*S-4)
zero('quotient_quartic_from_tower',
     s.expand(r*r*((Sr)**2-v*Sr-4))-(r**4-v*r**3-6*r*r+v*r+1))
for a in [0,1,-1]:
    check(f'quotient_no_forbidden_r_{a}',
          s.expand((r**4-v*r**3-6*r*r+v*r+1).subs(r,a)) != 0)
zero('quotient_removed_divisor',(Sr-4/Sr)**2+16-(Sr*Sr+4)**2/Sr**2)
zero('quotient_inverse_U_square',((2*r-Sr)**2-Sr**2-4))

# Supplement missing explicit strata and singularity checks.
H=(x*x+c)**2+2*c-4
F=s.expand(H*H+4*x*x*(x*x+2*c))
zz=H/(2*x); ss=x+zz; uu=-(c+x*x)
def modF(expr):
    top=s.fraction(s.cancel(expr))[0]
    return s.rem(top,F,c)==0
check('plane_lift_z_square',modF(zz*zz+2*c+x*x))
check('plane_lift_conic',modF(uu*uu-ss*ss-4))
zero('plane_nonprimitive_U0',F.subs(c,-x*x)-16*(x*x+1))
zero('C_x0_discriminant',s.discriminant(c*c+2*c-4,c)-20)
dc=s.symbols('dc'); c0=s.symbols('c0')
taylor=s.Poly(F.subs(c,c0+dc),x,dc)
quad=sum(coef*x**powers[0]*dc**powers[1]
         for powers,coef in taylor.terms() if sum(powers)==2)
zero('plane_C_x0_node_tangent_cone',
     s.rem(quad-((2*c0+2)**2*dc**2+8*c0*x*x),c0*c0+2*c0-4,c0))
certificates['plane_nodes']={'equation_for_c0':'c0^2+2*c0-4=0',
    'tangent_cone':'(2*c0+2)^2 dc^2+8*c0 x^2',
    'scope':'Two distinct geometric tangents since c0 != 0,-1; the article supplies smoothness of x!=0.'}
zero('C_c_minus3_factor',num-3*den-(r**4-6*r*r+1)**2)
check('C_c0_eight_simple_roots',s.gcd(num,s.diff(num,r))==1)
check('C_c0_admissible',s.gcd(num,r*(r*r-1)*(r*r+1))==1)

# Explicit field-valued x=0 lifting bridge, without claiming rational square roots.
S0=z; U0=-c
d0={x:0,y:(-4/z+c)/2,w:(-4/z-c)/2}
cycle=[z-y*y-c-x,w-z*z-c-y,x-w*w-c-z,y-x*x-c-w]
g0=s.groebner([c*c+2*c-4,z*z+2*c],z,c)
for i,e in enumerate(cycle):
    top=s.fraction(s.cancel(e.subs(d0,simultaneous=True)))[0]
    check(f'plane_C_x0_dynamic_bridge_{i}',g0.reduce(top)[1]==0)

result={'python':platform.python_version(),'sympy':s.__version__,
    'checks':checks,'certificates':certificates,
    'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'trust':'SymPy/Python exact arithmetic; universal dimension, fixed-field and order arguments in the article and supplement, not formalized in kernel.'}
(HERE/'supplement-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(f'{len(checks)} supplemental exact checks passed')
