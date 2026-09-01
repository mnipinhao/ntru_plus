#!/usr/bin/env python3
"""Build M5R-C from M5R-B by rewriting only the six level-1 B3 nodes."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "gt_forward_full_register_pass2_dag" / "gt864_forward_one_bank_full_register_pinned.sym.S"
BASELINE = ROOT / "baseline-region.S"
CANDIDATE = ROOT / "gt864_forward_one_bank_one_mul_b3.sym.S"
OLD_START = "gt864_forward_one_bank_full_register_pinned_slothy_start"
OLD_END = "gt864_forward_one_bank_full_register_pinned_slothy_end"
NEW_START = "gt864_forward_one_bank_one_mul_b3_slothy_start"
NEW_END = "gt864_forward_one_bank_one_mul_b3_slothy_end"


def instruction_count(text: str) -> int:
    return sum(bool(re.match(r"^\s{4}[a-z][a-z0-9]*\s", line))
               for line in text.splitlines())


def replace_b3(text: str, prefix: str, x0: str, x1: str, x2: str,
               y0: str, y1: str, y2: str) -> str:
    """Replace the exact 14-instruction two-product B3 with a 10-instruction B3."""
    names = {
        "p": re.escape(prefix), "x0": re.escape(x0), "x1": re.escape(x1),
        "x2": re.escape(x2), "y0": re.escape(y0), "y1": re.escape(y1),
        "y2": re.escape(y2),
    }
    pattern = re.compile(rf"""
\s+add\s+V<{names['p']}_sum01>\.8h,\s*V<{names['x0']}>\.8h,\s*V<{names['x1']}>\.8h
\s+add\s+V<{names['y0']}>\.8h,\s*V<{names['p']}_sum01>\.8h,\s*V<{names['x2']}>\.8h
\s+sqrdmulh\s+V<{names['p']}_qb>\.8h,\s*V<{names['x1']}>\.8h,\s*v15\.h\[1\]
\s+mul\s+V<{names['p']}_rb>\.8h,\s*V<{names['x1']}>\.8h,\s*v15\.h\[0\]
\s+mls\s+V<{names['p']}_rb>\.8h,\s*V<{names['p']}_qb>\.8h,\s*v14\.8h
\s+sqrdmulh\s+V<{names['p']}_qc>\.8h,\s*V<{names['x2']}>\.8h,\s*v15\.h\[3\]
\s+mul\s+V<{names['p']}_r2c>\.8h,\s*V<{names['x2']}>\.8h,\s*v15\.h\[2\]
\s+mls\s+V<{names['p']}_r2c>\.8h,\s*V<{names['p']}_qc>\.8h,\s*v14\.8h
\s+add\s+V<{names['p']}_weighted>\.8h,\s*V<{names['p']}_rb>\.8h,\s*V<{names['p']}_r2c>\.8h
\s+add\s+V<{names['y1']}>\.8h,\s*V<{names['p']}_weighted>\.8h,\s*V<{names['x0']}>\.8h
\s+sub\s+V<{names['p']}_p0>\.8h,\s*V<{names['x0']}>\.8h,\s*V<{names['y0']}>\.8h
\s+sub\s+V<{names['p']}_p1>\.8h,\s*V<{names['x0']}>\.8h,\s*V<{names['y1']}>\.8h
\s+add\s+V<{names['p']}_p2>\.8h,\s*V<{names['p']}_p0>\.8h,\s*V<{names['p']}_p1>\.8h
\s+add\s+V<{names['y2']}>\.8h,\s*V<{names['p']}_p2>\.8h,\s*V<{names['x0']}>\.8h
""", re.X)
    replacement = f"""
    add V<{prefix}_sum01>.8h, V<{x0}>.8h, V<{x1}>.8h
    add V<{y0}>.8h, V<{prefix}_sum01>.8h, V<{x2}>.8h
    sub V<{prefix}_diff>.8h, V<{x1}>.8h, V<{x2}>.8h
    sqrdmulh V<{prefix}_diff_q>.8h, V<{prefix}_diff>.8h, v15.h[1]
    mul V<{prefix}_rho_diff>.8h, V<{prefix}_diff>.8h, v15.h[0]
    mls V<{prefix}_rho_diff>.8h, V<{prefix}_diff_q>.8h, v14.8h
    sub V<{prefix}_y1_base>.8h, V<{x0}>.8h, V<{x2}>.8h
    add V<{y1}>.8h, V<{prefix}_y1_base>.8h, V<{prefix}_rho_diff>.8h
    sub V<{prefix}_y2_base>.8h, V<{x0}>.8h, V<{x1}>.8h
    sub V<{y2}>.8h, V<{prefix}_y2_base>.8h, V<{prefix}_rho_diff>.8h
"""
    text, count = pattern.subn(replacement, text, count=1)
    assert count == 1, prefix
    return text


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    start = text.index(OLD_START + ":")
    end = text.index(OLD_END + ":") + len(OLD_END) + 1
    baseline = text[start:end] + "\n"
    assert instruction_count(baseline) == 617
    BASELINE.write_text(baseline, encoding="utf-8")

    text = text.replace(OLD_START, NEW_START).replace(OLD_END, NEW_END)
    blocks = (
        ("a", "f0_raw", "f3", "f6", "a0", "a1", "a2"),
        ("b", "f1", "f4", "f7", "b0", "b1", "b2"),
        ("c", "f8", "f2", "f5", "c0_out", "c1_out", "c2_out"),
        ("second_a", "hold0", "h3", "h6", "second_a0", "second_a1", "second_a2"),
        ("second_b", "h1", "h4", "h7", "second_b0", "second_b1", "second_b2"),
        ("second_c", "h8", "h2", "h5", "second_c0", "second_c1", "second_c2"),
    )
    for args in blocks:
        text = replace_b3(text, *args)
    region = text[text.index(NEW_START + ":"):text.index(NEW_END + ":")]
    assert instruction_count(region) == 593
    CANDIDATE.write_text(text, encoding="utf-8")
    print("baseline_instructions=617")
    print("candidate_instructions=593")
    print("rewritten_level1_b3_per_bank=6")
    print("algorithm10_mulmods_deleted_per_ntt9_block=3")


if __name__ == "__main__":
    main()
