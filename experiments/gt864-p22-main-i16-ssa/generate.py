#!/usr/bin/env python3
"""Generate P22 two-output SSA butterflies from the P13-B symbolic DAG."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "experiments/gt864-p13b-inverse16-arithmetic/candidate.sym.S"
OUTPUT = HERE / "candidate.sym.S"

TOKEN = re.compile(r"([QV])<([A-Za-z0-9_]+)>")
COPY = re.compile(
    r"orr\s+V<([^>]+)>\.16b,\s*V<([^>]+)>\.16b,\s*V<\2>\.16b$",
    re.IGNORECASE,
)
ADD = re.compile(
    r"add\s+V<([^>]+)>\.8h,\s*V<([^>]+)>\.8h,\s*V<([^>]+)>\.8h$",
    re.IGNORECASE,
)
SUB = re.compile(
    r"sub\s+V<([^>]+)>\.8h,\s*V<([^>]+)>\.8h,\s*V<([^>]+)>\.8h$",
    re.IGNORECASE,
)


def instructions(path: Path) -> list[str]:
    lines = path.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "p13b_i16_slothy_start:") + 1
    end = next(i for i, line in enumerate(lines[start:], start)
               if line.strip() == "p13b_i16_slothy_end:")
    return [line.strip() for line in lines[start:end] if line.strip()]


def mapped(line: str, current: dict[str, str]) -> str:
    return TOKEN.sub(lambda m: f"{m[1]}<{current.get(m[2], m[2])}>", line)


def main() -> None:
    source = instructions(SOURCE)
    out: list[str] = []
    current: dict[str, str] = {}
    butterflies = 0
    i = 0
    while i < len(source):
        if i + 2 < len(source):
            copy = COPY.fullmatch(source[i])
            add = ADD.fullmatch(source[i + 1])
            sub = SUB.fullmatch(source[i + 2])
            if copy and add and sub:
                temp, left = copy.groups()
                add_dst, add_left, right = add.groups()
                sub_dst, sub_left, sub_right = sub.groups()
                if (add_dst, add_left, sub_dst, sub_left, sub_right) != (
                        left, left, right, temp, right):
                    raise RuntimeError(f"non-butterfly copy triple at {i}")
                old_left = current.get(left, left)
                old_right = current.get(right, right)
                sum_name = f"bf{butterflies}_sum"
                diff_name = f"bf{butterflies}_diff"
                out.append(f"add V<{sum_name}>.8h, V<{old_left}>.8h, V<{old_right}>.8h")
                out.append(f"sub V<{diff_name}>.8h, V<{old_left}>.8h, V<{old_right}>.8h")
                current[left] = sum_name
                current[right] = diff_name
                butterflies += 1
                i += 3
                continue
        out.append(mapped(source[i], current))
        i += 1

    if butterflies != 32:
        raise RuntimeError(f"expected 32 butterflies, found {butterflies}")
    if any(line.lower().startswith("orr ") for line in out):
        raise RuntimeError("unexpected ORR remains")
    if len(source) != 667 or len(out) != 635:
        raise RuntimeError(f"instruction count mismatch {len(source)} -> {len(out)}")

    header = [
        "#ifdef __APPLE__", "#define p22_i16 _p22_i16", "#endif", ".text",
        ".global p22_i16", "p22_i16:",
        "// live-in: x0 output, x1 packed scratch, x3 stage table, x4 P13-B composite table",
        "// live-out: exact baseline natural-order int16 stores at x0",
        "// unchanged range: input abs<=2617, I16 abs<=21397, output abs<=4454",
        "// reserved physical registers: x18-x30 and sp; no vector register is fixed",
        "p22_i16_slothy_start:",
    ]
    text = "\n".join(header + ["    " + line for line in out] +
                     ["p22_i16_slothy_end:", "    ret", ""])
    OUTPUT.write_text(text)
    report = {
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "candidate_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        "baseline_region_instructions": len(source),
        "candidate_region_instructions": len(out),
        "butterflies_rewritten": butterflies,
        "deleted_orr": butterflies,
        "arithmetic_reduction_load_store_delta": 0,
    }
    (HERE / "generation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
