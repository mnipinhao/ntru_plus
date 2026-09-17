#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,shutil,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[1];GEN=E/'generated';B=E/'build/correctness';OFF=ROOT.parents[3]/'third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768';TEST=ROOT/'experiments/gt32_hwa_encap_dead_slot_frame_trim_094/tests/deterministic_encap.c';EXPECTED='22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8'
COMMON=['baseinv.c','consts.c','decap.c','fips202.c','kem.c','keygen.c','poly.c','symmetric.c','add.s','basemul.s','batch_inverse.s','cbd.s','crepmod3.s','invntt.s','ntt.s','ntt_m.s','ntt_p.s','pack.s','KeccakP-1600-AVX2.s']
def run(c,cwd=None,env=None):return subprocess.check_output(c,cwd=cwd,env=env,text=True)
def build(profile,out,flags,harness):
 enc=ROOT/'encap.c' if profile=='control' else E/'encap-rhash.c'
 run(['gcc',*flags,f'-I{ROOT}',f'-I{OFF}','-Wl,--gc-sections','-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2',f'-Wl,-T,{GEN/"tails.ld"}','-o',str(out),*(str(x) for x in harness),str(enc),str(E/'hash-g-from-m.c'),*(str(ROOT/x) for x in COMMON)])
def main():
 if B.exists():shutil.rmtree(B)
 B.mkdir(parents=True);flags=['-march=native','-mtune=native','-O3','-fwrapv','-fomit-frame-pointer','-ffunction-sections','-fdata-sections'];det={};kat={}
 for p in ('control','candidate'):
  x=B/f'deterministic-{p}';build(p,x,flags,[OFF/'randombytes.c',TEST]);det[p]=run([str(x)]).strip()
 if len(set(det.values()))!=1:raise SystemExit(f'deterministic mismatch {det}')
 for p in ('control','candidate'):
  x=B/f'kat-{p}';build(p,x,flags+['-Wno-unused-result'],[OFF/'kat/PQCgenKAT_kem.c',OFF/'kat/aes.c',OFF/'kat/rng.c']);d=B/f'kat-run-{p}';d.mkdir();run([str(x)],cwd=d);rsp=d/'PQCkemKAT_2336.rsp';h=hashlib.sha256(rsp.read_bytes()).hexdigest()
  if h!=EXPECTED:raise SystemExit(f'KAT mismatch {p}: {h}')
  kat[p]={'bytes':rsp.stat().st_size,'sha256':h}
 x=B/'deterministic-candidate-sanitized';sf=['-march=native','-mtune=native','-O1','-fwrapv','-fno-omit-frame-pointer','-fsanitize=address,undefined','-fno-sanitize-recover=all','-ffunction-sections','-fdata-sections'];build('candidate',x,sf,[OFF/'randombytes.c',TEST]);env=os.environ.copy();env['ASAN_OPTIONS']='detect_leaks=0:halt_on_error=1';env['UBSAN_OPTIONS']='halt_on_error=1:print_stacktrace=1';san=run([str(x)],env=env).strip()
 result={'deterministic':det,'kat':kat,'asan_ubsan_candidate':san};(GEN/'correctness.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
