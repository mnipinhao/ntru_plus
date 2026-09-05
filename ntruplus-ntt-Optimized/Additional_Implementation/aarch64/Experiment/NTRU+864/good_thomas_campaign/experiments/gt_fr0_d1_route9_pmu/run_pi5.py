#!/usr/bin/env python3
from __future__ import annotations
import json,math,re,shutil,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent; OUT=HERE/"build/pi5"; SYNC=OUT/"sync"; RAW=OUT/"raw"
HOST="pi@100.99.191.9"; REMOTE="/home/pi/ntruplus-experiments/gt864-p3b1-route9"
OPS=("f2o_current","f2o_factor","f2o_r9a","f2o_r9b","o2f_current","o2f_factor","o2f_r9a","o2f_r9b")
def cmd(a,c=False):
 r=subprocess.run(a,check=True,text=True,capture_output=c);return r.stdout if c else ""
def ssh(s):return cmd(["ssh","-o","BatchMode=yes",HOST,s],True)
def pct(v,p):v=sorted(v);x=(len(v)-1)*p/100;l=math.floor(x);h=math.ceil(x);return v[l] if l==h else v[l]*(h-x)+v[h]*(x-l)
def parse(s):
 pat=re.compile(r"^sample,operation=(\w+),index=\d+,position=\d+,cycles=([0-9.]+),instructions=([0-9.]+),branches=([0-9.]+)$")
 rows=[(m.group(1),*[float(m.group(i)) for i in range(2,5)])for line in s.splitlines()if(m:=pat.match(line))];assert len(rows)==41*8;return rows
def summary(rows):return {op:{metric:pct([r[i] for r in rows if r[0]==op],50)for metric,i in(("cycles",1),("instructions",2),("branches",3))}for op in OPS}
def main():
 SYNC.mkdir(parents=True,exist_ok=True);RAW.mkdir(parents=True,exist_ok=True)
 cmd(["python3",str(HERE/"generate_tables.py")]);
 for name,src in {"Makefile":HERE/"pi5-Makefile","route9.c":HERE/"route9.c","route9.h":HERE/"route9.h","test_route9.c":HERE/"test_route9.c","bench_route9.c":HERE/"bench_route9.c","p3b1_tables.h":HERE/"build/p3b1_tables.h"}.items():shutil.copy2(src,SYNC/name)
 ssh(f"mkdir -p {REMOTE}");cmd(["rsync","-av",f"{SYNC}/",f"{HOST}:{REMOTE}/"])
 env=ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd get_throttled");assert "Cortex-A76" in env and "throttled=0x0" in env;(RAW/"environment.txt").write_text(env)
 build=ssh(f"cd {REMOTE} && make clean && make all && make check && size build/test build/bench && size -A build/route9.o && nm -S --size-sort build/route9.o && objdump -dr build/route9.o");assert "p3b1_route9=pass" in build;(RAW/"build-test-disassembly.log").write_text(build)
 reps=[];allrows=[]
 for n in range(3):
  rows=[]
  for order in ("01234567","76543210"):
   x=ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench {order}");(RAW/f"rep{n}-{order}.log").write_text(x);rows+=parse(x)
  reps.append(summary(rows));allrows+=rows
  thermal=ssh("vcgencmd get_throttled");assert "throttled=0x0" in thermal
 result={"experiment":"D1-P3B1","host":HOST,"core":3,"correctness":"pass","repetitions":reps,"overall":summary(allrows),"throttled":"0x0","production_linked":False}
 (OUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
