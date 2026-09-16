#!/usr/bin/env python3
"""Stage, audit, run, and summarize the D1-P3B7 Pi 5 hard gate."""

from __future__ import annotations

import hashlib
import json
import shutil
import statistics
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
P3B6 = HERE.parent / "gt_fr0_d1_input_once_tobytes"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-p3b7-input-once-lowering"
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
        "Makefile": HERE / "pi5-Makefile",
        "bench_pi5.c": HERE / "bench_pi5.c",
        "lowered_tobytes.h": HERE / "lowered_tobytes.h",
        "control.c": P3B6 / "build/input_once_tobytes.c",
        "input_once_tobytes.h": P3B6 / "input_once_tobytes.h",
        "l1_tobytes.c": OUT / "l1_tobytes.c",
        "l12_tobytes.c": OUT / "l12_tobytes.c",
    }
    for name, source in sources.items():
        shutil.copy2(source, SYNC / name)
    (OUT / "manifest.json").write_text(json.dumps({
        name: hashlib.sha256(source.read_bytes()).hexdigest()
        for name, source in sources.items()
    }, indent=2) + "\n", encoding="utf-8")
    ssh(f"mkdir -p {REMOTE}")
    print(command(["rsync", "-av", "--delete", "--exclude=build",
                   str(SYNC) + "/", HOST + ":" + REMOTE + "/"]), flush=True)
    environment = ssh("uname -a; lscpu | head -24; gcc --version | head -1; "
                      "vcgencmd measure_temp; vcgencmd get_throttled")
    if "Cortex-A76" not in environment or "throttled=0x0" not in environment:
        raise RuntimeError(environment)
    (RAW / "environment.txt").write_text(environment, encoding="utf-8")
    build = ssh(f"cd {REMOTE} && make clean && make -B all && make check && "
                "size build/*.o build/bench && "
                "objdump -dr build/control.o && objdump -dr build/l1_tobytes.o && "
                "objdump -dr build/l12_tobytes.o")
    if "p3b7_pi_correctness=pass" not in build:
        raise RuntimeError("Pi correctness marker absent")
    (RAW / "build-correctness-object.log").write_text(build, encoding="utf-8")

    repetitions, all_rows = [], []
    for repetition in range(3):
        rows = []
        for order in (0, 1):
            output = ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench {order}")
            (RAW / f"rep{repetition}-{order}.log").write_text(
                output, encoding="utf-8")
            parsed = [line.split(",") for line in output.splitlines()
                      if line.startswith("sample,")]
            if len(parsed) != 123:
                raise RuntimeError(f"expected 123 samples, got {len(parsed)}")
            rows.extend((parts[1], *(float(value) for value in parts[2:]))
                        for parts in parsed)
        repetitions.append(summarize(rows))
        all_rows.extend(rows)
        thermal = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        if "throttled=0x0" not in thermal:
            raise RuntimeError(thermal)
        (RAW / f"environment-rep{repetition}.txt").write_text(
            thermal, encoding="utf-8")

    overall = summarize(all_rows)
    control = overall["to_p3b6"]
    result = {
        "experiment": "D1-P3B7", "host": HOST, "core": 3,
        "correctness": "pass", "overall": overall,
        "deltas_from_p3b6": {
            name: {key: values[key] - control[key]
                   for key in ("cycles", "instructions", "branches")}
            for name, values in overall.items() if name != "to_p3b6"
        },
        "local_gate_cycles": 1350,
        "global_promotion_cycles": 1250,
        "best": min(overall, key=lambda name: overall[name]["cycles"]),
        "repetitions": repetitions, "throttled": "0x0",
        "production_linked": False,
    }
    (OUT / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
