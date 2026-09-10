"""Default-off BaseInv range/algebra model. No production assembly changes."""
import hashlib, itertools, json, pathlib, random, re, sys
P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P.parent))
import generate as g
import verify as v
Q, R, CORR = 3457, 65536, 32768*3457
PROD = P.parents[2]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
fixed = json.loads((P.parent/'baseinv-fixed-scale/candidate-model.json').read_text())

def ceilbound(t):
    assert t+CORR < 2**31
    return (t+CORR)//R

# No reliance on a sampled Forward maximum: accept every stored signed16 value.
ab = 32768*1972
early0, early1 = ceilbound(2*ab), ceilbound(ab)
wide = [early0*1728+ab, early1*1728+2*ab, 3*ab]
assert max(wide) < 2**31 and max(early0, early1) < 32768
# Exact SQRDMULH quotient buckets for the entire enlarged D1 accumulator interval.
lo, hi = -max(wide), max(wide)
recip, half, den = 621199, 1<<30, 1<<31
minimum, maximum, covered = Q, -Q, 0
for h in range((lo*recip+half)//den, (hi*recip+half)//den+1):
    a=max(lo, -((-(h*den-half))//recip))
    b=min(hi, ((h+1)*den-half-1)//recip)
    if a>b: continue
    minimum=min(minimum,a-h*Q);maximum=max(maximum,b-h*Q);covered+=b-a+1
assert covered==hi-lo+1 and -Q<minimum<=maximum<Q

class Fused(g.DAG):
    def fixed(self,a):
        z=self.binary('mul',a,'rmod')
        t=self.binary('sqrdmulh',a,'rhat')
        self.emit(f'mls V<{z}>.8h, V<{t}>.8h, V<q>.8h')
        return z
    def minuswide(self,a,b,acc):
        for op,reg,shape,ashape in [('smlsl',acc[0],'4s','4h'),('smlsl2',acc[1],'4s','8h')]:
            self.emit(f'{op} V<{reg}>.{shape}, V<{a}>.{ashape}, V<{b}>.{ashape}')
        return acc

def fused(tiles=1):
    d=Fused();d.constant('rmod',-147);d.constant('rhat',-1393)
    for tile in range(tiles):
        a,b,c=[d.fixed(d.load(f'in{tile}_{i}','x1',48*tile+16*i)) for i in range(3)]
        z=d.load(f'z{tile}','x2',16*tile)
        u=d.mm(b,c);w=d.mm(c,c)
        n2=d.redc(d.minuswide(a,c,d.wide(b,b)))
        n0=d.redc(d.minuswide(u,z,d.wide(a,a)))
        n1=d.redc(d.minuswide(a,b,d.wide(w,z)))
        h=d.redc(d.wide(n1,c,d.wide(n2,b)))
        det=d.redc(d.wide(n0,a,d.wide(h,z)))
        for i,n in enumerate([n0,n1,n2]):d.store(n,'x0',48*tile+16*i)
        d.store(det,'x3',16*tile)
    return d.lines

def finish_no_center():
    d=g.DAG();d.constant('rinv',-682);d.constant('rinvhat',-6464)
    a=[d.load(f'a{i}','x0',16*i) for i in range(3)]
    den=d.load('den','x1')
    corrected=d.binary('mul',den,'rinv');h=d.binary('sqrdmulh',den,'rinvhat')
    d.emit(f'mls V<{corrected}>.8h, V<{h}>.8h, V<q>.8h')
    shared=d.binary('mul',corrected,'qi')
    for i,x in enumerate(a):d.store(d.mm(x,corrected,shared),'x0',16*i)
    return d.lines

def peak_live(code):
    live=set();peak=0
    for line in reversed(code):
        op=line.split()[0];s=re.findall(r'<(\w+)>',line)
        if not s:continue
        defs=set() if op=='str' else {s[0]}
        uses=set(s if op=='str' else s[1:])
        if op in ('smlal','smlal2','smlsl','smlsl2','mls'):uses|=defs
        live=(live-defs)|uses;peak=max(peak,len(live))
    assert not live
    return peak

# Scalar polynomial ring certificate: evaluate the fused scale ledger formally.
# Coefficients are modulo q; variables a,b,c,z, so this is not random evidence.
def add(a,b,sign=1):
    out=dict(a)
    for m,c in b.items():out[m]=(out.get(m,0)+sign*c)%Q
    return {m:c for m,c in out.items() if c}
def mul(a,b):
    out={}
    for m,c in a.items():
        for n,d in b.items():
            k=tuple(x+y for x,y in zip(m,n));out[k]=(out.get(k,0)+c*d)%Q
    return {m:c for m,c in out.items() if c}
def scale(a,s):return {m:c*s%Q for m,c in a.items() if c*s%Q}
vars=[{tuple(int(i==j) for j in range(4)):1} for i in range(4)]
a,b,c,z=vars;ri=pow(R,-1,Q)
n0=add(mul(a,a),mul(z,mul(b,c)),-1)
n1=add(mul(z,mul(c,c)),mul(a,b),-1)
n2=add(mul(b,b),mul(a,c),-1)
det=add(mul(a,n0),mul(z,add(mul(b,n2),mul(c,n1))))
ar,br,cr,zr=[scale(x,R) for x in vars]
red=lambda x:scale(x,ri)
u=red(mul(br,cr));w=red(mul(cr,cr))
f2=red(add(mul(br,br),mul(ar,cr),-1))
f0=red(add(mul(ar,ar),mul(u,zr),-1))
f1=red(add(mul(w,zr),mul(ar,br),-1))
h=red(add(mul(f2,br),mul(f1,cr)))
fd=red(add(mul(h,zr),mul(f0,ar)))
assert [f0,f1,f2,fd]==[scale(x,R) for x in [n0,n1,n2,det]]

# Fused range chain, all intermediates including REDC correction fit signed32.
A=3013; Z=1728
U=ceilbound(A*A); N2=ceilbound(2*A*A)
N01=ceilbound(A*A+U*Z)
H=ceilbound((N2+N01)*A)
D=ceilbound(H*Z+N01*A)
assert max(U,N2,N01,H,D)<4000
assert D<=2000  # existing prefix/recovery/inversion bound is preserved

# Scalar mirror with exact signed REDC, test each FR0 root and edge representatives.
src=(PROD/'gt864_fr0_basemul_tables.h').read_text().split('gt864_fr0_zetas_mul',1)[1].split('=',1)[1].split(';',1)[0]
zetas=list(map(int,re.findall(r'-?\d+',src)));assert len(zetas)==288
def fixed_r(x):return v.signed(x*(-147)-((x*(-1393)+16384)//32768)*Q)
def num(x,z):
    a,b,c=map(fixed_r,x)
    u=v.redc(b*c);w=v.redc(c*c)
    n2=v.redc(b*b-a*c)
    n0=v.redc(a*a-u*z);n1=v.redc(w*z-a*b)
    h=v.redc(n2*b+n1*c);d=v.redc(h*z+n0*a)
    return [n0,n1,n2],d
rng=random.Random(8640910);cases=0
edge=[-32768,-3457,-1,0,1,3457,32767]
for zr in zetas:
    for x in itertools.chain(itertools.product(edge,repeat=3),
                             ([rng.randrange(-32768,32768) for _ in range(3)] for _ in range(32))):
        ns,d=num(x,zr);a,b,c=x;z=zr*ri%Q
        expected=[a*a-z*b*c,z*c*c-a*b,b*b-a*c]
        expected_d=a*expected[0]+z*(b*expected[2]+c*expected[1])
        assert [t%Q for t in ns+[d]]==[t*R%Q for t in expected+[expected_d]]
        assert max(map(abs,ns))<=max(N2,N01) and abs(d)<=D
        if d%Q:
            # Equivalent to recovered inverse denominator R1, then finish R1->R0.
            inv0=pow(d*ri%Q,-1,Q)
            out=[v.redc(n*v.center(inv0)) for n in ns]
            assert max(map(abs,out))<=1972
            assert v.cubic(x,out,z)==[1,0,0]
        cases+=1

# Execute unchanged real symbolic prefix/inverse/recovery DAGs and the new finish
# model for complete 36-tile batches. No Python pow shortcut for batch inversion.
completed=failed=0
for case in range(24):
    inp=[rng.randrange(-32768,32768) for _ in range(864)] if case else [0]*864
    nums=[];dens=[]
    for tile in range(36):
        ns=[];ds=[]
        for lane in range(8):
            n,d=num(inp[tile*24+lane:(tile+1)*24:8],zetas[tile*8+lane])
            ns.append(n);ds.append(d)
        nums.append([ns[l][c] for c in range(3) for l in range(8)]);dens.append(ds)
    triples=[sum([dens[i+12*k] for k in range(3)],[]) for i in range(12)]
    pref=[triples[0]]
    for i in range(1,12):pref.append(v.run('baseinv_prefix',{'x0':[0]*24,'x1':pref[-1],'x2':triples[i]})['x0'])
    if any(x==0 for x in pref[-1]):failed+=1;continue
    running=v.run('baseinv_inverse',{'x0':[0]*24,'x1':pref[-1]})['x0']
    invden=[None]*12
    for i in range(11,0,-1):
        out=v.run('baseinv_recover',{'x0':[0]*24,'x1':pref[i-1],'x2':running,'x3':triples[i]})
        invden[i]=out['x0'];running=out['x2']
    invden[0]=running
    for tile in range(36):
        chain,i=divmod(tile,12)
        buffers={'x0':nums[tile],'x1':invden[i][8*chain:8*(chain+1)]}
        out=v.run('unused',buffers,finish_no_center())['x0']
        centered=v.run('unused',buffers,fixed['baseinv_finish'])['x0']
        assert [v.center(x) for x in out]==centered and max(map(abs,out))<=1972
        for lane in range(8):
            assert v.cubic(inp[tile*24+lane:(tile+1)*24:8],out[lane::8],zetas[tile*8+lane]*ri%Q)==[1,0,0]
    completed+=1
assert completed>8 and failed>=1

result={'status':'algebra-and-range-pass','production_changed':False,
 'no_centering':{'input_inverse_bound':1972,'other_operand_bound':32768,
   'early_product_bounds':[2*ab,ab],'early_REDC_bounds':[early0,early1],
   'final_accumulator_bounds':wide,'D1_output_bound':[minimum,maximum],
   'quotient_bucket_inputs_covered':covered,
   'consumer_paths':['Keygen:g * finv -> h -> ToBytes_small',
                     'Keygen:f * ginv -> hinv -> ToBytes_small'],
   'centering_arithmetic_removed_per_call':648,
   'finish_instructions':[len(fixed['baseinv_finish']),len(finish_no_center())],
   'complete_symbolic_batches_pass':completed,'zero_batches_detected':failed,
   'full_KEM_physical_test':False},
 'fused_numerator':{'formal_polynomial_identity':'pass',
   'range':{'input_R1':A,'u_and_w':U,'n2':N2,'n0_n1':N01,'h':H,'den':D},
   'edge_and_random_cases':cases,'REDC_per_tile':7,
   'input_scale':'R0','internal_and_output_scale':'R1',
   'fixed_scale_baseline_instructions':len(fixed['baseinv_num']),
   'fused_one_tile_instructions':len(fused()),
   'fused_two_tile_shared_constants_instructions':len(fused(2)),
   'one_tile_vector_liveness_peak':peak_live(fused()),
   'two_tile_sequential_vector_liveness_peak':peak_live(fused(2)),
   'physical_assembly_test':False},
 'source_sha256':{str(f.relative_to(P.parents[2])):hashlib.sha256(f.read_bytes()).hexdigest()
   for f in [PROD/'kem.c',PROD/'Makefile',PROD/'gt864_fr0_basemul_d1.c',
             PROD/'gt864_fr0_basemul_tables.h',P.parent/'generate.py',
             PROD/'gt864_poly_api.c',P/'baseinv-proof.py',
             P.parent/'baseinv-fixed-scale/build/pi-20260910/official-source/base.s',
             P.parent/'baseinv-fixed-scale/candidate-model.json']}}
if __name__=='__main__':
    (P/'baseinv-results.json').write_text(json.dumps(result,indent=2)+'\n')
    # Instruction-list model only, not a candidate .S before a kernel contract.
    (P/'fused-numerator-model.json').write_text(json.dumps(fused(),indent=2)+'\n')
    (P/'finish-no-center-model.json').write_text(json.dumps(finish_no_center(),indent=2)+'\n')
    print(json.dumps(result,indent=2))
