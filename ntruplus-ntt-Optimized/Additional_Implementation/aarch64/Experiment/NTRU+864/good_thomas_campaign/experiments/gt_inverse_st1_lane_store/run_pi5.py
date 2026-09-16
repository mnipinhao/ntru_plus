#!/usr/bin/env python3
"""Run the A2 inverse-store shootout on the pinned Cortex-A76 core."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
A1 = HERE.parent / "gt_tail_architecture_shootout" / "run_pi5.py"
SPEC = importlib.util.spec_from_file_location("a1_runner", A1)
assert SPEC and SPEC.loader
BASE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(BASE)
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-a2-st1-lane"
OUTPUT = HERE / "build" / "pi5"
M5E = HERE.parent / "gt_fr0_inverse_asm_realization"
VARIANTS = ("i16_baseline", "i16_st1", "full_baseline", "full_st1", "noop")


def parse(raw: str) -> list[dict[str, object]]:
    assert "correctness,status=pass,i16=64,full_inverse=64" in raw
    pattern = re.compile(
        r"^sample,index=\d+,position=\d+,variant=(\w+),cycles=([0-9.]+),"
        r"instructions=([0-9.]+),branches=([0-9.]+)$")
    rows = []
    for line in raw.splitlines():
        if match := pattern.match(line):
            rows.append({"variant": match.group(1), "cycles": float(match.group(2)),
                         "instructions": float(match.group(3)), "branches": float(match.group(4))})
    assert len(rows) == 305
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
        for variant in VARIANTS[:-1]}
    return result


def main() -> None:
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise SystemExit(f"refusing to overwrite {OUTPUT}")
    sync, raw = OUTPUT / "sync", OUTPUT / "raw"
    (sync / "build").mkdir(parents=True); (sync / "deps").mkdir(); raw.mkdir(parents=True)
    BASE.command(["python3", str(HERE / "prepare.py")])
    files = {
        sync / "Makefile": HERE / "pi5-Makefile",
        sync / "bench_pmu.c": HERE / "bench_pmu.c",
        sync / "gt864_inverse_st1_wrapper.c": HERE / "gt864_inverse_st1_wrapper.c",
        sync / "build/gt864_inverse16_blocks_st1.s": HERE / "build/gt864_inverse16_blocks_st1.s",
        sync / "build/gt864_fr0_inverse_barrett_tables.h": HERE / "build/gt864_fr0_inverse_barrett_tables.h",
        sync / "build/gt864_fr0_inverse_tables.h": HERE / "build/gt864_fr0_inverse_tables.h",
        sync / "deps/gt864_fr0_inverse_asm.h": M5E / "gt864_fr0_inverse_asm.h",
        sync / "deps/gt864_fr0_inverse_asm_wrapper.c": M5E / "gt864_fr0_inverse_asm_wrapper.c",
        sync / "deps/gt864_fr0_inverse9_block.s": M5E / "gt864_fr0_inverse9_block.s",
        sync / "deps/gt864_inverse16_blocks.s": M5E / "gt864_inverse16_blocks.s",
    }
    for destination, source in files.items():
        if source.name == "gt864_fr0_inverse9_block.s":
            assembly = source.read_text(encoding="utf-8")
            assembly = assembly.replace(", \\\n           ", ", ")
            destination.write_text(assembly, encoding="utf-8")
        else:
            shutil.copy2(source, destination)
    BASE.ssh(f"mkdir -p {REMOTE}")
    BASE.command(["rsync", "-av", f"{sync}/", f"{HOST}:{REMOTE}/"])
    env = BASE.ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in env and "throttled=0x0" in env
    (raw / "environment-before.txt").write_text(env, encoding="utf-8")
    build = BASE.ssh(f"cd {REMOTE} && make clean && make all && size build/bench-pmu")
    (raw / "build.log").write_text(build, encoding="utf-8")
    all_rows, repetitions = [], []
    for rep in range(3):
        rows = []
        for order in ("abcdN", "Ndcba"):
            output = BASE.ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench-pmu {order}")
            (raw / f"rep{rep}-{order}.log").write_text(output, encoding="utf-8")
            parsed = parse(output); rows += parsed; all_rows += parsed
        repetitions.append(summarize(rows))
        thermal = BASE.ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{rep}.txt").write_text(thermal, encoding="utf-8")
    result = {"experiment": "gt864-a2-st1-lane", "host": HOST, "core": 3,
              "repetitions": repetitions, "overall": summarize(all_rows),
              "source_sha256": {str(path.relative_to(sync)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in files}, "slothy": "not_run"}
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__": main()
