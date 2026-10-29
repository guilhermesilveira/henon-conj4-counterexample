"""V-Q03B: exact real-algebraic checks for affine transport and escape.
Uses Z3/NLSAT, not SymPy or verify_exact.py. The rational lifting, Archimedean
and finite-set steps are proved in the article and supplement. No kernel proof is exported.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess

HERE=Path(__file__).resolve().parent
queries={}
def query(key,description,variables,assumptions,bad,expected='unsat'):
    text='(set-option :timeout 50000)\n(set-logic QF_NRA)\n'
    text+=''.join(f'(declare-fun {v} () Real)\n' for v in variables.split())
    text+=''.join(f'(assert {a})\n' for a in assumptions)
    text+=f'(assert {bad})\n(check-sat-using qfnra-nlsat)\n'
    queries[key]=(description,text,expected)
# R'_i = alpha^2 R_i identically (v0,v1,v2 arbitrary, not assumed a cycle).
transport=['(= (* 2 h) (- b 1))','(= a (+ h 1))', # h=2 beta; a=alpha
           '(= (* 2 beta) h)',
           '(= C (- (* a a q) (* 2 a beta (+ x y z)) (* 5 beta beta)))']
ux='(+ (* a x) beta)';uy='(+ (* a y) beta)';uz='(+ (* a z) beta)'
identity=f'(= (- (+ (* {uy} {uy}) C (* b {ux})) {uz}) (* a a (- (+ (* y y) q x) z)))'
query('Q01','Affine transport residual identity, all real inputs','b h a beta q C x y z',transport,f'(not {identity})')
query('Q02','Nonzero affine scaling preserves nonfixity','a beta x y z',
      ['(not (= a 0))','(or (not (= x y)) (not (= y z)))'],
      f'(and (= {ux} {uy}) (= {uy} {uz}))')
query('Q03','Bound on inherited sum sigma for all t>=1','t D sigma',
      ['(>= t 1)','(= D (- (* 4 t t) 1))','(= (* D sigma) (+ (- (* t D)) (* 8 t)))'],
      '(or (<= D 0) (>= sigma (* 4 t)) (<= sigma (* (- 4) t)))')
# The escape bound uses w=|alpha| t, v=|beta|, |sigma|<4t and q<-t^2.
# First certify the order-product estimate without enumerating parameters.
query('Q04','Quadratic escape bound once w>=16v','w v K',
      ['(> w 0)','(>= v 0)','(>= w (* 16 v))','(< K (+ (- (* w w)) (* 8 v w) (- (* 5 v v))))'],
      '(>= (* 2 K) (- (* w w)))')
# Complete exceptional real locus: a repeated scalar coordinate, not a fixed state.
E=['(= z (+ (* y y) c (- x)))','(= x (+ (* z z) c (- y)))','(= y (+ (* x x) c (- z)))']
nonfixed='(or (not (= x y)) (not (= y z)))'
components='(or (and (= x y) (= z (- (- x) 1)) (= c (- (- (* x x)) 1)) (not (= (* 2 x) (- 1)))) (and (= y z) (= x (- (- y) 1)) (= c (- (- (* y y)) 1)) (not (= (* 2 y) (- 1)))) (and (= z x) (= y (- (- z) 1)) (= c (- (- (* z z)) 1)) (not (= (* 2 z) (- 1)))))'
query('Q05','Every nonfixed b=-1 cycle lies in the three explicit components','x y z c',E+[nonfixed],f'(not {components})')
query('Q06','All three exceptional components close and are nonfixed','x y z c',[components],f'(not (and {" ".join(E)} {nonfixed}))')
query('Q07','Exceptional c_n=-n^2-1 strictly decreases on n>=0','m n',
      ['(>= n 0)','(> m n)'], '(>= (- (- (* m m)) 1) (- (- (* n n)) 1))')
query('C01','Dropping the nonzero scale allows collapse','a beta x y z',
      ['(= a 0)',nonfixed],f'(and (= {ux} {uy}) (= {uy} {uz}))','sat')
query('C02','The excluded exceptional a=-1/2 is fixed','x y z c',
      E+['(= x y)','(= (* 2 x) (- 1))'],'(and (= x y) (= y z))','sat')
query('C03','Changing c by 1 destroys transport','b h a beta q C x y z',transport,
      f'(not (= (- (+ (* {uy} {uy}) (+ C 1) (* b {ux})) {uz}) (* a a (- (+ (* y y) q x) z))))','sat')
query('C04','Without threshold, claimed quadratic bound fails','w v K',
      ['(> w 0)','(>= v 0)','(< K (+ (- (* w w)) (* 8 v w) (- (* 5 v v))))'],
      '(>= (* 2 K) (- (* w w)))','sat')
p=argparse.ArgumentParser();p.add_argument('--output');args=p.parse_args()
solver=shutil.which('z3')
if not solver: raise RuntimeError('z3 is required')
rows=[]
for key,(description,source,expected) in queries.items():
    path=HERE/'queries'/f'{key}.smt2'
    # Frozen queries must agree with this readable specification on subsequent runs.
    path.parent.mkdir(exist_ok=True)
    if path.exists() and path.read_text()!=source:raise RuntimeError(f'query drift: {key}')
    path.write_text(source)
    result=subprocess.run([solver,'-smt2',str(path)],capture_output=True,text=True,timeout=55)
    answer=result.stdout.strip()
    if result.returncode or result.stderr or answer!=expected:raise RuntimeError((key,result.returncode,answer,result.stderr))
    rows.append({'id':key,'description':description,'expected':expected,'answer':answer,'input_sha256':hashlib.sha256(source.encode()).hexdigest()})
    print(f'{key}: {answer}',flush=True)
out={'claim':'PUB15-Q03','route':'V-Q03B','python':platform.python_version(),'solver':subprocess.check_output([solver,'-version'],text=True).strip(),'decisions':rows,'passed':True,'kernel_proof':False,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Universal algebraic obligations only; full rational infinitude proof and dependencies in the article and supplement.'}
text=json.dumps(out,indent=2,ensure_ascii=False)+'\n'
if args.output:Path(args.output).write_text(text)
else:print(text,end='')
