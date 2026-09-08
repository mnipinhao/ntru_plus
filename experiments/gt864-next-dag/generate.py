"""Deterministic DAG authoring, not allocation/scheduling. Print apply_patch.
Run contract checks before invoking this generator. No physical candidate output.
"""
import pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[2]
PROD=ROOT/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
DEST='experiments/gt864-next-dag'

def expanded(filename,function):
    s=(PROD/filename).read_text()
    s=re.sub(r'/\*.*?\*/','',s,flags=re.S).replace('\\\n',' ')
    macros={}
    for m in re.finditer(r'\.macro\s+(\w+)([^\n]*)\n(.*?)\.endm',s,re.S):
        macros[m[1]]=([x.strip() for x in m[2].strip().split(',') if x.strip()],m[3])
    body=s.split('_'+function+':',1)[1].split('    ret',1)[0]
    def unfold(body):
        out=[]
        for line in body.splitlines():
            line=line.strip()
            if not line:continue
            op,*rest=line.split(None,1)
            if op in macros:
                params,template=macros[op]
                args=[a.strip() for a in rest[0].split(',')] if rest else []
                assert len(args)==len(params),(op,args,params)
                for key,value in sorted(zip(params,args),key=lambda p:-len(p[0])):
                    template=template.replace('\\'+key+'\\()',value)
                    template=re.sub(r'\\'+key+r'\b',lambda _:value,template)
                out.extend(unfold(template))
            else:
                assert '\\' not in line,line
                line=re.sub(r'#([()0-9xa-fA-F &+*\-]+)(?=\]|$)',
                    lambda m:'#'+str(eval(m[1],{'__builtins__':{}},{})),line)
                out.append(line)
        return out
    return unfold(body)

def sym(lines):
    return [re.sub(r'\b([vqdsbh])(\d+)\b',lambda m:{'v':'V','q':'Q','d':'D','s':'S','b':'B','h':'H'}[m[1]]+'<r'+m[2]+'>',l) for l in lines]

i9=expanded('gt864_fr0_inverse9_block.S','gt864_fr0_inverse9_block_asm')
start=next(i for i,l in enumerate(i9) if re.match(r'trn1\s+v22\.2d',l))
end=next(i for i in range(start,len(i9)) if re.match(r'mov\s+x4, #16',i9[i]))
store=['add x4, x0, #256']
for ptr,regs in [('x0',[0,1,4,5]),('x4',[2,3,6,7])]:
    store += [f'str d{r}, [{ptr}, #{16*c}]' for c,r in enumerate(regs)]
store += ['add x5, x0, #64','add x6, x4, #64','mov x7, #16']
for ptr,regs in [('x5',[0,1,4,5]),('x6',[2,3,6,7])]:
    store += [f'st1 {{v{r}.d}}[1], [{ptr}]'+(', x7' if i<3 else '') for i,r in enumerate(regs)]
old_i9=i9[:]
i9=i9[:start]+store+i9[end:]

i16=expanded('gt864_inverse16_blocks.s','gt864_inverse16_main_block_asm')
old_i16=i16[:]
new=[];i=0
while i<len(i16):
    m=re.fullmatch(r'ldr\s+d(\d+),\s*\[x1, #(\d+)\]',i16[i])
    if m:
        assert re.match(r'ldr\s+d30,',i16[i+1]) and i16[i+2].startswith('ins')
        new.append(f'ldr q{m[1]}, [x1, #{m[2]}]');i+=3
    else:new.append(i16[i]);i+=1
i16=new

# ToBytes: two transpose states (eight vectors plus the ninth-source vector).
# No complete w[9] array, only one row pair is materialized at a time.
tb=[]
def emit(s):tb.append(s)
def trn(out,a,b,width,which):emit(f'trn{which} V<{out}>.{width}, V<{a}>.{width}, V<{b}>.{width}')
for tag,ptr in [('a','x1'),('b','x2')]:
    for j in range(8):
        emit(f'ldr Q<{tag}j{j}>, [{ptr}, #{(8-j)*48}]')
        if j:emit(f'ext V<{tag}j{j}>.16b, V<{tag}j{j}>.16b, V<{tag}j{j}>.16b, #{2*(8-j)}')
    emit(f'ldr Q<{tag}ninth>, [{ptr}]')
    for j in range(4):
        trn(f'{tag}u{2*j}',f'{tag}j{2*j}',f'{tag}j{2*j+1}','8h',1)
        trn(f'{tag}u{2*j+1}',f'{tag}j{2*j}',f'{tag}j{2*j+1}','8h',2)
    for base in [0,4]:
        for j,(a,b,which) in enumerate([(0,2,1),(1,3,1),(0,2,2),(1,3,2)]):
            trn(f'{tag}z{base+j}',f'{tag}u{base+a}',f'{tag}u{base+b}','4s',which)
    for j in range(4):
        trn(f'{tag}t{j}',f'{tag}z{j}',f'{tag}z{j+4}','2d',1)
        trn(f'{tag}t{j+4}',f'{tag}z{j}',f'{tag}z{j+4}','2d',2)
emit('mov w8, #3457');emit('dup V<q>.8h, w8')
emit('mov w8, #9');emit('dup V<recip>.8h, w8')
# x8 also serves as the public output byte stride.
for k,row in enumerate([0,3,6,1,4,7,2,5,8]):
    emit(f'// ROW {k}: create only this pair; t{k-1} dies after this row when applicable')
    emit(f'ldr Q<idx{k}>, [x4, #{k*16}]')
    if 1<=k<=6:emit(f'ldr Q<mask{k}>, [x3, #{(k-1)*16}]')
    for tag in ['a','b']:
        dst=f'{tag}row{k}'
        if k in (0,7,8):
            emit(f'mov V<{dst}>.16b, V<{tag}t{0 if k==0 else 6 if k==7 else 7}>.16b')
        else:
            emit(f'mov V<{dst}>.16b, V<mask{k}>.16b')
            emit(f'bsl V<{dst}>.16b, V<{tag}t{k-1}>.16b, V<{tag}t{k}>.16b')
        if k<8:emit(f'ins V<{dst}>.h[{k}], V<{tag}ninth>.h[{k}]')
        emit(f'tbl V<{dst}>.16b, {{V<{dst}>.16b}}, V<idx{k}>.16b')
        emit(f'sqrdmulh V<{tag}quot{k}>.8h, V<{dst}>.8h, V<recip>.8h')
        emit(f'mls V<{dst}>.8h, V<{tag}quot{k}>.8h, V<q>.8h')
        emit(f'sshr V<{tag}sign{k}>.8h, V<{dst}>.8h, #15')
        emit(f'and V<{tag}sign{k}>.16b, V<{tag}sign{k}>.16b, V<q>.16b')
        emit(f'add V<{dst}>.8h, V<{dst}>.8h, V<{tag}sign{k}>.8h')
    emit(f'xtn V<lo{k}>.8b, V<arow{k}>.8h')
    emit(f'ushr V<mix{k}>.8h, V<arow{k}>.8h, #8')
    # Low four bits are a>>8; SLI inserts b<<4 directly (no shift temporary).
    emit(f'sli V<mix{k}>.8h, V<brow{k}>.8h, #4')
    emit(f'xtn V<mid{k}>.8b, V<mix{k}>.8h')
    emit(f'ushr V<brow{k}>.8h, V<brow{k}>.8h, #4')
    emit(f'xtn V<hi{k}>.8b, V<brow{k}>.8h')
    emit(f'add x5, x0, #{72*row}')
    for lane in range(8):emit(f'st3 {{V<lo{k}>.b, V<mid{k}>.b, V<hi{k}>.b}}[{lane}], [x5], x8')

files={}
for directory,kid,lines in [('inverse9','packed_i9',sym(i9)),('inverse16','packed_i16',sym(i16)),('tobytes','early_pair',tb)]:
    # MOV vector is the ORR alias; spell the architectural data dependencies.
    lines=[re.sub(r'^mov\s+(V<\w+>\.16b),\s*(V<\w+>\.16b)$',r'orr \1, \2, \2',l) for l in lines]
    files[f'{directory}/candidate.sym.S']='\n'.join(['.text',f'.global {kid}',f'{kid}:',
      '// live-in: concrete input and table pointers from kernel-contract.yml',
      '// live-out: memory stores; no vector result is live across return',
      '// range: inherited arithmetic bounds; ToBytes signed int16 to canonical bytes',
      '// reserved registers: x18-x30; outer ABI wrapper must preserve d8-d15',
      f'{kid}_slothy_start:']+['    '+l for l in lines]+[f'{kid}_slothy_end:','    ret',''])
    files[f'{directory}/count.txt']=str(sum(not l.startswith('//') for l in lines))+'\n'
files['cost-ledger.txt']=f'I9 old {len(old_i9)} new {len(i9)} delta {len(i9)-len(old_i9)} per block x12\nI16 main old {len(old_i16)} new {len(i16)} delta {len(i16)-len(old_i16)} per block x6\nCombined static delta {(len(i9)-len(old_i9))*12+(len(i16)-len(old_i16))*6}; no cycles claim\n'
print('*** Begin Patch')
for name,body in files.items():
    print('*** Add File: '+DEST+'/'+name)
    for line in body.splitlines():print('+'+line)
print('*** End Patch')
