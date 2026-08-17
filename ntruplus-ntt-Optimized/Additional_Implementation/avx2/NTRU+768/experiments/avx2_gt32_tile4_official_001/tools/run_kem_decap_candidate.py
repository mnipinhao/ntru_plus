#!/usr/bin/env python3
"""Summarize the short same-binary Official/GT32 decapsulation gate."""

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
    args = parser.parse_args()
    process = subprocess.run(
        [str(args.binary), str(args.iterations)],
        check=True,
        text=True,
        capture_output=True,
    )
    records = []
    metadata = []
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            metadata.append(line)
        elif fields[0] == "SAMPLE":
            records.append({
                "sample": int(fields[1]),
                "official_tsc": float(fields[2]),
                "gt32_sa_tsc": float(fields[3]),
                "gt32_soa_domain_tsc": float(fields[4]),
                "sa_delta_tsc": float(fields[5]),
                "soa_domain_delta_tsc": float(fields[6]),
                "gt32_soa_domain_zeroinit_tsc": float(fields[7]),
                "noinit_delta_vs_zeroinit_tsc": float(fields[8]),
                "gt32_soa_domain_direct_tsc": float(fields[9]),
                "direct_delta_vs_indirect_tsc": float(fields[10]),
            })
    if len(records) != 20:
        raise RuntimeError("benchmark did not emit 20 paired samples")
    official = [record["official_tsc"] for record in records]
    sa = [record["gt32_sa_tsc"] for record in records]
    soa_domain = [record["gt32_soa_domain_tsc"] for record in records]
    sa_deltas = [record["sa_delta_tsc"] for record in records]
    soa_domain_deltas = [record["soa_domain_delta_tsc"] for record in records]
    soa_vs_sa = [record["gt32_soa_domain_tsc"] - record["gt32_sa_tsc"]
                 for record in records]
    zeroinit = [record["gt32_soa_domain_zeroinit_tsc"]
                for record in records]
    noinit_vs_zeroinit = [record["noinit_delta_vs_zeroinit_tsc"]
                          for record in records]
    direct = [record["gt32_soa_domain_direct_tsc"]
                for record in records]
    direct_vs_indirect = [record["direct_delta_vs_indirect_tsc"]
                          for record in records]
    sa_delta_median = statistics.median(sa_deltas)
    soa_delta_median = statistics.median(soa_domain_deltas)
    soa_vs_sa_median = statistics.median(soa_vs_sa)
    noinit_vs_zeroinit_median = statistics.median(noinit_vs_zeroinit)
    direct_vs_indirect_median = statistics.median(direct_vs_indirect)
    result = {
        "scope": "same-binary valid crypto_kem_dec",
        "unit": "TSC ticks per decapsulation",
        "mode": "short-only-not-promotion",
        "iterations_per_sample": args.iterations,
        "samples": len(records),
        "metadata": metadata,
        "official_median": statistics.median(official),
        "gt32_sa_median": statistics.median(sa),
        "gt32_soa_domain_median": statistics.median(soa_domain),
        "gt32_soa_domain_zeroinit_median": statistics.median(zeroinit),
        "gt32_soa_domain_direct_median": statistics.median(direct),
        "sa_delta_vs_official_median": sa_delta_median,
        "sa_delta_vs_official_mad": statistics.median(
            abs(delta - sa_delta_median) for delta in sa_deltas),
        "soa_domain_delta_vs_official_median": soa_delta_median,
        "soa_domain_delta_vs_official_mad": statistics.median(
            abs(delta - soa_delta_median) for delta in soa_domain_deltas),
        "soa_domain_delta_vs_sa_median": soa_vs_sa_median,
        "soa_domain_delta_vs_sa_mad": statistics.median(
            abs(delta - soa_vs_sa_median) for delta in soa_vs_sa),
        "sa_wins_vs_official": sum(delta < 0.0 for delta in sa_deltas),
        "soa_domain_wins_vs_official": sum(
            delta < 0.0 for delta in soa_domain_deltas),
        "soa_domain_wins_vs_sa": sum(delta < 0.0 for delta in soa_vs_sa),
        "noinit_delta_vs_zeroinit_median": noinit_vs_zeroinit_median,
        "noinit_delta_vs_zeroinit_mad": statistics.median(
            abs(delta - noinit_vs_zeroinit_median)
            for delta in noinit_vs_zeroinit),
        "noinit_wins_vs_zeroinit": sum(
            delta < 0.0 for delta in noinit_vs_zeroinit),
        "direct_delta_vs_indirect_median": direct_vs_indirect_median,
        "direct_delta_vs_indirect_mad": statistics.median(
            abs(delta - direct_vs_indirect_median)
            for delta in direct_vs_indirect),
        "direct_wins_vs_indirect": sum(
            delta < 0.0 for delta in direct_vs_indirect),
        "decision": (
            "soa-domain-short-positive-vs-sa"
            if soa_vs_sa_median < 0.0 else "soa-domain-short-negative-vs-sa"
        ),
        "raw": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in (
        "official_median", "gt32_sa_median", "gt32_soa_domain_median",
        "sa_delta_vs_official_median", "soa_domain_delta_vs_official_median",
        "soa_domain_delta_vs_sa_median", "soa_domain_wins_vs_sa",
        "noinit_delta_vs_zeroinit_median", "noinit_wins_vs_zeroinit",
        "direct_delta_vs_indirect_median", "direct_wins_vs_indirect",
        "decision"
    )}, indent=2))


if __name__ == "__main__":
    main()
