#!/usr/bin/env python3
"""Run P3B23 local transpose FromBytes on Pi5."""
from __future__ import annotations
import json,re,shutil,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;P3B11=HERE.parent/"gt_fr0_d1_input_once_frombytes";HOST="pi@100.99.191.9";REMOTE="/home/pi/ntruplus-experiments/gt864-p3b23-cluster-transpose";OUT=HERE/"build";SYNC=OUT/"sync";RAW=OUT/"raw"
def command(a:list[str])->str:return subprocess.check_output(a,text=True,stderr=subprocess.STDOUT)
def ssh(s:str)->str:return command(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10",HOST,s])
def summary(rows):return {name:{m:statistics.median(r[i] for r in rows if r[0]==name) for i,m in enumerate(("cycles","instructions","branches"),1)} for name in sorted({r[0] for r in rows})}
def main()->None:
 command(["python3",str(HERE/"prepare.py")]);command(["python3",str(P3B11/"prepare.py")]);SYNC.mkdir(parents=True,exist_ok=True);RAW.mkdir(parents=True,exist_ok=True)
 sources={"Makefile":HERE/"pi5-Makefile","bench_pi5.c":HERE/"bench_pi5.c","cluster_transpose_frombytes.h":HERE/"cluster_transpose_frombytes.h","input_once_frombytes.h":P3B11/"input_once_frombytes.h","control.c":P3B11/"build/input_once_frombytes.c","candidate.c":OUT/"cluster_transpose_frombytes.c"}
 for n,p in sources.items():shutil.copy2(p,SYNC/n)
 ssh(f"mkdir -p {REMOTE}");print(command(["rsync","-av","--delete",str(SYNC)+"/",HOST+":"+REMOTE+"/"]),flush=True)
 env=ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
 if "Cortex-A76" not in env or "throttled=0x0" not in env:raise RuntimeError(env)
 (RAW/"environment.txt").write_text(env);build=ssh(f"cd {REMOTE} && make clean && make -B all && make check && size build/*.o build/bench && objdump -dr build/control.o && objdump -dr build/candidate.o")
 if "p3b23_pi_correctness=pass" not in build:raise RuntimeError("correctness")
 (RAW/"build-correctness-object.log").write_text(build)
 body=build.split("<transpose_top>:",1)[1].split("\n\n",1)[0];stack=[x for x in body.splitlines() if "[sp" in x];nonabi=[x for x in stack if not re.search(r"\b(?:stp|ldp)\s+d(?:8|10|12|14), d(?:9|11|13|15)",x)]
 counts={op:sum(re.search(rf"\b{op}\b",x) is not None for x in body.splitlines()) for op in ("trn1","trn2","zip1","zip2","ldr","str","stp","ldp")};rows=[];reps=[]
 for rep in range(3):
  rr=[]
  for order in (0,1):
   out=ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench {order}");(RAW/f"rep{rep}-{order}.log").write_text(out);parsed=[x.split(",") for x in out.splitlines() if x.startswith("sample,")]
   if len(parsed)!=82:raise RuntimeError(f"samples={len(parsed)}")
   rr.extend((p[1],*(float(v) for v in p[2:])) for p in parsed)
  reps.append(summary(rr));rows.extend(rr)
  if "throttled=0x0" not in ssh("vcgencmd get_throttled"):raise RuntimeError("throttled")
 overall=summary(rows);a=overall["from_p3b11"];b=overall["from_cluster_transpose"];delta={k:b[k]-a[k] for k in ("cycles","instructions","branches")};result={"experiment":"D1-P3B23","correctness":"pass","overall":overall,"candidate_minus_p3b11":delta,"object_counts":counts,"stack_references":len(stack),"non_ABI_stack_references":len(nonabi),"no_spill_gate":not nonabi,"cycle_target":-145.0,"cycle_target_pass":delta["cycles"]<=-145.0,"repetitions":reps,"throttled":"0x0","production_linked":False}
 (OUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
