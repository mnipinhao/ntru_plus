"""Execute authored symbolic instructions; not physical assembly execution.

Checks exact widening/wrapping semantics, scalar cubic identities, and complete
36-tile/3-chain BaseInv flow. Analytic bounds are separate from random tests.
"""
import json,random,re
from pathlib import Path

P=Path(__file__).resolve().parent
Q=3457;R=65536;RI=pow(R,-1,Q)
def signed(x,bits=16):return (x+(1<<(bits-1)))%(1<<bits)-(1<<(bits-1))
def pack(xs,width=2):return b''.join((x%(1<<(8*width))).to_bytes(width,'little') for x in xs)
def unpack(x,width=2):return [int.from_bytes(x[i:i+width],'little',signed=True) for i in range(0,len(x),width)]
def redc(x):return (x+signed(x*-12929)*Q)//R
def center(x):return (x+1728)%Q-1728
CODES={p.parent.name:[l.strip() for l in p.read_text().splitlines()
       if l.startswith('    ') and l.strip()!='ret' and not l.strip().startswith('//')] for p in P.glob('*/candidate.sym.S')}

def run(kernel, buffers, code=None):
    mem={k:bytearray(pack(v)) for k,v in buffers.items()};regs={};w=0;scalar={}
    for line in CODES[kernel] if code is None else code:
        op=line.split()[0];s=re.findall(r'<(\w+)>',line)
        imm=[int(x) for x in re.findall(r'#(-?\d+)',line)]
        if op=='mov':w=imm[0]
        elif op=='dup':regs[s[0]]=pack([w]*8)
        elif op in ('ldr','str'):
            ptr=re.search(r'\[(x\d+)',line)[1];off=imm[0]
            assert off+16<=len(mem[ptr]),line
            if op=='ldr':regs[s[0]]=bytes(mem[ptr][off:off+16])
            else:mem[ptr][off:off+16]=regs[s[0]]
        elif op=='umov':
            lane=int(re.search(r'\.h\[(\d+)\]',line)[1])
            scalar[re.search(r'\bw\d+',line)[0]]=unpack(regs[s[0]])[lane]&65535
        elif op=='strh':
            ptr=re.search(r'\[(x\d+)',line)[1];off=imm[0]
            assert off+2<=len(mem[ptr])
            mem[ptr][off:off+2]=pack([scalar[re.search(r'\bw\d+',line)[0]]])
        elif op=='ext':regs[s[0]]=(regs[s[1]]+regs[s[2]])[imm[0]:imm[0]+16]
        elif op=='orr':regs[s[0]]=bytes(x|y for x,y in zip(regs[s[1]],regs[s[2]]))
        elif op in ('smull','smull2','smlal','smlal2'):
            a,b=[unpack(regs[x]) for x in s[1:]];idx=4 if op.endswith('2') else 0
            old=unpack(regs[s[0]],4) if op.startswith('smlal') else [0]*4
            val=[old[i]+a[idx+i]*b[idx+i] for i in range(4)]
            assert all(-(1<<31)<=x<(1<<31) for x in val),line
            regs[s[0]]=pack(val,4)
        elif op in ('uzp1','uzp2'):
            a,b=[unpack(regs[x]) for x in s[1:]];par=int(op[-1])-1
            regs[s[0]]=pack(a[par::2]+b[par::2])
        elif op=='and':regs[s[0]]=bytes(x&y for x,y in zip(regs[s[1]],regs[s[2]]))
        elif op=='sshr':regs[s[0]]=pack([x>>imm[0] for x in unpack(regs[s[1]])])
        elif op in ('mul','add','sub','mls','sqrdmulh','cmgt'):
            a,b=[unpack(regs[x]) for x in s[1:]]
            lane=re.search(r'\.h\[(\d+)\]',line)
            if lane:b=[b[int(lane[1])]]*8
            if op=='mul':v=[x*y for x,y in zip(a,b)]
            elif op=='add':v=[x+y for x,y in zip(a,b)]
            elif op=='sub':v=[x-y for x,y in zip(a,b)]
            elif op=='mls':v=[z-x*y for z,x,y in zip(unpack(regs[s[0]]),a,b)]
            elif op=='cmgt':v=[-1 if x>y else 0 for x,y in zip(a,b)]
            else:v=[max(-32768,min(32767,(x*y+16384)//32768)) for x,y in zip(a,b)]
            if op in ('add','sub'):assert all(-32768<=x<=32767 for x in v),line
            regs[s[0]]=pack(v)
        else:raise AssertionError(line)
    return {k:unpack(v) for k,v in mem.items()}

def cubic(a,b,z):
    return [(a[0]*b[0]+z*(a[1]*b[2]+a[2]*b[1]))%Q,
      (a[0]*b[1]+a[1]*b[0]+z*a[2]*b[2])%Q,
      (a[0]*b[2]+a[1]*b[1]+a[2]*b[0])%Q]

def main():
    # Mathematical bound: t is signed int16 and REDC numerator divisible by R.
    correction=32768*Q
    assert R%Q==Q-147 and (R*R)%Q==867
    assert Q*(-12929)%R==R-1
    initial=(32768*867+correction)//R
    lazy=(4000*4000+correction)//R
    assert initial==2162 and lazy<2000
    assert 32768*867+correction<2**31
    assert 4000*4000+correction<2**31
    actual_initial=max(abs(redc(x*867)) for x in range(-32768,32768))
    assert actual_initial<=initial
    for x in range(-1999,2000):
        y=x+Q if x<0 else x
        y=y-Q if y>1728 else y
        assert y==center(x)
    # FromBytes BaseMul: conservative union includes all three accumulators.
    early=(2*4095**2+correction)//R
    final=max(3*4095**2, early*1728+2*4095**2)
    assert final==3*4095**2 and final+correction<2**31
    assert (final+correction)//R==2496  # previous 2497 contract is conservative
    rng=random.Random(864)
    prod=P.parents[1]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
    src=(prod/'gt864_fr0_basemul_tables.h').read_text().split('gt864_fr0_zetas_mul',1)[1].split('=',1)[1].split(';',1)[0]
    zetas=list(map(int,re.findall(r'-?\d+',src)))
    assert len(zetas)==288 and max(map(abs,zetas))<=1728
    for case in range(520):
        a=[rng.randrange(4096) for _ in range(24)]
        b=[rng.randrange(4096) for _ in range(24)]
        if case<8:a=[4095 if case&1 else 0]*24;b=[4095 if case&2 else 0]*24
        z=zetas[(case%36)*8:(case%36+1)*8]
        out=run('basemul',{'x0':[0]*24,'x1':a,'x2':b,'x3':z})['x0']
        assert max(map(abs,out))<=2497
        for lane in range(8):
            expected=cubic(a[lane::8],b[lane::8],z[lane]*RI%Q)
            assert [x%Q for x in out[lane::8]]==[x*RI%Q for x in expected]
    # Full 36-tile inverse, 3 independent prefix chains interleaved in scratch.
    # Arithmetic kernels are executed, not replaced with Python mm shortcuts.
    completed=0
    for case in range(12):
        inp=[rng.randrange(-32768,32768) for _ in range(864)]
        if case<2:inp=[32767 if case else -32768]*864
        nums=[];den=[]
        for j in range(36):
            r=run('baseinv_num',{'x0':[0]*24,'x1':inp[j*24:(j+1)*24],
                'x2':zetas[j*8:(j+1)*8],'x3':[0]*8})
            nums.append(r['x0']);den.append(r['x3'])
            assert max(map(abs,r['x0']+r['x3']))<=4000
        triples=[sum([den[i+12*k] for k in range(3)],[]) for i in range(12)]
        pref=[triples[0]]
        for i in range(1,12):pref.append(run('baseinv_prefix',{
            'x0':[0]*24,'x1':pref[-1],'x2':triples[i]})['x0'])
        # Failure detection must occur before inverse3; its precondition excludes 0.
        if any(x%Q==0 for x in pref[-1]):continue
        completed+=1
        running=run('baseinv_inverse',{'x0':[0]*24,'x1':pref[-1]})['x0']
        invden=[None]*12
        for i in range(11,0,-1):
            r=run('baseinv_recover',{'x0':[0]*24,'x1':pref[i-1],'x2':running,'x3':triples[i]})
            invden[i]=r['x0'];running=r['x2']
        invden[0]=running
        for j in range(36):
            k,i=divmod(j,12)
            inv=invden[i][8*k:8*(k+1)]
            out=run('baseinv_finish',{'x0':nums[j],'x1':inv})['x0']
            assert max(map(abs,out))<=1728
            for lane in range(8):
                assert cubic(inp[24*j+lane:24*(j+1):8],out[lane::8],zetas[j*8+lane]*RI%Q)==[1,0,0]
    assert completed>=8,completed
    # Main I16 symbolic differential against the same packed input baseline.
    # Tail shares exactly the same butterfly network/deletion mask; separately
    # compare the known old version reconstructed by the authoring helper.
    import contextlib,importlib.util,io
    with contextlib.redirect_stdout(io.StringIO()):
        spec=importlib.util.spec_from_file_location('gi',P/'generate_inverse.py')
        gi=importlib.util.module_from_spec(spec);spec.loader.exec_module(gi)
    from inverse_range import table,scaled
    stage=table(scaled,'gt864_inverse16_stage_barrett')
    for kind,baseline,scale_name in [('inverse16_lazy',gi.main,'gt864_inverse16_main_scale_barrett'),
        ('inverse_tail_lazy',gi.tail,'gt864_inverse16_tail_scale_barrett')]:
        scale=table(scaled,scale_name)
        for case in range(136):
            inp=[rng.randrange(-3456,3457) for _ in range(128)]
            if case<8:inp=[3456 if ((i>>(case%4))&1) else -3456 for i in range(128)]
            buffers={'x0':[12000]*864,'x1':inp,'x3':stage,'x4':scale}
            a=run(kind,buffers,baseline)['x0'];b=run(kind,buffers)['x0']
            assert [center(x) for x in a]==[center(x) for x in b],(kind,case)
            assert [i for i,x in enumerate(a) if x!=12000]==[i for i,x in enumerate(b) if x!=12000]
    print(json.dumps({'status':'symbolic-model-pass','initial_REDC_bound':initial,
      'initial_REDC_exhaustive_max':actual_initial,'lazy_REDC_bound':lazy,
      'basemul_cases':520,'baseinv_full_inputs':12,'baseinv_successful_roundtrips':completed,
      'inverse_main_and_tail_differentials':272,
      'instruction_counts':{k:len(v) for k,v in CODES.items()},
      'physical_assembly_execution':False,'range_proof':'analytic envelopes plus exhaustive initial conversion'},indent=2))

if __name__=='__main__':main()
