#!/usr/bin/env python3
"""Stage, run and summarize the D1-P3B5 isolated Pi 5 hard gate."""

from __future__ import annotations

import hashlib
import json
import shutil
import statistics
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
P3B3 = EXPERIMENTS / "gt_fr0_d1_byte_boundary_pmu"
R9 = EXPERIMENTS / "gt_fr0_d1_route9_pmu"
PACK = HERE.parents[4] / "NTRU+864/asm/pack.s"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-p3b5-fused-tobytes"
OUT = HERE / "build"
SYNC = OUT / "sync"
RAW = OUT / "raw"


def command(arguments: list[str]) -> str:
    return subprocess.check_output(arguments, text=True,
                                   stderr=subprocess.STDOUT)


def ssh(script: str) -> str:
    return command([
        "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
        HOST, script,
    ])


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
    SYNC.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    command(["python3", str(HERE / "prepare.py")])
    command(["python3", str(R9 / "generate_tables.py")])

    sources = {
        "Makefile": HERE / "pi5-Makefile",
        "bench_pi5.c": HERE / "bench_pi5.c",
        "fused_tobytes.c": HERE / "fused_tobytes.c",
        "fused_tobytes.h": HERE / "fused_tobytes.h",
        "baseline_r9_to.c": HERE / "baseline_r9_to.c",
        "p3b5_tables.h": OUT / "p3b5_tables.h",
        "route9.c": R9 / "route9.c",
        "route9.h": R9 / "route9.h",
        "p3b1_tables.h": R9 / "build/p3b1_tables.h",
        "stock_wrapper.S": P3B3 / "stock_wrapper.S",
        "pack.s": PACK,
    }
    for name, source in sources.items():
        target = SYNC / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    (OUT / "manifest.json").write_text(json.dumps({
        name: hashlib.sha256(source.read_bytes()).hexdigest()
        for name, source in sources.items()
    }, indent=2) + "\n", encoding="utf-8")

    ssh(f"mkdir -p {REMOTE}")
    print(command([
        "rsync", "-av", "--delete", "--exclude=build",
        str(SYNC) + "/", HOST + ":" + REMOTE + "/",
    ]), flush=True)
    environment = ssh(
        "uname -a; lscpu | head -24; gcc --version | head -1; "
        "vcgencmd measure_temp; vcgencmd get_throttled"
    )
    if "Cortex-A76" not in environment or "throttled=0x0" not in environment:
        raise RuntimeError(environment)
    (RAW / "environment.txt").write_text(environment, encoding="utf-8")

    try:
        build = ssh(
            f"cd {REMOTE} && make clean && make -B all && make check && "
            "size build/bench && objdump -dr build/fused_tobytes.o && "
            "readelf -sW build/bench"
        )
    except subprocess.CalledProcessError as error:
        (RAW / "build-failure.log").write_text(error.output, encoding="utf-8")
        print(error.output)
        raise
    if "p3b5_pi_correctness=pass" not in build:
        raise RuntimeError("Pi correctness marker absent")
    (RAW / "build-correctness-object.log").write_text(build, encoding="utf-8")

    repetitions = []
    all_rows: list[tuple[str, float, float, float]] = []
    for repetition in range(3):
        rows = []
        for order in (0, 1):
            output = ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench {order}")
            (RAW / f"rep{repetition}-{order}.log").write_text(
                output, encoding="utf-8")
            parsed = [line.split(",") for line in output.splitlines()
                      if line.startswith("sample,")]
            if len(parsed) != 82:
                raise RuntimeError(f"expected 82 samples, got {len(parsed)}")
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
    r9 = overall["to_r9"]
    fused = overall["to_fused"]
    result = {
        "experiment": "D1-P3B5",
        "host": HOST,
        "core": 3,
        "correctness": "pass",
        "overall": overall,
        "fused_minus_r9": {
            key: fused[key] - r9[key]
            for key in ("cycles", "instructions", "branches")
        },
        "threshold_cycles": 1250,
        "threshold_pass": fused["cycles"] < 1250,
        "repetitions": repetitions,
        "throttled": "0x0",
        "production_linked": False,
    }
    (OUT / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
