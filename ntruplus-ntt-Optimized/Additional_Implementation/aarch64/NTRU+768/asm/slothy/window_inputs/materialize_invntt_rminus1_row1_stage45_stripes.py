#!/usr/bin/env python3
"""Materialize and check InvNTT rminus1 row1 stage45 stripe-pair windows.

This is a benchmark-only Slothy input helper.  It does not modify production
assembly and it does not run Slothy.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SLOTHY_DIR = SCRIPT_DIR.parent
PRODUCTION = SLOTHY_DIR / "invntt_opt.production.s"
OUTPUT = SCRIPT_DIR / "invntt_rminus1_row1_stage45_stripes_marked.s"

PARENT_START = "slothy_start_invntt_block_row1_stage45"
PARENT_END = "slothy_end_invntt_block_row1_stage45"
CHILD_START = "slothy_start_invntt_rm1_row1_stage45_stripes2_3"
CHILD_END = "slothy_end_invntt_rm1_row1_stage45_stripes2_3"

STRIPE_MACRO = "INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH"
PARENT_MACRO = "RUN_INVNTT32_STAGE45_SCRATCH_ROW"


def strip_block_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def extract_macro(text: str, name: str) -> list[str]:
    lines = text.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if re.match(rf"\s*\.macro\s+{re.escape(name)}(?:\s|$)", line):
            start = idx + 1
            break
    if start is None:
        raise SystemExit(f"missing macro: {name}")

    for idx in range(start, len(lines)):
        if re.match(r"\s*\.endm\s*$", lines[idx]):
            return lines[start:idx]

    raise SystemExit(f"unterminated macro: {name}")


def split_code_lines(lines: list[str]) -> list[str]:
    text = strip_block_comments("\n".join(lines))
    result: list[str] = []
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line:
            continue
        if line.startswith("."):
            continue
        if line.endswith(":"):
            continue
        result.append(line)
    return result


def eval_immediate_expression(expr: str, stripe: int) -> int:
    expr = expr.replace(r"\j", str(stripe))
    if not re.fullmatch(r"[0-9+\-*/() \t]+", expr):
        raise SystemExit(f"unsafe immediate expression after substitution: {expr!r}")
    return int(eval(expr, {"__builtins__": {}}, {}))


def replace_balanced_immediates(line: str, stripe: int) -> str:
    out: list[str] = []
    i = 0
    while i < len(line):
        if line.startswith("#(", i):
            depth = 1
            j = i + 2
            while j < len(line) and depth:
                if line[j] == "(":
                    depth += 1
                elif line[j] == ")":
                    depth -= 1
                j += 1
            if depth:
                raise SystemExit(f"unbalanced immediate expression: {line}")
            value = eval_immediate_expression(line[i + 2 : j - 1], stripe)
            out.append(f"#{value}")
            i = j
            continue
        out.append(line[i])
        i += 1
    return "".join(out).replace(r"\j", str(stripe))


def expand_stripe(stripe_macro_lines: list[str], stripe: int) -> list[str]:
    expanded: list[str] = []
    for line in split_code_lines(stripe_macro_lines):
        expanded.append(replace_balanced_immediates(line, stripe))
    return expanded


def normalize_instruction(line: str) -> str:
    line = line.split("//", 1)[0].strip()
    line = re.sub(r"\s+", " ", line)
    line = re.sub(r"\s*,\s*", ", ", line)
    return line.lower()


def instruction_count(lines: list[str]) -> int:
    return len(split_code_lines(lines))


def extract_between_labels(text: str, start_label: str, end_label: str) -> list[str]:
    start = None
    selected: list[str] = []
    for line in text.splitlines():
        if line.strip() == f"{start_label}:":
            start = True
            continue
        if line.strip() == f"{end_label}:":
            if start is None:
                raise SystemExit(f"end label before start label: {end_label}")
            return selected
        if start:
            selected.append(line)
    raise SystemExit(f"missing label pair: {start_label} / {end_label}")


def source_header() -> str:
    return """/*
 * Benchmark-only Slothy input for InvNTT rminus1 row1 stage45 stripe-pair
 * windows.  This file is generated from INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH
 * in asm/slothy/invntt_opt.production.s by
 * window_inputs/materialize_invntt_rminus1_row1_stage45_stripes.py.
 *
 * It is not included by production wrappers and must not replace
 * poly_invntt_from_rminus1.  The production row-level macro is already
 * cross-stripe scheduled, so this file materializes exact canonical
 * per-stripe windows for Slothy input labels without using the 337-instruction
 * parent row labels as a substitute.
 *
 * Region contract for each stripe-pair:
 *   live-in:  x14 = stage123 stripe scratch base
 *             x2  = row1 row-buffer output base
 *             x3  = invntt32_stage45_consts base
 *             v0  = q / Barrett constants
 *   live-out: memory side effects only, row-buffer q-stores at [x2,#offset]
 *   pointer mutation: none
 */

.text
.align 2
.global invntt_rminus1_row1_stage45_stripes_marked_slothy_input
.type invntt_rminus1_row1_stage45_stripes_marked_slothy_input, %function
invntt_rminus1_row1_stage45_stripes_marked_slothy_input:
"""


def materialize_source(stripe_macro_lines: list[str]) -> str:
    pairs = [(0, 1), (2, 3), (4, 5), (6, 7)]
    output: list[str] = [source_header().rstrip()]
    for lo, hi in pairs:
        output.append("")
        output.append(f"slothy_start_invntt_rm1_row1_stage45_stripes{lo}_{hi}:")
        for stripe in (lo, hi):
            output.append(f"    /* stripe {stripe} */")
            for inst in expand_stripe(stripe_macro_lines, stripe):
                output.append(f"    {inst}")
        output.append(f"slothy_end_invntt_rm1_row1_stage45_stripes{lo}_{hi}:")
    output.extend(
        [
            "",
            "    ret",
            ".size invntt_rminus1_row1_stage45_stripes_marked_slothy_input, .-invntt_rminus1_row1_stage45_stripes_marked_slothy_input",
            "",
        ]
    )
    return "\n".join(output)


def verify(marked_source: str, production_text: str) -> tuple[int, int, bool]:
    parent_count = instruction_count(extract_macro(production_text, PARENT_MACRO))
    child_lines = split_code_lines(
        extract_between_labels(marked_source, CHILD_START, CHILD_END)
    )
    child_count = len(child_lines)

    stripe_macro_lines = extract_macro(production_text, STRIPE_MACRO)
    expected = expand_stripe(stripe_macro_lines, 2) + expand_stripe(stripe_macro_lines, 3)
    equivalent = [normalize_instruction(x) for x in child_lines] == [
        normalize_instruction(x) for x in expected
    ]
    return parent_count, child_count, equivalent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the marked source")
    args = parser.parse_args()

    production_text = PRODUCTION.read_text()
    stripe_macro_lines = extract_macro(production_text, STRIPE_MACRO)
    marked_source = materialize_source(stripe_macro_lines)

    if args.write:
        OUTPUT.write_text(marked_source)

    source_to_check = OUTPUT.read_text() if OUTPUT.exists() else marked_source
    parent_count, child_count, equivalent = verify(source_to_check, production_text)

    print(f"parent_window,start={PARENT_START},end={PARENT_END}")
    print(f"child_window,start={CHILD_START},end={CHILD_END}")
    print(f"parent_instruction_count={parent_count}")
    print(f"child_instruction_count={child_count}")
    print(
        "equivalence_check="
        + ("pass" if equivalent else "fail")
        + " (child equals canonical production per-stripe macro expansion)"
    )
    print(
        "contiguous_parent_slice_check=not_applicable "
        "(production parent row is cross-stripe scheduled)"
    )

    if parent_count != 337:
        raise SystemExit(f"unexpected parent instruction count: {parent_count}")
    if child_count != 84:
        raise SystemExit(f"unexpected child instruction count: {child_count}")
    if not equivalent:
        raise SystemExit("marked child source does not match canonical macro expansion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
