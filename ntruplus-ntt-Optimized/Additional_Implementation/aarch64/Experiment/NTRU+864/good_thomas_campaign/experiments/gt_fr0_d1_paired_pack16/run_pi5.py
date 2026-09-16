#!/usr/bin/env python3
"""Run the D1-P3B9 paired-pack primitive hard gate on Pi 5."""

from __future__ import annotations

import json
import shutil
import statistics
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-p3b9-paired-pack16"
OUT, SYNC, RAW = HERE / "build", HERE / "build/sync", HERE / "build/raw"


def command(arguments: list[str]) -> str:
    return subprocess.check_output(arguments, text=True,
                                   stderr=subprocess.STDOUT)


def ssh(script: str) -> str:
    return command(["ssh", "-o", "BatchMode=yes", "-o",
                    "ConnectTimeout=10", HOST, script])


def summarize(rows: list[tuple[str, float, float, float]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for name in sorted({row[0] for row in rows}):
        selected = [row for row in rows if row[0] == name]
        result[name] = {
            metric: statistics.median(row[index] for row in selected)
            for index, metric in enumerate(
                ("cycles", "instructions", "branches"), 1)
        }
    return result


def main() -> None:
    command(["python3", str(HERE / "prepare.py")])
    SYNC.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    sources = {
        "Makefile": HERE / "pi5-Makefile", "bench_pi5.c": HERE / "bench_pi5.c",
        "paired_pack16.h": HERE / "paired_pack16.h",
        "pack8.c": OUT / "pack8.c", "pack16.c": OUT / "pack16.c",
    }
    for name, source in sources.items(): shutil.copy2(source, SYNC / name)
    ssh(f"mkdir -p {REMOTE}")
    print(command(["rsync", "-av", "--delete", "--exclude=build",
                   str(SYNC) + "/", HOST + ":" + REMOTE + "/"]), flush=True)
    environment = ssh("uname -a; lscpu | head -24; gcc --version | head -1; "
                      "vcgencmd measure_temp; vcgencmd get_throttled")
    if "Cortex-A76" not in environment or "throttled=0x0" not in environment:
        raise RuntimeError(environment)
    (RAW / "environment.txt").write_text(environment, encoding="utf-8")
    build = ssh(f"cd {REMOTE} && make clean && make -B all && make check && "
                "size build/*.o build/bench && objdump -dr build/pack8.o && "
                "objdump -dr build/pack16.o")
    if "p3b9_pi_correctness=pass" not in build: raise RuntimeError("correctness")
    (RAW / "build-correctness-object.log").write_text(build, encoding="utf-8")
    repetitions, all_rows = [], []
    for repetition in range(3):
        rows = []
        for order in (0, 1):
            output = ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench {order}")
            (RAW / f"rep{repetition}-{order}.log").write_text(output, encoding="utf-8")
            parsed = [line.split(",") for line in output.splitlines()
                      if line.startswith("sample,")]
            if len(parsed) != 82: raise RuntimeError(f"samples={len(parsed)}")
            rows.extend((p[1], *(float(v) for v in p[2:])) for p in parsed)
        repetitions.append(summarize(rows)); all_rows.extend(rows)
        thermal = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        if "throttled=0x0" not in thermal: raise RuntimeError(thermal)
    overall = summarize(all_rows)
    control, candidate = overall["pack8"], overall["pack16"]
    result = {
        "experiment": "D1-P3B9", "correctness": "pass", "overall": overall,
        "pack16_minus_pack8": {k: candidate[k] - control[k]
                                for k in ("cycles", "instructions", "branches")},
        "partner_memory_instructions_full_call": 108,
        "repetitions": repetitions, "throttled": "0x0",
        "production_linked": False,
    }
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__": main()
