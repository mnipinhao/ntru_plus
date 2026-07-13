#!/usr/bin/env python3
"""Audit production NTT32 stage12 stores against stage345 loads.

This intentionally checks the current assembly text instead of relying only on
the design notes.  The contract under audit is one row of _gt_ntt32_batch8_to_blockmajor:

  stage12 stripe s stores Q[s], Q[s+8], Q[s+16], Q[s+24]
  stage345 block b loads Q[8*b .. 8*b+7]

All offsets are relative to x4 = row_base.
"""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
ASM = ROOT / "asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S"

LABEL_STAGE12_START = re.compile(r"^_gt_ntt32_batch8_ct_stage12_stripe(\d+)_slothy_start:$")
LABEL_STAGE12_END = re.compile(r"^_gt_ntt32_batch8_ct_stage12_stripe(\d+)_slothy_end:$")
LABEL_STAGE345_START = re.compile(r"^_gt_ntt32_batch8_ct_stage345_block(\d+)_slothy_start:$")
LABEL_STAGE345_END = re.compile(r"^_gt_ntt32_batch8_ct_stage345_block(\d+)_slothy_end:$")
STR_X4 = re.compile(r"\bstr\s+q\d+,\s*\[x4,\s*#(\d+)\]")
LDR_X4 = re.compile(r"\bldr\s+q\d+,\s*\[x4,\s*#(\d+)\]")


def qname(offset: int) -> str:
    return f"Q{offset // 16}"


def fmt_offsets(offsets: list[int]) -> str:
    return ", ".join(f"{qname(o)}@{o}" for o in offsets)


def main() -> int:
    stage12: dict[int, list[int]] = {i: [] for i in range(8)}
    stage345: dict[int, list[int]] = {i: [] for i in range(4)}

    current: tuple[str, int] | None = None

    for raw_line in ASM.read_text().splitlines():
        line = raw_line.split("//", 1)[0].strip()
        if not line:
            continue

        if m := LABEL_STAGE12_START.match(line):
            current = ("stage12", int(m.group(1)))
            continue
        if LABEL_STAGE12_END.match(line) and current and current[0] == "stage12":
            current = None
            continue
        if m := LABEL_STAGE345_START.match(line):
            current = ("stage345", int(m.group(1)))
            continue
        if LABEL_STAGE345_END.match(line) and current and current[0] == "stage345":
            current = None
            continue

        if current is None:
            continue

        kind, index = current
        if kind == "stage12" and (m := STR_X4.search(line)):
            stage12[index].append(int(m.group(1)))
        elif kind == "stage345" and (m := LDR_X4.search(line)):
            stage345[index].append(int(m.group(1)))

    errors: list[str] = []

    print(f"asm: {ASM}")
    print()
    print("stage12 stores by stripe:")
    for stripe in range(8):
        expected = [16 * (stripe + 8 * k) for k in range(4)]
        actual = stage12[stripe]
        print(f"  stripe{stripe}: actual-order {fmt_offsets(actual)}")
        if sorted(actual) != expected:
            errors.append(
                f"stage12 stripe{stripe}: expected {expected}, got {sorted(actual)}"
            )

    print()
    print("stage345 loads by block:")
    stage12_by_block: dict[int, list[int]] = {i: [] for i in range(4)}
    for offsets in stage12.values():
        for offset in offsets:
            stage12_by_block[offset // 128].append(offset)

    for block in range(4):
        expected = [16 * q for q in range(8 * block, 8 * block + 8)]
        actual_loads = stage345[block]
        actual_stores = sorted(stage12_by_block[block])
        print(f"  block{block}: load-order  {fmt_offsets(actual_loads)}")
        print(f"          store-set   {fmt_offsets(actual_stores)}")
        if sorted(actual_loads) != expected:
            errors.append(
                f"stage345 block{block}: expected loads {expected}, "
                f"got {sorted(actual_loads)}"
            )
        if actual_stores != expected:
            errors.append(
                f"stage12 block{block}: expected stores {expected}, "
                f"got {actual_stores}"
            )
        if sorted(actual_loads) != actual_stores:
            errors.append(
                f"block{block}: stage12 store set does not match stage345 load set"
            )

    print()
    if errors:
        print("stage12_to_stage345_layout_FAIL")
        for error in errors:
            print(f"  {error}")
        return 1

    print("stage12_to_stage345_layout_ok")
    print(
        "conclusion: production stage12 already stores row-major Q0..Q31, "
        "and stage345 consumes the same memory as four Q blocks."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
