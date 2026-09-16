#!/usr/bin/env python3
"""Run the D1-P3B10 complete ToBytes integration gate on Pi 5."""
from __future__ import annotations
import json,shutil,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
P3B6=HERE.parent/"gt_fr0_d1_input_once_tobytes"
HOST="pi@100.99.191.9"; REMOTE="/home/pi/ntruplus-experiments/gt864-p3b10-paired-integration"
OUT=HERE/"build"; SYNC=OUT/"sync"; RAW=OUT/"raw"
def command(a:list[str])->str:return subprocess.check_output(a,text=True,stderr=subprocess.STDOUT)
def ssh(s:str)->str:return command(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10",HOST,s])
def summarize(rows):
    return {name:{metric:statistics.median(r[i] for r in rows if r[0]==name)
                  for i,metric in enumerate(("cycles","instructions","branches"),1)}
            for name in sorted({r[0] for r in rows})}
def main()->None:
    command(["python3",str(HERE/"prepare.py")]);SYNC.mkdir(parents=True,exist_ok=True);RAW.mkdir(parents=True,exist_ok=True)
    sources={"Makefile":HERE/"pi5-Makefile","bench_pi5.c":HERE/"bench_pi5.c",
             "paired_tobytes.h":HERE/"paired_tobytes.h",
             "control.c":P3B6/"build/input_once_tobytes.c",
             "input_once_tobytes.h":P3B6/"input_once_tobytes.h",
             "candidate.c":OUT/"paired_tobytes.c"}
    for name,source in sources.items():shutil.copy2(source,SYNC/name)
    ssh(f"mkdir -p {REMOTE}");print(command(["rsync","-av","--delete","--exclude=build",str(SYNC)+"/",HOST+":"+REMOTE+"/"]),flush=True)
    env=ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
    if "Cortex-A76" not in env or "throttled=0x0" not in env:raise RuntimeError(env)
    (RAW/"environment.txt").write_text(env)
    build=ssh(f"cd {REMOTE} && make clean && make -B all && make check && size build/*.o build/bench && objdump -dr build/control.o && objdump -dr build/candidate.o")
    if "p3b10_pi_correctness=pass" not in build:raise RuntimeError("correctness")
    (RAW/"build-correctness-object.log").write_text(build)
    repetitions=[];all_rows=[]
    for repetition in range(3):
        rows=[]
        for order in (0,1):
            output=ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench {order}")
            (RAW/f"rep{repetition}-{order}.log").write_text(output)
            parsed=[line.split(",") for line in output.splitlines() if line.startswith("sample,")]
            if len(parsed)!=82:raise RuntimeError(f"samples={len(parsed)}")
            rows.extend((p[1],*(float(v) for v in p[2:])) for p in parsed)
        repetitions.append(summarize(rows));all_rows.extend(rows)
        thermal=ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        if "throttled=0x0" not in thermal:raise RuntimeError(thermal)
    overall=summarize(all_rows);control=overall["to_p3b6"];candidate=overall["to_paired"]
    result={"experiment":"D1-P3B10","correctness":"pass","overall":overall,
            "paired_minus_p3b6":{k:candidate[k]-control[k] for k in ("cycles","instructions","branches")},
            "promotion_threshold_cycles":1250,"promotion_pass":candidate["cycles"]<1250,
            "scratch_bytes":432,"repetitions":repetitions,"throttled":"0x0","production_linked":False}
    (OUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
