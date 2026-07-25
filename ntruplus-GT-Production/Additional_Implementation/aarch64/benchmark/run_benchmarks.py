#!/usr/bin/env python3
"""Build and run the GT-Optimized versus KPQC-final full-KEM benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import statistics
import subprocess
from pathlib import Path
from typing import Any


MODES = ("keygen", "encap", "decap")
VARIANTS = ("kpqc", "gt")
ORDERS = (("kpqc", "gt"), ("gt", "kpqc"))


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
    lines = [
        "# GT-Optimized versus KPQC Final",
        "",
        f"- Host: `{report['environment']['uname']}`",
        f"- Compiler: `{report['environment']['compiler']}`",
        f"- CPU core: `{report['configuration']['core']}`",
        f"- Samples per variant: `{report['configuration']['combined_samples']}`",
        f"- Operations per sample: `{report['configuration']['iterations']}`",
        "",
        "| Operation | KPQC p10/p50/p90 | GT p10/p50/p90 | Reduction |",
        "|---|---:|---:|---:|",
    ]
    for mode in MODES:
        kpqc = report["results"][mode]["kpqc"]
        gt = report["results"][mode]["gt"]
        reduction = 100.0 * (kpqc["p50"] - gt["p50"]) / kpqc["p50"]
        lines.append(
            f"| {mode} | {kpqc['p10']}/{kpqc['p50']}/{kpqc['p90']} | "
            f"{gt['p10']}/{gt['p50']}/{gt['p90']} | {reduction:.2f}% |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kpqc-root", type=Path, required=True)
    parser.add_argument("--core", default="3")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tests", type=int, default=31)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--warmups", type=int, default=100)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    gt_root = (root / "../NTRU+768").resolve()
    kpqc_root = args.kpqc_root.resolve()
    output = args.output.resolve()
    raw = output / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    make_args = [
        "make",
        "clean",
        "all",
        f"GT_ROOT={gt_root}",
        f"KPQC_ROOT={kpqc_root}",
        f"NTESTS={args.tests}",
        f"NITERATIONS={args.iterations}",
        f"NWARMUP={args.warmups}",
    ]
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
        "source_hashes": {
            "gt_optimized": hash_tree(gt_root),
            "kpqc_final": hash_tree(kpqc_root),
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
