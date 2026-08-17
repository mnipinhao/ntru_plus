#!/usr/bin/env python3
"""Summarize direct native-cost attribution for the GT32 decap gap."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--full-result", type=Path)
    args = parser.parse_args()
    process = subprocess.run(
        [str(args.binary), str(args.iterations)], check=True, text=True,
        capture_output=True)
    records: dict[str, list[dict[str, float]]] = {}
    metadata = []
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            metadata.append(line)
        elif fields[0] == "SAMPLE":
            records.setdefault(fields[1], []).append({
                "sample": int(fields[2]),
                "official": float(fields[3]),
                "gt32": float(fields[4]),
                "delta": float(fields[5]),
            })
    phases = {}
    reconstructed_gap = 0.0
    for name, values in records.items():
        if len(values) != 20:
            raise RuntimeError(f"{name} emitted {len(values)} samples")
        official = [value["official"] for value in values]
        gt32 = [value["gt32"] for value in values]
        deltas = [value["delta"] for value in values]
        delta = statistics.median(deltas)
        if not name.startswith("control_"):
            reconstructed_gap += delta
        phases[name] = {
            "official_median": statistics.median(official),
            "gt32_median": statistics.median(gt32),
            "paired_delta_median": delta,
            "paired_delta_mad": statistics.median(
                abs(value - delta) for value in deltas),
            "gt32_wins": sum(value < 0.0 for value in deltas),
            "samples": len(values),
            "raw": values,
        }
    result = {
        "scope": "direct native phase-cost attribution for valid decapsulation",
        "unit": "TSC ticks per phase call",
        "mode": "short-only",
        "iterations_per_sample": args.iterations,
        "metadata": metadata,
        "phases": phases,
        "reconstructed_differential_sum": reconstructed_gap,
        "closure_note": (
            "Direct costs exclude cross-phase cache/code-placement effects; "
            "sub uses the shared Official elementwise kernel on both layouts."
        ),
    }
    if args.full_result and args.full_result.exists():
        full = json.loads(args.full_result.read_text())
        measured = float(full["soa_domain_delta_vs_official_median"])
        error = reconstructed_gap - measured
        result["full_decap_soa_domain_gap"] = measured
        result["closure_error"] = error
        result["closure_error_fraction"] = abs(error) / abs(measured)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "phase_deltas": {
            name: phase["paired_delta_median"]
            for name, phase in phases.items()
        },
        "reconstructed_differential_sum": reconstructed_gap,
        "full_decap_soa_domain_gap": result.get(
            "full_decap_soa_domain_gap"),
        "closure_error_fraction": result.get("closure_error_fraction"),
    }, indent=2))


if __name__ == "__main__":
    main()
