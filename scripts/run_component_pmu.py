#!/usr/bin/env python3
"""Collect baseline-subtracted diagnostic PMU counts from a component ELF."""
from __future__ import annotations
import argparse, json, os, statistics, subprocess
from datetime import datetime, timezone
from pathlib import Path
EVENTS=("cpu_core/cycles/u","cpu_core/instructions/u",
        "cpu_core/mem_inst_retired.all_loads/u",
        "cpu_core/mem_inst_retired.all_stores/u")
def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--binary",type=Path,required=True); ap.add_argument("--cpu",type=int,required=True)
    ap.add_argument("--component",action="append",required=True); ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists(): raise SystemExit(f"refusing to overwrite {a.output}")
    a.output.mkdir(parents=True); raw=a.output/"raw"; raw.mkdir()
    modes=("baseline",*a.component); values={m:{e:[] for e in EVENTS} for m in modes}; unavailable=set()
    for mode in modes:
      for run in range(1,4):
        env=os.environ.copy(); env["NTRUPLUS_COMPONENT_PMU"]=mode
        cmd=["taskset","-c",str(a.cpu),"perf","stat","-x",";","-e",",".join(EVENTS),str(a.binary.resolve())]
        p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
        (raw/f"{mode}-{run}.out").write_text(p.stdout); (raw/f"{mode}-{run}.err").write_text(p.stderr)
        if p.returncode: unavailable.add(f"process:{p.returncode}"); continue
        found={}
        for line in p.stderr.splitlines():
          f=line.split(";")
          if len(f)<3: continue
          event=next((e for e in EVENTS
                      if e.removeprefix("cpu_core/").removesuffix("/u")
                      in f[2]),None)
          count=f[0].strip().replace(",","")
          if event and count.isdigit(): found[event]=found.get(event,0)+int(count)
        for e in EVENTS:
          if e in found: values[mode][e].append(found[e])
          else: unavailable.add(e)
    med={m:{e:statistics.median(v) for e,v in es.items() if v} for m,es in values.items()}
    adjusted={}; validity={}
    for mode in a.component:
      adjusted[mode]={e:(med[mode][e]-med["baseline"][e])/4096 for e in EVENTS
                      if e in med.get(mode,{}) and e in med.get("baseline",{})}
      missing=[e for e in EVENTS if e not in adjusted[mode]]
      invalid=[e for e,value in adjusted[mode].items() if value < 0]
      validity[mode]={"valid":not invalid and not missing,
                      "negative_events":invalid,
                      "missing_events":missing,
                      "note":("invalid or incomplete whole-process subtraction; do not use for attribution"
                              if invalid or missing else
                              "whole-process diagnostic passed arithmetic checks; region PMU remains authoritative")}
      if EVENTS[0] in adjusted[mode] and EVENTS[1] in adjusted[mode] and adjusted[mode][EVENTS[0]]:
        adjusted[mode]["ipc"]=adjusted[mode][EVENTS[1]]/adjusted[mode][EVENTS[0]]
    record={"schema":"ntruplus-component-pmu/v2","created_at":datetime.now(timezone.utc).isoformat(),
      "role":"diagnostic-only-not-promotion-headline","binary":str(a.binary.resolve()),"cpu":a.cpu,
      "fresh_processes":3,"operations_per_process":4096,"events":list(EVENTS),
      "baseline_contract":"whole-process diagnostic only; explicit cpu_core events; region-controlled same-ELF PMU is authoritative",
      "unavailable":sorted(unavailable),"raw_medians":med,
      "baseline_adjusted_per_operation":adjusted,"component_validity":validity}
    (a.output/"summary.json").write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print(f"completed PMU diagnostics: {a.output}"); return 0
if __name__=="__main__": raise SystemExit(main())
