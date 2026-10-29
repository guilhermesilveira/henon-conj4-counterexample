"""PUB15-F04: exact polynomial/ideal verification, not finite sampling.
Run: python3 reproducibility/period4/verify.py [--output FILE]
Requires Python 3 and SymPy. Does not execute preserved scientific scripts.
"""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import sympy as sp


def run():
    checks = {}
    bases = {}

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks[name] = True

    def zero(name, expr):
        check(name, sp.cancel(expr) == 0)

    x, y, z, w, c, h, k = sp.symbols('x y z w c h k')
    variables = [h, w, z, y, c, x]
    cycle = [z-y**2-c-x, w-z**2-c-y, x-w**2-c-z, y-x**2-c-w]
    primitive = cycle + [h*(z-x)-1]

    def gb(fs, vs=variables):
        return sp.groebner(fs, *vs, domain=sp.QQ, order='lex')

    def record(name, fs, vs=variables):
        g = gb(fs, vs)
        bases[name] = {'variables': list(map(str, vs)),
                       'inputs': list(map(str, fs)),
                       'basis': [str(p.as_expr()) for p in g.polys]}
        return g

    def intersect(a, b):
        g = gb([k*f for f in a]+[(1-k)*f for f in b], [k]+variables)
        return [p.as_expr() for p in g.polys if not p.as_expr().has(k)]

    period2 = [z-x, w-y, x**2+c, y**2+c]
    check('lower_period_exact_ideal', gb(cycle+[z-x]) == gb(period2))
    check('either_opposite_difference_zero_same_locus',
          gb(cycle+[z-x]) == gb(cycle+[w-y]))
    components = []
    for eps in [1, -1]:
        components.append([z+x-2*eps, y-eps*x+1+eps,
                           c+1+(eps-x)**2, w-y+(x-z)*eps,
                           h*(z-x)-1])
    components.append([x*x+z*z+2*c, 2*(w-y)-(z*z-x*x),
                       (x+z)*(y+w)+4,
                       (z*z-x*x)**2-4*(x+z)**2-16,
                       h*(z-x)-1])
    original = record('primitive_original_equations', primitive)
    gs = [record(name, fs) for name, fs in zip(['Lplus','Lminus','C'], components)]
    full = intersect(intersect(components[0], components[1]), components[2])
    check('original_equals_intersection_of_three_ideals', original == gb(full))
    H = (x*x+c)**2+2*c-4
    F = H**2+4*x*x*(x*x+2*c)
    Eplus = c+x*x-2*x+2
    Eminus = c+x*x+2*x+2
    for name, g, f in zip(['Lplus','Lminus','C','union'], gs+[original],
                          [Eplus,Eminus,F,Eplus*Eminus*F]):
        es = [p.as_expr() for p in g.polys if not p.as_expr().has(h,w,z,y)]
        check(name+'_exact_elimination_kernel', gb(es,[c,x]) == gb([f],[c,x]))
    z_it=y*y+c+x; w_it=z_it*z_it+c+y
    resultant=sp.resultant(x-w_it*w_it-c-z_it,y-x*x-c-w_it,y)
    zero('raw_resultant_all_factors',resultant-(c+x*x)**2*Eplus*Eminus*F)
    check('plane_C_degree_8', sp.Poly(F,x,c).total_degree() == 8)
    check('plane_union_degree_12', sp.Poly(Eplus*Eminus*F,x,c).total_degree() == 12)

    # Difference/sum presentation linked to ALL original equations.
    S,T,A,B = sp.symbols('S T A B')
    sub = {x:(S-A)/2, z:(S+A)/2, y:(T-B)/2, w:(T+B)/2}
    changed = [sp.expand(e.subs(sub, simultaneous=True)) for e in cycle]
    target = [2*A+B*T, 2*B-A*S, S*S+A*A+4*c,T*T+B*B+4*c]
    vs=[T,B,c,A,S]
    check('sum_difference_ideal_equality', gb(changed,vs)==gb(target,vs))
    residual = (S*S+A*A-T*T-B*B).subs({T:-4/S,B:A*S/2})
    zero('factor_after_localization', residual-(4-S*S)*(S*S*A*A-4*S*S-16)/(4*S*S))

    # Rational parametrizations; equations are identities in Q(t), Q(r).
    t, r, U, v = sp.symbols('t r U v')
    params = {}
    for eps in [1,-1]:
        params[str(eps)] = [eps-t, -eps-eps*t, eps+t, -eps+eps*t, -1-t*t]
    Sr=r-1/r; Ur=r+1/r
    params['C']=[(Sr-2*Ur/Sr)/2,(-4/Sr-Ur)/2,
                 (Sr+2*Ur/Sr)/2,(-4/Sr+Ur)/2,-Sr**2/4-Ur**2/Sr**2]
    for name, p in params.items():
        d=dict(zip([x,y,z,w,c],p))
        for i,e in enumerate(cycle):
            zero(name+'_cycle_'+str(i),e.subs(d, simultaneous=True))
        if name=='C':
            zero('C_inverse_parameter', ((w-y+x+z)/2).subs(d,simultaneous=True)-r)
        else:
            zero(name+'_inverse_parameter', ((z-x)/2).subs(d,simultaneous=True)-t)
    zero('C_c_formula',params['C'][4]+(r**8+14*r**4+1)/(4*r*r*(r*r-1)**2))
    zero('C_conic', Ur*Ur-Sr*Sr-4)
    # Projective conic has no singular point: gradients vanish only at origin.
    V=sp.symbols('V'); conic=U*U-S*S-4*V*V
    check('conic_gradient_origin_only',gb([sp.diff(conic,a) for a in [U,S,V]], [U,S,V])==gb([U,S,V],[U,S,V]))
    zero('conic_rational_point', conic.subs({U:2,S:0,V:1}))

    # Base-free maps into P^5 [x:y:z:w:c:1], both source charts.
    projective={}
    for name,p in params.items():
        a = r if name=='C' else t
        denominator = 4*r*r*(r*r-1)**2 if name=='C' else sp.Integer(1)
        fs=[sp.cancel(q*denominator) for q in p]+[denominator]
        degree=max(sp.degree(q,a) for q in fs)
        forms=[sp.Poly(q,a) for q in fs]
        opposite=[sp.expand(sum(coef*a**(degree-mon[0]) for mon,coef in q.terms())) for q in forms]
        for chart,vals in [('finite',fs),('infinity',opposite)]:
            check(name+'_no_basepoint_'+chart, gb(vals,[a])==gb([1],[a]))
        projective[name]={'degree':int(degree),'finite_chart':list(map(str,fs)),
                          'infinity_chart':list(map(str,opposite))}
    # Boundary/poles of the marked model: no omitted cancellation of c.
    cn,cd=map(sp.expand,sp.fraction(sp.cancel(params['C'][4])))
    check('C_no_cancellation',sp.gcd(cn,cd)==1)
    check('C_fiber_degree_eight', sp.degree(cn-v*cd,r)==8)
    check('C_c_four_double_poles',sp.factor(cd)==4*r*r*(r-1)**2*(r+1)**2 and sp.degree(cn,r)-sp.degree(cd,r)==2)
    check('line_fiber_degree_two',sp.degree(-1-t*t-v,t)==2)
    n,m=sp.symbols('n m')
    zero('ordered_integer_witness_difference',(-1-n*n)-(-1-m*m)-(m-n)*(m+n))

    # Direct lifting of plane C in the open x != 0.
    zz=H/(2*x); ss=x+zz; uu=-(c+x*x)
    lift={z:zz,y:(-4/ss-uu)/2,w:(-4/ss+uu)/2}
    for i,e in enumerate(cycle):
        numerator=sp.fraction(sp.cancel(e.subs(lift,simultaneous=True)))[0]
        check('plane_C_lift_mod_ideal_'+str(i),gb([F],[c,x]).reduce(numerator)[1]==0)
    check('plane_C_x0_fiber',sp.expand(F.subs(x,0))==sp.expand((c*c+2*c-4)**2))
    # S=0 incompatible even before excluding nonprimitive points.
    check('plane_C_S_zero_impossible',gb([F,H+2*x*x,h*x-1],[h,c,x])==gb([1],[h,c,x]))
    for name,q in [('plus',params['1']),('minus',params['-1'])]:
        zero('plane_intersection_'+name,F.subs({x:q[0],c:q[4]},simultaneous=True)+16*(t*t-2))
    zero('C_A_zero_fixed_projection',F.subs(c,1)-(x*x+1)**4)

    # Rotation and invariants of the normalized component quotients.
    rho=(r+1)/(1-r)
    for i in range(4):
        zero('C_rotation_'+str(i),params['C'][i].subs(r,rho)-params['C'][(i+1)%4])
    vr=sp.cancel(Sr-4/Sr)
    zero('quotient_v_rotation',vr.subs(r,rho)-vr)
    zero('quotient_c',params['C'][4]+3+vr*vr/4)
    zero('quotient_lift_quartic',r**4-vr*r**3-6*r*r+vr*r+1)
    for eps in [1,-1]:
        p=params[str(eps)]; q=[a.subs(t,eps*t) if hasattr(a,'subs') else a for a in params[str(-eps)]]
        for i in range(4): zero('line_rotation_'+str(eps)+'_'+str(i),q[i]-p[(i+1)%4])

    # Adversarial controls target incorrect universality/lifting/minimality.
    controls={}
    def expect_fail(name,call):
        try: call()
        except AssertionError: controls[name]='rejected as expected'
        else: raise AssertionError('control accepted: '+name)
    expect_fail('wrong_sign_of_c',lambda:zero('bad_c', cycle[0].subs(dict(zip([x,y,z,w,c],params['1'][:4]+[1+t*t])),simultaneous=True)))
    expect_fail('remove_a_line_component',lambda:check('bad_components',original==gb(intersect(components[0],components[2]))))
    # t=0 is exactly period 2, not minimum 4.
    p0=[sp.sympify(a).subs(t,0) for a in params['1']]
    check('t0_is_period2',p0[2]==p0[0] and p0[3]==p0[1] and p0[0]!=p0[1])
    controls['quotient_v0_no_Q_lift']='S^2=4 and U^2=8: no rational U (proved in the article and supplement)'
    controls['quotient_line_a_minus1_no_Q_lift']='t^2=-1: no rational t (proved in the article and supplement)'
    controls['all_c_false']='all rational primitive c<-1 (proved in the article and supplement); c=0 excluded'
    return {'python':platform.python_version(),'sympy':sp.__version__,'checks':checks,
            'groebner_bases':bases,'projective_maps':projective,'adversarial_controls':controls,
            'trust':'Exact rational symbolic computation; trust SymPy/Python and theorem application in the article and supplement. No kernel proof and no sampling proof.',
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output'); args=parser.parse_args()
    result=run(); out=json.dumps(result,indent=2)+'\n'
    if args.output: Path(args.output).write_text(out)
    else: print(out,end='')
    print(str(len(result['checks']))+' exact checks passed')
