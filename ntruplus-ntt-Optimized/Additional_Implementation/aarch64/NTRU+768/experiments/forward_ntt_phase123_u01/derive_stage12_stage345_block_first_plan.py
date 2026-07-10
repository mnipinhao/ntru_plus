#!/usr/bin/env python3
"""Derive the block-first stage12 -> stage345 fusion plan.

Stage12 stripe s consumes raw Q[s], Q[s+8], Q[s+16], Q[s+24] and produces four
post-stage12 outputs:

  out0 -> Q[s]
  out1 -> Q[s+8]
  out2 -> Q[s+16]
  out3 -> Q[s+24]

Stage345 block b consumes Q[8*b .. 8*b+7].  Therefore block b wants output b
from every stage12 stripe 0..7.
"""


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

STAGE12_OUT_REG = {
    0: "q22",
    1: "q23",
    2: "q26",
    3: "q27",
}


def qlist(values):
    return ", ".join(f"Q{v}" for v in values)


def main() -> int:
    print("stage12_stage345_block_first_plan")
    print()
    print("stage12 stripe contract:")
    for stripe in range(8):
        raw = [stripe + 8 * i for i in range(4)]
        outputs = [stripe + 8 * i for i in range(4)]
        print(
            f"  stripe{stripe}: raw {qlist(raw)} -> post {qlist(outputs)} "
            f"({SLICE_FAMILY_BY_STRIPE[stripe]})"
        )

    print()
    print("block-first selection:")
    for block in range(4):
        wanted = [8 * block + stripe for stripe in range(8)]
        print(f"  block{block}: wants {qlist(wanted)}")
        for stripe in range(8):
            q_index = 8 * block + stripe
            print(
                f"    stripe{stripe}: keep stage12 out{block} "
                f"({STAGE12_OUT_REG[block]}) -> Q{q_index} "
                f"from {SLICE_FAMILY_BY_STRIPE[stripe]}"
            )

    print()
    print("block0_first_minimum_shape:")
    print("  1. Produce raw inputs for stripes0..7 from the four slice families.")
    print("  2. Run stage12 stripes0..7.")
    print("  3. Keep out0 from each stripe as Q0..Q7 for stage345 block0.")
    print("  4. Store out1/out2/out3 for later block1/block2/block3, unless a")
    print("     larger prototype can keep more block outputs live.")
    print("  5. Rewrite stage345 block0 input contract from eight row_base loads to")
    print("     eight live input vectors or a compact block scratch.")
    print()
    print("block_first_plan_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
