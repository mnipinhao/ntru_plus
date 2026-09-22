#!/usr/bin/env python3
"""Archive installed sources, exact linked body audits and qualification deltas."""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from install_encap_eager import EXP,REPO,sha
from run_encap_live_b3_short import command
from vector_mapping_source_ledger import stats
sys.path.insert(0,str(REPO/'scripts'))
from run_supercop_benchmark import elf_layout,decode_observations,stabilized_quartiles

def body_audit(elf,name):
    raw=command(['objdump','-d','--no-show-raw-insn','--disassemble='+name,str(elf)]).stdout
    ins=[]
    for line in raw.splitlines():
        m=re.match(r'\s*([0-9a-f]+):\s+(.+)',line)
        if m:
            ins.append((int(m[1],16),m[2].split('#')[0].strip()))
            if ins[-1][1]=='ret':break
    assert ins and ins[-1][1]=='ret'
    assert not any(re.search(r'%(?:rsp|rbp|rbx|r1[2-5])\b',x) or x.startswith(('call','push','pop')) for _,x in ins)
    branches=[i for i,(_,x) in enumerate(ins) if x.startswith('j')]
    assert len(branches)==1 and ins[branches[0]][1].startswith('jne ')
    end=branches[0];target=int(ins[end][1].split()[1],16)
    begin=next(i for i,(a,_) in enumerate(ins) if a==target)
    path=[x for _,x in ins[:begin]]+([x for _,x in ins[begin:end]]+['jne public_loop'])*12+[x for _,x in ins[end+1:]]
    path=[x for x in path if not x.startswith(('nop','data16','cs '))]
    ledger=stats(path,('r8','r9'))
    assert ins[0][0]%32==0
    assert ledger['classes']['data_load_instructions']==96
    assert ledger['classes']['data_store_instructions']==48
    return dict(disassembly=raw,ledger=ledger,stack=0,spills=0,public_loop_tripcount=12,
                alignment_mod32=ins[0][0]%32,alignment_mod64=ins[0][0]%64)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('result',type=Path);a=ap.parse_args()
    root=a.result.resolve();records={}
    serious=json.loads((EXP/'results/encap-eager-serious-20260922/metadata.json').read_text())
    clean=EXP.parents[1]/'clean/avx2-gt32-clean'
    assert all(sha(clean/p)==d for p,d in serious['frozen_clean_manifest'].items())
    for d in sorted(root.iterdir()):
        if not (d/'stq-summary.json').exists():continue
        meta=json.loads((d/'metadata.json').read_text())
        summary=json.loads((d/'stq-summary.json').read_text())
        source=Path(meta['campaign'])/'crypto_kem/ntruplus768'/meta['implementation']
        target=root/'installed-sources'/meta['implementation']
        if not target.exists():shutil.copytree(source,target)
        manifest={str(p.relative_to(target)):sha(p) for p in target.rglob('*') if p.is_file()}
        assert all(sha(source/p)==h for p,h in manifest.items())
        assert sha(d/'measure')==meta['measure_elf_sha256']
        pristine=Path('/home/nuc/supercop-20260627')
        assert sha(pristine/'crypto_kem/measure.c')==meta['measure_source_sha256']
        launches=[]
        for path in sorted((d/'fresh-launches').glob('launch-*.out')):
            text=path.read_text();row={}
            for op in ['keypair_cycles','enc_cycles','dec_cycles']:
                values=decode_observations(text,op);assert len(values)==96
                row[op]=stabilized_quartiles(values)
            launches.append(row)
        assert len(launches)==9
        symbols=['ntruplus768_keypair_impl','ntruplus768_enc_derand_impl','ntruplus768_dec_impl',
                 'ntruplus768_basemul_general_m_avx2','ntruplus768_exp001_basemul_eager_m']
        record={'source_manifest':manifest,'elf_sha256':sha(d/'measure'),
                'compiler':summary['measure_identity'],'layout':elf_layout(d/'measure',tuple(symbols)),
                'stq':summary['operations'],'launches':launches}
        if 'candidate' in d.name:
            name='ntruplus768_basemul_general_m_avx2' if 'shared-eager' in meta['implementation'] else 'ntruplus768_exp001_basemul_eager_m'
            record['eager_body_audit']=body_audit(d/'measure',name)
        records[d.name]=record
    deltas={}
    for control in ['native-official','native-current']:
        deltas[control]={}
        for op in ['keypair_cycles','enc_cycles','dec_cycles']:
            base=records[control]['stq'][op]['stq2'];new=records['native-candidate']['stq'][op]['stq2']
            ds=[c[op][1]-b[op][1] for c,b in zip(records['native-candidate']['launches'],records[control]['launches'])]
            deltas[control][op]={'pooled_stq2_delta':new-base,'percent':100*(new-base)/base,
                'index_matched_launch_deltas':ds,'favorable_launches':sum(x<0 for x in ds),
                'caution':'independent sequential campaign launches; not balanced paired causal evidence'}
    pairs=json.loads((root/'paired/summary.json').read_text())
    primary=next(x for x in pairs['rows'] if x['setting']=='normal-aslr-on' and x['operation']=='enc_cycles')
    regressions=[x for x in pairs['rows'] if x['bootstrap_ci95_low']>0]
    report={'evidence':records,'native_deltas':deltas,'paired':pairs,
            'gates':{'clean_unchanged':True,'native_measure_unmodified':True,
                     'primary_encap_CI_excludes_zero':primary['bootstrap_ci95_high']<0,
                     'paired_significant_regressions':regressions},
            'automatic_promotion':False,
            'note':'Review all gates; a local win is not qualification. Pinned Official remains the sole production baseline.'}
    (root/'qualification-summary.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'native_deltas':deltas,'gates':report['gates']},indent=2))

if __name__=='__main__':main()
