#!/usr/bin/env python3
"""Serial Native, then conditional fixed-ELF confirmation; no clean changes."""
import argparse
import json
import shutil
import sys
from pathlib import Path
from install_pack_maskstore import EXP,REPO,NAME,sha
from qualify_encap_eager import run

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--campaign-root',type=Path,required=True)
    ap.add_argument('--stage',choices=['native','fixed'],required=True)
    a=ap.parse_args();campaign=a.campaign_root.resolve()
    out=EXP/'results/maskstore-native-qualification-20260922';out.mkdir(exist_ok=True)
    (out/'.gitignore').write_text('**/measure\n')
    base='avx2-gt32-clean';impl=campaign/'crypto_kem/ntruplus768'
    if a.stage=='native':
        if not (impl/base).exists():run([sys.executable,REPO/'scripts/install_supercop_768_clean.py','--campaign-root',campaign])
        if not (impl/NAME).exists():run([sys.executable,EXP/'tools/install_pack_maskstore.py','--campaign-root',campaign])
        if not (out/'installed-check-final/summary.json').exists():
            run([sys.executable,EXP/'tools/check_maskstore_installed.py','--campaign-root',campaign,'--output',out/'installed-check-final'])
        jobs=[('official','avx2'),('current',base),('candidate',NAME)]
    else:
        assert (out/'native-candidate/stq-summary.json').exists()
        for name in (base,NAME):
            target=impl/(name+'-reversed')
            if not target.exists():
                shutil.copytree(impl/name,target)
                mapping={'ntt.s':'aaa_ntt.s','ntt_m.s':'aab_ntt_m.s','basemul.s':'zzz_basemul.s','pack.s':'yyy_pack.s'}
                for src,dst in mapping.items():
                    (target/src).rename(target/dst);assert sha(target/dst)==sha(impl/name/src)
                (target/'PLACEMENT.json').write_text(json.dumps(mapping,indent=2)+'\n')
        jobs=[('current',base),('candidate',NAME),('current-reversed',base+'-reversed'),('candidate-reversed',NAME+'-reversed')]
    for label,name in jobs:
        target=out/(a.stage+'-'+label)
        if (target/'stq-summary.json').exists():continue
        cmd=[sys.executable,REPO/'scripts/run_supercop_benchmark.py','--campaign-root',campaign,
             '--parameter','768','--implementation',name,'--cpu','1','--mode','native-kem',
             '--fresh-launches','9','--require-frequency-control','--result-dir',target]
        if a.stage=='fixed':cmd+=['--compiler-wrapper',REPO/'bench/supercop/okc-o3gc.sh']
        run(cmd)
    if a.stage=='fixed':
        run([sys.executable,REPO/'scripts/run_supercop_paired.py','--official',out/'fixed-current/measure',
             '--candidate',out/'fixed-candidate/measure','--official-reversed',out/'fixed-current-reversed/measure',
             '--candidate-reversed',out/'fixed-candidate-reversed/measure','--cpu','1',
             '--compiler-recipe','SUPERCOP common O3GC','--output',out/'paired'])
        run([sys.executable,REPO/'scripts/summarize_supercop_paired.py','--campaign',out/'paired','--parameter','768'])

if __name__=='__main__':main()
