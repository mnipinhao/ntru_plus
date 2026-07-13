#!/usr/bin/env python3
"""Derive the Stage12-out0 -> Stage345-block0 live-in contract.

This audits the current production Stage345 block0 load order.  The goal is to
make the next experimental cut explicit:

  replace the eight row_base loads for Q0..Q7 with live vectors produced by
  Stage12 stripes0..7 out0.

No candidate assembly is emitted here.
"""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
ASM = ROOT / "asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S"

START = "_gt_ntt32_batch8_ct_stage345_block0_slothy_start:"
END = "_gt_ntt32_batch8_ct_stage345_block0_slothy_end:"
LOAD_RE = re.compile(r"\bldr\s+q(\d+),\s*\[x4,\s*#(\d+)\]")

SLICE_FAMILY_BY_STRIPE = {
    0: "even U01",
    1: "even U01",
    2: "even U23",
    3: "even U23",
    4: "odd U01",
    5: "odd U01",
    6: "odd U23",
    7: "odd U23",
}


def block0_loads() -> list[tuple[int, str, int, int]]:
    loads: list[tuple[int, str, int, int]] = []
    inside = False
    for lineno, raw in enumerate(ASM.read_text().splitlines(), start=1):
        line = raw.split("//", 1)[0].strip()
        if line == START:
            inside = True
            continue
        if line == END:
            break
        if not inside:
            continue
        match = LOAD_RE.search(line)
        if not match:
            continue
        reg = f"q{match.group(1)}"
        offset = int(match.group(2))
        q_index = offset // 16
        loads.append((lineno, reg, offset, q_index))
    return loads


def main() -> int:
    loads = block0_loads()
    errors: list[str] = []
    q_set = sorted(q for _, _, _, q in loads)
    if q_set != list(range(8)):
        errors.append(f"expected block0 Q0..Q7 load set, got {q_set}")

    print("stage345_block0_livein_contract")
    print(f"asm: {ASM}")
    print()
    print("current production block0 row_base loads:")
    for ordinal, (lineno, reg, offset, q_index) in enumerate(loads, start=1):
        stripe = q_index
        print(
            f"  load{ordinal}: line {lineno}: {reg} <- [x4, #{offset}] "
            f"= Q{q_index}; producer = stage12 stripe{stripe} out0 "
            f"({SLICE_FAMILY_BY_STRIPE[stripe]})"
        )

    print()
    print("proposed live-in replacement table:")
    for lineno, reg, offset, q_index in sorted(loads, key=lambda item: item[3]):
        stripe = q_index
        print(
            f"  Q{q_index}: stage12 stripe{stripe} out0 -> live input {reg} "
            f"(replaces line {lineno} ldr [x4, #{offset}])"
        )

    print()
    print("required stage12 output handling:")
    print("  out0 from stripes0..7: keep live for block0, do not store/load on the hot path")
    print("  out1/out2/out3 from stripes0..7: still store for later block1/block2/block3")
    print()
    print("important pressure note:")
    print("  block0 wants all Q0..Q7 available before its arithmetic can complete.")
    print("  removing eight loads saves memory traffic, but keeps eight vectors live")
    print("  across the Stage12 -> Stage345 boundary.")
    print()
    if errors:
        print("stage345_block0_livein_contract_FAIL")
        for error in errors:
            print(f"  {error}")
        return 1
    print("stage345_block0_livein_contract_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
