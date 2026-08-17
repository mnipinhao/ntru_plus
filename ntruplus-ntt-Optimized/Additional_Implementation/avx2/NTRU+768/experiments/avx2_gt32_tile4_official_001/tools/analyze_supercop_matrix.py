#!/usr/bin/env python3
"""Aggregate forced-compiler SUPERCOP results with stabilized quartiles."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


OPS = ("keypair", "enc", "dec")


def stabilized_quartiles(values: list[int]) -> list[float]:
    if not values:
        raise ValueError("empty measurement list")
    expanded = sorted(value for value in values for _ in range(8))
    n = len(values)
    return [
        sum(expanded[n + 2 * n * index : n + 2 * n * (index + 1)]) / (2 * n)
        for index in range(3)
    ]


def decode_measurement(line: str) -> list[int]:
    fields = line.split()
    base = int(fields[-2])
    deviations = [int(item) for item in re.findall(r"[+-]\d+", fields[-1])]
    return [base + deviation for deviation in deviations]


def parse_result(result_dir: Path) -> dict[str, object]:
    data = (result_dir / "data").read_text().splitlines()
    compiler_lines = [line for line in data if " compiler " in line]
    if not compiler_lines:
        raise ValueError(f"no compiler line in {result_dir}")
    compiler = compiler_lines[-1].split(" compiler ", 1)[1].split()[0]
    measurements: dict[str, list[int]] = {op: [] for op in OPS}
    for line in data:
        for op in OPS:
            if f" {op}_cycles " in line:
                measurements[op].extend(decode_measurement(line))
    if any(not measurements[op] for op in OPS):
        raise ValueError(f"incomplete cycle data in {result_dir}")
    return {"compiler": compiler, "measurements": measurements}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dirs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    cells: dict[str, dict[str, object]] = {}
    for result_dir in args.result_dirs:
        parsed = parse_result(result_dir)
        implementation = result_dir.name.split("-2026", 1)[0].removeprefix("ntruplus768-")
        compiler = str(parsed["compiler"])
        optimization = "O3" if "_-O3_" in compiler else "O2" if "_-O2_" in compiler else compiler
        key = f"{implementation}:{optimization}"
        cell = cells.setdefault(
            key,
            {
                "implementation": implementation,
                "optimization": optimization,
                "compiler": compiler,
                "result_dirs": [],
                "measurements": {op: [] for op in OPS},
            },
        )
        cell["result_dirs"].append(str(result_dir))
        for op in OPS:
            cell["measurements"][op].extend(parsed["measurements"][op])

    for cell in cells.values():
        summaries = {}
        for op in OPS:
            values = cell["measurements"].pop(op)
            quartiles = stabilized_quartiles(values)
            summaries[op] = {
                "observations": len(values),
                "stabilized_quartiles": quartiles,
                "q2_cycles": quartiles[1],
            }
        cell["operations"] = summaries

    output = {
        "schema": "ntruplus768-supercop-cross-compiler-v1",
        "estimator": "SUPERcop stabilized quartiles; Q2 primary",
        "cells": cells,
    }
    encoded = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()
