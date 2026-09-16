#!/usr/bin/env python3
"""Five-way paired Pi 5 PMU: Official, M5R-D, CF0, CF5-B, and noop."""

from __future__ import annotations

import hashlib, json, math, re, shutil, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-cf5b-forward"
OUTPUT = HERE / "build/pi5-formal"
M5RD = HERE.parent / "gt_forward_level2_one_mul_b3"
CF0 = HERE.parent / "gt_friso2_forward_absorption"
M5O = HERE.parent / "gt_forward_full_poly_ntt_asm"
TOP = HERE.parent / "gt_2x9x16_ld3_top_split"
NOOP = HERE.parent / "gt_forward_dynamic_cost_decomposition/gt864_forward_noop.S"
VARIANTS = ("official", "m5rd", "cf0", "cf5b", "noop")

def command(args, capture=False):
    result = subprocess.run(args, check=True, text=True, capture_output=capture)
    return result.stdout if capture else ""
def ssh(cmd): return command(["ssh", "-o", "BatchMode=yes", HOST, cmd], True)
def percentile(values, p):
    values = sorted(values); at = (len(values) - 1) * p / 100
    lo, hi = math.floor(at), math.ceil(at)
    return values[lo] if lo == hi else values[lo] * (hi-at) + values[hi] * (at-lo)
def stats(values): return {name: percentile(values, p) for name, p in (("p10",10),("p25",25),("p50",50),("p75",75),("p90",90))}
def parse(text):
    assert "correctness,status=pass" in text
    pat = re.compile(r"^sample,order=(\w+),index=(\d+),position=(\d+),variant=(\w+),cycles=([0-9.]+),instructions=([0-9.]+)$")
    rows = [{"order":m.group(1), "index":int(m.group(2)), "variant":m.group(4), "cycles":float(m.group(5)), "instructions":float(m.group(6))}
            for line in text.splitlines() if (m := pat.match(line))]
    assert len(rows) == 305
    return rows
def summarize(rows):
    result = {}
    for variant in VARIANTS:
        selected = [r for r in rows if r["variant"] == variant]
        result[variant] = {"count":len(selected), "cycles":stats([r["cycles"] for r in selected]), "instructions":stats([r["instructions"] for r in selected])}
    for lhs, rhs in (("cf5b","m5rd"),("cf5b","cf0"),("cf5b","official")):
        values=[]
        for order in ("ODFCN","NCFDO"):
            ordered=[r for r in rows if r["order"] == order]
            for index in sorted({r["index"] for r in ordered}):
                pair={r["variant"]:r["cycles"] for r in ordered if r["index"] == index}
                values.append(pair[lhs]-pair[rhs])
        result[f"paired_{lhs}_minus_{rhs}_cycles"] = stats(values)
    overhead = result["noop"]["instructions"]["p50"] - 1.0
    result["derived"] = {"common_harness_instructions":overhead}
    for variant in VARIANTS[:-1]: result["derived"][variant+"_kernel_instructions"] = result[variant]["instructions"]["p50"] - overhead
    return result
def main():
    if OUTPUT.exists() and any(OUTPUT.iterdir()): raise SystemExit(f"refusing to overwrite {OUTPUT}")
    sync, deps, raw = OUTPUT/"sync", OUTPUT/"sync/deps", OUTPUT/"raw"
    deps.mkdir(parents=True); raw.mkdir(parents=True)
    command(["python3", str(HERE/"generate_cf5b.py")])
    command(["python3", str(M5O/"generate_official_map.py"), str(deps/"gt864_fr0_to_official_map.h"), str(OUTPUT/"abi-map-proof.json")])
    sources = {
        deps/"official_ntt.s": REPO/"ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+864/asm/ntt.s",
        deps/"top_split.s": TOP/"gt864_top_split.s",
        deps/"m5rd_pass2.S": M5RD/"gt864_forward_six_bank_all_one_mul_b3.S",
        deps/"m5rd_wrapper.S": M5RD/"gt864_forward_poly_ntt_all_one_mul_b3.S",
        deps/"cf0_pass2.S": CF0/"gt864_forward_six_bank_friso2.S",
        deps/"cf0_wrapper.S": CF0/"gt864_forward_poly_ntt_friso2.S",
        deps/"cf5b_pass2.S": HERE/"gt864_forward_six_bank_cf5b.S",
        deps/"cf5b_wrapper.S": HERE/"gt864_forward_poly_ntt_cf5b.S",
        deps/"noop.S": NOOP,
        sync/"Makefile": HERE/"pi5-Makefile", sync/"bench_pmu.c": HERE/"bench_pmu.c"}
    for dst, src in sources.items(): shutil.copy2(src, dst)
    ssh(f"mkdir -p {REMOTE}"); command(["rsync","-av",f"{sync}/",f"{HOST}:{REMOTE}/"])
    env = ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in env and "throttled=0x0" in env
    (raw/"environment-before.txt").write_text(env)
    build = ssh(f"cd {REMOTE} && make clean && make all && size build/*.o")
    (raw/"build.log").write_text(build)
    repetitions=[]; all_rows=[]
    for rep in range(3):
        rows=[]
        for order in ("ODFCN","NCFDO"):
            out=ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench_pmu {order}")
            (raw/f"rep{rep}-{order}.log").write_text(out); rows += parse(out); all_rows += parse(out)
        repetitions.append(summarize(rows))
        thermal=ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal; (raw/f"environment-rep{rep}.txt").write_text(thermal)
    overall=summarize(all_rows); derived=overall["derived"]
    expected={"official":4028,"m5rd":4446,"cf0":4738,"cf5b":4726}
    for name, count in expected.items(): assert abs(derived[name+"_kernel_instructions"]-count)<0.01
    result={"experiment":"M5U-CF5-B","host":HOST,"core":3,"repetitions":repetitions,"overall":overall,"throttled":"0x0","source_sha256":{str(dst.relative_to(sync)):hashlib.sha256(dst.read_bytes()).hexdigest() for dst in sources}}
    (OUTPUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__ == "__main__": main()
