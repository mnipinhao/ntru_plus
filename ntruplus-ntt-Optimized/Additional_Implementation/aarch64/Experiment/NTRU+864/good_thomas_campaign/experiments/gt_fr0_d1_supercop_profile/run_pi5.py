#!/usr/bin/env python3
from pathlib import Path
import subprocess,json,statistics,collections
HERE=Path(__file__).resolve().parent;HOST='pi@100.99.191.9';REMOTE='/home/pi/ntruplus-experiments/gt864-p3b25-supercop-profile'
def cmd(a):return subprocess.check_output(a,text=True,stderr=subprocess.STDOUT)
def ssh(s):return cmd(['ssh','-o','BatchMode=yes',HOST,s])
def main():
 raw=HERE/'build/raw';raw.mkdir(parents=True,exist_ok=True)
 env=ssh('uname -a; gcc --version | head -1; vcgencmd get_throttled; git -C /home/pi/supercop-20260627/import/ntruplus-20260723 rev-parse HEAD; git -C /home/pi/supercop-20260627/import/ntruplus-20260723 remote -v; sha256sum /home/pi/supercop-20260627/crypto_kem/ntruplus864/aarch64/*')
 assert 'throttled=0x0' in env;(raw/'provenance.txt').write_text(env)
 audit=ssh(f'cd {REMOTE} && sha256sum *.so bench && objdump -dr gt/kem-normal.o && objdump -dr sc/kem-normal.o && readelf -d gt.so && readelf -d sc.so')
 (raw/'objects.log').write_text(audit)
 full=collections.defaultdict(list);profile=collections.defaultdict(list);counts=collections.defaultdict(set);overheads=[]
 for rep in range(3):
  for order in (0,1):
   out=ssh(f'cd {REMOTE} && taskset -c 3 ./bench {order}');(raw/f'rep{rep}-{order}.log').write_text(out)
   assert 'correctness=pass' in out and 'cross_version_pk_ct_differences=0' in out
   for l in out.splitlines():
    p=l.split(',')
    if p[0]=='full':full[tuple(p[1:3])].append(list(map(float,p[3:])))
    elif p[0]=='profile':profile[tuple(p[1:4])].append(float(p[5]));counts[tuple(p[1:4])].add(int(p[4]))
    elif l.startswith('profiler_empty_boundary_cycles='):overheads.append(float(l.split('=')[1]))
  thermal=ssh('vcgencmd measure_temp; vcgencmd get_throttled');assert 'throttled=0x0' in thermal
  print(f'repetition {rep+1}/3 complete',flush=True)
 result={'baseline':'SUPERCOP 20260627 installed aarch64 NTRU+864; upstream latest not verified','full':{'/'.join(k):dict(zip(('cycles','instructions','branches'),(statistics.median(row[i] for row in rows) for i in range(3)))) for k,rows in full.items()},'profile':{'/'.join(k):{'cycles':statistics.median(rows),'calls':sorted(counts[k])} for k,rows in profile.items()},'empty_boundary_cycles':overheads,'profile_method':'actual KEM direct-call instrumentation; empty-boundary adjusted cycles; separate from uninstrumented full benchmark','production_changed':False}
 (HERE/'build/summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
