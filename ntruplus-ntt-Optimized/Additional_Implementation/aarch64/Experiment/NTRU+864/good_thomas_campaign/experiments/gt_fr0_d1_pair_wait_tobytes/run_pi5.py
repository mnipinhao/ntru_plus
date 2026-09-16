#!/usr/bin/env python3
"""Run the D1-P3B15 no-scratch pair-wait gate on Cortex-A76."""
from __future__ import annotations
import json,re,shutil,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;P3B6=HERE.parent/"gt_fr0_d1_input_once_tobytes"
HOST="pi@100.99.191.9";REMOTE="/home/pi/ntruplus-experiments/gt864-p3b15-pair-wait"
OUT=HERE/"build";SYNC=OUT/"sync";RAW=OUT/"raw"
def command(a:list[str],cwd:Path|None=None)->str:return subprocess.check_output(a,text=True,stderr=subprocess.STDOUT,cwd=cwd)
def ssh(s:str)->str:return command(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10",HOST,s])
def summary(rows):return {name:{m:statistics.median(r[i] for r in rows if r[0]==name) for i,m in enumerate(("cycles","instructions","branches"),1)} for name in sorted({r[0] for r in rows})}
def main()->None:
 command(["python3",str(HERE/"prepare.py")]);command(["python3",str(P3B6/"prepare.py")])
 SYNC.mkdir(parents=True,exist_ok=True);RAW.mkdir(parents=True,exist_ok=True)
 sources={"Makefile":HERE/"pi5-Makefile","bench_pi5.c":HERE/"bench_pi5.c","pair_wait_tobytes.h":HERE/"pair_wait_tobytes.h","input_once_tobytes.h":P3B6/"input_once_tobytes.h","control.c":P3B6/"build/input_once_tobytes.c","candidate.c":OUT/"pair_wait_tobytes.c"}
 for name,path in sources.items():shutil.copy2(path,SYNC/name)
 ssh(f"mkdir -p {REMOTE}");print(command(["rsync","-av","--delete",str(SYNC)+"/",HOST+":"+REMOTE+"/"]),flush=True)
 env=ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
 if "Cortex-A76" not in env or "throttled=0x0" not in env:raise RuntimeError(env)
 (RAW/"environment.txt").write_text(env)
 build=ssh(f"cd {REMOTE} && make clean && make -B all && make check && size build/*.o build/bench && objdump -dr build/candidate.o")
 if "p3b15_pi_correctness=pass" not in build:raise RuntimeError("correctness marker absent")
 (RAW/"build-correctness-object.log").write_text(build)
 body=build.split("<pair_wait_top>:",1)[1].split("\n\n",1)[0]
 vector_spills=[line for line in body.splitlines() if re.search(r"\b(?:str|stp|ldr|ldp)\s+[qds][0-9]+.*\[sp",line)]
 stack_refs=[line for line in body.splitlines() if "[sp" in line]
 rows=[];repetitions=[]
 for rep in range(3):
  rr=[]
  for order in (0,1):
   text=ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench {order}");(RAW/f"rep{rep}-{order}.log").write_text(text)
   parsed=[line.split(",") for line in text.splitlines() if line.startswith("sample,")]
   if len(parsed)!=82:raise RuntimeError(f"samples={len(parsed)}")
   rr.extend((p[1],*(float(v) for v in p[2:])) for p in parsed)
  repetitions.append(summary(rr));rows.extend(rr)
  thermal=ssh("vcgencmd measure_temp; vcgencmd get_throttled")
  if "throttled=0x0" not in thermal:raise RuntimeError(thermal)
 overall=summary(rows);a=overall["to_p3b6"];b=overall["to_pair_wait"]
 result={"experiment":"D1-P3B15","correctness":"pass","overall":overall,"pair_wait_minus_p3b6":{k:b[k]-a[k] for k in ("cycles","instructions","branches")},"candidate_stack_refs":len(stack_refs),"candidate_vector_spills":len(vector_spills),"register_gate_pass":not vector_spills,"repetitions":repetitions,"throttled":"0x0","production_linked":False}
 (OUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
