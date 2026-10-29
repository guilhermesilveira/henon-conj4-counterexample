"""Targeted exact checks of logical bridges omitted by mere substitution.
Standard library only. No solver, no sampling, no claim of kernel proof.
Default prints JSON; --output writes only the nominated new result file.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json
import platform

NVAR = 9
ZERO = (0,) * NVAR

class P:
    def __init__(self, value=0):
        self.terms = dict(value) if isinstance(value, dict) else ({ZERO: F(value)} if value else {})
        self.terms = {e: F(c) for e, c in self.terms.items() if c}
    def __add__(self, other):
        other = other if isinstance(other, P) else P(other)
        out = self.terms.copy()
        for e, c in other.terms.items(): out[e] = out.get(e, 0) + c
        return P(out)
    __radd__ = __add__
    def __neg__(self): return P({e: -c for e, c in self.terms.items()})
    def __sub__(self, other): return self + (-other if isinstance(other, P) else -F(other))
    def __rsub__(self, other): return -self + other
    def __mul__(self, other):
        other = other if isinstance(other, P) else P(other)
        out = {}
        for e, c in self.terms.items():
            for f, d in other.terms.items():
                g = tuple(a+b for a,b in zip(e,f)); out[g] = out.get(g, 0)+c*d
        return P(out)
    __rmul__ = __mul__
    def __pow__(self, n):
        assert isinstance(n, int) and n >= 0
        out = P(1)
        for _ in range(n): out = out*self
        return out

variables = []
for i in range(NVAR):
    e = list(ZERO); e[i] = 1; variables.append(P({tuple(e): 1}))
x,d,r,b,c,e,t,v,w = variables
checks = []
def identity(name, left, right):
    residual = left-right
    assert not residual.terms, (name, residual.terms)
    checks.append({'id':name,'result':'exact polynomial identity'})

def residuals(word, constant, linear):
    return [word[(i+2)%3]-word[(i+1)%3]**2-constant-linear*word[i] for i in range(3)]

# Necessity: the two equations really are differences of the ORIGINAL equations,
# for arbitrary x,d,r,b,c, not only at the proposed rational solution.
E0,E1,E2 = residuals([x,x+d,x+r*d],c,b)
H1 = (r-1)*(2*x+(r+1)*d)+r+b
H2 = r*(2*x+r*d-b)+b+1
identity('B01-original-difference-01',E0-E1,d*H1)
identity('B02-original-difference-12',E1-E2,-d*H2)
identity('B03-elimination',r*H1-(r-1)*H2,r*(r-1)*d+(b+1)*(r*r-r+1))
identity('B04-linear-system-determinant',(r-1)*r*r-r*(r*r-1),-r*(r-1))
# Same equations, equal adjacent coordinates: for b!=-1 they force a fixed word.
E0,E1,E2=residuals([x,x,e],c,b)
identity('B05-repeated-coordinate',E0-E2,(b+1)*(e-x))
# Exceptional component necessity before choosing the nonfixed branch.
E0,E1,E2=residuals([x,x,e],e-x*x+x,-1)
identity('B06-exception-first',E0,P(0))
identity('B07-exception-last',E2,P(0))
identity('B08-exception-factor',E1,-(e-x)*(e+x+1))
# Endpoint/domain bridge for t=(r+1)/(2(r-1)): its two forbidden values cannot
# occur at r!=0,1; conversely t!=+-1/2 gives r!=0,1.
identity('B09-chart-minus', (r+1)-(r-1),P(2))
identity('B10-chart-plus', (r+1)+(r-1),2*r)
identity('B11-inverse-chart', (2*t+1)-(2*t-1),P(2))
# All residuals under the affine transport; unlike Q01 no cycling is implicit.
alpha=(b+1)*F(1,2); beta=(b-1)*F(1,4)
word=[x,d,e]; sigma=sum(word); transformed=[alpha*z+beta for z in word]
C=alpha*alpha*c-2*alpha*beta*sigma-5*beta*beta
for i,(before,after) in enumerate(zip(residuals(word,c,1),residuals(transformed,C,b))):
    identity(f'B{12+i}-transport-{i}',after,alpha*alpha*before)
# Supplementary certificate for the hand-written transition from linear to
# quadratic domination, universally in w and v (sign hypotheses in the article and supplement).
identity('B15-escape-factor',2*(-w*w+8*v*w-5*v*v)+w*w,-w*(w-16*v)-10*v*v)
# In b=0 these are exactly numerator/denominator changes in Poonen 1(3).
L=2*r*(r-1); X=r**3-r*r+1; Y=r**3-3*r*r+2*r-1; Z=-(r**3-r*r+2*r-1)
tau=r-1
identity('B16-poonen-denominator',L,2*tau*(tau+1))
identity('B17-poonen-x',X,tau**3+2*tau*tau+tau+1)
identity('B18-poonen-y',Y,tau**3-tau-1)
identity('B19-poonen-z',Z,-(tau**3+2*tau*tau+3*tau+1))
identity('B20-poonen-c',Z*L-Y*Y,-(tau**6+2*tau**5+4*tau**4+8*tau**3+9*tau*tau+4*tau+1))
# Concrete rational countercontrol of a forbidden promotion: affine word
# transport is not planar conjugacy even when b!=0,-1.
# b=3: alpha=2, beta=1/2; b=1 word (-3,3,0), q=-6, C=-101/4.
def mapf(point, constant, linear):
    u,z=point; return (z,z*z+constant+linear*u)
def T(point):return tuple(2*z+F(1,2) for z in point)
left=mapf(T((F(0),F(0))),-F(101,4),3)
right=T(mapf((F(0),F(0)),-6,1))
assert left != right
out={'claim':'PUB15-Q03','purpose':'audit necessity/domain/translation bridges; not a third complete route',
     'python':platform.python_version(),'arithmetic':'standard-library Fraction sparse polynomials',
     'checks':checks,'nonconjugacy_countercontrol':{'b':3,'q':-6,'C':'-101/4','point':['0','0'],
      'f_C_b_after_T':list(map(str,left)),'T_after_f_q_1':list(map(str,right))},
     'passed':True,'kernel_proof':False,
     'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
p=argparse.ArgumentParser();p.add_argument('--output');args=p.parse_args()
text=json.dumps(out,indent=2,ensure_ascii=False)+'\n'
if args.output:Path(args.output).write_text(text)
else:print(text,end='')
