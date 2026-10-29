"""V-Q03A: symbolic identities over QQ(b,r); no sampled proof of infinitude.
Run without arguments to print; --output PATH writes the report.
The root-count and finite-union arguments are in the article and supplement, not implemented here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sympy as s

b,r,t,k,a=s.symbols('b r t k a')
Q=r*r-r+1
L=2*r*(r-1)
X=b*r**3-b*r+b+r**3-r**2+1
Y=b*r**3-2*b*r**2+b*r-b+r**3-3*r**2+2*r-1
Z=-(b*r**3-2*b*r**2+3*b*r-b+r**3-r**2+2*r-1)
N=s.expand(Z*L-Y*Y-b*X*L)
x,y,z=X/L,Y/L,Z/L
c=N/L**2
checks={}
def zero(name,expression):
    value=s.cancel(expression)
    if value != 0: raise AssertionError((name,value))
    checks[name]='zero identity'
zero('closure_0', z-y*y-c-b*x)
zero('closure_1', x-z*z-c-b*y)
zero('closure_2', y-x*x-c-b*z)
zero('difference',y-x+(b+1)*Q/(r*(r-1)))
zero('ratio',z-x-r*(y-x))
zero('positive_quadratic',4*Q-((2*r-1)**2+3))
zero('derive_x',2*x+r*(y-x)-b+(b+1)/r)
zero('derive_difference',(r-1)*(2*x+(r+1)*(y-x))+r+b)
assert s.degree(N-k*L**2,r)==6
zero('fiber_leading_coefficient',s.Poly(N-k*L**2,r).LC()+(b+1)**2)
for name,e,old in [('x',x,-(5*b+7)/4),('y',y,(7*b+5)/4),('z',z,(b-1)/4),('c',c,-(29*b*b+38*b+29)/16)]:
    zero('old_family_'+name,e.subs(r,s.Rational(1,2))-old)
# Independent construction used by V-Q03B: inherited b=1 family.
D=4*t*t-1
v=[t*(4*t*t+7)/D,(8*t*t+6)/(2*D)-t,-(8*t*t+6)/(2*D)-t]
q=-(16*t**6+24*t**4+33*t*t+6)/D**2
alpha=(b+1)/2; beta=(b-1)/4
u=[alpha*vi+beta for vi in v]
C=alpha**2*q-2*alpha*beta*sum(v)-5*beta**2
# This comparison is provenance only, not an extra independent proof.
# Ratio parameter of v (and u) is (2t+1)/(2t-1).
rr=s.cancel((v[2]-v[0])/(v[1]-v[0]))
for name,e,other in zip(['x','y','z','c'],[x,y,z,c],u+[C]):
    zero('route_comparison_'+name,e.subs(r,rr)-other)
# Poonen, arXiv:math/9512217v1 Theorem 1(3), tau=r-1.
tau=r-1
pc=-(tau**6+2*tau**5+4*tau**4+8*tau**3+9*tau**2+4*tau+1)/(4*tau**2*(tau+1)**2)
zero('poonen_b0_c',c.subs(b,0)-pc)
pv=[(tau**3+2*tau**2+tau+1)/(2*tau*(tau+1)),(tau**3-tau-1)/(2*tau*(tau+1)),-(tau**3+2*tau**2+3*tau+1)/(2*tau*(tau+1))]
for name,e,other in zip(['x','y','z'],[x,y,z],pv):zero('poonen_b0_'+name,e.subs(b,0)-other)
# Exceptional component, explicitly outside the ratio chart.
w=[a,a,-a-1]; cc=-a*a-1
for i in range(3):zero('exception_closure_'+str(i),w[(i+2)%3]-w[(i+1)%3]**2-cc+w[i])
zero('exception_nonfixity',w[2]-w[0]+2*a+1)
# Adversarial controls are not proofs of general statements.
assert s.cancel((c+1)-c)!=0
assert s.cancel((x-y).subs(b,-1))==0
assert all(s.cancel(vv.subs(a,-s.Rational(1,2))+s.Rational(1,2))==0 for vv in w)
assert s.cancel(c.subs({b:-1,r:2})+s.Rational(5,4))==0
out={'claim':'PUB15-Q03','route':'V-Q03A','python':platform.python_version(),'sympy':s.__version__,'checks':checks,'fiber_polynomial':str(s.Poly(N-k*L**2,r).as_expr()),'ratio_of_route_B':str(rr),'adversarial_controls':['adding 1 to c violates closure','generic b=-1 collapses','exception a=-1/2 is fixed','generic b=-1 c=-5/4'],'passed':True,'scope':'Universal polynomial/rational identities; infinitude and necessity use the explicit proof in the article and supplement. No kernel formalization.','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
p=argparse.ArgumentParser();p.add_argument('--output');args=p.parse_args()
text=json.dumps(out,indent=2,ensure_ascii=False)+'\n'
if args.output:Path(args.output).write_text(text)
else: print(text,end='')
