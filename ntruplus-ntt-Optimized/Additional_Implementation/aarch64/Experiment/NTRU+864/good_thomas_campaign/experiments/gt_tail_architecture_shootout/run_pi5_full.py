#!/usr/bin/env python3
"""A1 one-bank, six-bank and complete-Forward paired Pi 5 PMU run."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("a1_tail_runner", HERE / "run_pi5.py")
assert SPEC and SPEC.loader
BASE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(BASE)
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-a1-tail-full-boundaries"
OUTPUT = HERE / "build/pi5-full"
M5RD = HERE.parent / "gt_forward_level2_one_mul_b3"
TOP = HERE.parent / "gt_2x9x16_ld3_top_split/gt864_top_split.s"
VARIANTS = ("one_T0", "one_T1", "one_T2", "six_T0", "six_T1", "six_T2",
            "full_T0", "full_T1", "full_T2", "noop")


def parse(text: str) -> list[dict[str, object]]:
    assert "correctness,status=pass,one_bank=64,six_bank=64,full=64" in text
    pattern = re.compile(
        r"^sample,index=\d+,position=\d+,variant=(\w+),cycles=([0-9.]+),"
        r"instructions=([0-9.]+),branches=([0-9.]+)$")
    rows = []
    for line in text.splitlines():
        if match := pattern.match(line):
            rows.append({"variant": match.group(1), "cycles": float(match.group(2)),
                         "instructions": float(match.group(3)), "branches": float(match.group(4))})
    assert len(rows) == 610
    return rows


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    result = {}
    for variant in VARIANTS:
        chosen = [row for row in rows if row["variant"] == variant]
        result[variant] = {metric: BASE.stats([float(row[metric]) for row in chosen])
                           for metric in ("cycles", "instructions", "branches")}
        result[variant]["ipc"] = (result[variant]["instructions"]["p50"] /
                                   result[variant]["cycles"]["p50"])
    overhead = result["noop"]["instructions"]["p50"]
    result["kernel_instructions_minus_noop"] = {
        variant: result[variant]["instructions"]["p50"] - overhead
        for variant in VARIANTS[:-1]
    }
    return result


def main() -> None:
    if OUTPUT.exists() and any(OUTPUT.iterdir()): raise SystemExit(f"refusing to overwrite {OUTPUT}")
    sync, raw = OUTPUT / "sync", OUTPUT / "raw"
    (sync / "build").mkdir(parents=True); (sync / "deps").mkdir(); raw.mkdir(parents=True)
    BASE.command(["python3", str(HERE / "prepare.py")])
    files = {
        sync / "Makefile": HERE / "pi5-full-Makefile",
        sync / "bench_full_pmu.c": HERE / "bench_full_pmu.c",
        sync / "build/tail_variants.S": HERE / "build/tail_variants.S",
        sync / "build/pass2_t0.S": HERE / "build/pass2_t0.S",
        sync / "build/pass2_t1.S": HERE / "build/pass2_t1.S",
        sync / "build/pass2_t2.S": HERE / "build/pass2_t2.S",
        sync / "build/full_t0_wrapper.S": HERE / "build/full_t0_wrapper.S",
        sync / "build/full_t1_wrapper.S": HERE / "build/full_t1_wrapper.S",
        sync / "build/full_t2_wrapper.S": HERE / "build/full_t2_wrapper.S",
        sync / "deps/top_split.s": TOP,
    }
    for destination, source in files.items(): shutil.copy2(source, destination)
    BASE.ssh(f"mkdir -p {REMOTE}")
    BASE.command(["rsync", "-av", f"{sync}/", f"{HOST}:{REMOTE}/"])
    env = BASE.ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in env and "throttled=0x0" in env
    (raw / "environment-before.txt").write_text(env, encoding="utf-8")
    build = BASE.ssh(f"cd {REMOTE} && make clean && make all && size build/bench-full")
    (raw / "build.log").write_text(build, encoding="utf-8")
    all_rows, repetitions = [], []
    for rep in range(3):
        rows = []
        for order in ("abcdefghiN", "Nihgfedcba"):
            output = BASE.ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench-full {order}")
            (raw / f"rep{rep}-{order}.log").write_text(output, encoding="utf-8")
            parsed = parse(output); rows += parsed; all_rows += parsed
        repetitions.append(summarize(rows))
        thermal = BASE.ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{rep}.txt").write_text(thermal, encoding="utf-8")
    result = {
        "experiment": "gt864-a1-tail-full-boundaries", "host": HOST, "core": 3,
        "repetitions": repetitions, "overall": summarize(all_rows),
        "source_sha256": {str(path.relative_to(sync)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in files},
        "slothy": "not_run",
    }
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__": main()
