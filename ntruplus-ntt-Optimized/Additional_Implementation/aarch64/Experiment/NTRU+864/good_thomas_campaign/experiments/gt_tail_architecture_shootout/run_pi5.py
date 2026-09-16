#!/usr/bin/env python3
"""Build and run the paired A1 tail-only PMU shootout on the Pi 5."""

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
REMOTE = "/home/pi/ntruplus-experiments/gt864-a1-tail-architecture"
OUTPUT = HERE / "build/pi5-tail"
VARIANTS = ("T0", "T1", "T2", "noop")


def command(args: list[str], capture: bool = False) -> str:
    result = subprocess.run(args, check=True, text=True, capture_output=capture)
    return result.stdout if capture else ""


def ssh(text: str) -> str:
    return command(["ssh", "-o", "BatchMode=yes", HOST, text], True)


def percentile(values: list[float], p: float) -> float:
    values = sorted(values)
    at = (len(values) - 1) * p / 100
    lo, hi = math.floor(at), math.ceil(at)
    return values[lo] if lo == hi else values[lo] * (hi - at) + values[hi] * (at - lo)


def stats(values: list[float]) -> dict[str, float]:
    return {name: percentile(values, p) for name, p in
            (("p10", 10), ("p25", 25), ("p50", 50), ("p75", 75), ("p90", 90))}


def parse(text: str) -> list[dict[str, object]]:
    assert "correctness,status=pass,cases=64" in text
    pattern = re.compile(
        r"^sample,index=\d+,position=\d+,variant=(\w+),cycles=([0-9.]+),"
        r"instructions=([0-9.]+),loads=([0-9.]+),stores=([0-9.]+),branches=([0-9.]+)$")
    rows = []
    for line in text.splitlines():
        if match := pattern.match(line):
            rows.append({"variant": match.group(1), "cycles": float(match.group(2)),
                         "instructions": float(match.group(3)), "loads": float(match.group(4)),
                         "stores": float(match.group(5)), "branches": float(match.group(6))})
    assert len(rows) == 244
    return rows


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    result = {}
    for variant in VARIANTS:
        selected = [row for row in rows if row["variant"] == variant]
        metrics = {metric: stats([float(row[metric]) for row in selected])
                   for metric in ("cycles", "instructions", "loads", "stores", "branches")}
        metrics["ipc"] = metrics["instructions"]["p50"] / metrics["cycles"]["p50"]
        result[variant] = metrics
    overhead = result["noop"]["instructions"]["p50"]
    result["kernel_instructions_minus_noop"] = {
        variant: result[variant]["instructions"]["p50"] - overhead
        for variant in VARIANTS[:-1]
    }
    return result


def main() -> None:
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise SystemExit(f"refusing to overwrite {OUTPUT}")
    sync, raw = OUTPUT / "sync", OUTPUT / "raw"
    sync.mkdir(parents=True); raw.mkdir(parents=True)
    command(["python3", str(HERE / "prepare.py")])
    sources = {
        sync / "Makefile": HERE / "pi5-Makefile",
        sync / "bench_pmu.c": HERE / "bench_pmu.c",
        sync / "tail_variants.S": HERE / "build/tail_variants.S",
    }
    for destination, source in sources.items(): shutil.copy2(source, destination)
    # The synced Makefile expects the generated assembly under build/.
    (sync / "build").mkdir()
    shutil.move(sync / "tail_variants.S", sync / "build/tail_variants.S")
    synced_sources = [sync / "Makefile", sync / "bench_pmu.c",
                      sync / "build/tail_variants.S"]
    ssh(f"mkdir -p {REMOTE}")
    command(["rsync", "-av", f"{sync}/", f"{HOST}:{REMOTE}/"])
    environment = ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in environment and "throttled=0x0" in environment
    (raw / "environment-before.txt").write_text(environment, encoding="utf-8")
    build = ssh(f"cd {REMOTE} && make clean && make all && size build/bench-pmu")
    (raw / "build.log").write_text(build, encoding="utf-8")
    all_rows = []
    repetitions = []
    for rep in range(3):
        rows = []
        for order in ("012N", "N210"):
            output = ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench-pmu {order}")
            (raw / f"rep{rep}-{order}.log").write_text(output, encoding="utf-8")
            parsed = parse(output); rows += parsed; all_rows += parsed
        repetitions.append(summarize(rows))
        thermal = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{rep}.txt").write_text(thermal, encoding="utf-8")
    result = {
        "experiment": "gt864-a1-tail-architecture", "host": HOST, "core": 3,
        "repetitions": repetitions, "overall": summarize(all_rows),
        "source_sha256": {str(path.relative_to(sync)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in synced_sources},
        "slothy": "not_run",
    }
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
