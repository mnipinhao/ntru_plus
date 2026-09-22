#!/usr/bin/env python3
"""Serial Native and fixed-ELF qualification; never writes clean sources."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from install_encap_eager import REPO, EXP, NAME, sha

def run(args):
    print('RUN',*map(str,args),flush=True)
    subprocess.run(list(map(str,args)),cwd=REPO,check=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--campaign-root',type=Path,required=True)
    ap.add_argument('--stage',choices=['native','fixed'],required=True)
    ap.add_argument('--shared-body',action='store_true')
    ap.add_argument('--result-tag',help='new result directory name for an independent rerun')
    a=ap.parse_args()
    campaign=a.campaign_root.resolve()
    tag=a.result_tag or ('eager-shared-inplace-qualification-20260922' if a.shared_body else 'eager-qualification-20260922')
    if Path(tag).name!=tag:raise SystemExit('result tag must be one directory name')
    out=EXP/'results'/tag
    out.mkdir(exist_ok=True)
    (out/'.gitignore').write_text('**/measure\n')
    base='avx2-gt32-clean'
    candidate=NAME.replace('encap-eager','shared-eager-inplace') if a.shared_body else NAME
    impl=campaign/'crypto_kem/ntruplus768'
    if a.stage=='native':
        if not (impl/base).exists():
            run([sys.executable,REPO/'scripts/install_supercop_768_clean.py','--campaign-root',campaign])
        if not (impl/candidate).exists():
            run([sys.executable,EXP/'tools/install_encap_eager.py','--campaign-root',campaign,
                 '--qualification',EXP/'results/encap-eager-serious-20260922']+
                (['--shared-body'] if a.shared_body else []))
        jobs=[('official','avx2'),('current',base),('candidate',candidate)]
    else:
        # Source-identical assembly content, distinct archive member order.
        for name in [base,candidate]:
            target=impl/(name+'-reversed')
            if not target.exists():
                shutil.copytree(impl/name,target)
                mapping={'ntt.s':'aaa_ntt.s','ntt_m.s':'aab_ntt_m.s',
                         'basemul.s':'zzz_basemul.s','pack.s':'yyy_pack.s'}
                if (target/'encap_eager.s').exists():mapping['encap_eager.s']='zzx_encap_eager.s'
                for src,dst in mapping.items():
                    (target/src).rename(target/dst)
                    assert sha(target/dst)==sha(impl/name/src)
                (target/'PLACEMENT.json').write_text(json.dumps(mapping,indent=2)+'\n')
        jobs=[('current',base),('candidate',candidate),
              ('current-reversed',base+'-reversed'),('candidate-reversed',candidate+'-reversed')]
    for label,name in jobs:
        target=out/(a.stage+'-'+label)
        if (target/'stq-summary.json').exists():continue
        command=[sys.executable,REPO/'scripts/run_supercop_benchmark.py',
                 '--campaign-root',campaign,'--parameter','768','--implementation',name,
                 '--cpu','1','--mode','native-kem','--fresh-launches','9',
                 '--require-frequency-control','--result-dir',target]
        if a.stage=='fixed':command+=['--compiler-wrapper',REPO/'bench/supercop/okc-o3gc.sh']
        run(command)
    if a.stage=='fixed':
        run([sys.executable,REPO/'scripts/run_supercop_paired.py',
             '--official',out/'fixed-current/measure','--candidate',out/'fixed-candidate/measure',
             '--official-reversed',out/'fixed-current-reversed/measure',
             '--candidate-reversed',out/'fixed-candidate-reversed/measure',
             '--cpu','1','--compiler-recipe','SUPERCOP common O3GC', '--output',out/'paired'])

if __name__=='__main__':main()
