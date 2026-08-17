#!/usr/bin/env python3
"""Run and summarize the corrected-semantic Decodeq short gate."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def median_mad(values: list[float]) -> tuple[float, float]:
    median = statistics.median(values)
    mad = statistics.median(abs(value - median) for value in values)
    return median, mad


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
    decoder: list[dict[str, float]] = []
    decoder3: list[dict[str, float]] = []
    island: list[dict[str, float]] = []
    metadata: list[str] = []
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            metadata.append(line)
        elif fields[:2] == ["SAMPLE", "decoder"]:
            decoder.append({
                "sample": int(fields[2]),
                "official": float(fields[3]),
                "aos": float(fields[4]),
                "soa": float(fields[5]),
            })
        elif fields[:2] == ["SAMPLE", "decoder3"]:
            decoder3.append({
                "sample": int(fields[2]),
                "separate": float(fields[3]),
                "combined": float(fields[4]),
                "delta": float(fields[5]),
            })
        elif fields[:2] == ["SAMPLE", "island"]:
            island.append({
                "sample": int(fields[2]),
                "aa": float(fields[3]),
                "sa_f": float(fields[4]),
                "sa_c": float(fields[5]),
                "ss": float(fields[6]),
                "ss_preserve_c": float(fields[7]),
            })

    if len(decoder) != 20 or len(decoder3) != 20 or len(island) != 20:
        raise RuntimeError("benchmark did not emit 20 paired samples per gate")

    decoder_summary: dict[str, object] = {}
    for name in ("official", "aos", "soa"):
        values = [record[name] for record in decoder]
        median, mad = median_mad(values)
        decoder_summary[name] = {"median": median, "mad": mad}
    for candidate, baseline in (("aos", "official"), ("soa", "official"),
                                ("soa", "aos")):
        deltas = [record[candidate] - record[baseline]
                  for record in decoder]
        median, mad = median_mad(deltas)
        decoder_summary[f"{candidate}_vs_{baseline}"] = {
            "paired_delta_median": median,
            "paired_delta_mad": mad,
            "candidate_wins": sum(delta < 0.0 for delta in deltas),
            "samples": len(deltas),
        }

    decoder3_deltas = [record["delta"] for record in decoder3]
    decoder3_delta_median, decoder3_delta_mad = median_mad(decoder3_deltas)
    decoder3_summary = {
        "separate_median": statistics.median(
            record["separate"] for record in decoder3),
        "combined_median": statistics.median(
            record["combined"] for record in decoder3),
        "paired_delta_median": decoder3_delta_median,
        "paired_delta_mad": decoder3_delta_mad,
        "combined_wins": sum(delta < 0.0 for delta in decoder3_deltas),
        "samples": len(decoder3_deltas),
        "note": (
            "Three corrected-semantic SoA decodes share mask setup, "
            "error accumulation, and the AVX/SSE transition."
        ),
    }

    island_summary: dict[str, object] = {}
    for name in ("aa", "sa_f", "sa_c", "ss", "ss_preserve_c"):
        values = [record[name] for record in island]
        median, mad = median_mad(values)
        entry: dict[str, object] = {"median": median, "mad": mad}
        if name != "aa":
            deltas = [record[name] - record["aa"] for record in island]
            delta_median, delta_mad = median_mad(deltas)
            entry.update({
                "paired_delta_vs_aa_median": delta_median,
                "paired_delta_vs_aa_mad": delta_mad,
                "wins_vs_aa": sum(delta < 0.0 for delta in deltas),
                "samples": len(deltas),
            })
        island_summary[name] = entry

    isolated_champion = min(
        ("aa", "sa_f", "sa_c", "ss"),
        key=lambda name: statistics.median(
            record[name] for record in island),
    )
    realistic_champion = min(
        ("aa", "sa_f", "ss_preserve_c"),
        key=lambda name: statistics.median(
            record[name] for record in island),
    )
    realistic_entry = island_summary[realistic_champion]
    if realistic_champion == "aa":
        decision = "stop-decoder-layout-no-real-decap-saving"
    else:
        saving = -float(realistic_entry["paired_delta_vs_aa_median"])
        wins = int(realistic_entry["wins_vs_aa"])
        if saving >= 10.0 and wins >= 18:
            decision = f"short-pass-integrate-{realistic_champion}"
        elif saving > 0.0:
            decision = f"inconclusive-short-{realistic_champion}"
        else:
            decision = "stop-decoder-layout-no-real-decap-saving"

    result = {
        "scope": "correct-semantic Decodeq layout and private decap.m1 island",
        "mapping": (
            "serialized slot -> Official index[192] leaf -> "
            "GT(branch,k3,k32) -> Q=brv5(k32)"
        ),
        "unit": "TSC ticks per call",
        "mode": "short-only",
        "iterations_per_sample": args.iterations,
        "samples": 20,
        "metadata": metadata,
        "decoder": decoder_summary,
        "decoder3_boundary": decoder3_summary,
        "island": island_summary,
        "selection": {
            "isolated_champion": isolated_champion,
            "real_decap_dag_champion": realistic_champion,
            "decision": decision,
            "note": (
                "SS must preserve c in AoS for the later c-m edge; "
                "ss_preserve_c includes that third decode."
            ),
        },
        "raw": {"decoder": decoder, "decoder3": decoder3,
                "island": island},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "decoder_medians": {
            name: decoder_summary[name]["median"]
            for name in ("official", "aos", "soa")
        },
        "decoder3_boundary": decoder3_summary,
        "island_medians": {
            name: island_summary[name]["median"]
            for name in ("aa", "sa_f", "sa_c", "ss", "ss_preserve_c")
        },
        "selection": result["selection"],
    }, indent=2))


if __name__ == "__main__":
    main()
