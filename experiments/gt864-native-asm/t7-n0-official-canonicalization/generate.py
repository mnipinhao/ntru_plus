#!/usr/bin/env python3
"""Generate isolated T7-N0 baseline extracts and symbolic candidates."""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTRACT = Path("/Users/chenpinhao/.codex/skills/slothy-symbolic-asm-authoring/scripts/extract-slothy-region.py")
SOURCES = [
    ("pair_full", HERE.parent / "tobytes_block/candidate.sym.S", "byte_pair_block_slothy_start", "byte_pair_block_slothy_end", "ac3eb29971e85e66d10c16d4ecc75d258f372088"),
    ("pair_small", HERE.parent / "tobytes_small/candidate.sym.S", "byte_pair_small_slothy_start", "byte_pair_small_slothy_end", "8cf0085c554ff179eb0fc712dd8f577ada8e46c0"),
    ("pair_merge_full", HERE.parent / "baseinv-tobytes-next-model/bytes-full/candidate.sym.S", "pair_merge_full_slothy_start", "pair_merge_full_slothy_end", "7b3f5c90093fe28843ab79a9835d0e76bdf77be6"),
    ("pair_merge_small", HERE.parent / "baseinv-tobytes-next-model/bytes-small/candidate.sym.S", "pair_merge_small_slothy_start", "pair_merge_small_slothy_end", "393d12def2ab4725d4c7b119218ba36dd21f8741"),
]

SIGN = re.compile(r"^(\s*)sshr V<([ab]sign[0-8])>\.8h, V<([ab]row[0-8])>\.8h, #15\s*$")


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def lower(text: str) -> tuple[str, int]:
    lines = text.splitlines()
    out: list[str] = []
    count = 0
    i = 0
    while i < len(lines):
        match = SIGN.match(lines[i])
        if match is None:
            out.append(lines[i])
            i += 1
            continue
        indent, sign, row = match.groups()
        expected_and = f"{indent}and V<{sign}>.16b, V<{sign}>.16b, V<q>.16b"
        expected_add = f"{indent}add V<{row}>.8h, V<{row}>.8h, V<{sign}>.8h"
        if i + 2 >= len(lines) or lines[i + 1] != expected_and or lines[i + 2] != expected_add:
            raise AssertionError(f"non-canonical correction sequence at {lines[i]!r}")
        out.append(f"{indent}cmlt V<{sign}>.8h, V<{row}>.8h, #0")
        out.append(f"{indent}mls V<{row}>.8h, V<{sign}>.8h, V<q>.8h")
        count += 1
        i += 3
    return "\n".join(out) + "\n", count


def main() -> None:
    baseline_dir = HERE / "build/baseline"
    candidate_dir = HERE / "build/candidate"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    candidate_dir.mkdir(parents=True, exist_ok=True)
    baseline_regions: list[str] = []
    candidate_functions: list[str] = []
    for name, source, start, end, expected_hash in SOURCES:
        actual_hash = git_blob(source)
        if actual_hash != expected_hash:
            raise SystemExit(f"{source}: baseline drift: expected {expected_hash}, got {actual_hash}")
        extracted = baseline_dir / f"{name}.region.S"
        subprocess.run(["python3", str(EXTRACT), str(source), "--start", start, "--end", end, "--output", str(extracted)], check=True)
        baseline_regions.append(extracted.read_text())
        candidate, lowered = lower(source.read_text())
        if lowered != 18:
            raise AssertionError(f"{name}: expected 18 canonicalization groups, got {lowered}")
        out_dir = candidate_dir / name
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "candidate.sym.S").write_text(candidate)
        candidate_functions.append(candidate)
    (baseline_dir / "baseline-regions.S").write_text("\n".join(baseline_regions))
    (candidate_dir / "candidate.sym.S").write_text("\n".join(candidate_functions))
    digest = hashlib.sha256((candidate_dir / "candidate.sym.S").read_bytes()).hexdigest()
    print(f"T7-N0 generated: 72 canonicalization groups lowered; candidate sha256={digest}")


if __name__ == "__main__":
    main()
