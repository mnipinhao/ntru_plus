#!/usr/bin/env python3
"""Non-overwriting experiment-only Native install; replace Encap Forward only."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
REPO=next(p for p in ROOT.parents if (p/'bench/supercop.lock').exists())
NAME='avx2-gt32-encap-wavefront1-exp-sc20260831'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--campaign-root',type=Path,required=True)
    ap.add_argument('--qualification',type=Path,required=True)
    a=ap.parse_args()
    report=json.loads(a.qualification.read_text())
    assert report['label']=='supercop-derived-poly'
    for relative,digest in report['source_sha256'].items():
        if relative.startswith('clean/'):
            assert hashlib.sha256((ROOT.parent.parent/relative).read_bytes()).hexdigest()==digest
    range_report=json.loads((ROOT/'generated/tile4_encap_range_closure.json').read_text())
    assert range_report['status']=='proved-safe'
    for name,digest in range_report['source_sha256'].items():
        assert hashlib.sha256((ROOT.parent.parent/'clean/avx2-gt32-clean'/name).read_bytes()).hexdigest()==digest
    passed=next(x for x in report['pooled'] if x['candidate']==1 and x['mode']==4)
    assert passed['delta_stq2']<0 and passed['favorable_launches']==9
    generated=ROOT/'generated/encap_wavefront_1.s'
    expected=report['source_sha256']['experiments/avx2_gt32_tile4_official_001/generated/encap_wavefront_1.s']
    assert hashlib.sha256(generated.read_bytes()).hexdigest()==expected
    target=a.campaign_root/'crypto_kem/ntruplus768'/NAME
    assert not target.exists()
    subprocess.run([sys.executable,str(REPO/'scripts/install_supercop_768_clean.py'),
                    '--campaign-root',str(a.campaign_root),'--implementation',NAME],check=True)
    shutil.copy2(generated,target/'encap_wavefront.s')
    encap=target/'encap.c';text=encap.read_text()
    old='\tntruplus768_ntt_frontend_avx2(frontend, in);\n\tntruplus768_ntt_m_avx2(out, frontend);'
    assert text.count(old)==1
    text=text.replace(old,'\tntruplus768_exp_encap_wavefront_1(out, in, frontend);')
    declaration='extern void ntruplus768_exp_encap_wavefront_1(int16_t *, const int16_t *, int16_t *);\n\n'
    text=text.replace('static void forward_m(',declaration+'static void forward_m(',1)
    encap.write_text(text)
    manifest=target/'SOURCE-MANIFEST.json';m=json.loads(manifest.read_text())
    m['qualification']='experiment-only; no clean promotion'
    m['encap_wavefront']={'variant':1,'changed_caller':'encap only','new_reductions':0,
                         'qualification_sha256':hashlib.sha256(a.qualification.read_bytes()).hexdigest(),
                         'kernel_sha256':expected,'range_artifact_sha256':hashlib.sha256((ROOT/'generated/tile4_encap_range_closure.json').read_bytes()).hexdigest()}
    manifest.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    files=sorted(p for p in target.iterdir() if p.is_file() and p.name!='SHA256SUMS')
    (target/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
    print(target)


if __name__=='__main__':main()
