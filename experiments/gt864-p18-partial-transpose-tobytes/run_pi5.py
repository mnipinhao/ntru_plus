#!/usr/bin/env python3
"""Run P18 through the reviewed P15 package/correctness/paired-PMU harness."""

from __future__ import annotations

import hashlib
import importlib.util
import csv
import json
import re
import shutil
import statistics
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
P15=ROOT/"experiments/gt864-p15-p9-scheduling/run_pi5.py"
spec=importlib.util.spec_from_file_location("p15_runner",P15)
assert spec is not None and spec.loader is not None
p15=importlib.util.module_from_spec(spec); spec.loader.exec_module(p15)

p15.HERE=HERE
p15.BUILD=HERE/"build"
p15.SYNC=p15.BUILD/"sync"
p15.RAW=p15.BUILD/"pi5"
p15.REMOTE="/home/pi/supercop-20260831/bench/pinhao/gt864-p18-20260912"
EXPECTED_KAT="0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c"
EXPECTED_MALFORMED="2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67"

def stage():
    if p15.SYNC.exists(): shutil.rmtree(p15.SYNC)
    for name in ("baseline","candidate"):
        p15.extract(p15.SYNC/"packages"/name)
    candidate=p15.SYNC/"packages"/"candidate"
    for mode in ("full","small"):
        text=(p15.BUILD/f"p18_tobytes_{mode}.opt.S").read_text()
        text=text.replace(f"gt864_p18_tobytes_{mode}_asm",
                          f"gt864_p9_tobytes_{mode}_asm")
        (candidate/f"p18-{mode}.S").write_text(text)
    makefile=candidate/"Makefile"; text=makefile.read_text()
    old_full="""gt864_p9_tobytes_full.o: gt864_p16_tobytes_full.S p9_tobytes.h
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@"""
    old_small="""gt864_p9_tobytes_small.o: gt864_p9_tobytes_small.c p9_tobytes.h
	$(CC) $(CFLAGS) -I. -c $< -o $@"""
    new_full="""gt864_p9_tobytes_full.o: p18-full.S p9_tobytes.h
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@"""
    new_small="""gt864_p9_tobytes_small.o: p18-small.S p9_tobytes.h
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@"""
    if text.count(old_full)!=1 or text.count(old_small)!=1:
        raise RuntimeError("production ToBytes Makefile binding drift")
    text=text.replace(old_full,new_full).replace(old_small,new_small)
    # The generated P18 objects are complete public functions: they save the
    # ABI-preserved registers, invoke both top halves, erase SIMD state, and
    # restore the frame.  Do not also link the legacy P9 public wrappers,
    # which define the same public symbols around separate inner functions.
    old_objects=("gt864_p9_tobytes_full.o p9_tobytes_public_full.o "
                 "gt864_p9_tobytes_small.o p9_tobytes_public_small.o")
    new_objects=("gt864_p9_tobytes_full.o "
                 "gt864_p9_tobytes_small.o")
    if text.count(old_objects)!=1:
        raise RuntimeError("production ToBytes object list drift")
    makefile.write_text(text.replace(old_objects,new_objects))
    component=(ROOT/("experiments/gt864-native-asm/p6-zero-scratch-tobytes/"
                     "p6e-pi-timing/bench.c")).read_text().replace(
        'must_symbol(hc, small ? "gt864_p6d3_small_asm" : "gt864_p6d3_full_asm")',
        'must_symbol(hc, small ? "gt864_fr0_tobytes_small" : "gt864_fr0_tobytes_full")')
    (p15.SYNC/"component.c").write_text(component)
    harness=(ROOT/"experiments/gt864-official-profile-p8/full_harness.c").read_text()
    harness=harness.replace('v?"gt":"official"','v?"candidate":"baseline"')
    (p15.SYNC/"kem.c").write_text(harness)
    shutil.copy2(ROOT/"experiments/gt864-native-asm/kem-malformed-transcript.c",
                 p15.SYNC/"malformed.c")
    manifest={str(path.relative_to(p15.SYNC)):hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(p15.SYNC.rglob("*")) if path.is_file()}
    (p15.BUILD/"source-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")

def target_audit():
    result={}
    for mode in ("full","small"):
        result[mode]={}
        for variant in ("baseline","candidate"):
            dis=p15.ssh(f"cd {p15.REMOTE}/packages/{variant} && objdump -d gt864_p9_tobytes_{mode}.o")
            (p15.RAW/f"object-{variant}-{mode}.log").write_text(dis)
            instructions=len(re.findall(r"(?m)^\s*[0-9a-f]+:\s+[0-9a-f]+\s+\S+",dis))
            q_stack=len(re.findall(r"(?mi)^.*\b(?:ldr|str|ldp|stp)\s+q[^\n]*\[sp[^\n]*$",dis))
            if q_stack: raise RuntimeError(f"{variant} {mode} vector spill")
            result[mode][variant]={"object_instructions":instructions,
                                   "q_stack_accesses":q_stack}
    return result

def parse_kem(paths):
    values={}; deltas={}
    for path in paths:
        rows=[row for row in csv.reader(path.read_text().splitlines())
              if row and row[0]=="clean"]
        by_operation={}
        for row in rows:
            by_operation.setdefault(row[1],[]).append(row)
            values.setdefault((row[1],row[2]),[]).append([float(x) for x in row[3:6]])
        for operation,operation_rows in by_operation.items():
            if len(operation_rows)%2:
                raise RuntimeError(f"unpaired samples in {path}: {operation}")
            for index in range(0,len(operation_rows),2):
                pair={row[2]:[float(x) for x in row[3:6]]
                      for row in operation_rows[index:index+2]}
                if set(pair)!={"baseline","candidate"}:
                    raise RuntimeError(f"bad pair in {path}: {pair}")
                deltas.setdefault(operation,[]).append(
                    [pair["candidate"][i]-pair["baseline"][i] for i in range(3)])
    metrics=("cycles","instructions","branches")
    result={}
    for operation in ("keygen","encaps","decaps"):
        result[operation]={
            variant:{metric:statistics.median(sample[i]
                                               for sample in values[(operation,variant)])
                     for i,metric in enumerate(metrics)}
            for variant in ("baseline","candidate")}
        result[operation]["paired_delta"]={
            metric:statistics.median(sample[i] for sample in deltas[operation])
            for i,metric in enumerate(metrics)}
        result[operation]["observations"]=len(deltas[operation])
    return result

def full_kem_gate():
    remote=p15.REMOTE
    p15.ssh(f"cd {remote} && gcc -O3 -std=c11 -march=armv8-a+simd "
            "-D_DEFAULT_SOURCE -rdynamic kem.c -ldl -o kem")
    malformed=[]
    for variant in ("baseline","candidate"):
        command=(
            f"cd {remote} && gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE "
            f"-Ipackages/{variant} malformed.c -Lpackages/{variant} -lgt864 "
            f"-Wl,-rpath,{remote}/packages/{variant} -o malformed-{variant} && "
            f"./malformed-{variant} | sha256sum")
        malformed.append(p15.ssh(command).split()[0])
    if malformed!=[EXPECTED_MALFORMED,EXPECTED_MALFORMED]:
        raise RuntimeError(f"malformed transcript mismatch: {malformed}")
    paths=[]
    for process in range(6):
        path=p15.RAW/f"kem-{process}.csv"
        measured=p15.ssh(
            f"cd {remote} && taskset -c 3 ./kem packages/baseline/libgt864.so "
            f"packages/candidate/libgt864.so {process%2}")
        path.write_text(measured)
        if "correctness=pass exact=100 tampered=100" not in measured:
            raise RuntimeError(f"full KEM compatibility failed in process {process}")
        paths.append(path)
    kem=parse_kem(paths)
    environment_after=p15.ssh("vcgencmd measure_temp; vcgencmd get_throttled").strip().splitlines()
    if "throttled=0x0" not in environment_after:
        raise RuntimeError(f"Pi 5 throttled during full-KEM gate: {environment_after}")
    return {"malformed_transcript_sha256":malformed[0],"kem":kem,
            "wins_all_kem_cycles":all(kem[op]["paired_delta"]["cycles"]<0
                                      for op in ("keygen","encaps","decaps")),
            "environment_after":environment_after}

def main():
    p15.stage=stage; p15.target_audit=target_audit
    p15.main()
    path=HERE/"pi-results.json"; result=json.loads(path.read_text())
    result["experiment"]="GT864-P18-PARTIAL-TRANSPOSE-TOBYTES-20260912"
    result["slothy_results"]="slothy-results.json"
    if result["kat_sha256"]!=EXPECTED_KAT:
        raise RuntimeError(f"unexpected KAT hash: {result['kat_sha256']}")
    result["full_kem_gate"]=full_kem_gate()
    result["promotion_gate_passed"]=(
        result["promotion_gate_passed"] and
        result["full_kem_gate"]["wins_all_kem_cycles"])
    path.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result["full_kem_gate"],indent=2),flush=True)

if __name__=="__main__": main()
