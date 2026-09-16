#!/usr/bin/env python3
"""Run paired baseline-vs-Slothy T1 boundaries on the Raspberry Pi 5."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
A1 = HERE.parent / "gt_tail_architecture_shootout"
SPEC = importlib.util.spec_from_file_location("a1_runner", A1 / "run_pi5.py")
assert SPEC and SPEC.loader
BASE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(BASE)
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/ntruplus-experiments/gt864-t1-slothy"
DEFAULT_OUTPUT = HERE / "pi5-results"
VARIANTS = ("one_T1", "one_T1S", "six_T1", "six_T1S", "full_T1", "full_T1S", "noop")


def parse(text: str) -> list[dict[str, object]]:
    assert "correctness,status=pass,one_bank=64,six_bank=64,full=64,slothy=64" in text
    pattern = re.compile(r"^sample,index=\d+,position=\d+,variant=(\w+),cycles=([0-9.]+),instructions=([0-9.]+),branches=([0-9.]+)$")
    rows = []
    for line in text.splitlines():
        if match := pattern.match(line):
            rows.append({"variant": match.group(1), "cycles": float(match.group(2)),
                         "instructions": float(match.group(3)), "branches": float(match.group(4))})
    assert len(rows) == 61 * len(VARIANTS)
    return rows


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    result = {}
    for variant in VARIANTS:
        chosen = [row for row in rows if row["variant"] == variant]
        result[variant] = {metric: BASE.stats([float(row[metric]) for row in chosen])
                           for metric in ("cycles", "instructions", "branches")}
        result[variant]["ipc"] = result[variant]["instructions"]["p50"] / result[variant]["cycles"]["p50"]
    overhead = result["noop"]["instructions"]["p50"]
    result["kernel_instructions_minus_noop"] = {
        variant: result[variant]["instructions"]["p50"] - overhead
        for variant in VARIANTS[:-1]
    }
    for base, candidate in (("one_T1", "one_T1S"), ("six_T1", "six_T1S"), ("full_T1", "full_T1S")):
        result[f"delta_{candidate}_minus_{base}"] = {
            metric: result[candidate][metric]["p50"] - result[base][metric]["p50"]
            for metric in ("cycles", "instructions", "branches")
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--candidate-source", type=Path)
    parser.add_argument("--preserve-physical-outputs", action="store_true")
    parser.add_argument("--workflow", default="functional_RA_then_split_window_schedule")
    args = parser.parse_args()
    output_dir = args.output_dir
    if (output_dir / "summary.json").exists():
        raise SystemExit(f"refusing to overwrite {output_dir}")
    sync, raw = output_dir / "sync", output_dir / "raw"
    (sync / "build").mkdir(parents=True, exist_ok=True)
    (sync / "deps").mkdir(exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)
    BASE.command(["python3", str(A1 / "prepare.py")])
    prepare = ["python3", str(HERE / "prepare_candidate.py")]
    if args.candidate_source is not None:
        prepare += ["--scheduled", str(args.candidate_source)]
    if args.preserve_physical_outputs:
        prepare += ["--preserve-physical-outputs"]
    BASE.command(prepare)
    files = {
        sync / "Makefile": HERE / "pi5-Makefile",
        sync / "bench_candidate_pmu.c": HERE / "bench_candidate_pmu.c",
        sync / "test_candidate.c": HERE / "test_candidate.c",
        sync / "build/gt864_fr0_to_official_map.h": A1 / "build/gt864_fr0_to_official_map.h",
        sync / "build/tail_variants.S": A1 / "build/tail_variants.S",
        sync / "build/pass2_t1.S": A1 / "build/pass2_t1.S",
        sync / "build/full_t1_wrapper.S": A1 / "build/full_t1_wrapper.S",
        sync / "build/pass2_t1_slothy.S": HERE / "build/pass2_t1_slothy.S",
        sync / "build/full_t1_slothy_wrapper.S": HERE / "build/full_t1_slothy_wrapper.S",
        sync / "deps/top_split.s": A1.parent / "gt_2x9x16_ld3_top_split/gt864_top_split.s",
        sync / "deps/official_ntt.s": A1.parents[4] / "NTRU+864/asm/ntt.s",
    }
    for destination, source in files.items(): shutil.copy2(source, destination)
    BASE.ssh(f"mkdir -p {REMOTE}")
    BASE.command(["rsync", "-av", f"{sync}/", f"{HOST}:{REMOTE}/"])
    env = BASE.ssh("uname -a; lscpu | head -24; gcc --version | head -1; vcgencmd measure_temp; vcgencmd get_throttled")
    assert "Cortex-A76" in env and "throttled=0x0" in env
    (raw / "environment-before.txt").write_text(env, encoding="utf-8")
    build = BASE.ssh(f"cd {REMOTE} && make clean && make all && make check && size build/bench-candidate")
    (raw / "build-and-correctness.log").write_text(build, encoding="utf-8")
    all_rows, repetitions = [], []
    for rep in range(3):
        rows = []
        for order in ("abcdefN", "Nfedcba"):
            remote_output = BASE.ssh(f"cd {REMOTE} && taskset -c 3 ./build/bench-candidate {order}")
            (raw / f"rep{rep}-{order}.log").write_text(remote_output, encoding="utf-8")
            parsed = parse(remote_output); rows += parsed; all_rows += parsed
        repetitions.append(summarize(rows))
        thermal = BASE.ssh("vcgencmd measure_temp; vcgencmd get_throttled")
        assert "throttled=0x0" in thermal
        (raw / f"environment-rep{rep}.txt").write_text(thermal, encoding="utf-8")
    result = {
        "experiment": "gt864-t1-slothy", "host": HOST, "core": 3,
        "repetitions": repetitions, "overall": summarize(all_rows),
        "source_sha256": {str(path.relative_to(sync)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in files},
        "slothy": {"version": "0.2.0", "checkout": "f8462d0deb9973565b525f7e63636630fa679bd7f",
                   "workflow": args.workflow},
    }
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__": main()
