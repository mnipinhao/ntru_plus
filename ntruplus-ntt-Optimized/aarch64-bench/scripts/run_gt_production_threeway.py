#!/usr/bin/env python3
"""Build and run the promoted/legacy/KPQC full-KEM comparison on Linux."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


VARIANTS = (
    "gt_production_default",
    "gt_production_legacy_ntt",
    "kpqc_final",
)
MODES = ("kem_keygen", "kem_enc", "kem_dec")
COUNTERS = {
    "cycles": "PERF",
    "instructions": "INSTRUCTIONS",
}
RUN_ORDERS = {
    ("cycles", "kem_keygen"): VARIANTS,
    ("cycles", "kem_enc"): (VARIANTS[1], VARIANTS[2], VARIANTS[0]),
    ("cycles", "kem_dec"): (VARIANTS[2], VARIANTS[0], VARIANTS[1]),
    ("instructions", "kem_keygen"): (VARIANTS[1], VARIANTS[0], VARIANTS[2]),
    ("instructions", "kem_enc"): (VARIANTS[2], VARIANTS[1], VARIANTS[0]),
    ("instructions", "kem_dec"): (VARIANTS[0], VARIANTS[2], VARIANTS[1]),
}
PERCENTILES = (1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99)


def run(command: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout


def parse_benchmark(output: str, counter: str) -> dict[str, Any]:
    median_match = re.search(rf"\s{re.escape(counter)} = (\d+)$", output, re.MULTILINE)
    percentile_match = re.search(r"percentiles:\s+([0-9 ]+)$", output, re.MULTILINE)
    if median_match is None or percentile_match is None:
        raise ValueError(f"unable to parse {counter} output")
    values = [int(value) for value in percentile_match.group(1).split()]
    if len(values) != len(PERCENTILES):
        raise ValueError(f"expected {len(PERCENTILES)} percentiles, got {len(values)}")
    percentile_values = dict(zip((str(value) for value in PERCENTILES), values))
    return {
        "median": int(median_match.group(1)),
        "percentiles": percentile_values,
        "p10": percentile_values["10"],
        "p50": percentile_values["50"],
        "p90": percentile_values["90"],
    }


def binary_metadata(binary: Path, cwd: Path) -> dict[str, Any]:
    size_output = run(["size", str(binary)], cwd)
    size_fields = size_output.splitlines()[-1].split()
    nm_output = run(["nm", "-S", "--defined-only", str(binary)], cwd)
    poly_ntt = None
    for line in nm_output.splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[3] in {"poly_ntt", "_poly_ntt"}:
            poly_ntt = {
                "symbol": fields[3],
                "address": int(fields[0], 16),
                "size": int(fields[1], 16),
                "address_mod32": int(fields[0], 16) % 32,
                "address_mod64": int(fields[0], 16) % 64,
            }
            if fields[3] == "poly_ntt":
                break
    return {
        "text": int(size_fields[0]),
        "data": int(size_fields[1]),
        "bss": int(size_fields[2]),
        "total": int(size_fields[3]),
        "poly_ntt": poly_ntt,
    }


def percent_delta(value: int, baseline: int) -> float:
    return 100.0 * (value - baseline) / baseline


def render_markdown(report: dict[str, Any]) -> str:
    rows = report["measurements"]
    lines = [
        "# GT Production Three-Way Full-KEM Benchmark",
        "",
        "Pi 5 Cortex-A76, core pinned, portable NO_CE hash path.",
        f"Each cell is the median of {report['settings']['ntests']} samples with "
        f"{report['settings']['niterations']} calls per sample.",
        "",
        "Variants:",
        "",
        "- new: promoted G1R123+S2 GT production",
        "- legacy: original GT production forward NTT",
        "- kpqc: unmodified KPQC final",
    ]
    for counter in COUNTERS:
        lines.extend(
            [
                "",
                f"## {counter.title()}",
                "",
                "| Operation | KPQC final | GT legacy | GT new | New vs KPQC | New vs legacy |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for mode in MODES:
            kpqc = rows[counter][mode]["kpqc_final"]["p50"]
            legacy = rows[counter][mode]["gt_production_legacy_ntt"]["p50"]
            new = rows[counter][mode]["gt_production_default"]["p50"]
            lines.append(
                f"| {mode} | {kpqc} | {legacy} | {new} | "
                f"{percent_delta(new, kpqc):+.3f}% | {percent_delta(new, legacy):+.3f}% |"
            )

    lines.extend(
        [
            "",
            "## Cycle Distributions",
            "",
            "| Operation | Variant | p10 | p50 | p90 |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for mode in MODES:
        for variant in VARIANTS:
            row = rows["cycles"][mode][variant]
            lines.append(
                f"| {mode} | {variant} | {row['p10']} | {row['p50']} | {row['p90']} |"
            )

    lines.extend(
        [
            "",
            "## Binary Metadata",
            "",
            "| Variant | Text bytes | poly_ntt bytes | poly_ntt mod32/mod64 |",
            "|---|---:|---:|---:|",
        ]
    )
    for variant in VARIANTS:
        metadata = report["binaries"][variant]
        symbol = metadata["poly_ntt"] or {}
        lines.append(
            f"| {variant} | {metadata['text']} | {symbol.get('size', 'n/a')} | "
            f"{symbol.get('address_mod32', 'n/a')}/{symbol.get('address_mod64', 'n/a')} |"
        )
    lines.extend(
        [
            "",
            "All runs completed the harness setup KEM correctness check before measurement.",
            "Keypair is reported but G1R123+S2 is not expected to improve it because the GT "
            "keypair path uses the specialized triple NTT.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--core", type=int, default=3)
    parser.add_argument("--ntests", type=int, default=61)
    parser.add_argument("--niterations", type=int, default=2000)
    parser.add_argument("--nwarmup", type=int, default=100)
    parser.add_argument("--keep-binaries", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output = args.output if args.output.is_absolute() else root / args.output
    output.mkdir(parents=True, exist_ok=True)
    (output / "bin").mkdir(exist_ok=True)
    (output / "raw").mkdir(exist_ok=True)

    measurements: dict[str, dict[str, dict[str, Any]]] = {
        counter: {mode: {} for mode in MODES} for counter in COUNTERS
    }
    binaries: dict[str, dict[str, Any]] = {}
    build_log = []

    for counter, make_counter in COUNTERS.items():
        for mode in MODES:
            built: dict[str, Path] = {}
            for variant in VARIANTS:
                binary = output / "bin" / f"{variant}_{mode}_{counter}"
                command = [
                    "make",
                    "-B",
                    str(binary),
                    f"TARGET={binary}",
                    f"VARIANT={variant}",
                    f"BENCH_MODE={mode}",
                    f"CYCLES={make_counter}",
                    f"NTESTS={args.ntests}",
                    f"NITERATIONS={args.niterations}",
                    f"NWARMUP={args.nwarmup}",
                ]
                build_log.append(f"$ {' '.join(command)}\n")
                build_log.append(run(command, root))
                built[variant] = binary
                if counter == "cycles" and mode == "kem_enc":
                    binaries[variant] = binary_metadata(binary, root)

            for variant in RUN_ORDERS[(counter, mode)]:
                raw = run(["taskset", "-c", str(args.core), str(built[variant])], root)
                raw_path = output / "raw" / f"{variant}_{mode}_{counter}.out"
                raw_path.write_text(raw)
                measurements[counter][mode][variant] = parse_benchmark(raw, counter)

    report = {
        "settings": {
            "host": "Pi5 Cortex-A76",
            "core": args.core,
            "ntests": args.ntests,
            "niterations": args.niterations,
            "nwarmup": args.nwarmup,
            "hash_path": "NO_CE",
            "deterministic_inputs": True,
            "run_orders": {
                f"{counter}/{mode}": list(order)
                for (counter, mode), order in RUN_ORDERS.items()
            },
        },
        "measurements": measurements,
        "binaries": binaries,
    }
    (output / "build.log").write_text("".join(build_log))
    (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    (output / "summary.md").write_text(render_markdown(report))
    if not args.keep_binaries:
        shutil.rmtree(output / "bin")
    print(output / "summary.json")
    print(output / "summary.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
