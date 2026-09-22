#!/usr/bin/env python3
"""Non-overwriting Encap-only eager BaseMul qualification installation."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

EXP=Path(__file__).resolve().parents[1]
REPO=next(p for p in EXP.parents if (p/'bench/supercop.lock').exists())
CLEAN=EXP.parents[1]/'clean/avx2-gt32-clean'
NAME='avx2-gt32-encap-eager-exp-sc20260831'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--campaign-root',type=Path,required=True)
    ap.add_argument('--qualification',type=Path,required=True)
    ap.add_argument('--shared-body',action='store_true')
    a=ap.parse_args()
    meta=json.loads((a.qualification/'metadata.json').read_text())
    summary=json.loads((a.qualification/'summary.json').read_text())
    assert meta['fresh_process_launches']==9
    assert summary['full_polynomial_island']['favorable_launches']==9
    for name,digest in meta['frozen_clean_manifest'].items():
        assert sha(CLEAN/name)==digest, name
    source=EXP/'generated/encap_fn_eager.S'
    assert sha(source)==meta['source_sha256'][str(source)]
    name=NAME.replace('encap-eager','shared-eager-inplace') if a.shared_body else NAME
    subprocess.run([sys.executable,str(REPO/'scripts/install_supercop_768_clean.py'),
        '--campaign-root',str(a.campaign_root),'--implementation',name],check=True)
    target=a.campaign_root/'crypto_kem/ntruplus768'/name
    if a.shared_body:
        # Replace exactly one existing emission, retaining original constant
        # tables. No duplicate multiplication body or new caller wrapper.
        symbol='ntruplus768_basemul_general_m_avx2'
        generated_symbol='ntruplus768_exp001_basemul_eager_m'
        body=source.read_text().split(generated_symbol+':\n',1)[1].split('.size ',1)[0]
        body=re.sub(r'\.Leager_bm_b3_loop\d+', '.Lqualified_eager_loop',body)
        body=body.replace('.Leager_', '.Ltile4_')
        # Remain in the ORIGINAL .text section. A new per-function section
        # would reorder this body relative to unrelated legacy functions.
        emission=f'.p2align 5\n.globl {symbol}\n.type {symbol},@function\n{symbol}:\n{body}.size {symbol},.-{symbol}'
        path=target/'basemul.s';text=path.read_text()
        old=' TILE4_BASEMUL_B3_FUNCTION '+symbol+', TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA'
        assert text.count(old)==1
        path.write_text(text.replace(old,emission))
    else:
        shutil.copy2(source,target/'encap_eager.s')
        path=target/'encap.c'; text=path.read_text()
        old='ntruplus768_basemul_general_m_avx2(scratch.c, scratch.h, scratch.r);'
        assert text.count(old)==1
        text=text.replace(old,'ntruplus768_exp001_basemul_eager_m(scratch.c, scratch.h, scratch.r);')
        text='extern void ntruplus768_exp001_basemul_eager_m(short *, const short *, const short *);\n'+text
        path.write_text(text)
    manifest=target/'SOURCE-MANIFEST.json'; data=json.loads(manifest.read_text())
    data['qualification']='candidate only; promotion requires Native and paired controls'
    data['delta']={'caller':'Encap and Decap general-M product' if a.shared_body else 'Encap only',
        'files':['basemul.s'] if a.shared_body else ['encap.c','encap_eager.s'],
        'kernel_sha256':sha(source),'diagnostic_metadata_sha256':sha(a.qualification/'metadata.json'),
        'test_wrapper_installed':False,'add_m':'unchanged separate call',
        'hash_staging':'unchanged; no prefixed-buffer optimization'}
    data['delta']['shared_body']=a.shared_body
    manifest.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    (target/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(target.iterdir())
        if p.is_file() and p.name!='SHA256SUMS'))
    print(target)

if __name__=='__main__':main()
