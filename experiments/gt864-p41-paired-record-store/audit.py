#!/usr/bin/env python3
"""Static P41 candidate hard gates."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def instructions(path):
    result = []
    for raw in path.read_text().splitlines():
        code = raw.split("//", 1)[0].strip().lower()
        if code and not code.startswith((".", "#", "/*")) and not code.endswith(":"):
            result.append(code)
    return result


def main():
    report = {}
    for mode in ("full", "small"):
        path = HERE / f"candidate-{mode}.phys.S"
        values = instructions(path)
        counts = Counter(value.split()[0] for value in values)
        helper = path.read_text().split(f"p41_top_{mode}:", 1)[1].split(
            f"p41_pack_index_{mode}:", 1)[0]
        assert counts["stur"] == 81
        assert "mov x9" not in "\n".join(values)  # no packed vector-to-GPR transfer
        assert len(re.findall(r"(?m)^\s*stur q", helper)) == 27
        assert len(re.findall(r"(?m)^\s*stur s", helper)) == 27
        assert len(re.findall(r"(?m)^\s*stur d", helper)) == 27
        assert not re.search(r"\[(?:sp|x29)(?:,|\])", helper)
        text = path.read_text()
        helper_text = text.split(f"p41_top_{mode}:", 1)[1].split(
            f"p41_pack_index_{mode}:", 1)[0]
        helper_path = HERE / f".audit-{mode}-helper.tmp"
        helper_path.write_text(helper_text)
        helper_count = len(instructions(helper_path))
        helper_path.unlink()
        report[mode] = {"source": path.name, "static_source_instructions": len(values),
                        "complete_dynamic_instructions": len(values) + helper_count,
                        "counts": dict(sorted(counts.items()))}
    search = json.loads((HERE / "precedence-search-results.json").read_text())
    assert search["precedence_verified"]
    assert search["net_delta_vs_p24_complete_call"]["instructions"] < 0
    report["search"] = search["net_delta_vs_p24_complete_call"]
    (HERE / "static-results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
