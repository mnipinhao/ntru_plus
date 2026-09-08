"""Executable coordinate checks and a small interpreter for early_pair.sym.S.
Not a Slothy allocation or a microarchitecture timing model.
"""
import pathlib,re,random,json
P=pathlib.Path(__file__).resolve().parent
PROD=P.parents[1]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
def numbers(file,name):
    s=(PROD/file).read_text().split(name,1)[1].split('=',1)[1].split(';',1)[0]
    return list(map(int,re.findall(r'-?\d+',s)))
def signed(x):return (x+32768)%65536-32768
def chunks(x,n):return [x[i:i+n] for i in range(0,len(x),n)]
def lanes(x):return [int.from_bytes(bytes(c),'little') for c in chunks(x,2)]
def halfs(x):return sum([list((v&65535).to_bytes(2,'little')) for v in x],[])

# Coordinates: main [component][half_s][column][top][lane4], tail unchanged.
# Compare producer half stores to precisely the vectors the old I16 loaded.
seen=set()
for c in range(3):
 for half in range(2):
  for col in range(16):
   packed=[]
   for top in range(2):
    for lane in range(4):
     addr=c*512+half*256+col*16+top*8+lane*2
     assert addr not in seen;seen.add(addr)
     packed.append((top,c,col,4*half+lane))
   old=[(0,c,col,4*half+l) for l in range(4)]+[(1,c,col,4*half+l) for l in range(4)]
   assert packed==old
assert seen==set(range(0,1536,2))

# After the original 8h/4s transpose stages: each low/high D holds four rows.
# New stores consume those directly; final TRN .2d is unnecessary.
regs={0:([0,1,2,3],0,4),1:([0,1,2,3],1,5),4:([0,1,2,3],2,6),5:([0,1,2,3],3,7),
      2:([4,5,6,7],0,4),3:([4,5,6,7],1,5),6:([4,5,6,7],2,6),7:([4,5,6,7],3,7)}
stores=(P/'inverse9/candidate.sym.S').read_text()
for half,rs in enumerate([[0,1,4,5],[2,3,6,7]]):
 for col,r in enumerate(rs):
  assert regs[r]==(list(range(4*half,4*half+4)),col,col+4)
  assert f'str D<r{r}>, [x{0 if half==0 else 4}, #{16*col}]' in stores
  assert (f'st1 {{V<r{r}>.d}}[1], [x{5 if half==0 else 6}]'+(', x7' if col<3 else '')) in stores

prefix=numbers('p3b1_tables.h','p3b1_prefix')
indices=numbers('p3b1_tables.h','p3b1_a_fwd')
wire=numbers('tables.h','map_f')
assert len(indices)==144 and len(wire)==864
code=[l.strip() for l in (P/'tobytes/candidate.sym.S').read_text().splitlines()
      if l.startswith('    ') and not l.strip().startswith(('//','ret'))]

def execute(inp,top,pair,out,scratch_mode=False):
    mem={}
    for i,b in enumerate(halfs(inp)):mem[10000+i]=b
    for i,b in enumerate(halfs(prefix)):mem[20000+i]=b
    for i,b in enumerate(indices):mem[30000+i]=b
    a,b=[(0,8),(16,216),(224,232)][pair]
    g={'x0':1000+648*top+3*pair,'x1':10000+2*(432*top+a),
       'x2':10000+2*(432*top+b),'x3':20000,'x4':30000}
    if scratch_mode:g['x0']=1000+648*top+216*pair
    v={}
    for line in code:
        op=line.split()[0];syms=re.findall(r'<(\w+)>',line)
        imms=list(map(int,re.findall(r'#(-?\d+)',line)))
        if op=='mov':g['x8']=imms[0]
        elif op=='dup':v[syms[0]]=halfs([g['x8']]*8)
        elif op=='ldr':
            ptr=re.search(r'\[(x\d+)',line)[1];off=imms[0] if imms else 0
            v[syms[0]]=[mem[g[ptr]+off+i] for i in range(16)]
        elif op.startswith('trn'):
            width={'8h':2,'4s':4,'2d':8}[re.search(r'>\.(\w+)',line)[1]]
            a,b=chunks(v[syms[1]],width),chunks(v[syms[2]],width)
            v[syms[0]]=sum([a[i]+b[i] for i in range(int(op[-1])-1,len(a),2)],[])
        elif op=='ext':v[syms[0]]=(v[syms[1]]+v[syms[2]])[imms[0]:imms[0]+16]
        elif op in ['orr','and','bic']:
            a,b=v[syms[1]],v[syms[2]]
            v[syms[0]]=[(x|y) if op=='orr' else (x&(255^y)) if op=='bic' else (x&y) for x,y in zip(a,b)]
        elif op=='bsl':
            mask=v[syms[0]];a,b=v[syms[1]],v[syms[2]]
            v[syms[0]]=[(m&x)|((255^m)&y) for m,x,y in zip(mask,a,b)]
        elif op=='bif':
            a=v[syms[0]];b=v[syms[1]];mask=v[syms[2]]
            v[syms[0]]=[(m&x)|((255^m)&y) for m,x,y in zip(mask,a,b)]
        elif op=='ins':
            lane=list(map(int,re.findall(r'\.h\[(\d+)\]',line)))
            d=v[syms[0]][:];d[2*lane[0]:2*lane[0]+2]=v[syms[1]][2*lane[1]:2*lane[1]+2];v[syms[0]]=d
        elif op=='tbl':
            a=v[syms[1]];v[syms[0]]=[a[i] if i<16 else 0 for i in v[syms[2]]]
        elif op=='sqrdmulh':
            a,b=lanes(v[syms[1]]),lanes(v[syms[2]])
            v[syms[0]]=halfs([max(-32768,min(32767,(signed(x)*signed(y)+16384)//32768)) for x,y in zip(a,b)])
        elif op=='mls':
            d,a,b=[lanes(v[s]) for s in syms]
            v[syms[0]]=halfs([z-x*y for z,x,y in zip(d,a,b)])
        elif op in ['sshr','ushr']:
            a=lanes(v[syms[1]]);v[syms[0]]=halfs([(signed(x) if op=='sshr' else x)>>imms[0] for x in a])
        elif op=='sli':
            a,b=[lanes(v[s]) for s in syms];n=imms[0]
            v[syms[0]]=halfs([(x&((1<<n)-1))|(y<<n) for x,y in zip(a,b)])
        elif op=='add' and syms:v[syms[0]]=halfs([x+y for x,y in zip(lanes(v[syms[1]]),lanes(v[syms[2]]))])
        elif op=='add':g['x5']=g['x0']+imms[0]
        elif op=='xtn':v[syms[0]]=[x&255 for x in lanes(v[syms[1]])]+[0]*8
        elif op=='st3':
            match=re.search(r'\}\[(\d+)\]',line)
            if match:
                lane=int(match[1])
                for j,s in enumerate(syms):
                    addr=g['x5']+j-1000
                    assert addr not in out
                    out[addr]=v[s][lane]
                g['x5']+=g['x8']
            else:
                assert '.8b' in line
                for lane in range(8):
                    for j,s in enumerate(syms):
                        addr=g['x5']+3*lane+j-1000
                        assert addr not in out
                        out[addr]=v[s][lane]
        else:raise AssertionError(line)

rng=random.Random(864)
cases=[list(range(864)),[-32768]*864,[32767]*864]+[[rng.randrange(-32768,32768) for _ in range(864)] for _ in range(64)]
for inp in cases:
    out={}
    for top in range(2):
        for pair in range(3):execute(inp,top,pair,out)
    expect=[]
    for k in range(0,864,2):
        a,b=inp[wire[k]]%3457,inp[wire[k+1]]%3457
        expect.extend([a&255,(a>>8)|((b&15)<<4),b>>4])
    assert set(out)==set(range(1296))
    assert [out[i] for i in range(1296)]==expect

# Backwards liveness includes destructive dependencies. This is not RA:
# ST3 needs three consecutive physical registers and ABI saves are external.
live=set();peak=0
for line in reversed(code):
    op=line.split()[0];s=re.findall(r'<(\w+)>',line)
    if not s:continue
    defs=set() if op.startswith('st') else {s[0]}
    uses=set(s if op.startswith('st') else s[1:])
    if op in ['mls','bsl','ins','sli']:uses|=defs
    live=(live-defs)|uses;peak=max(peak,len(live))
assert not live
print(json.dumps({'inverse_main_coordinates':768,'inverse_mapping':'pass',
    'tobytes_symbolic_interpreter_cases':len(cases),'bytes_exact':'pass',
    'tobytes_vector_live_peak':peak,'allocation':'not run; consecutive ST3 register constraint pending'},indent=2))
