"""Generate the P7-C0 mask-0 arithmetic and existing P8 store contract."""
from pathlib import Path
P=Path(__file__).resolve().parent
lines=[]
def emit(x):lines.append('    '+x)
def vec(x):return f'V<{x}>'
def op(code,d,a,b):emit(f'{code} {vec(d)}.8h, {vec(a)}.8h, {vec(b)}.8h')
def constant(name,value):
    emit(f'mov w8, #{value&65535}');emit(f'dup {vec(name)}.8h, w8')
def fm(d,a,b,h):
    op('sqrdmulh',d+'quot',a,h);op('mul',d,a,b);op('mls',d,d+'quot','q')
def b3(a,b,c,n):
    op('sub',n+'d',b,c);fm(n+'p',n+'d','rho','rhoh')
    op('add',n+'sum',a,b);op('add',n+'y0',n+'sum',c)
    op('sub',n+'ac',a,c);op('add',n+'y1',n+'ac',n+'p')
    op('sub',n+'ab',a,b);op('sub',n+'y2',n+'ab',n+'p')
    return [n+'y0',n+'y1',n+'y2']
constant('q',3457);constant('rho',722);constant('rhoh',6844)
v=[f'input{i}' for i in range(9)]
for i in range(9):emit(f'ldr Q<{v[i]}>, [x2, #{i*96}]')
for k,ids in enumerate([(0,3,6),(1,4,7),(8,2,5)]):
    out=b3(*(v[i] for i in ids),f'L1b{k}')
    for i,x in zip(ids,out):v[i]=x
constant('ei',366);constant('eih',3469);constant('e',1124);constant('eh',10654)
for i,b in [(4,'ei'),(5,'ei'),(7,'e'),(2,'e')]:
    fm(f'eta{i}',v[i],b,b+'h');v[i]=f'eta{i}'
for k,ids in enumerate([(0,1,8),(3,4,2),(6,7,5)]):
    out=b3(*(v[i] for i in ids),f'L2b{k}')
    for i,x in zip(ids,out):v[i]=x
for s,i in enumerate([0,3,7,1,4,5,8,2,6]):
    emit(f'ldr Q<scale{s}>, [x3, #{s*32}]')
    emit(f'ldr Q<scaleh{s}>, [x3, #{s*32+16}]')
    fm(f'u{s}',v[i],f'scale{s}',f'scaleh{s}')
def trn(d,a,b,width,which):emit(f'trn{which} {vec(d)}.{width}, {vec(a)}.{width}, {vec(b)}.{width}')
for i in range(4):
    trn(f'h{2*i}',f'u{2*i}',f'u{2*i+1}','8h',1)
    trn(f'h{2*i+1}',f'u{2*i}',f'u{2*i+1}','8h',2)
for half in range(2):
    for c in range(4):
        trn(f'out{half}_{c}',f'h{half*4+c%2}',f'h{half*4+c%2+2}','4s',1+c//2)
emit('add x4, x0, #256')
for half,ptr in [(0,'x0'),(1,'x4')]:
    for c in range(4):emit(f'str D<out{half}_{c}>, [{ptr}, #{16*c}]')
emit('add x5, x0, #64');emit('add x6, x4, #64');emit('mov x7, #16')
for half,ptr in [(0,'x5'),(1,'x6')]:
    for c in range(4):emit(f'st1 {{{vec(f"out{half}_{c}")}.d}}[1], [{ptr}]'+(', x7' if c<3 else ''))
for lane in range(8):emit(f'st1 {{{vec("u8")}.h}}[{lane}], [x1]'+(', x7' if lane<7 else ''))
text='\n'.join(['.text','.global packed_i9','packed_i9:',
    '// live-in x0 main x1 tail x2 input x3 table; live-out memory',
    '// reserved x18-x30 sp; all SIMD registers allocated by Slothy',
    '// range abs input2497 output2617; R^-1; constants q3457',
    '// memory: same coefficient and table reads; same P8 stores',
    'packed_i9_slothy_start:']+lines+['packed_i9_slothy_end:','ret',''])
(P/'candidate.sym.S').write_text(text)
print('body instructions',len(lines))
