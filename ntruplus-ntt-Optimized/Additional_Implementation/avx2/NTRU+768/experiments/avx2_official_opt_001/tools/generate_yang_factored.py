#!/usr/bin/env python3
"""Faithful compact lowering of the closed factored schedule; no rescheduling."""
import hashlib,json,re
from close_yang_contract import ROOT

NAME='ntruplus768_officialopt_invntt_yang_factored'
def generate():
    proof=json.loads((ROOT/'results/yang-closure-schedule-20260923.json').read_text())
    for name,h in proof['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,('stale proof',name)
    dep=json.loads((ROOT/'results/yang-tail-proof-20260922.json').read_text())
    base=ROOT/'asm/ntruplus768_officialopt_invntt_ct_wresident.s'
    assert hashlib.sha256(base.read_bytes()).hexdigest()==dep['source_sha256'][str(base.relative_to(ROOT))]
    source=base.read_text();prefix=source.split('#level1:')[0]
    prefix=prefix.replace('ntruplus768_officialopt_invntt_ct_wresident',NAME)
    oldtables=source[source.index('.section .rodata'):source.index('ct_r3_pair_constants:')]
    prefix=prefix.replace('ct_stage','yang_stage');oldtables=oldtables.replace('ct_stage','yang_stage')
    p=proof['tail']['factored'];ops=p['operations'];layout=p['table_layout']
    lines=[prefix,NAME+'_tail:','mov %rdi,%r8'];vector_lines=[]
    def lower(o,loop=None):
        def operand(s):
            if s.startswith('v'):return '%ymm'+str(o['read_registers'][s])
            if s.startswith('data:'):
                return str(32*(int(s[5:])-loop['data_base']))+'(%rdi)'
            off=layout[s[6:]]['offset']
            return (str(off-loop['const_base'])+'(%r10)' if loop else 'yang_tail_table+'+str(off)+'(%rip)')
        if o['op']=='store':
            line='vmovdqa '+operand(o['src'][0])+','+str(32*(o['address']-loop['data_base']))+'(%rdi)'
        else:
            dst='%ymm'+str(o['write_register']);args=[operand(s) for s in o['src']]
            opcode='vmovdqa' if o['op']=='load' else o['op']
            if len(args)==2:args.reverse()  # SSA lhs,rhs -> AT&T rhs,lhs,dst
            line=opcode+' '+','.join(args+[dst])
        lines.append(line);vector_lines.append(line)
    loops={l['expanded_start']:l for l in p['loops']};i=0
    while i<len(ops):
        if i not in loops:lower(ops[i]);i+=1;continue
        l=loops[i];body=l['body']
        data_base=min(int(s[5:]) for o in body for s in o['src'] if s.startswith('data:'))
        const_base=min(layout[s[6:]]['offset'] for o in body for s in o['src'] if s.startswith('const:'))
        label='_yang_'+l['label']
        lines += [f'lea {32*data_base}(%r8),%rdi','lea 256(%rdi),%r9',f'lea yang_tail_table+{const_base}(%rip),%r10','.p2align 5',label+':']
        for o in body:lower(o,dict(data_base=data_base,const_base=const_base))
        lines += [f'add ${l["constant_cursor_stride_bytes"]},%r10','add $32,%rdi','cmp %r9,%rdi','jb '+label]
        i=l['expanded_end']
    lines+=['ret',f'.size {NAME},.-{NAME}',oldtables,'.p2align 5','yang_tail_table:']
    cursor=0;raw=bytearray()
    for name,v in sorted(layout.items(),key=lambda kv:kv[1]['offset']):
        assert cursor==v['offset']
        words=p['tables'][name] if v['bytes']==32 else v['int16_payload']
        lines += ['# '+name,'.short '+','.join(map(str,words))]
        for w in words:raw+=int(w).to_bytes(2,'little',signed=True)
        cursor+=v['bytes']
    padding=p['constant_bytes']-cursor
    if padding:lines+=['.zero '+str(padding)];raw+=bytes(padding)
    lines+=['.size yang_tail_table,.-yang_tail_table','.section .note.GNU-stack,"",@progbits']
    path=ROOT/'asm'/f'{NAME}.s';path.write_text('\n'.join(lines)+'\n')
    result={'asm_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'control_prefix_sha256':hashlib.sha256(prefix.encode()).hexdigest(),
            'tail_vector_instructions':vector_lines,'table_hex':raw.hex(),'tail_model_peak_YMM':p['peak_YMM'],
            'schedule_sha256':hashlib.sha256((ROOT/'results/yang-closure-schedule-20260923.json').read_bytes()).hexdigest()}
    (ROOT/'results/yang-factored-lowering.json').write_text(json.dumps(result,indent=2)+'\n')
    print(path)
if __name__=='__main__':generate()
