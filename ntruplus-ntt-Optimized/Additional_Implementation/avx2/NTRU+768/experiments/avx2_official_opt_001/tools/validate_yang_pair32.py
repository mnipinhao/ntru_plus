#!/usr/bin/env python3
"""Re-run non-timing gates and preserve outputs and artifact identities."""
import hashlib
import json
import os
import subprocess
from pathlib import Path
from close_yang_contract import ROOT


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0')
    records=[]
    commands=[['make','check-yang-pair32'],
      ['make','BUILD=build_yang_pair32_san',
       'CFLAGS=-O1 -g -mavx2 -fsanitize=address,undefined -fno-omit-frame-pointer -fwrapv',
       'check-yang-pair32'],['python3','tools/audit_yang_pair32.py']]
    for args in commands:
        run=subprocess.run(args,cwd=ROOT,env=env,text=True,capture_output=True)
        records.append({'argv':args,'returncode':run.returncode,
                        'stdout':run.stdout,'stderr':run.stderr})
        if run.returncode:
            print(run.stdout,run.stderr);raise SystemExit(run.returncode)
    generated=[ROOT/'asm/ntruplus768_officialopt_invntt_yang_pair32.s',
               ROOT/'results/yang-pair32-lowering.json']
    before=[sha(p) for p in generated]
    subprocess.run(['python3','tools/generate_yang_pair32.py'],cwd=ROOT,check=True)
    assert before==[sha(p) for p in generated]
    sources=[ROOT/'tools'/n for n in ('generate_yang_pair32.py','audit_yang_pair32.py',
             'validate_yang_pair32.py','audit_yang_followup.py','close_yang_contract.py')]
    sources += [ROOT/'tests'/n for n in ('test_inverse_ct.c','test_kem_ct.c',
                 'test_yang_guard.c','kem_yang_diag.c')]
    sources += [ROOT/'yang.mk',ROOT/'src/kem_lazy.c',generated[0]]
    binaries=[ROOT/b/n for b in ('build','build_yang_pair32_san') for n in
              ('test_inverse_yang_pair32','test_kem_yang_pair32','test_yang_pair32_guard')]
    result={'class':'correctness_and_reproducibility_not_benchmark','commands':records,
      'ASAN_OPTIONS':env['ASAN_OPTIONS'],
      'sanitizer_scope':'C harness; ASM memory covered separately by guard-page/canary and linked audit',
      'generator_reproducible':True,
      'compiler':subprocess.check_output(['cc','--version'],text=True).splitlines()[0],
      'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sources},
      'elf_sha256':{str(p.relative_to(ROOT)):sha(p) for p in binaries}}
    (ROOT/'results/yang-pair32-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Combined candidate: correctness, sanitizer, linked audit and reproducibility pass; no timing')


if __name__=='__main__':main()
