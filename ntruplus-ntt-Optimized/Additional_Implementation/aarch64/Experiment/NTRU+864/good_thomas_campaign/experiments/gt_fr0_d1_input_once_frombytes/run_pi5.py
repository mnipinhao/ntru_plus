#!/usr/bin/env python3
"""Stage, run and summarize the D1-P3B11 isolated Pi 5 hard gate."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import statistics
import subprocess
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
P3B3 = HERE.parent / "gt_fr0_d1_byte_boundary_pmu"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-p3b11-input-once-frombytes"
OUT, SYNC, RAW = HERE / "build", HERE / "build/sync", HERE / "build/raw"


def command(arguments: list[str], cwd: Path | None = None) -> str:
    try:
        return subprocess.check_output(arguments, text=True,
                                       stderr=subprocess.STDOUT, cwd=cwd)
    except subprocess.CalledProcessError as error:
        if error.output:
            print(error.output, end="", flush=True)
        raise


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


def audit_object(disassembly: str) -> dict[str, object]:
    match = re.search(
        r"<input_once_top>:\n(?P<body>.*?)(?=\n[0-9a-f]+ <|\Z)",
        disassembly, re.S)
    if match is None:
        raise RuntimeError("input_once_top disassembly missing")
    body = match.group("body")
    lines = [line for line in body.splitlines()
             if re.match(r"\s*[0-9a-f]+:\s+[0-9a-f]+", line)]
    opcodes = Counter()
    for line in lines:
        opcode = re.match(r"\s*[0-9a-f]+:\s+[0-9a-f]+\s+(\S+)", line)
        if opcode:
            opcodes[opcode.group(1)] += 1
    stack = [line.strip() for line in lines if "[sp" in line]
    registers = sorted({int(value) for line in lines
                        for value in re.findall(r"\bv(\d+)\b", line)})
    # GCC may pair adjacent q-vector output stores as STP.  Stack references,
    # not STP itself, are the spill criterion.
    if stack:
        raise RuntimeError("coefficient core has stack references: " + str(stack))
    return {
        "static_instructions": len(lines),
        "opcode_histogram": dict(sorted(opcodes.items())),
        "vector_registers": registers,
        "stack_references": stack,
        "coefficient_spill": False,
    }


def main() -> None:
    SYNC.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    command(["python3", str(HERE / "prepare.py")])
    command(["python3", "generate.py"], cwd=P3B3)
    sources = {
        "Makefile": HERE / "pi5-Makefile",
        "bench_pi5.c": HERE / "bench_pi5.c",
        "input_once_frombytes.c": OUT / "input_once_frombytes.c",
        "input_once_frombytes.h": HERE / "input_once_frombytes.h",
        "baseline_c1_from.c": HERE / "baseline_c1_from.c",
        "p3b11_tables.h": OUT / "p3b11_tables.h",
        "gather.h": P3B3 / "build/gather.h",
        "tables.h": P3B3 / "build/tables.h",
    }
    for name, source in sources.items():
        shutil.copy2(source, SYNC / name)
    manifest = {name: hashlib.sha256(source.read_bytes()).hexdigest()
                for name, source in sources.items()}
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    ssh(f"mkdir -p {REMOTE}")
    print(command(["rsync", "-av", "--delete", "--exclude=build",
                   str(SYNC) + "/", HOST + ":" + REMOTE + "/"]), flush=True)
    environment = ssh("uname -a; lscpu | head -24; gcc --version | head -1; "
                      "vcgencmd measure_temp; vcgencmd get_throttled")
    if "Cortex-A76" not in environment or "throttled=0x0" not in environment:
        raise RuntimeError(environment)
    (RAW / "environment.txt").write_text(environment, encoding="utf-8")

    build = ssh(f"cd {REMOTE} && make clean && make -B all && make check && "
                "size build/bench && objdump -dr build/input_once_frombytes.o")
    if "p3b11_pi_correctness=pass" not in build:
        raise RuntimeError("Pi correctness marker absent")
    (RAW / "build-correctness-object.log").write_text(build, encoding="utf-8")
    object_audit = audit_object(build)

    repetitions, all_rows = [], []
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
    baseline, candidate = overall["from_c1"], overall["from_input_once"]
    result = {
        "experiment": "D1-P3B11", "host": HOST, "core": 3,
        "correctness": "pass", "object_audit": object_audit,
        "overall": overall,
        "input_once_minus_c1": {
            key: candidate[key] - baseline[key]
            for key in ("cycles", "instructions", "branches")
        },
        "cycle_gate_pass": candidate["cycles"] < baseline["cycles"],
        "repetitions": repetitions, "throttled": "0x0",
        "production_linked": False,
    }
    (OUT / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
