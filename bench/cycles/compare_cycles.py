#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


METRICS = [
    "poly_cbd1",
    "poly_sotp_encode",
    "poly_sotp_decode",
    "poly_ntt",
    "poly_baseinv",
    "keygen",
    "encap",
    "decap",
]


def speedup_and_gain(baseline_mean: float, optimized_mean: float) -> tuple[float, float]:
    if optimized_mean == 0:
        return 0.0, 0.0
    speedup = baseline_mean / optimized_mean
    gain = ((baseline_mean - optimized_mean) / baseline_mean) * 100.0 if baseline_mean != 0 else 0.0
    return speedup, gain


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare baseline and optimized cycle benchmark outputs.")
    parser.add_argument("--baseline", required=True, help="Path to baseline JSON benchmark output")
    parser.add_argument("--optimized", required=True, help="Path to optimized JSON benchmark output")
    parser.add_argument("--output-json", required=True, help="Path to write comparison JSON")
    parser.add_argument("--output-md", required=True, help="Path to write summary markdown")
    parser.add_argument("--tag", required=True, help="Run tag for report metadata")
    args = parser.parse_args()

    baseline = json.loads(Path(args.baseline).read_text())
    optimized = json.loads(Path(args.optimized).read_text())

    if baseline.get("unit") != optimized.get("unit"):
        raise SystemExit("Unit mismatch between baseline and optimized benchmark outputs")

    unit = baseline["unit"]
    comparison = {}
    for metric in METRICS:
        b_mean = float(baseline["results"][metric]["mean"])
        o_mean = float(optimized["results"][metric]["mean"])
        speedup, gain = speedup_and_gain(b_mean, o_mean)
        comparison[metric] = {
            "baseline_mean": b_mean,
            "optimized_mean": o_mean,
            "unit": unit,
            "speedup": speedup,
            "improvement_pct": gain,
            "baseline_median": float(baseline["results"][metric]["median"]),
            "optimized_median": float(optimized["results"][metric]["median"]),
        }

    output = {
        "tag": args.tag,
        "unit": unit,
        "iterations": baseline["iterations"],
        "warmup": baseline["warmup"],
        "comparison": comparison,
    }

    output_json_path = Path(args.output_json)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(json.dumps(output, indent=2) + "\n")

    lines = [
        "# NTRU+ Baseline vs Optimized Cycle Comparison",
        "",
        f"- Run tag: `{args.tag}`",
        f"- Unit: `{unit}`",
        f"- Iterations: `{baseline['iterations']}`",
        f"- Warmup: `{baseline['warmup']}`",
        "",
        "| Metric | Baseline mean | Optimized mean | Speedup | Improvement |",
        "|---|---:|---:|---:|---:|",
    ]

    for metric in METRICS:
        row = comparison[metric]
        lines.append(
            f"| `{metric}` | {row['baseline_mean']:.3f} | {row['optimized_mean']:.3f} | "
            f"{row['speedup']:.3f}x | {row['improvement_pct']:.2f}% |"
        )

    kem_metrics = ["keygen", "encap", "decap"]
    baseline_total = sum(comparison[m]["baseline_mean"] for m in kem_metrics)
    optimized_total = sum(comparison[m]["optimized_mean"] for m in kem_metrics)
    overall_speedup, overall_gain = speedup_and_gain(baseline_total, optimized_total)

    lines.extend(
        [
            "",
            "## KEM Aggregate",
            "",
            f"- Baseline total mean: `{baseline_total:.3f} {unit}`",
            f"- Optimized total mean: `{optimized_total:.3f} {unit}`",
            f"- Overall speedup: `{overall_speedup:.3f}x`",
            f"- Overall improvement: `{overall_gain:.2f}%`",
            "",
        ]
    )

    output_md_path = Path(args.output_md)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.write_text("\n".join(lines))

    print(f"Comparison JSON: {output_json_path}")
    print(f"Summary markdown: {output_md_path}")
    print(f"KEM overall speedup: {overall_speedup:.3f}x ({overall_gain:.2f}% improvement)")


if __name__ == "__main__":
    main()
