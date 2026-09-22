#!/usr/bin/env python3
"""Matched readonly banks; exact pinned StQ slices; archive all raw cycles."""
import argparse, hashlib, json, subprocess, shutil
from pathlib import Path
from run_forward_caller_lazy_short import stq
ROOT=Path(__file__).resolve().parents[1]
def run(cmd):
    return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--launches',type=int,default=3);a=p.parse_args()
    controls={ '/sys/devices/system/cpu/cpu1/cpufreq/scaling_governor':'performance', '/sys/devices/system/cpu/intel_pstate/no_turbo':'1', '/proc/sys/kernel/randomize_va_space':'2'}
    for path,expected in controls.items():
        if Path(path).read_text().strip()!=expected:raise SystemExit('timing blocked: '+path)
    out=ROOT/'results'/a.tag;out.mkdir(exist_ok=False)
    for cmd in [['make','check-serialize-compare'],['make','build/bench_serialize_compare']]:
        r=run(cmd);(out/('check.log' if 'check-serialize-compare' in cmd else 'build.log')).write_text(r.stdout+r.stderr)
    elf=ROOT/'build/bench_serialize_compare';shutil.copy2(elf,out/'measure.elf')
    rows=[];ids=[]
    for launch in range(a.launches):
        r=run(['taskset','-c','1',str(elf)]);(out/f'launch-{launch}.out').write_text(r.stdout);(out/f'launch-{launch}.err').write_text(r.stderr)
        assert 'preflight=pass' in r.stderr;ids.append(r.stderr)
        rows.extend((launch,*map(int,line.split(','))) for line in r.stdout.splitlines() if line[:1].isdigit())
    summary={}
    for region,name in enumerate(['serialize_verify','full_decap']):
        values=lambda v,l=None:[row[-1] for row in rows if row[1:3]==(region,v) and (l is None or row[0]==l)]
        c=stq(values(0));s=stq(values(1));d=[stq(values(1,l))[1]-stq(values(0,l))[1] for l in range(a.launches)]
        summary[name]={'control_stq':c,'candidate_stq':s,'delta_stq2':s[1]-c[1],'launch_deltas':d,'favorable':sum(x<0 for x in d)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    sourcefiles=[ROOT/'Makefile',ROOT/'serialize_compare.mk']
    for directory in ['src','asm','tests','bench','tools','upstream/supercop-avx2']:
        sourcefiles.extend(x for x in (ROOT/directory).rglob('*') if x.is_file() and '__pycache__' not in str(x))
    (out/'metadata.json').write_text(json.dumps({'class':'SUPERCOP-derived diagnostic, NOT Native','backend':ids,'controls':controls,'elf_sha256':sha(elf),'source_sha256':{str(x.relative_to(ROOT)):sha(x) for x in sourcefiles},'compiler':run(['cc','--version']).stdout,'cpu1_siblings':Path('/sys/devices/system/cpu/cpu1/topology/thread_siblings_list').read_text(),'placement':'normal/ASLR-on','input':'16 identical read-only banks; output scratch required only by control; dispatch outside region'},indent=2)+'\n')
    (out/'disassembly.txt').write_text(run(['objdump','-d',str(elf)]).stdout)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
