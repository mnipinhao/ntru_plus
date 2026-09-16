#!/usr/bin/env python3
"""Direct same-binary Official versus P3B11 FromBytes PMU."""
from __future__ import annotations
import json,shutil,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;EXP=HERE.parent;P3B11=EXP/"gt_fr0_d1_input_once_frombytes";P3B3=EXP/"gt_fr0_d1_byte_boundary_pmu";PACK=HERE.parents[4]/"NTRU+864/asm/pack.s"
HOST="pi@100.99.191.9";REMOTE="/home/pi/ntruplus-experiments/gt864-p3b17-frombytes-remaining";OUT=HERE/"build";SYNC=OUT/"sync";RAW=OUT/"raw"
def command(a:list[str],cwd:Path|None=None)->str:return subprocess.check_output(a,text=True,stderr=subprocess.STDOUT,cwd=cwd)
def ssh(s:str)->str:return command(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10",HOST,s])
def summary(rows):return {name:{m:statistics.median(r[i] for r in rows if r[0]==name) for i,m in enumerate(("cycles","instructions","branches"),1)} for name in sorted({r[0] for r in rows})}
def main()->None:
 command(["python3",str(P3B11/"prepare.py")]);SYNC.mkdir(parents=True,exist_ok=True);RAW.mkdir(parents=True,exist_ok=True)
 sources={"Makefile":HERE/"pi5-Makefile","bench_pi5.c":HERE/"bench_pi5.c","candidate.c":P3B11/"build/input_once_frombytes.c","input_once_frombytes.h":P3B11/"input_once_frombytes.h","p3b11_tables.h":P3B11/"build/p3b11_tables.h","stock_wrapper.S":P3B3/"stock_wrapper.S","pack.s":PACK}
 for n,p in sources.items():shutil.copy2(p,SYNC/n)
 ssh(f"mkdir -p {REMOTE}");print(command(["rsync","-av","--delete",str(SYNC)+"/",HOST+":"+REMOTE+"/"]),flush=True)
 env=ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
 if "Cortex-A76" not in env or "throttled=0x0" not in env:raise RuntimeError(env)
 (RAW/"environment.txt").write_text(env)
 build=ssh(f"cd {REMOTE} && make clean && make -B all && make check && size build/*.o build/bench && objdump -dr build/candidate.o && objdump -dr build/raw_pack.o")
 if "p3b17_correctness=pass" not in build:raise RuntimeError("correctness marker absent")
 (RAW/"build-correctness-object.log").write_text(build)
 rows=[];reps=[]
 for rep in range(3):
  rr=[]
  for order in (0,1):
   text=ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench {order}");(RAW/f"rep{rep}-{order}.log").write_text(text)
   parsed=[line.split(",") for line in text.splitlines() if line.startswith("sample,")]
   if len(parsed)!=82:raise RuntimeError(f"samples={len(parsed)}")
   rr.extend((p[1],*(float(v) for v in p[2:])) for p in parsed)
  reps.append(summary(rr));rows.extend(rr)
  thermal=ssh("vcgencmd measure_temp; vcgencmd get_throttled")
  if "throttled=0x0" not in thermal:raise RuntimeError(thermal)
 overall=summary(rows);a=overall["from_official_api"];b=overall["from_p3b11"]
 result={"experiment":"D1-P3B17","correctness":"pass","overall":overall,"p3b11_minus_official":{k:b[k]-a[k] for k in ("cycles","instructions","branches")},"repetitions":reps,"throttled":"0x0","production_linked":False}
 (OUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
