"""Execute allocated BaseInv cores on local arm64 and compare exact integers."""
import ctypes as ct, hashlib, itertools, json, pathlib, random, re, subprocess
P=pathlib.Path(__file__).resolve().parent
PROD=P.parents[2]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
Q,R=3457,65536
def signed(x):return (x+32768)%65536-32768
def redc(x):return (x+signed(x*-12929)*Q)//R
def fixed(x,b,bhat):return signed(signed(x*b)-max(-32768,min(32767,(x*bhat+16384)//32768))*Q)
def make_mac(work,kid):
    src=(work/'candidate.opt.S').read_text()
    emitted=[x for x in src.splitlines() if x.startswith('    ') and x.strip()!='ret'
             and not x.strip().startswith('//') and not x.strip().endswith(':')]
    assert len(emitted) in (84,37) and not any('sp' in x for x in emitted)
    assert not any(re.search(r'<\w+>',x) for x in emitted)
    src=src.replace('.global '+kid,'.global _'+kid).replace('\n'+kid+':','\n_'+kid+':')
    out=work/'candidate.mac.S';out.write_text(src);return out,len(emitted)
num,count_num=make_mac(P/'baseinv-num-physical','binv_num_fused_tile')
fin,count_fin=make_mac(P/'baseinv-finish-physical','binv_finish_nocenter_tile')
lib=P/'baseinv-test.dylib'
subprocess.run(['clang','-dynamiclib','-arch','arm64',str(P/'baseinv-test-wrapper.S'),str(num),str(fin),'-o',str(lib)],check=True)
dll=ct.CDLL(str(lib));numfn=dll.test_binv_num;finfn=dll.test_binv_finish
numfn.argtypes=[ct.c_void_p]*4;finfn.argtypes=[ct.c_void_p]*2
source=(PROD/'gt864_fr0_basemul_tables.h').read_text().split('gt864_fr0_zetas_mul',1)[1].split('=',1)[1].split(';',1)[0]
zetas=list(map(int,re.findall(r'-?\d+',source)));assert len(zetas)==288
def oracle_num(x,z):
    a,b,c=[fixed(v,-147,-1393) for v in x]
    u=redc(b*c);w=redc(c*c)
    n2=redc(b*b-a*c);n0=redc(a*a-u*z);n1=redc(w*z-a*b)
    h=redc(n2*b+n1*c);return [n0,n1,n2],redc(h*z+n0*a)
rng=random.Random(8640912);num_cases=finish_cases=0
edge=[-32768,-32767,-3457,-1,0,1,3457,32767]
inputs=list(itertools.product(edge,repeat=3))+[tuple(rng.randrange(-32768,32768) for _ in range(3)) for _ in range(12000)]
for case,x in enumerate(inputs):
    tile=[];want=[];den=[];z=[]
    for lane in range(8):
        lane_x=tuple(signed(v+lane*(case%7)) for v in x);tile.extend(lane_x)
        root=zetas[(case*8+lane)%288];n,d=oracle_num(lane_x,root);want.append(n);den.append(d);z.append(root)
    # component-major tile layout
    packed=[tile[3*l+c] for c in range(3) for l in range(8)]
    buf=(ct.c_int16*26)(*packed,0x1234,0x2345);rootbuf=(ct.c_int16*8)(*z);out=(ct.c_int16*26)(*([0x3456]*26));dbuf=(ct.c_int16*10)(*([0x4567]*10))
    numfn(out,buf,rootbuf,dbuf)
    flat=[want[l][c] for c in range(3) for l in range(8)]
    assert list(out)[:24]==flat and list(dbuf)[:8]==den
    assert list(out)[24:]==[0x3456]*2 and list(dbuf)[8:]==[0x4567]*2 and list(buf)[24:]==[0x1234,0x2345]
    num_cases+=8
    # Finish uses valid numerator/inverse-denominator ranges independently.
    inv=[rng.randint(-2000,2000) for _ in range(8)]
    nbuf=(ct.c_int16*26)(*flat,0x1357,0x2468);ibuf=(ct.c_int16*10)(*inv,0x1111,0x2222)
    corrected=[fixed(v,-682,-6464) for v in inv]
    expected=[redc(flat[c*8+l]*corrected[l]) for c in range(3) for l in range(8)]
    finfn(nbuf,ibuf)
    assert list(nbuf)[:24]==expected and max(map(abs,expected))<=1972
    assert list(nbuf)[24:]==[0x1357,0x2468] and list(ibuf)[8:]==[0x1111,0x2222]
    finish_cases+=24
result={'status':'physical-mac-differential-pass','numerator_instructions':count_num,
 'finish_instructions':count_fin,'numerator_lane_cases':num_cases,
 'finish_lane_cases':finish_cases,'canaries':'pass','input_unchanged':'pass',
 'physical_objects':[str(num),str(fin)],'library_sha256':hashlib.sha256(lib.read_bytes()).hexdigest(),
 'scope':'isolated leaf cores on local Apple arm64; full BaseInv and Pi timing are recorded separately'}
(P/'baseinv-physical-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
