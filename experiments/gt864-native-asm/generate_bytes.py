"""Re-tile packed bytes: no lane ST3; print apply_patch after contracts pass."""
import re
from pathlib import Path
P=Path(__file__).resolve().parent
old=(P.parent/'gt864-next-dag/tobytes/candidate.sym.S').read_text().splitlines()
producer=[]
for line in old:
    if not line.startswith('    ') or line.strip()=='ret':continue
    line=line.strip()
    # The current checkout's BIF parser raises a datatype exception. Spell the
    # select as AND/BIC/ORR (one extra instruction vs MOV+BSL), don't fake costs.
    m=re.fullmatch(r'orr V<([ab])row(\d+)>.16b, V<mask\d+>.16b, V<mask\d+>.16b',line)
    if m:
        tag,k=m[1],int(m[2]);line=f'and V<{tag}row{k}>.16b, V<{tag}t{k-1}>.16b, V<mask{k}>.16b'
    m=re.fullmatch(r'bsl V<([ab])row(\d+)>.16b, V<\w+>.16b, V<\w+>.16b',line)
    if m:
        tag,k=m[1],int(m[2])
        producer += [f'bic V<{tag}other{k}>.16b, V<{tag}t{k}>.16b, V<mask{k}>.16b',
          f'orr V<{tag}row{k}>.16b, V<{tag}row{k}>.16b, V<{tag}other{k}>.16b']
        continue
    if line.startswith('add x5, x0, #'):
        n=int(line.split('#')[1]);assert n%72==0
        line=f'add x5, x0, #{n//3}'
    if line.startswith('st3 '):
        if '}[0]' not in line:continue
        line=re.sub(r'\.b([,}])',r'.8b\1',line)
        line=line.replace('}[0], [x5], x8','}, [x5]')
    producer.append(line)

consumer=[];indices=[]
for pair in range(3):
    consumer += [f'ldr Q<p{pair}lo>, [x{pair+1}, #0]',
      f'add x5, x{pair+1}, #16',f'ldr D<p{pair}hi>, [x5]']
for chunk in range(5):
    for pair in range(3):
        row=[]
        for lane in range(16):
            byte=16*chunk+lane
            row.append(3*(byte//9)+byte%3 if byte<72 and (byte%9)//3==pair else 255)
        indices+=row
        n=3*chunk+pair
        consumer += [f'ldr Q<idx{n}>, [x4, #{16*n}]',
          f'tbl V<part{n}>.16b, {{V<p{pair}lo>.16b, V<p{pair}hi>.16b}}, V<idx{n}>.16b']
    consumer += [f'orr V<out{chunk}>.16b, V<part{3*chunk}>.16b, V<part{3*chunk+1}>.16b',
      f'orr V<out{chunk}>.16b, V<out{chunk}>.16b, V<part{3*chunk+2}>.16b',
      f'str {"D" if chunk==4 else "Q"}<out{chunk}>, [x0, #{16*chunk}]']
small=[l for l in producer if not l.startswith(('sqrdmulh ','mls ','mov w8, #9','dup V<recip>'))]
assert len(producer)-len(small)==38
if __name__=='__main__':
    print('*** Begin Patch')
    for directory,kid,body in [('tobytes_block','byte_pair_block',producer),('tobytes_small','byte_pair_small',small),('tobytes_merge','byte_merge_row',consumer)]:
        assert (P/directory/'kernel-contract.yml').exists()
        lines=['.text',f'.global {kid}',f'{kid}:',
          '// live-in: x0-x4 as specified in kernel-contract.yml.',
          '// live-out: exact output memory; no coefficient scratch.',
          '// range: normalized bytes; small producer requires -3457 < input < 3457; see contract.',
          '// reserved registers: x18-x30; outer wrapper preserves d8-d15.',
          f'{kid}_slothy_start:']+['    '+l for l in body]+[f'{kid}_slothy_end:','    ret']
        print(f'*** Add File: experiments/gt864-native-asm/{directory}/candidate.sym.S')
        for line in lines:print('+'+line)
    print('*** Add File: experiments/gt864-native-asm/integration/byte_merge_tables.h')
    print('+#include <stdint.h>\n+static const uint8_t gt864_byte_merge_indices[240] = {')
    for i in range(0,240,16):print('+    '+','.join(map(str,indices[i:i+16]))+',')
    print('+};\n*** End Patch')
