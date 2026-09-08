"""Print apply_patch for range-checked I16 variants, never allocate registers."""
import contextlib,importlib.util,io,re
from pathlib import Path
from inverse_range import main as prove,table,scaled
stage=table(scaled,'gt864_inverse16_stage_barrett')
P=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    proof=prove()
    spec=importlib.util.spec_from_file_location('old_generator',P.parent/'gt864-next-dag/generate.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
deleted=set(proof['deleted_butterflies'])

def lower(lines):
    out=[];seen=0;group={};qmap={};offset=None;removed=0
    for line in lines:
        m=re.fullmatch(r'ldr\s+Q<r0>,\s*\[x3, #(\d+)\]',line)
        if m:offset=int(m[1]);group={};qmap={}
        if seen<32 and line.startswith('sqrdmulh') and '.h[' in line:
            regs=re.findall(r'<(\w+)>',line);lane=int(re.search(r'\.h\[(\d+)\]',line)[1])
            b,h=stage[offset//2+lane-1:offset//2+lane+1]
            assert (b==1)==(seen in proof['identity_positions'])
            group[regs[1]]=(seen,b);qmap[regs[1]]=regs[0]
            remove=seen in deleted;seen+=1
            if remove:removed+=1;continue
        if line.startswith('mul ') and '.h[' in line:
            regs=re.findall(r'<(\w+)>',line)
            if regs[0] in group:
                idx,b=group[regs[0]]
                if b==1:
                    assert regs[0]==regs[1]
                    removed+=1;continue
        if line.startswith('mls '):
            regs=re.findall(r'<(\w+)>',line)
            if regs[0] in group:
                idx,b=group[regs[0]]
                assert regs[1]==qmap[regs[0]]
                if idx in deleted:removed+=1;continue
        out.append(line)
        # SCALE uses q0 at x4; prevent stage mappings from matching its MLS.
        if re.match(r'ldr\s+Q<r0>,\s*\[x4',line):group={}
    assert seen==32 and removed==43,(seen,removed)
    # Entire first-stage constant vectors became unused after all eight b=1
    # groups disappeared. Remove only provably dead public table loads.
    live=set();kept=[];dead_tables=0
    for line in reversed(out):
        op=line.split()[0];symbols=re.findall(r'<(\w+)>',line)
        defs=set(symbols[:1]) if symbols and not op.startswith(('st','umov')) else set()
        uses=set(symbols if op.startswith(('st','umov')) else symbols[1:])
        if op in ('mls','ins'):uses|=defs
        if op=='ldr' and '[x3' in line and not (defs&live):
            dead_tables+=1;continue
        live=(live-defs)|uses;kept.append(line)
    assert dead_tables==2,dead_tables
    return list(reversed(kept))

main=[l.strip() for l in (P.parent/'gt864-next-dag/inverse16/candidate.sym.S').read_text().splitlines()
      if l.startswith('    ') and l.strip()!='ret']
tail=old.sym(old.expanded('gt864_inverse16_blocks.s','gt864_inverse16_tail_block_asm'))
tail=[re.sub(r'^mov\s+(V<\w+>\.16b),\s*(V<\w+>\.16b)$',r'orr \1, \2, \2',l) for l in tail]
print('*** Begin Patch')
for directory,kid,lines in [('inverse16_lazy','lazy_i16',main),('inverse_tail_lazy','lazy_itail',tail)]:
    assert (P/directory/'kernel-contract.yml').exists()
    body=['.text',f'.global {kid}',f'{kid}:',
      '// live-in: x0 natural output; x1 scratch; x3 stage; x4 scaled constants.',
      '// live-out: natural output memory, still requires centered correction.',
      '// range: I9 <=3456; I16 <=30939; top output <=6912.',
      '// reserved registers: x18-x30; public wrapper must preserve d8-d15.',
      f'{kid}_slothy_start:']+['    '+x for x in lower(lines)]+[f'{kid}_slothy_end:','    ret']
    print(f'*** Add File: experiments/gt864-native-asm/{directory}/candidate.sym.S')
    for line in body:print('+'+line)
print('*** End Patch')
