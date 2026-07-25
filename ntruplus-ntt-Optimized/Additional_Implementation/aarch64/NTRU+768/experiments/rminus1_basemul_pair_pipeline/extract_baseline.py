#!/usr/bin/env python3
"""Extract the production rminus1 basemul loop and materialize two iterations."""

from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "asm/gt/basemul/poly_basemul_body.inc"
OUTPUT = HERE / "baseline-region.S"


def expand_load4(line: str) -> str:
    match = re.search(
        r"GT_LOAD4_BLOCK\((\d+), (\d+), (\d+), (\d+), (x\d+),.*\)",
        line,
    )
    if match is None:
        return line
    d0, d1, d2, d3, ptr = match.groups()
    return (
        f"ld4 {{v{d0}.8H, v{d1}.8H, v{d2}.8H, v{d3}.8H}}, "
        f"[{ptr}], #64"
    )


def extract_body() -> list[str]:
    lines = SOURCE.read_text(encoding="ascii").splitlines()
    start = lines.index("Lgt_basemul_loop:") + 1
    end = next(
        i for i in range(start, len(lines))
        if lines[i].strip() == "subs counter, counter, #1"
    )
    body = []
    mnemonics = {
        "ld1", "ld4", "mls", "mul", "smull", "smull2", "smlal", "smlal2",
        "st4", "uzp1", "uzp2",
    }
    active_stack = [True]
    for line in lines[start:end]:
        directive = line.strip()
        if directive == "#ifdef GT_BASEMUL_STORE_RMINUS1":
            active_stack.append(active_stack[-1])
            continue
        if directive == "#ifndef GT_BASEMUL_STORE_RMINUS1":
            active_stack.append(False)
            continue
        if directive == "#else" and len(active_stack) > 1:
            active_stack[-1] = active_stack[-2] and not active_stack[-1]
            continue
        if directive == "#endif" and len(active_stack) > 1:
            active_stack.pop()
            continue
        if not active_stack[-1]:
            continue
        code = line.split("//", 1)[0].strip()
        if not code:
            continue
        if not (
            code.startswith("GT_LOAD4_BLOCK(")
            or code.split(None, 1)[0].lower() in mnemonics
        ):
            continue
        body.append(expand_load4(code))
    if len(body) != 77:
        raise SystemExit(f"unexpected production loop body size: {len(body)}")
    return body


def main() -> None:
    body = extract_body()
    out = [
        "// Synthetic two-dynamic-iteration baseline extracted from production.",
        "rminus1_pair_baseline_start:",
        *[f"    {line}" for line in body],
        *[f"    {line}" for line in body],
        "rminus1_pair_baseline_end:",
        "",
    ]
    OUTPUT.write_text("\n".join(out), encoding="ascii")
    print(f"baseline_instruction_count={2 * len(body)}")
    print(f"output={OUTPUT}")


if __name__ == "__main__":
    main()
