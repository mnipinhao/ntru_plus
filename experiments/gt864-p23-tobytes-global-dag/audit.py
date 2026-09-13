#!/usr/bin/env python3
"""Static hard gates for generated and scheduled P23 assembly."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def instructions(path: Path):
    lines = []
    for raw in path.read_text().splitlines():
        code = raw.split("//", 1)[0].strip().lower()
        if code and not code.startswith((".", "#", "/*")) and not code.endswith(":"):
            lines.append(code)
    return lines


def audit(mode: str, suffix: str):
    path = HERE / f"candidate-{mode}.{suffix}.S"
    values = instructions(path)
    counts = Counter(value.split()[0] for value in values)
    static_expected = 1103 if mode == "full" else 993
    dynamic_expected = 2154 if mode == "full" else 1934
    assert len(values) == static_expected
    assert counts["ldr"] == 62  # one helper body: one index plus 61 coefficient loads
    assert counts["stur"] == 108
    assert counts["ext"] == 24
    assert counts["trn1"] + counts["trn2"] == 200
    text = path.read_text()
    helper = text.split(f"p23_top_{mode}:", 1)[1].split(
        f"p23_pack_index_{mode}:", 1)[0]
    assert not re.search(r"\[(?:sp|x29)(?:,|\])", helper)
    return {"path": path.name, "static_source_instructions": len(values),
            "complete_dynamic_instructions": dynamic_expected, "counts": dict(counts)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", choices=("phys", "opt", "g3.opt"), default="g3.opt")
    arguments = parser.parse_args()
    report = {mode: audit(mode, arguments.tag) for mode in ("full", "small")}
    (HERE / "static-results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
