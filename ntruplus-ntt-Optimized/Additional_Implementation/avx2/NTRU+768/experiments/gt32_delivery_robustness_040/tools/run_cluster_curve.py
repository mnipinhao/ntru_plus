#!/usr/bin/env python3
"""Balanced ASLR-off causal curves for individually moved GT hot clusters."""

from __future__ import annotations

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
    result = []
    for line in text.splitlines():
        if f" {operation} " not in f" {line} ":
            continue
        encoded = re.findall(r"[+-]?\d+", line.split(operation, 1)[1])
        if len(encoded) >= 2:
            center = int(encoded[0])
            result.extend(center + int(delta) for delta in encoded[1:])
    return result


def launch(binary: pathlib.Path) -> dict[str, float]:
    command = ["taskset", "-c", "1", "setarch", platform.machine(), "-R",
               str(binary.resolve())]
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError(" ".join(command) + "\n" + completed.stdout + completed.stderr)
    result = {}
    for operation in OPERATIONS:
        values = observations(completed.stdout, operation)
        if len(values) < 96:
            raise RuntimeError(f"too few {operation}: {len(values)}")
        result[operation] = statistics.median(values)
    return result


def addresses(binary: pathlib.Path) -> dict[str, int]:
    wanted = {
        "ntruplus768_unpack_m_body_avx2", "ntruplus768_unpack3_m_avx2",
        "ntruplus768_unpack_m_avx2",
        "ntruplus768_ntt_frontend_avx2", "ntruplus768_ntt_m_avx2",
        "ntruplus768_basemul_scale_m_avx2", "ntruplus768_basemul_general_m_avx2",
        "ntruplus768_invntt_m_avx2", "ntruplus768_invntt_tail_avx2",
        "ntruplus768_pack_m_centered_avx2",
        "ntruplus768_pack_m_lazy10788_avx2",
        "ntruplus768_pack_m_highrange12699_avx2",
    }
    result = {}
    output = subprocess.check_output(["nm", "-an", str(binary)], text=True)
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[-1] in wanted:
            result[fields[-1]] = int(fields[0], 16)
    return result


def main() -> None:
    pattern = re.compile(r"cluster-(.+)-pad-([0-9a-f]{4})-measure$")
    binaries = {}
    for binary in BUILD.glob("cluster-*-measure"):
        match = pattern.fullmatch(binary.name)
        if match:
            cluster, encoded = match.groups()
            binaries.setdefault(cluster, {})[int(encoded, 16)] = binary
    blocks = 48
    records = []
    for cluster, variants in sorted(binaries.items()):
        offsets = sorted(variants)
        samples = {offset: {operation: [] for operation in OPERATIONS} for offset in offsets}
        slots = {offset: [] for offset in offsets}
        for block in range(blocks):
            order = offsets[block % len(offsets):] + offsets[:block % len(offsets)]
            if block & 1:
                order.reverse()
            for slot, offset in enumerate(order):
                measured = launch(variants[offset])
                slots[offset].append({"block": block, "slot": slot})
                for operation, value in measured.items():
                    samples[offset][operation].append(value)
        points = []
        for offset in offsets:
            points.append({
                "offset": offset,
                "binary": str(variants[offset].resolve()),
                "addresses": addresses(variants[offset]),
                "slots": slots[offset],
                "launch_medians": samples[offset],
                "median_cycles": {
                    operation: statistics.median(values)
                    for operation, values in samples[offset].items()
                },
            })
        records.append({"cluster": cluster, "points": points})
    summary = {}
    for record in records:
        summary[record["cluster"]] = {}
        for operation in OPERATIONS:
            values = [point["median_cycles"][operation] for point in record["points"]]
            summary[record["cluster"]][operation] = {
                "range_cycles": max(values) - min(values),
                "points": [
                    {"offset": point["offset"], "cycles": point["median_cycles"][operation]}
                    for point in record["points"]
                ],
            }
    result = {"blocks": blocks, "records": records, "summary": summary}
    (RESULTS / "cluster_sensitivity_curve.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
