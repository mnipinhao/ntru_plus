#!/usr/bin/env python3
"""Build and run a GT-Optimized paired full-KEM benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import statistics
import subprocess
from pathlib import Path
from typing import Any


MODES = ("keygen", "encap", "decap")
VARIANTS = ("baseline", "gt")
ORDERS = (("baseline", "gt"), ("gt", "baseline"))


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout


def hash_tree(root: Path) -> str:
    digest = hashlib.sha256()
    suffixes = {".c", ".h", ".s", ".S"}

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name != "Makefile" and path.suffix not in suffixes:
            continue
        relative = path.relative_to(root).as_posix().encode()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(path.read_bytes())
    return digest.hexdigest()


def parse_output(output: str) -> dict[str, Any]:
    fields: dict[str, str] = {}

    for line in output.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key] = value
    samples = [int(value) for value in fields["samples"].split(",")]
    return {
        "variant": fields["variant"],
        "mode": fields["mode"],
        "samples": samples,
        "sink": fields["sink"],
    }


def percentile(values: list[int], percent: int) -> int:
    ordered = sorted(values)
    return ordered[len(ordered) * percent // 100]


def summarize(values: list[int]) -> dict[str, Any]:
    return {
        "count": len(values),
        "min": min(values),
        "p10": percentile(values, 10),
        "p50": int(statistics.median(values)),
        "p90": percentile(values, 90),
        "max": max(values),
    }


def render_markdown(report: dict[str, Any]) -> str:
    baseline_label = report["baseline"]["label"]
    gt_label = report["gt"]["label"]
    lines = [
        f"# {gt_label} versus {baseline_label}",
        "",
        f"- Host: `{report['environment']['uname']}`",
        f"- Compiler: `{report['environment']['compiler']}`",
        f"- CPU core: `{report['configuration']['core']}`",
        f"- Samples per variant: `{report['configuration']['combined_samples']}`",
        f"- Operations per sample: `{report['configuration']['iterations']}`",
        "",
        f"| Operation | {baseline_label} p10/p50/p90 | "
        f"{gt_label} p10/p50/p90 | Reduction |",
        "|---|---:|---:|---:|",
    ]
    for mode in MODES:
        baseline = report["results"][mode]["baseline"]
        gt = report["results"][mode]["gt"]
        reduction = (
            100.0
            * (baseline["p50"] - gt["p50"])
            / baseline["p50"]
        )
        lines.append(
            f"| {mode} | "
            f"{baseline['p10']}/{baseline['p50']}/{baseline['p90']} | "
            f"{gt['p10']}/{gt['p50']}/{gt['p90']} | {reduction:.2f}% |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    baseline_group = parser.add_mutually_exclusive_group(required=True)
    baseline_group.add_argument("--baseline-root", type=Path)
    baseline_group.add_argument(
        "--kpqc-root",
        dest="baseline_root",
        type=Path,
        help="legacy alias for --baseline-root",
    )
    parser.add_argument("--baseline-label", default="Baseline")
    parser.add_argument(
        "--baseline-supercop-flat",
        action="store_true",
        help=(
            "build the generated SUPERCOP flat aarch64 source shape "
            "(kem.c plus lower-case .s files) without modifying that tree"
        ),
    )
    parser.add_argument("--gt-root", type=Path)
    parser.add_argument("--gt-overlay-root", type=Path)
    parser.add_argument("--gt-label", default="GT-Optimized")
    parser.add_argument("--core", default="3")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tests", type=int, default=31)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--warmups", type=int, default=100)
    args = parser.parse_args()
    baseline_id = re.sub(
        r"[^a-z0-9]+", "-", args.baseline_label.lower()
    ).strip("-")
    if not baseline_id:
        parser.error("--baseline-label must contain a letter or digit")

    root = Path(__file__).resolve().parent
    if args.gt_root is None:
        gt_root = (
            root
            / "../../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768"
        ).resolve()
    else:
        gt_root = args.gt_root.resolve()
    gt_overlay_root = (
        args.gt_overlay_root.resolve()
        if args.gt_overlay_root is not None
        else None
    )
    baseline_root = args.baseline_root.resolve()
    output = args.output.resolve()
    raw = output / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    make_args = [
        "make",
        "clean",
        "all",
        f"GT_ROOT={gt_root}",
        f"GT_VARIANT_STR={args.gt_label}",
        f"BASELINE_ROOT={baseline_root}",
        f"BASELINE_VARIANT_STR={baseline_id}",
        f"NTESTS={args.tests}",
        f"NITERATIONS={args.iterations}",
        f"NWARMUP={args.warmups}",
    ]
    if gt_overlay_root is not None:
        make_args.append(f"GT_OVERLAY_ROOT={gt_overlay_root}")
    if args.baseline_supercop_flat:
        make_args.append("BASELINE_SUPERCOP_FLAT=1")
    build_output = run(make_args, root, env)
    (raw / "build.log").write_text(build_output)

    collected: dict[str, dict[str, list[int]]] = {
        mode: {variant: [] for variant in VARIANTS} for mode in MODES
    }
    invocation = 0
    for mode in MODES:
        for order in ORDERS:
            for variant in order:
                binary = root / "build" / f"{variant}-{mode}"
                command = ["taskset", "-c", args.core, str(binary)]
                output_text = run(command, root, env)
                (raw / f"{invocation:02d}-{mode}-{variant}.log").write_text(
                    output_text
                )
                parsed = parse_output(output_text)
                collected[mode][variant].extend(parsed["samples"])
                invocation += 1

    compiler = run([env.get("CC", "cc"), "--version"], root).splitlines()[0]
    report: dict[str, Any] = {
        "environment": {
            "uname": platform.platform(),
            "compiler": compiler,
        },
        "configuration": {
            "core": args.core,
            "tests_per_invocation": args.tests,
            "combined_samples": args.tests * len(ORDERS),
            "iterations": args.iterations,
            "warmups": args.warmups,
            "orders": [list(order) for order in ORDERS],
        },
        "baseline": {
            "label": args.baseline_label,
            "variant": baseline_id,
            "internal_variant_key": "baseline",
            "root": str(baseline_root),
        },
        "gt": {
            "label": args.gt_label,
            "root": str(gt_root),
            "overlay_root": (
                str(gt_overlay_root)
                if gt_overlay_root is not None
                else None
            ),
        },
        "source_hashes": {
            "gt_optimized": hash_tree(gt_root),
            "gt_overlay": (
                hash_tree(gt_overlay_root)
                if gt_overlay_root is not None
                else None
            ),
            "baseline": hash_tree(baseline_root),
        },
        "results": {
            mode: {
                variant: summarize(collected[mode][variant])
                for variant in VARIANTS
            }
            for mode in MODES
        },
    }
    (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    (output / "summary.md").write_text(render_markdown(report))
    print(render_markdown(report))


if __name__ == "__main__":
    main()
