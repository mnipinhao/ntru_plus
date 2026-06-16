#!/usr/bin/env python3
"""Gate 9 checker for the rowpack Forward v3b stage345 contract.

The checker is deliberately dependency-free so it can run on the Pi5 build
tree.  It validates the contract scaffold and, once a candidate exists, rejects
the store forms that Gate 6 and Gate 8 ruled out.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_CONTRACT_SNIPPETS = [
    "mode: new_symbolic_kernel",
    "candidate_status: investigate",
    "gt_rowpack_forward_v3b_stage345_liveout",
    "aarch64_neon",
    "cortex_a76",
    "instruction-dag.yml",
    "plain vector stores only",
    "st4",
    "lane_store",
    "scalar_scatter",
    "rowpack_index(branch,row,lane,k32)",
    "make test_gt_rowpack_forward_v3b_stage345_contract",
]

REQUIRED_DAG_SNIPPETS = [
    "stage3_layout_seed",
    "stage4_grouped_butterflies",
    "stage5_plane_liveout_reduce",
    "plain_vector_store_planes",
    "rowpack_plane_vectors",
    "no st4, lane store, or scalar scatter",
]

REQUIRED_LAYOUT_SEARCH_FILES = [
    "current_liveout.json",
    "target_rowpack_planes.json",
    "required_permutation.json",
    "candidate_sequences.json",
    "layout_search_summary.md",
]

FORBIDDEN_CANDIDATE_PATTERNS = [
    ("st4 structured store", re.compile(r"\bst4\b", re.IGNORECASE)),
    ("st1 lane store", re.compile(r"\bst1\s+\{[^}]*\}\s*\[\d+\]", re.IGNORECASE)),
    ("scalar halfword store", re.compile(r"\b(?:str|stur)\s+h\d+\b|\bstrh\b", re.IGNORECASE)),
]


def strip_asm_comment(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith(("//", "/*", "*", "#")):
        return ""
    for marker in ("//", "/*"):
        if marker in line:
            line = line.split(marker, 1)[0]
    return line.strip()


def require_file(path: Path) -> list[str]:
    if path.is_file():
        return []
    return [f"{path}: missing required file"]


def require_snippets(path: Path, snippets: list[str]) -> list[str]:
    errors = require_file(path)
    if errors:
        return errors
    text = path.read_text(errors="replace")
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{path}: missing required snippet: {snippet}")
    return errors


def check_layout_search_dir(path: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_LAYOUT_SEARCH_FILES:
        errors.extend(require_file(path / name))
    return errors


def check_candidate(path: Path, allow_missing: bool) -> list[str]:
    if not path.exists():
        if allow_missing:
            print(f"{path}: candidate not present; contract-only gate")
            return []
        return [f"{path}: candidate file is required"]

    errors: list[str] = []
    for lineno, raw in enumerate(path.read_text(errors="replace").splitlines(), 1):
        line = strip_asm_comment(raw)
        if not line:
            continue
        for label, pattern in FORBIDDEN_CANDIDATE_PATTERNS:
            if pattern.search(line):
                errors.append(f"{path}:{lineno}: forbidden {label}: {line}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--dag", required=True, type=Path)
    parser.add_argument("--layout-search-dir", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--allow-missing-candidate", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    errors.extend(require_snippets(args.contract, REQUIRED_CONTRACT_SNIPPETS))
    errors.extend(require_snippets(args.dag, REQUIRED_DAG_SNIPPETS))
    errors.extend(check_layout_search_dir(args.layout_search_dir))
    errors.extend(check_candidate(args.candidate, args.allow_missing_candidate))

    if errors:
        for error in errors:
            print(error)
        print(f"forward-v3b-stage345-check: failed with {len(errors)} error(s)")
        return 1

    print("forward-v3b-stage345-check: contract scaffold passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
