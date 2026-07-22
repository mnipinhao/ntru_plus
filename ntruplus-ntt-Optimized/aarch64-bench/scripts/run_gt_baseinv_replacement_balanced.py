#!/usr/bin/env python3
"""Run balanced separate-binary PMU for the baseinv replacement candidate."""

from __future__ import annotations

import argparse
import os
import statistics
import subprocess
import sys
from pathlib import Path


DEFAULT_EVENTS = (
    "cycles",
    "instructions",
    "branch_misses",
    "l1i_refill",
    "l1i_miss",
    "stall_frontend",
    "stall_backend",
)


def run_command(command: list[str], allow_unavailable: bool = False) -> str | None:
    completed = subprocess.run(command, text=True, capture_output=True)
    if allow_unavailable and completed.returncode == 2:
        return None
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed.stdout


def pinned_command(core: int, binary: Path, *args: str) -> list[str]:
    return ["taskset", "-c", str(core), str(binary), *args]


def parse_record(output: str, prefix: str) -> dict[str, str]:
    for line in output.splitlines():
        if not line.startswith(prefix + ","):
            continue
        fields: dict[str, str] = {}
        for item in line.split(",")[1:]:
            key, value = item.split("=", 1)
            fields[key] = value
        return fields
    raise RuntimeError(f"missing {prefix} record in output:\n{output}")


def percentile(values: list[float], percent: int) -> float:
    ordered = sorted(values)
    index = percent * (len(ordered) - 1) // 100
    return ordered[index]


def static_metadata(binary: Path) -> list[str]:
    records: list[str] = []
    size_output = run_command(["size", str(binary)])
    assert size_output is not None
    size_lines = [line.split() for line in size_output.splitlines() if line.strip()]
    if len(size_lines) >= 2 and len(size_lines[-1]) >= 4:
        records.append(
            "static_layout,binary={},text={},data={},bss={}".format(
                binary.name, size_lines[-1][0], size_lines[-1][1], size_lines[-1][2]
            )
        )

    nm_output = run_command(["nm", "-S", "--defined-only", str(binary)])
    assert nm_output is not None
    wanted = {"crypto_kem_keypair", "poly_baseinv_scaled_r"}
    for line in nm_output.splitlines():
        fields = line.split()
        if len(fields) < 4 or fields[-1] not in wanted:
            continue
        records.append(
            "static_symbol,binary={},symbol={},address=0x{},size={}".format(
                binary.name, fields[-1], fields[0], int(fields[1], 16)
            )
        )
    return records


def run_correctness(core: int, binary: Path, cases: int) -> tuple[dict[str, str], str]:
    output = run_command(pinned_command(core, binary, "--correctness", str(cases)))
    assert output is not None
    return parse_record(output, "correctness"), output


def run_layout(core: int, binary: Path) -> list[str]:
    output = run_command(pinned_command(core, binary, "--layout"))
    assert output is not None
    return [line for line in output.splitlines() if line.startswith("layout,")]


def run_sample(
    core: int,
    binary: Path,
    event: str,
    iterations: int,
    warmup: int,
    sample: int,
) -> tuple[dict[str, str], str] | None:
    output = run_command(
        pinned_command(
            core,
            binary,
            "--sample",
            event,
            str(iterations),
            str(warmup),
            str(sample),
        ),
        allow_unavailable=True,
    )
    if output is None:
        return None
    return parse_record(output, "sample"), output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--core", type=int, default=3)
    parser.add_argument("--tests", type=int, default=31)
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--correctness-cases", type=int, default=256)
    parser.add_argument("--events", default=",".join(DEFAULT_EVENTS))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    current = args.current.resolve()
    candidate = args.candidate.resolve()
    for binary in (current, candidate):
        if not binary.is_file() or not os.access(binary, os.X_OK):
            raise SystemExit(f"binary is missing or not executable: {binary}")

    report: list[str] = [
        "benchmark,separate_binaries=1,single_kem_body=1,direct_backend=1,"
        f"order=AB_BA,core={args.core},tests={args.tests},"
        f"iterations={args.iterations},warmup={args.warmup}"
    ]
    for binary in (current, candidate):
        report.extend(static_metadata(binary))
        report.extend(run_layout(args.core, binary))

    current_correctness, current_raw = run_correctness(
        args.core, current, args.correctness_cases
    )
    candidate_correctness, candidate_raw = run_correctness(
        args.core, candidate, args.correctness_cases
    )
    report.extend(line for line in current_raw.splitlines() if line.startswith("correctness,"))
    report.extend(line for line in candidate_raw.splitlines() if line.startswith("correctness,"))
    correctness_match = (
        current_correctness["digest"] == candidate_correctness["digest"]
        and current_correctness["decap_failures"] == "0"
        and candidate_correctness["decap_failures"] == "0"
        and current_correctness["shared_secret_mismatches"] == "0"
        and candidate_correctness["shared_secret_mismatches"] == "0"
    )
    report.append(
        "cross_binary_correctness,cases={},digest_match={},mismatches={}".format(
            args.correctness_cases, int(correctness_match), 0 if correctness_match else 1
        )
    )
    if not correctness_match:
        for line in report:
            print(line)
        return 1

    medians: dict[str, tuple[float, float]] = {}
    for event in [item for item in args.events.split(",") if item]:
        current_values: list[float] = []
        candidate_values: list[float] = []
        deltas: list[float] = []
        unavailable = False

        for sample in range(args.tests):
            order = (
                (("current", current), ("candidate", candidate))
                if sample % 2 == 0
                else (("candidate", candidate), ("current", current))
            )
            pair: dict[str, dict[str, str]] = {}
            for label, binary in order:
                result = run_sample(
                    args.core, binary, event, args.iterations, args.warmup, sample
                )
                if result is None:
                    unavailable = True
                    break
                record, _ = result
                pair[label] = record
            if unavailable:
                break
            if pair["current"]["digest"] != pair["candidate"]["digest"]:
                raise RuntimeError(
                    f"output digest mismatch for event={event} sample={sample}"
                )

            current_value = float(pair["current"]["per_keypair"])
            candidate_value = float(pair["candidate"]["per_keypair"])
            delta = candidate_value - current_value
            current_values.append(current_value)
            candidate_values.append(candidate_value)
            deltas.append(delta)
            report.append(
                "pair,event={},sample={},first={},current={:.6f},"
                "candidate={:.6f},delta={:.6f},digest_match=1".format(
                    event, sample, order[0][0], current_value, candidate_value, delta
                )
            )

        if unavailable:
            report.append(f"event_support,event={event},available=0")
            continue

        current_median = statistics.median(current_values)
        candidate_median = statistics.median(candidate_values)
        delta_median = statistics.median(deltas)
        mad = statistics.median(abs(value - delta_median) for value in deltas)
        wins = sum(value < 0 for value in deltas)
        reduction = (
            -100.0 * delta_median / current_median if current_median else 0.0
        )
        medians[event] = (current_median, candidate_median)
        report.append(
            "summary,event={},current_p50={:.6f},candidate_p50={:.6f},"
            "delta_p10={:.6f},delta_p50={:.6f},delta_p90={:.6f},"
            "mad={:.6f},reduction_percent={:.4f},wins={},win_rate={:.4f},"
            "samples={}".format(
                event,
                current_median,
                candidate_median,
                percentile(deltas, 10),
                delta_median,
                percentile(deltas, 90),
                mad,
                reduction,
                wins,
                wins / len(deltas),
                len(deltas),
            )
        )

    if "cycles" in medians and "instructions" in medians:
        current_cycles, candidate_cycles = medians["cycles"]
        current_instructions, candidate_instructions = medians["instructions"]
        report.append(
            "cpi,current={:.6f},candidate={:.6f}".format(
                current_cycles / current_instructions,
                candidate_cycles / candidate_instructions,
            )
        )

    for line in report:
        if not line.startswith("pair,"):
            print(line)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text("\n".join(report) + "\n", encoding="utf-8")
        print(f"result_file={args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
