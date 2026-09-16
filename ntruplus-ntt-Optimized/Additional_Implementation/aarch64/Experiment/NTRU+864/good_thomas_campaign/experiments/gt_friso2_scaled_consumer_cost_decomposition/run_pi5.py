#!/usr/bin/env python3
"""Run four isolated M5R-D versus CF5-B scaled-bank paired PMU campaigns."""
from __future__ import annotations
import hashlib,json,math,re,shutil,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent; BUILD=HERE/"build"; OUT=BUILD/"pi5-formal-r1"; SYNC=OUT/"sync"; RAW=OUT/"raw"
HOST="pi@100.99.191.9"; REMOTE="/home/pi/ntruplus-experiments/gt864-cf5c-consumer-cost"
EXPS=HERE.parent; CASES=("t0c1","t0c2","t1c1","t1c2")
def cmd(a,capture=False):
 r=subprocess.run(a,check=True,text=True,capture_output=capture);return r.stdout if capture else ""
def ssh(s):return cmd(["ssh","-o","BatchMode=yes",HOST,s],True)
def pct(v,p):
 v=sorted(v);x=(len(v)-1)*p/100;lo,hi=math.floor(x),math.ceil(x);return v[lo] if lo==hi else v[lo]*(hi-x)+v[hi]*(x-lo)
def stats(v):return {n:pct(v,p) for n,p in (("p10",10),("p25",25),("p50",50),("p75",75),("p90",90))}
def parse(text,case):
 assert f"correctness,status=pass,case={case}" in text
 pat=re.compile(r"^sample,case=(\d+),order=(\w+),index=(\d+),variant=(\w+),cycles=([0-9.]+),instructions=([0-9.]+)$")
 rows=[{"case":int(m.group(1)),"order":m.group(2),"index":int(m.group(3)),"variant":m.group(4),"cycles":float(m.group(5)),"instructions":float(m.group(6))} for line in text.splitlines() if(m:=pat.match(line))]
 assert len(rows)==183;return rows
def summarize(rows):
 out={}
 for v in ("baseline","candidate","noop"):
  s=[r for r in rows if r["variant"]==v];out[v]={"cycles":stats([r["cycles"] for r in s]),"instructions":stats([r["instructions"] for r in s])}
 ds=[]
 for order in ("BCN","NCB"):
  for i in range(61):
   p={r["variant"]:r["cycles"] for r in rows if r["order"]==order and r["index"]==i};ds.append(p["candidate"]-p["baseline"])
 out["paired_candidate_minus_baseline_cycles"]=stats(ds)
 out["instruction_delta"]=out["candidate"]["instructions"]["p50"]-out["baseline"]["instructions"]["p50"]
 return out
def main():
 if OUT.exists() and any(OUT.iterdir()):raise SystemExit(f"refusing to overwrite {OUT}")
 OUT.mkdir(parents=True);SYNC.mkdir();RAW.mkdir();cmd(["python3",str(HERE/"generate_isolated.py")])
 sources={SYNC/"deps/isolated-banks.S":BUILD/"isolated-banks.S",SYNC/"bank_offsets.h":BUILD/"bank_offsets.h",SYNC/"bench_bank.c":HERE/"bench_bank.c",SYNC/"Makefile":HERE/"pi5-Makefile",SYNC/"deps/m5rd-pass2.S":EXPS/"gt_forward_level2_one_mul_b3/gt864_forward_six_bank_all_one_mul_b3.S",SYNC/"deps/cf5b-pass2.S":EXPS/"gt_friso2_code_size_faithful_forward/gt864_forward_six_bank_cf5b.S",SYNC/"deps/top-split.s":EXPS/"gt_2x9x16_ld3_top_split/gt864_top_split.s",SYNC/"deps/noop.S":EXPS/"gt_forward_dynamic_cost_decomposition/gt864_forward_noop.S"}
 for d,s in sources.items():d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,d)
 ssh(f"mkdir -p {REMOTE}");cmd(["rsync","-av",f"{SYNC}/",f"{HOST}:{REMOTE}/"])
 env=ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled");assert "Cortex-A76" in env and "throttled=0x0" in env;(RAW/"environment-before.txt").write_text(env)
 build=ssh(f"cd {REMOTE} && make clean && make all && size build/*.o");(RAW/"build.log").write_text(build)
 reports=[]
 for case,name in enumerate(CASES):
  allrows=[]
  for rep in range(3):
   rows=[]
   for order in ("BCN","NCB"):
    text=ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench_bank {case} {order}");(RAW/f"{name}-rep{rep}-{order}.log").write_text(text);rows+=parse(text,case)
   allrows+=rows
  report=summarize(allrows);report["case"]=name;reports.append(report)
  thermal=ssh("vcgencmd measure_temp; vcgencmd get_throttled");assert "throttled=0x0" in thermal;(RAW/f"environment-{name}.txt").write_text(thermal)
 expected=(85,85,55,55)
 for i,r in enumerate(reports):assert abs(r["instruction_delta"]-expected[i])<0.01
 isolated_sum=sum(r["paired_candidate_minus_baseline_cycles"]["p50"] for r in reports)
 full=351.93645
 result={"experiment":"M5U-CF5-C","host":HOST,"core":3,"cases":reports,"isolated_delta_sum_p50":isolated_sum,"CF5B_full_forward_delta_p50":full,"reconciliation_residual":full-isolated_sum,"required_cycle_saving":184.83945,"source_sha256":{str(d.relative_to(SYNC)):hashlib.sha256(d.read_bytes()).hexdigest() for d in sources},"throttled":"0x0"}
 (OUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
