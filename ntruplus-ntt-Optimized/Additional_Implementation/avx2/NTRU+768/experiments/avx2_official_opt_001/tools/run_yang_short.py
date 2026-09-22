#!/usr/bin/env python3
"""Fixed normal/ASLR-on, three launches, pinned SUPERCOP cycle-counter short test."""
import argparse,hashlib,json,subprocess,shutil,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(args):return subprocess.run(args,cwd=ROOT,text=True,capture_output=True,check=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stq(v):
    n=len(v);s=[float(x) for x in sorted(v) for _ in range(8)]
    return [sum(s[n+2*i*n:3*n+2*i*n])/(2*n) for i in range(3)]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tag',required=True);ap.add_argument('--control',choices=['official','wresident','factored','pair32'],default='official');ap.add_argument('--candidate',choices=['factored','pair32','stage5reuse'],default='factored');ap.add_argument('--reversed-placement',action='store_true');a=ap.parse_args()
    assert (a.candidate,a.control) in [('factored','official'),('factored','wresident'),('pair32','official'),('pair32','factored'),('stage5reuse','pair32')]
    assert not a.reversed_placement or a.candidate=='stage5reuse'
    policy={'/sys/devices/system/cpu/cpu1/cpufreq/scaling_governor':'performance','/sys/devices/system/cpu/intel_pstate/no_turbo':'1','/proc/sys/kernel/randomize_va_space':'2'}
    def check():
        for path,value in policy.items():assert Path(path).read_text().strip()==value,('timing blocked',path)
    check();out=ROOT/'results'/a.tag;out.mkdir(exist_ok=False)
    binary=('bench_yang_stage5reuse_pair32'+('_reversed' if a.reversed_placement else '') if a.candidate=='stage5reuse' else
            'bench_yang_pair32'+('_factored' if a.control=='factored' else '') if a.candidate=='pair32' else
            'bench_yang'+('_wresident' if a.control=='wresident' else ''))
    checktarget='check-yang-stage5reuse' if a.candidate=='stage5reuse' else 'check-yang-pair32' if a.candidate=='pair32' else 'check-yang'
    for target in [checktarget,'build/'+binary]:
        r=run(['make',target]);(out/('check.log' if target==checktarget else 'build.log')).write_text(r.stdout+r.stderr)
    sanbuild='build_yang_stage5reuse_san' if a.candidate=='stage5reuse' else 'build_yang_pair32_san' if a.candidate=='pair32' else 'build_yang_san'
    san=subprocess.run(['make','BUILD='+sanbuild,'CFLAGS=-O1 -g -mavx2 -fsanitize=address,undefined -fno-omit-frame-pointer -fwrapv',checktarget],cwd=ROOT,text=True,capture_output=True,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
    (out/'sanitizer.log').write_text(san.stdout+san.stderr);san.check_returncode()
    r=run(['python3','tools/audit_yang_'+a.candidate+'.py']);(out/'audit.log').write_text(r.stdout+r.stderr)
    elf=ROOT/'build'/binary;shutil.copy2(elf,out/'measure.elf');rows=[];ids=[]
    for launch in range(3):
        check();r=run(['taskset','-c','1',str(elf)]);assert 'preflight=pass' in r.stderr
        (out/f'launch-{launch}.out').write_text(r.stdout);(out/f'launch-{launch}.err').write_text(r.stderr);ids.append(r.stderr)
        rows += [(launch,*map(int,s.split(','))) for s in r.stdout.splitlines() if s[:1].isdigit()]
    summary={}
    for region,name in enumerate(['inverse','inverse_crepmod3','complete_decap']):
        def values(v,l=None):return [r[-1] for r in rows if r[1:3]==(region,v) and (l is None or r[0]==l)]
        c=stq(values(0));s=stq(values(1));ds=[stq(values(1,l))[1]-stq(values(0,l))[1] for l in range(3)]
        summary[name]={'control_stq':c,'candidate_stq':s,'delta':s[1]-c[1],'launch_deltas':ds,'favorable':sum(x<0 for x in ds)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    files=[ROOT/'Makefile',ROOT/'yang.mk']
    for directory in ['src','asm','tests','bench','tools','upstream/supercop-avx2']:
        files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in str(p))
    (out/'metadata.json').write_text(json.dumps({'class':'SUPERCOP-derived diagnostic NOT Native','control_inverse':a.control,'candidate':'yang-'+a.candidate,'caller':'both frozen caller-lazy; only inverse substituted',
        'backend':ids,'counter_policy':policy,'cpu1_siblings':Path('/sys/devices/system/cpu/cpu1/topology/thread_siblings_list').read_text(),'placement':'reversed/ASLR-on diagnostic' if a.reversed_placement else 'normal/ASLR-on preselected','elf_sha256':sha(elf),
        'compiler':run(['cc','--version']).stdout,'build_recipe_file':'build.log','source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in files},
        'stq_header_sha256':sha(Path('/home/nuc/supercop-20260627/include/stq.h')),
        'residency':'16 matched banks; reset outside timing; public operation dispatch outside region; 8 balanced blocks of 64 observations per variant'},indent=2)+'\n')
    (out/'disassembly.txt').write_text(run(['objdump','-d',str(elf)]).stdout)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
