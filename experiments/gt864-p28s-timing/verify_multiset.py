#!/usr/bin/env python3
"""Verify timing candidates retain the exact executable instruction multiset."""

from collections import Counter
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent


def instructions(path):
    result = []
    for raw in path.read_text().splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line or line.endswith(":") or line.startswith((".", "#")):
            continue
        # Slothy canonicalizes AArch64 arrangement suffixes (for example
        # ``.8h`` -> ``.8H``).  AArch64 assembly is case-insensitive, so fold
        # case before comparing the executable instruction multisets.
        line = re.sub(r"\s+", " ", line).lower()
        result.append(line)
    return Counter(result)


pairs = [
    ("baseline-main.alloc.S", "candidate-main.timing.S"),
    ("baseline-tail.alloc.S", "candidate-tail.timing.S"),
    ("baseline-route.windowed.S", "candidate-route.timing.S"),
]
for baseline, candidate in pairs:
    before, after = instructions(HERE / baseline), instructions(HERE / candidate)
    if before != after:
        print("removed", before - after)
        print("added", after - before)
        raise SystemExit(f"instruction multiset mismatch: {baseline} -> {candidate}")
    print(f"PASS {baseline} -> {candidate}: {sum(before.values())} instructions")
