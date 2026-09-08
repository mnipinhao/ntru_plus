"""Author arithmetic DAGs, not physical register allocation. Prints apply_patch.

Run check-kernel-contract.py for all six contracts before this generator.
The C references remain the oracle; these regions do not contain public wrappers.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class DAG:
    def __init__(self):
        self.lines = []
        self.seq = 0
        self.constant('q', 3457)
        self.constant('qi', -12929)
    def emit(self, text): self.lines.append(text)
    def fresh(self):
        self.seq += 1
        return f'tmpv_{self.seq}'  # t0..tN are Slothy HINT registers.
    def constant(self, name, value):
        self.emit(f'mov w8, #{value}')
        self.emit(f'dup V<{name}>.8h, w8')
        return name
    def load(self, name, ptr, offset=0):
        self.emit(f'ldr Q<{name}>, [{ptr}, #{offset}]')
        return name
    def store(self, name, ptr, offset=0):
        self.emit(f'str Q<{name}>, [{ptr}, #{offset}]')
    def binary(self, op, a, b):
        dst=self.fresh()
        self.emit(f'{op} V<{dst}>.8h, V<{a}>.8h, V<{b}>.8h')
        return dst
    def wide(self, a, b, acc=None):
        lo,hi = (self.fresh(),self.fresh()) if acc is None else acc
        op='smull' if acc is None else 'smlal'
        self.emit(f'{op} V<{lo}>.4s, V<{a}>.4h, V<{b}>.4h')
        self.emit(f'{op}2 V<{hi}>.4s, V<{a}>.8h, V<{b}>.8h')
        return lo,hi
    def redc(self, acc):
        lo,hi=acc
        low=self.fresh()
        self.emit(f'uzp1 V<{low}>.8h, V<{lo}>.8h, V<{hi}>.8h')
        quotient=self.binary('mul',low,'qi')
        self.wide(quotient,'q',acc)
        dst=self.fresh()
        self.emit(f'uzp2 V<{dst}>.8h, V<{lo}>.8h, V<{hi}>.8h')
        return dst
    def mm(self, a, b, bqi=None):
        # REDC(a*b), sharing b*(-q^-1) where requested.
        if bqi is None: bqi=self.binary('mul',b,'qi')
        quotient=self.binary('mul',a,bqi)
        lo,hi=self.wide(a,b)
        self.wide(quotient,'q',(lo,hi))
        dst=self.fresh()
        self.emit(f'uzp2 V<{dst}>.8h, V<{lo}>.8h, V<{hi}>.8h')
        return dst
    def center_constants(self, loose=True):
        if loose:self.constant('recip',9)
        self.constant('halfq',1728)
    def center(self,a,loose=True):
        # Exact same normalization as lazy BaseInv reference, not a theorem
        # transplant of refined Barrett from another modulus.
        if loose:
            quot=self.binary('sqrdmulh',a,'recip')
            self.emit(f'mls V<{a}>.8h, V<{quot}>.8h, V<q>.8h')
        sign=self.fresh()
        self.emit(f'sshr V<{sign}>.8h, V<{a}>.8h, #15')
        self.emit(f'and V<{sign}>.16b, V<{sign}>.16b, V<q>.16b')
        a=self.binary('add',a,sign)
        mask=sign
        self.emit(f'cmgt V<{mask}>.8h, V<{a}>.8h, V<halfq>.8h')
        self.emit(f'and V<{mask}>.16b, V<{mask}>.16b, V<q>.16b')
        return self.binary('sub',a,mask)

def basemul():
    d=DAG()
    a=[d.load(f'a{i}','x1',16*i) for i in range(3)]
    b=[d.load(f'b{i}','x2',16*i) for i in range(3)]
    z=d.load('z','x3')
    c0=d.wide(a[2],b[1]);d.wide(a[1],b[2],c0)
    c1=d.wide(a[2],b[2])
    r0=d.redc(c0);r1=d.redc(c1)
    p0=d.wide(r0,z);d.wide(a[0],b[0],p0)
    p1=d.wide(r1,z);d.wide(a[0],b[1],p1);d.wide(a[1],b[0],p1)
    p2=d.wide(a[2],b[0]);d.wide(a[1],b[1],p2);d.wide(a[0],b[2],p2)
    for i,p in enumerate([p0,p1,p2]):d.store(d.redc(p),'x0',16*i)
    return d

def numerator():
    d=DAG();r2=d.constant('r2',867)
    a,b,c=[d.load(f'in{i}','x1',16*i) for i in range(3)]
    z=d.load('z','x2')
    # full-i16 * 867 plus REDC correction fits i32; output <=2162.
    # All later products accept <=4000, so input centering is redundant.
    a,b,c=[d.mm(x,r2) for x in [a,b,c]]
    b0=d.binary('sub',d.mm(a,a),d.mm(z,d.mm(b,c)))
    b1=d.binary('sub',d.mm(z,d.mm(c,c)),d.mm(a,b))
    b2=d.binary('sub',d.mm(b,b),d.mm(a,c))
    den=d.binary('add',d.mm(a,b0),d.mm(z,d.binary('add',d.mm(b,b2),d.mm(c,b1))))
    for i,x in enumerate([b0,b1,b2]):d.store(x,'x0',16*i)
    d.store(den,'x3')
    return d

def prefix():
    d=DAG()
    a=[d.load(f'a{i}','x1',16*i) for i in range(3)]
    b=[d.load(f'b{i}','x2',16*i) for i in range(3)]
    for i in range(3):d.store(d.mm(a[i],b[i]),'x0',16*i)
    return d

def inverse():
    d=DAG()
    x,y,z=[d.load(f'a{i}','x1',16*i) for i in range(3)]
    xy=d.mm(x,y);xyz=d.mm(xy,z)
    inv=d.constant('oneR',-147)
    for bit in range(11,-1,-1):
        inv=d.mm(inv,inv)
        if (3455>>bit)&1:inv=d.mm(inv,xyz)
    invxy=d.mm(inv,z)
    result=[d.mm(invxy,y),d.mm(invxy,x),d.mm(inv,xy)]
    for i,r in enumerate(result):d.store(r,'x0',16*i)
    return d

def recover():
    d=DAG()
    p=[d.load(f'p{i}','x1',16*i) for i in range(3)]
    r=[d.load(f'r{i}','x2',16*i) for i in range(3)]
    den=[d.load(f'd{i}','x3',16*i) for i in range(3)]
    for i in range(3):
        out=d.mm(p[i],r[i]);nxt=d.mm(r[i],den[i])
        d.store(out,'x0',16*i);d.store(nxt,'x2',16*i)
    return d

def finish():
    d=DAG();d.center_constants(loose=False);one=d.constant('one',1)
    a=[d.load(f'a{i}','x0',16*i) for i in range(3)]
    den=d.mm(d.load('den','x1'),one)
    dqi=d.binary('mul',den,'qi')
    # mm output is strictly inside (-q,q); only canonical correction is needed.
    for i,x in enumerate(a):d.store(d.center(d.mm(x,den,dqi),loose=False),'x0',16*i)
    return d

def center32():
    d=DAG();d.lines=d.lines[:2];d.center_constants() # no Montgomery qi needed
    a=[d.load(f'a{i}','x0',16*i) for i in range(4)]
    for i,x in enumerate(a):d.store(d.center(x),'x0',16*i)
    return d

KERNELS={'center32':('center32',center32),'basemul':('bm_rinv_tile',basemul),
 'baseinv_num':('binv_num_tile',numerator),
 'baseinv_prefix':('binv_prefix3',prefix),
 'baseinv_inverse':('binv_inverse3',inverse),
 'baseinv_recover':('binv_recover3',recover),
 'baseinv_finish':('binv_finish_tile',finish)}

if __name__=='__main__':
    print('*** Begin Patch')
    for directory,(kid,build) in KERNELS.items():
        assert (ROOT/directory/'kernel-contract.yml').exists()
        d=build()
        text='\n'.join(['.text',f'.global {kid}',f'{kid}:',
            '// Internal region only: public wrapper must preserve d8-d15.',
            '// live-in: x0-x3 memory pointers; x8 is temporary.',
            '// live-out: x0-x3 unchanged; output memory updated.',
            '// range: kernel-contract.yml; widening and REDC checked by verify.py.',
            '// reserved registers: x18-x30; no fixed vector registers.',
            '// No coefficient scratch or hidden calls inside region.',
            f'{kid}_slothy_start:']+['    '+l for l in d.lines]+[f'{kid}_slothy_end:','    ret',''])
        print(f'*** Add File: experiments/gt864-native-asm/{directory}/candidate.sym.S')
        for line in text.splitlines():print('+'+line)
    print('*** End Patch')
