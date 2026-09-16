#!/usr/bin/env python3
"""Run the D1-P3B21 peak-26 pair-wait ToBytes gate on Cortex-A76."""
from __future__ import annotations
import json,re,shutil,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;BASE=HERE.parent/"gt_fr0_d1_pair_wait_tobytes";P3B6=HERE.parent/"gt_fr0_d1_input_once_tobytes"
HOST="pi@100.99.191.9";REMOTE="/home/pi/ntruplus-experiments/gt864-p3b21-peak26";OUT=HERE/"build";SYNC=OUT/"sync";RAW=OUT/"raw"
def command(a:list[str])->str:return subprocess.check_output(a,text=True,stderr=subprocess.STDOUT)
def ssh(s:str)->str:return command(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10",HOST,s])
def summary(rows):return {name:{m:statistics.median(r[i] for r in rows if r[0]==name) for i,m in enumerate(("cycles","instructions","branches"),1)} for name in sorted({r[0] for r in rows})}
def main()->None:
 command(["python3",str(HERE/"prepare.py")]);command(["python3",str(P3B6/"prepare.py")]);SYNC.mkdir(parents=True,exist_ok=True);RAW.mkdir(parents=True,exist_ok=True)
 sources={"Makefile":BASE/"pi5-Makefile","bench_pi5.c":BASE/"bench_pi5.c","pair_wait_tobytes.h":BASE/"pair_wait_tobytes.h","input_once_tobytes.h":P3B6/"input_once_tobytes.h","control.c":P3B6/"build/input_once_tobytes.c","candidate.c":OUT/"pair_wait_tobytes.c"}
 for n,p in sources.items():shutil.copy2(p,SYNC/n)
 ssh(f"mkdir -p {REMOTE}");print(command(["rsync","-av","--delete",str(SYNC)+"/",HOST+":"+REMOTE+"/"]),flush=True)
 env=ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
 if "Cortex-A76" not in env or "throttled=0x0" not in env:raise RuntimeError(env)
 (RAW/"environment.txt").write_text(env)
 build=ssh(f"cd {REMOTE} && make clean && make -B all && make check && size build/*.o build/bench && objdump -dr build/candidate.o")
 if "p3b15_pi_correctness=pass" not in build:raise RuntimeError("correctness")
 (RAW/"build-correctness-object.log").write_text(build);body=build.split("<pair_wait_top>:",1)[1].split("\n\n",1)[0]
 stack=[x for x in body.splitlines() if "[sp" in x];vector=[x for x in stack if re.search(r"\b(?:str|stp|ldr|ldp)\s+[qds][0-9]+",x)];nonabi=[x for x in vector if not re.search(r"\b(?:stp|ldp)\s+d(?:8|10|12|14), d(?:9|11|13|15)",x)]
 rows=[];reps=[]
 for rep in range(3):
  rr=[]
  for order in (0,1):
   out=ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench {order}");(RAW/f"rep{rep}-{order}.log").write_text(out);parsed=[x.split(",") for x in out.splitlines() if x.startswith("sample,")]
   if len(parsed)!=82:raise RuntimeError(f"samples={len(parsed)}")
   rr.extend((p[1],*(float(v) for v in p[2:])) for p in parsed)
  reps.append(summary(rr));rows.extend(rr)
  if "throttled=0x0" not in ssh("vcgencmd get_throttled"):raise RuntimeError("throttled")
 overall=summary(rows);a=overall["to_p3b6"];b=overall["to_pair_wait"]
 result={"experiment":"D1-P3B21","correctness":"pass","overall":overall,"candidate_minus_p3b6":{k:b[k]-a[k] for k in ("cycles","instructions","branches")},"stack_references":len(stack),"vector_stack_references":len(vector),"non_ABI_vector_stack_references":len(nonabi),"no_spill_gate":not nonabi,"cycle_gate":"candidate < P3B6","cycle_gate_pass":b["cycles"]<a["cycles"],"repetitions":reps,"throttled":"0x0","production_linked":False}
 (OUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
