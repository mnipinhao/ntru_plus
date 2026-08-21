#!/usr/bin/env python3
"""Record balanced LBR traces from the frozen 043 production ELFs."""

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def launch(binary: Path, cpu: int, output: Path, period: int) -> None:
    command = [
        "perf", "record", "-q", "-o", str(output),
        "-e", "cpu_core/cycles/u", "-c", str(period),
        "-j", "any_call,any_ret", "--",
        "taskset", "-c", str(cpu), str(binary),
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official", type=Path, required=True)
    parser.add_argument("--gt", type=Path, required=True)
    parser.add_argument("--blocks", type=int, default=32)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--period", type=int, default=50000)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    binaries = {
        "official": args.official.resolve(),
        "gt": args.gt.resolve(),
    }
    for path in binaries.values():
        if not path.is_file():
            raise SystemExit(f"missing frozen binary: {path}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for _ in range(args.warmup):
        for binary in binaries.values():
            subprocess.run(
                ["taskset", "-c", str(args.cpu), str(binary)],
                stdout=subprocess.DEVNULL, check=True,
            )

    rows = []
    for block in range(args.blocks):
        order = ("official", "gt") if block % 2 == 0 else ("gt", "official")
        for implementation in order:
            output = args.output_dir / f"{block + 1:03d}-{implementation}.data"
            launch(binaries[implementation], args.cpu, output, args.period)
            rows.append({
                "block": block + 1,
                "order": order.index(implementation),
                "implementation": implementation,
                "perf_data": output.name,
            })

    manifest = {
        "schema": "gt32-exact-elf-dynamic-map-055-record-v1",
        "cpu": args.cpu,
        "blocks": args.blocks,
        "period": args.period,
        "branch_filter": "any_call,any_ret",
        "binaries": {
            name: {"path": str(path), "sha256": sha256(path)}
            for name, path in binaries.items()
        },
        "rows": rows,
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    print(json.dumps(manifest["binaries"], indent=2))


if __name__ == "__main__":
    main()

