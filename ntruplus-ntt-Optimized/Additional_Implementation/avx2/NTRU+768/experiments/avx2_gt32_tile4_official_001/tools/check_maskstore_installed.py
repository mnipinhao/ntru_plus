"""Test the actual installed files (not a research call redirection)."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from install_pack_maskstore import EXP,REPO,NAME,sha
from run_pack_triad import audit

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--campaign-root',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    a.output.mkdir(exist_ok=False)
    kat=REPO/'third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768'
    names=['keygen.c','encap.c','decap.c','poly.c','symmetric.c','fips202.c','baseinv.c','consts.c',
           'KeccakP-1600-AVX2.s','cbd.s','crepmod3.s','add.s','ntt.s','ntt_m.s','ntt_p.s','invntt.s','basemul.s','batch_inverse.s','pack.s']
    records={};reference=None
    for label,impl in [('current','avx2-gt32-clean'),('candidate',NAME)]:
        src=a.campaign_root/'crypto_kem/ntruplus768'/impl
        for san in (False,True):
            key=label+('-san' if san else '');exe=a.output/key
            cmd=['cc','-O1' if san else '-O3','-g','-mavx2','-march=native','-fwrapv','-fno-strict-aliasing',
                 '-I'+str(src),'-I'+str(kat),str(EXP/'tests/test_maskstore_installed.c'),
                 *[str(src/n) for n in names],str(kat/'kat/aes.c'),str(kat/'kat/rng.c'),'-o',str(exe)]
            if san:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
            build=subprocess.run(cmd,cwd=src,capture_output=True,check=True)
            (a.output/(key+'.build.log')).write_bytes(build.stdout+build.stderr)
            proc=subprocess.run([str(exe)],capture_output=True,
                env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
            (a.output/(key+'.transcript')).write_bytes(proc.stdout)
            (a.output/(key+'.log')).write_bytes(proc.stderr)
            proc.check_returncode()
            if reference is None:reference=proc.stdout
            assert proc.stdout==reference
            records[key]={'command':cmd,'ELF_sha256':sha(exe),'transcript_sha256':sha(a.output/(key+'.transcript'))}
            if not san:
                leaf=audit(exe,a.output,{'m' if label=='candidate' else 'c':'ntruplus768_pack_m_lazy10788_avx2'})
                (a.output/(key+'.linked-audit.json')).write_text(json.dumps(leaf,indent=2)+'\n')
    sources={}
    for impl in ['avx2-gt32-clean',NAME]:
        src=a.campaign_root/'crypto_kem/ntruplus768'/impl
        sources[impl]={p.name:sha(p) for p in src.iterdir() if p.is_file()}
    changed=[n for n in names if sources[NAME][n]!=sources['avx2-gt32-clean'][n]]
    assert changed==['pack.s']
    (a.output/'summary.json').write_text(json.dumps({'tests':records,'source_manifests':sources,
        'changed_code_files':changed,'distinct_key_vectors':100,'sanitizers':'ASan/UBSan pass',
        'against':'frozen current GT; Official compatibility also checked by Native SUPERCOP try'},indent=2)+'\n')
    (a.output/'.gitignore').write_text('current\ncandidate\ncurrent-san\ncandidate-san\n')
    print('PASS installed current/candidate and sanitized transcripts exact; only pack.s differs')

if __name__=='__main__':main()
