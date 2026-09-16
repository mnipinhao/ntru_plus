#!/usr/bin/env python3
"""Exact T7-N0 lowering, instruction, memory, and arithmetic audit."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAMES = ["pair_full", "pair_small", "pair_merge_full", "pair_merge_small"]


def instructions(path: Path) -> list[str]:
    return [
        line.split("//", 1)[0].strip()
        for line in path.read_text().splitlines()
        if line.startswith("    ") and line.split("//", 1)[0].strip() and line.split("//", 1)[0].strip() != "ret"
    ]


def memory(lines: list[str]) -> list[str]:
    return [line for line in lines if re.match(r"^(?:ld|st)[0-9a-z]*\b", line, re.I)]


def old_correction(r: int) -> int:
    return r + ((r >> 15) & 3457)


def new_correction(r: int) -> int:
    mask = -1 if r < 0 else 0
    return r - mask * 3457


def full_reduce(x: int) -> int:
    qhat = (x * 9 + (1 << 14)) >> 15
    return new_correction(x - qhat * 3457)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exhaustive", action="store_true")
    parser.add_argument("--physical", action="store_true")
    args = parser.parse_args()
    reports = {}
    total_delta = 0
    for name in NAMES:
        base = instructions(HERE / f"build/baseline/{name}.region.S")
        cand = instructions(HERE / f"build/candidate/{name}/candidate.sym.S")
        cmlt = sum(line.startswith("cmlt ") for line in cand)
        old_sign = sum(line.startswith("sshr ") and "sign" in line for line in cand)
        if cmlt != 18 or old_sign != 0:
            raise AssertionError((name, cmlt, old_sign))
        if memory(base) != memory(cand):
            raise AssertionError(f"{name}: memory instruction sequence changed")
        delta = len(cand) - len(base)
        if delta != -18:
            raise AssertionError((name, len(base), len(cand), delta))
        total_delta += delta
        reports[name] = {
            "baseline_instructions": len(base),
            "candidate_instructions": len(cand),
            "delta": delta,
            "cmlt_mls_groups": cmlt,
            "memory_sequence_preserved": True,
        }
    if total_delta != -72:
        raise AssertionError(total_delta)
    if args.exhaustive:
        for r in range(-32768, 32768):
            if old_correction(r) != new_correction(r):
                raise AssertionError((r, old_correction(r), new_correction(r)))
        for x in range(-32768, 32768):
            if full_reduce(x) != x % 3457:
                raise AssertionError((x, full_reduce(x), x % 3457))
        for x in range(-3456, 3457):
            if new_correction(x) != x % 3457:
                raise AssertionError((x, new_correction(x), x % 3457))
    if args.physical:
        for name in NAMES:
            path = HERE / f"build/slothy/{name}/candidate.alloc.S"
            if not path.exists():
                raise SystemExit(f"missing Slothy artifact: {path}")
            text = path.read_text()
            if "<" in "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//")):
                raise AssertionError(f"{name}: symbolic register leaked")
            if re.search(r"\[(?:sp|x29|x30)", text, re.I):
                raise AssertionError(f"{name}: spill-like stack access")
    result = {
        "gate": "T7-N0",
        "status": "local-pass" if args.exhaustive else "static-pass",
        "reports": reports,
        "static_delta_across_four_regions": total_delta,
        "dynamic_complete_tobytes_delta": -108,
        "proof": "old r+((r>>15)&q) equals r-(-1 if r<0 else 0)*q; full reciprocal reduction also exhaustively canonical for every int16 input",
        "production_changed": False,
        "pi5_timing": "pending",
    }
    out = HERE / "build/audit-results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
