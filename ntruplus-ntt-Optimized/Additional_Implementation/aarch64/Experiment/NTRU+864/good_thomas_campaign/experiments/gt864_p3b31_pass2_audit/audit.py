#!/usr/bin/env python3
"""Read-only kernel audit: resolve every actual scheduled MUL constant.
No instruction scheduling, kernel changes, or simulated cycle claims.
"""
from pathlib import Path
from collections import Counter
import re,json,csv,hashlib
H=Path(__file__).resolve().parent;B=H/'build'
SOURCE=H.parent/'gt864_p3b29_raw_top/build/sync/raw/gt864_forward_six_bank.S'
def main():
    text=SOURCE.read_text();B.mkdir(exist_ok=True)
    tables={};label=None
    for line in text.splitlines():
        if line.startswith('.Lgt864_a1t1_') and line.endswith(':'):
            label=line[:-1];tables[label]=[]
        if line.strip().startswith('.short'):
            tables[label]+=list(map(int,line.split('.short')[1].split(',')))
    start=text.index('.Lgt864_a1t1_one_bank:')
    end=text.index('    ret',start)+len('    ret')
    body=[(text[:start].count('\n')+i+1,line.strip().split('//')[0].strip())
          for i,line in enumerate(text[start:end].splitlines()) if line.strip() and not line.endswith(':')]
    assert len(body)==553
    records=[];counts=Counter(line.split()[0] for _,line in body)
    assert counts['mul']==counts['sqrdmulh']==counts['mls']==90
    for top in range(2):
        reg={14:([3457]*8,'q',0),15:(tables['.Lgt864_a1t1_common'][8:16],'common',0)}
        ptr={2:0,3:0};index=0
        for lineno,line in body:
            op=line.split()[0]
            if op=='ldr':
                m=re.fullmatch(r'ldr q(\d+), \[x([023])\], #16',line);assert m,line
                dst,p=map(int,m.groups())
                if p==0:reg.pop(dst,None)
                else:
                    kind='ntt16' if p==2 else 'ntt9'
                    data=tables[f'.Lgt864_a1t1_{kind}_top{top}']
                    offset=ptr[p];values=data[offset:offset+8];assert len(values)==8
                    reg[dst]=(values,kind,offset//8);ptr[p]+=8
                continue
            if op=='ldp':
                for dst in re.findall(r'q(\d+)',line):reg.pop(int(dst),None)
                continue
            if op=='mul':
                m=re.search(r', v(\d+)\.(8H|H\[(\d+)\])$',line);assert m,line
                src=int(m[1]);assert src in reg,(line,src)
                values,origin,offset=reg[src]
                constants=values if m[2]=='8H' else [values[int(m[3])]]*8
                if origin=='ntt16':stage='tail_ntt16' if offset<12 else 'main_ntt16'
                elif origin=='ntt9':stage='ntt9_twist'
                elif origin=='common':stage='ntt9_B3' if int(m[3])==0 else 'ntt9_eta'
                else:raise AssertionError(origin)
                identity=[i for i,x in enumerate(constants) if x==1]
                records.append({'top':top,'mul_index':index,'line':lineno,'stage':stage,'constants':constants,
                    'identity_lanes':identity,'classification':'all_identity_reduction' if len(identity)==8 else 'mixed_identity' if identity else 'nonidentity_fixed_product',
                    'deletion_proven':False})
                index+=1
            # All other arithmetic/permutation destinations lose known-constant status.
            m=re.match(r'\w+ v(\d+)\.',line)
            if m:reg.pop(int(m[1]),None)
        assert index==90 and ptr=={2:168,3:256},ptr
    stage_counts=Counter(r['stage'] for r in records if r['top']==0)
    assert stage_counts=={'tail_ntt16':6,'main_ntt16':48,'ntt9_twist':16,'ntt9_B3':12,'ntt9_eta':8}
    classes={str(t):dict(Counter(r['classification'] for r in records if r['top']==t)) for t in (0,1)}
    noop=[a for a in range(-32768,32768) if a-((a*9+16384)//32768)*3457==a]
    assert noop==list(range(-1820,1821))
    report={'gate':'P3B31','scope':'static instruction/constant provenance audit, not cycle attribution',
       'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'one_bank_instructions':553,
       'instruction_histogram':dict(counts),'mulmods_per_bank_by_stage':dict(stage_counts),'classes':classes,
       'table_q_loads_per_bank':{'ntt16':21,'ntt9':32},'records':records,
       'identity_noop_domain':[-1820,1820],'identity_counterexample':{'input':2000,'output':2000-3457},
       'kernel_changed':False,'cycle_claim':False}
    (B/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
    with (B/'multiplications.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=records[0].keys());writer.writeheader();writer.writerows(records)
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
if __name__=='__main__':main()
