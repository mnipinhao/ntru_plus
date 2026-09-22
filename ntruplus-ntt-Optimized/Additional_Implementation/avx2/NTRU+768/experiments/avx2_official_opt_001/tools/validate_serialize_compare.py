#!/usr/bin/env python3
"""Archive non-timing gates and repeatability checks without altering exports."""
import os,subprocess,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'results/serialize-compare-validation-20260922';out.mkdir(exist_ok=False)
    files=[ROOT/'asm/ntruplus768_officialopt_serialize_compare.s',ROOT/'src/kem_serialize_compare.c']
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    before=[digest(p) for p in files]
    env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0')
    commands=[['python3','tools/generate_serialize_compare.py'],['make','check-serialize-compare'],['make','BUILD=build_compare_san','CFLAGS=-O1 -g -mavx2 -march=native -fsanitize=address,undefined -fno-omit-frame-pointer -fwrapv','check-serialize-compare'],['python3','tools/audit_serialize_compare.py']]
    for i,cmd in enumerate(commands):
        r=subprocess.run(cmd,cwd=ROOT,env=env,text=True,capture_output=True)
        (out/f'gate-{i}.log').write_text(r.stdout+r.stderr)
        if r.returncode:raise SystemExit(f'failed {cmd}: see {out}')
    assert before==[digest(p) for p in files]
    (out/'summary.json').write_text(json.dumps({'commands':commands,'repeatable_source_sha256':dict(zip((str(p.relative_to(ROOT)) for p in files),before)),'all_passed':True,'f_retry':'injection only, natural failure not covered','sanitizer':'ASan/UBSan C; LSan disabled for ptrace; ASM additionally uses guard-page and immutability tests'},indent=2)+'\n')
if __name__=='__main__':main()
