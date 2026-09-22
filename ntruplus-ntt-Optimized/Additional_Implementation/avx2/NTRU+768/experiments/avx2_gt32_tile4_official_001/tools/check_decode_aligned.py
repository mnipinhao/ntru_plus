#!/usr/bin/env python3
"""Reproducible primitive/guard-page/sanitizer closure, never benchmarks."""
import argparse
import json
import os
import subprocess
from run_encap_live_b3_short import EXP,CLEAN,sha

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tag',required=True);a=ap.parse_args()
    root=EXP/'results'/a.tag;root.mkdir()
    commands=[]
    def run(args,label):
        args=list(map(str,args));commands.append(args)
        p=subprocess.run(args,text=True,capture_output=True,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
        (root/(label+'.out')).write_text(p.stdout);(root/(label+'.err')).write_text(p.stderr)
        assert p.returncode==0,(label,p.stderr)
    run(['python3',EXP/'tools/generate_decode_aligned.py','--check'],'generator')
    for mode in ('normal','sanitize'):
        flags=['-O3','-mavx2','-Wall','-Wextra','-Werror','-I'+str(EXP/'generated')]
        if mode=='sanitize':flags+=['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
        elf=root/('test-'+mode)
        run(['cc',*flags,EXP/'tests/test_decode_aligned.c',EXP/'generated/decode_aligned.S',CLEAN/'pack.s','-o',elf],mode+'-build')
        run([elf],mode+'-test')
        sub=root/mode;sub.mkdir()
        run(['python3',EXP/'tools/audit_decode_aligned.py',elf,sub],mode+'-audit')
    paths=[EXP/'tests/test_decode_aligned.c',EXP/'generated/decode_aligned.S',EXP/'generated/decode_aligned_mapping.h',
           EXP/'tools/generate_decode_aligned.py',EXP/'tools/audit_decode_aligned.py',CLEAN/'pack.s']
    (root/'manifest.json').write_text(json.dumps({'commands':commands,'source_sha256':{str(p):sha(p) for p in paths},
        'test_elf_sha256':{m:sha(root/('test-'+m)) for m in ('normal','sanitize')},'all_pass':True},indent=2)+'\n')
    (root/'.gitignore').write_text('test-normal\ntest-sanitize\n')
    print(root)
if __name__=='__main__':main()
