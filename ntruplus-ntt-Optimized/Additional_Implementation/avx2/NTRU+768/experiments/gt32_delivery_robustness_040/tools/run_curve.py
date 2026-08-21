#!/usr/bin/env python3
"""Measure cycles as a function of deterministic linked layout."""

from __future__ import annotations

import hashlib
import json
import pathlib
import platform
import re
import statistics
import subprocess

EXP = pathlib.Path(__file__).resolve().parents[1]
BUILD = EXP / "build"
RESULTS = EXP / "results"
OPERATIONS = ("keypair_cycles", "enc_cycles", "dec_cycles")


def observations(text: str, operation: str) -> list[int]:
    values = []
    for line in text.splitlines():
        if f" {operation} " not in f" {line} ":
            continue
        encoded = re.findall(r"[+-]?\d+", line.split(operation, 1)[1])
        if len(encoded) >= 2:
            center = int(encoded[0])
            values.extend(center + int(delta) for delta in encoded[1:])
    return values


def launch(binary: pathlib.Path, aslr_off: bool) -> str:
    command = ["taskset", "-c", "1"]
    if aslr_off:
        command += ["setarch", platform.machine(), "-R"]
    command.append(str(binary.resolve()))
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError(" ".join(command) + "\n" + completed.stdout + completed.stderr)
    return completed.stdout


def addresses(binary: pathlib.Path) -> dict[str, str]:
    wanted = {
        "poly_ntt", "crypto_kem_keypair", "crypto_kem_enc", "crypto_kem_dec",
        "ntruplus768_ntt_frontend_avx2", "ntruplus768_ntt_m_avx2",
        "ntruplus768_basemul_scale_m_avx2", "ntruplus768_invntt_m_avx2",
        "ntruplus768_invntt_tail_avx2", "ntruplus768_pack_m_lazy10788_avx2",
    }
    result = {}
    for line in subprocess.check_output(["nm", "-an", str(binary)], text=True).splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[-1] in wanted:
            result[fields[-1]] = fields[0]
    return result


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    launches = 10
    records = []
    binaries = {"official": {}, "gt": {}}
    for binary in sorted(BUILD.glob("*-measure")):
        match = re.fullmatch(r"(official|gt)-pad-([0-9a-f]{4})-measure", binary.name)
        if match:
            family, encoded = match.groups()
            binaries[family][int(encoded, 16)] = binary
    for family in ("official", "gt"):
        offsets = sorted(binaries[family])
        for aslr_off in (False, True):
            setting = "aslr-off" if aslr_off else "aslr-on"
            family_records = {
                offset: {
                    "family": family,
                    "offset": offset,
                    "setting": setting,
                    "binary": str(binaries[family][offset].resolve()),
                    "sha256": hashlib.sha256(binaries[family][offset].read_bytes()).hexdigest(),
                    "addresses": addresses(binaries[family][offset]),
                    "launch_medians": {operation: [] for operation in OPERATIONS},
                    "launch_slots": [],
                }
                for offset in offsets
            }
            # Latin rotation balances every offset across launch slots. Odd
            # blocks reverse the rotation to limit monotonic drift.
            for block in range(launches):
                rotated = offsets[block % len(offsets):] + offsets[:block % len(offsets)]
                if block & 1:
                    rotated.reverse()
                for slot, offset in enumerate(rotated):
                    output = launch(binaries[family][offset], aslr_off)
                    record = family_records[offset]
                    record["launch_slots"].append({"block": block, "slot": slot})
                    for operation in OPERATIONS:
                        values = observations(output, operation)
                        if len(values) < 96:
                            raise RuntimeError(f"too few {operation}: {len(values)}")
                        record["launch_medians"][operation].append(statistics.median(values))
            for record in family_records.values():
                record["median_cycles"] = {
                    operation: statistics.median(values)
                    for operation, values in record["launch_medians"].items()
                }
                records.append(record)

    summary = {}
    for family in ("official", "gt"):
        summary[family] = {}
        for setting in ("aslr-on", "aslr-off"):
            selected = [r for r in records if r["family"] == family and r["setting"] == setting]
            operation_summary = {}
            for operation in OPERATIONS:
                points = [
                    {"offset": r["offset"], "cycles": r["median_cycles"][operation]}
                    for r in sorted(selected, key=lambda value: value["offset"])
                ]
                cycle_values = [point["cycles"] for point in points]
                operation_summary[operation] = {
                    "points": points,
                    "range_cycles": max(cycle_values) - min(cycle_values),
                    "standard_deviation_cycles": statistics.pstdev(cycle_values),
                }
            summary[family][setting] = operation_summary
    result = {"launches_per_layout_setting": launches, "records": records, "summary": summary}
    (RESULTS / "layout_sensitivity_curve.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
