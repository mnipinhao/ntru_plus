#!/usr/bin/env python3
"""Paired Pi5 PMU: Official versus M5R-C versus all-one-mul B3 M5R-D."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
M5RC_PATH = HERE.parent / "gt_forward_one_mul_b3/run_pi5.py"
SPEC = importlib.util.spec_from_file_location("m5rc_pi5", M5RC_PATH)
assert SPEC and SPEC.loader
M5RC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M5RC)
BASE = M5RC.BASE
BASE.HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-forward-level2-one-mul-b3"
OUTPUT = HERE / "build/pi5-formal"
M5R = HERE.parent / "gt_forward_full_register_pass2_dag"
M5RC_DIR = HERE.parent / "gt_forward_one_mul_b3"
M5O = HERE.parent / "gt_forward_full_poly_ntt_asm"
TOP = HERE.parent / "gt_2x9x16_ld3_top_split"
M5Q = HERE.parent / "gt_forward_dynamic_cost_decomposition"


def main() -> None:
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise SystemExit(f"refusing to overwrite {OUTPUT}")
    sync, raw, deps = OUTPUT / "sync", OUTPUT / "raw", OUTPUT / "sync/deps"
    deps.mkdir(parents=True)
    raw.mkdir(parents=True)
    BASE.command(["python3", str(M5O / "generate_official_map.py"),
                  str(deps / "gt864_fr0_to_official_map.h"),
                  str(OUTPUT / "abi-map-proof.json")])
    bench = (M5R / "bench_pmu.c").read_text(encoding="utf-8")
    bench = bench.replace("gt864_forward_poly_ntt_full_register",
                          "gt864_forward_poly_ntt_all_one_mul_b3")
    bench = bench.replace("gt864_forward_poly_ntt_experiment",
                          "gt864_forward_poly_ntt_one_mul_b3")
    (sync / "bench_pmu.c").write_text(bench, encoding="utf-8")
    shutil.copy2(M5R / "pi5-Makefile", sync / "Makefile")
    sources = {
        deps / "official_ntt.s": REPO / "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+864/asm/ntt.s",
        deps / "top_split.s": TOP / "gt864_top_split.s",
        deps / "baseline_pass2.S": M5RC_DIR / "gt864_forward_six_bank_one_mul_b3.S",
        deps / "baseline_wrapper.S": M5RC_DIR / "gt864_forward_poly_ntt_one_mul_b3.S",
        deps / "candidate_pass2.S": HERE / "gt864_forward_six_bank_all_one_mul_b3.S",
        deps / "candidate_wrapper.S": HERE / "gt864_forward_poly_ntt_all_one_mul_b3.S",
        deps / "noop.S": M5Q / "gt864_forward_noop.S",
    }
    for destination, source in sources.items():
        shutil.copy2(source, destination)
    BASE.ssh(f"mkdir -p {REMOTE}")
    BASE.command(["rsync", "-av", f"{sync}/", f"{BASE.HOST}:{REMOTE}/"])
    environment = BASE.ssh(
        "uname -a; lscpu | head -24; gcc --version | head -1; "
        "vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in environment and "throttled=0x0" in environment
    (raw / "environment-before.txt").write_text(environment, encoding="utf-8")
    build = BASE.ssh(f"cd {REMOTE} && make clean && make all && size build/*.o")
    (raw / "build.log").write_text(build, encoding="utf-8")
    repetitions, all_rows = [], []
    for repetition in range(3):
        rows = []
        for order in ("OBCN", "NCBO"):
            output = BASE.ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench_pmu {order}")
            (raw / f"rep{repetition}-{order}.log").write_text(output, encoding="utf-8")
            parsed = BASE.parse(output)
            rows += parsed
            all_rows += parsed
        repetitions.append(BASE.summarize(rows))
        thermal = BASE.ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{repetition}.txt").write_text(thermal, encoding="utf-8")
    result = {
        "experiment": "gt864-forward-level2-one-mul-b3",
        "host": BASE.HOST,
        "core": 3,
        "repetitions": repetitions,
        "overall": BASE.summarize(all_rows),
        "throttled": "0x0",
        "source_sha256": {
            str(destination.relative_to(sync)): hashlib.sha256(destination.read_bytes()).hexdigest()
            for destination in sources
        },
    }
    derived = result["overall"]["derived"]
    assert abs(derived["official_kernel_instructions"] - 4028) < 0.01
    assert abs(derived["baseline_gt_kernel_instructions"] - 4590) < 0.01
    assert abs(derived["candidate_gt_kernel_instructions"] - 4446) < 0.01
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
