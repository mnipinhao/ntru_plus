#!/usr/bin/env python3
"""Paired Cortex-A76 PMU run for staged versus direct FR-ISO2 BaseMul."""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-friso2-basemul-cycle"
OUTPUT = HERE / "build/pi5-formal"
VARIANTS = ("staged", "direct", "staged_add", "direct_add", "noop")


def command(args: list[str], capture: bool = False) -> str:
    result = subprocess.run(args, check=True, text=True, capture_output=capture)
    return result.stdout if capture else ""


def ssh(text: str) -> str:
    return command(["ssh", "-o", "BatchMode=yes", HOST, text], True)


def percentile(values: list[float], p: int) -> float:
    values = sorted(values)
    at = (len(values) - 1) * p / 100
    low, high = math.floor(at), math.ceil(at)
    if low == high:
        return values[low]
    return values[low] * (high - at) + values[high] * (at - low)


def stats(values: list[float]) -> dict[str, float]:
    out = {name: percentile(values, p) for name, p in
           (("p10", 10), ("p25", 25), ("p50", 50),
            ("p75", 75), ("p90", 90))}
    out["iqr"] = out["p75"] - out["p25"]
    return out


def parse(text: str) -> list[dict[str, object]]:
    expected = "correctness,status=pass,basemul=64,basemul_alias=64,basemuladd=64"
    assert expected in text
    pattern = re.compile(
        r"^sample,order=\w+,index=\d+,position=\d+,variant=(\w+),"
        r"cycles=([0-9.]+),instructions=([0-9.]+)$")
    rows = [{"variant": match.group(1),
             "cycles": float(match.group(2)),
             "instructions": float(match.group(3))}
            for line in text.splitlines()
            if (match := pattern.match(line))]
    assert len(rows) == 305
    return rows


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for variant in VARIANTS:
        selected = [row for row in rows if row["variant"] == variant]
        cycles = stats([float(row["cycles"]) for row in selected])
        instructions = stats([float(row["instructions"]) for row in selected])
        result[variant] = {
            "count": len(selected),
            "cycles": cycles,
            "instructions": instructions,
            "ipc": instructions["p50"] / cycles["p50"],
        }
    noop = result["noop"]
    assert isinstance(noop, dict)
    overhead = noop["instructions"]["p50"]
    derived = {"common_harness_instructions": overhead}
    for variant in VARIANTS[:-1]:
        item = result[variant]
        assert isinstance(item, dict)
        derived[variant + "_kernel_instructions"] = \
            item["instructions"]["p50"] - overhead
    result["derived"] = derived
    return result


def main() -> None:
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise SystemExit(f"refusing to overwrite {OUTPUT}")
    sync, raw = OUTPUT / "sync", OUTPUT / "raw"
    sync.mkdir(parents=True)
    raw.mkdir(parents=True)
    sources = {
        sync / "Makefile": HERE / "pi5-Makefile",
        sync / "bench_pmu.c": HERE / "bench_pmu.c",
        sync / "gt864_friso2_basemul_neon.c": HERE / "gt864_friso2_basemul_neon.c",
        sync / "gt864_friso2_basemul_neon.h": HERE / "gt864_friso2_basemul_neon.h",
    }
    for destination, source in sources.items():
        shutil.copy2(source, destination)
    ssh(f"mkdir -p {REMOTE}")
    command(["rsync", "-av", f"{sync}/", f"{HOST}:{REMOTE}/"])
    environment = ssh(
        "uname -a; lscpu | head -24; gcc --version | head -1; "
        "vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in environment and "throttled=0x0" in environment
    (raw / "environment-before.txt").write_text(environment, encoding="utf-8")
    build = ssh(
        f"cd {REMOTE} && make clean && make all && size build/kernel.o && "
        "objdump -d build/kernel.o")
    (raw / "build-and-disassembly.log").write_text(build, encoding="utf-8")
    repetitions, all_rows = [], []
    for repetition in range(3):
        rows = []
        for order in ("SDBAN", "NABDS"):
            output = ssh(
                f"cd {REMOTE} && taskset -c 3 ./build/bench_pmu {order}")
            (raw / f"rep{repetition}-{order}.log").write_text(
                output, encoding="utf-8")
            parsed = parse(output)
            rows += parsed
            all_rows += parsed
        repetitions.append(summarize(rows))
        thermal = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{repetition}.txt").write_text(
            thermal, encoding="utf-8")
    result = {
        "experiment": "gt864-friso2-basemul-cycle",
        "host": HOST,
        "core": 3,
        "repetitions": repetitions,
        "overall": summarize(all_rows),
        "throttled": "0x0",
        "source_sha256": {
            str(destination.relative_to(sync)):
                hashlib.sha256(destination.read_bytes()).hexdigest()
            for destination in sources
        },
    }
    (OUTPUT / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
