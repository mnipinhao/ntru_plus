#!/usr/bin/env python3
"""Freeze the exact GCC FR0 BaseMul object and paired Pi 5 PMU baseline."""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "gt_fr0_basemul_arithmetic"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-fr0-basemul-b1-0"
OUTPUT = HERE / "build/pi5-b1-0"
VARIANTS = ("basemul", "basemuladd", "noop")


def command(args: list[str], capture: bool = False) -> str:
    result = subprocess.run(args, check=True, text=True, capture_output=capture)
    return result.stdout if capture else ""


def ssh(command_text: str) -> str:
    return command(["ssh", "-o", "BatchMode=yes", HOST, command_text], True)


def percentile(values: list[float], p: int) -> float:
    values = sorted(values)
    at = (len(values) - 1) * p / 100
    low, high = math.floor(at), math.ceil(at)
    return values[low] if low == high else values[low] * (high - at) + values[high] * (at - low)


def stats(values: list[float]) -> dict[str, float]:
    return {name: percentile(values, p) for name, p in
            (("p10", 10), ("p25", 25), ("p50", 50), ("p75", 75), ("p90", 90))}


def parse(text: str) -> list[dict[str, object]]:
    assert "correctness,status=pass,basemul_alias_a_b=64,basemuladd_alias_c=64" in text
    pattern = re.compile(r"^sample,index=\d+,position=\d+,variant=(\w+),"
                         r"cycles=([0-9.]+),instructions=([0-9.]+),branches=([0-9.]+)$")
    rows = [{"variant": match.group(1), "cycles": float(match.group(2)),
             "instructions": float(match.group(3)), "branches": float(match.group(4))}
            for line in text.splitlines() if (match := pattern.match(line))]
    assert len(rows) == 61 * len(VARIANTS)
    return rows


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    result = {}
    for variant in VARIANTS:
        selected = [row for row in rows if row["variant"] == variant]
        result[variant] = {metric: stats([float(row[metric]) for row in selected])
                           for metric in ("cycles", "instructions", "branches")}
        result[variant]["ipc"] = (result[variant]["instructions"]["p50"] /
                                  result[variant]["cycles"]["p50"])
    overhead = result["noop"]["instructions"]["p50"]
    result["kernel_instructions_minus_noop"] = {
        variant: result[variant]["instructions"]["p50"] - overhead
        for variant in VARIANTS[:-1]}
    return result


def main() -> None:
    if (OUTPUT / "summary.json").exists():
        raise SystemExit(f"refusing to overwrite {OUTPUT}")
    sync, raw = OUTPUT / "sync", OUTPUT / "raw"
    sync.mkdir(parents=True, exist_ok=True); raw.mkdir(parents=True, exist_ok=True)
    sources = {
        sync / "Makefile": HERE / "pi5-Makefile",
        sync / "bench_pmu.c": HERE / "bench_pmu.c",
        sync / "gt864_fr0_basemul.c": SOURCE / "gt864_fr0_basemul.c",
        sync / "gt864_fr0_basemul.h": SOURCE / "gt864_fr0_basemul.h",
        sync / "test_gt864_fr0_basemul.c": SOURCE / "test_gt864_fr0_basemul.c",
    }
    for destination, source in sources.items(): shutil.copy2(source, destination)
    table = sync / "gt864_fr0_basemul_tables.h"
    command(["python3", str(SOURCE / "generate_tables.py"), "--header", str(table)])
    sources[table] = table
    ssh(f"mkdir -p {REMOTE}")
    command(["rsync", "-av", f"{sync}/", f"{HOST}:{REMOTE}/"])
    environment = ssh("uname -a; lscpu | head -24; gcc --version | head -1; "
                      "vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in environment and "throttled=0x0" in environment
    (raw / "environment-before.txt").write_text(environment, encoding="utf-8")
    build = ssh(f"cd {REMOTE} && make clean && make all && make check && "
                "size build/kernel.o build/bench-baseline && "
                "objdump -drwC build/kernel.o")
    assert "gt864_fr0_basemul_arithmetic_gate=pass" in build
    (raw / "build-correctness-disassembly.log").write_text(build, encoding="utf-8")
    repetitions, all_rows = [], []
    for repetition in range(3):
        rows = []
        for order in ("BAN", "NAB"):
            remote_output = ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench-baseline {order}")
            (raw / f"rep{repetition}-{order}.log").write_text(remote_output, encoding="utf-8")
            parsed = parse(remote_output); rows += parsed; all_rows += parsed
        repetitions.append(summarize(rows))
        thermal = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{repetition}.txt").write_text(thermal, encoding="utf-8")
    result = {
        "experiment": "B1-0_FR0_compiler_baseline", "host": HOST, "core": 3,
        "compiler_flags": "gcc -O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd",
        "repetitions": repetitions, "overall": summarize(all_rows),
        "source_sha256": {str(path.relative_to(sync)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in sources}, "throttled": "0x0"}
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
