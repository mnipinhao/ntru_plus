#!/usr/bin/env python3
"""Generate the A2 ST1-lane inverse-finish candidate from the M5E baseline."""

from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "gt_fr0_inverse_asm_realization" / "gt864_inverse16_blocks.s"
OUT = HERE / "build" / "gt864_inverse16_blocks_st1.s"


MAIN = r""".macro FINISH_MAIN2 r0, low0, r1, low1
    mov     v25.16b, \r0\().16b
    mov     v26.16b, \r1\().16b
    ext     \r0\().16b, \r0\().16b, \r0\().16b, #8
    ext     \r1\().16b, \r1\().16b, \r1\().16b, #8
    sub     \r0\().8h, \r0\().8h, v25.8h
    sub     \r1\().8h, \r1\().8h, v26.8h
    LOAD_FIXED_PAIR -1634, -15488
    sqrdmulh v27.8h, \r0\().8h, v30.8h
    sqrdmulh v28.8h, \r1\().8h, v30.8h
    mul     \r0\().8h, \r0\().8h, v0.8h
    mul     \r1\().8h, \r1\().8h, v0.8h
    mls     \r0\().8h, v27.8h, v31.8h
    mls     \r1\().8h, v28.8h, v31.8h
    add     x9, x0, #(\low0 + 864)
    st1     {\r0\().h}[0], [x9], x10
    st1     {\r0\().h}[1], [x9], x10
    st1     {\r0\().h}[2], [x9], x10
    st1     {\r0\().h}[3], [x9]
    add     x9, x0, #(\low1 + 864)
    st1     {\r1\().h}[0], [x9], x10
    st1     {\r1\().h}[1], [x9], x10
    st1     {\r1\().h}[2], [x9], x10
    st1     {\r1\().h}[3], [x9]
    LOAD_FIXED_PAIR -722, -6844
    sqrdmulh v27.8h, \r0\().8h, v30.8h
    sqrdmulh v28.8h, \r1\().8h, v30.8h
    mul     \r0\().8h, \r0\().8h, v0.8h
    mul     \r1\().8h, \r1\().8h, v0.8h
    mls     \r0\().8h, v27.8h, v31.8h
    mls     \r1\().8h, v28.8h, v31.8h
    sub     \r0\().8h, v25.8h, \r0\().8h
    sub     \r1\().8h, v26.8h, \r1\().8h
    add     x9, x0, #\low0
    st1     {\r0\().h}[0], [x9], x10
    st1     {\r0\().h}[1], [x9], x10
    st1     {\r0\().h}[2], [x9], x10
    st1     {\r0\().h}[3], [x9]
    add     x9, x0, #\low1
    st1     {\r1\().h}[0], [x9], x10
    st1     {\r1\().h}[1], [x9], x10
    st1     {\r1\().h}[2], [x9], x10
    st1     {\r1\().h}[3], [x9]
.endm"""


TAIL = r""".macro FINISH_TAIL2 r0, low0, r1, low1
    mov     v25.16b, \r0\().16b
    mov     v26.16b, \r1\().16b
    ext     \r0\().16b, \r0\().16b, \r0\().16b, #6
    ext     \r1\().16b, \r1\().16b, \r1\().16b, #6
    sub     \r0\().8h, \r0\().8h, v25.8h
    sub     \r1\().8h, \r1\().8h, v26.8h
    LOAD_FIXED_PAIR -1634, -15488
    sqrdmulh v27.8h, \r0\().8h, v30.8h
    sqrdmulh v28.8h, \r1\().8h, v30.8h
    mul     \r0\().8h, \r0\().8h, v0.8h
    mul     \r1\().8h, \r1\().8h, v0.8h
    mls     \r0\().8h, v27.8h, v31.8h
    mls     \r1\().8h, v28.8h, v31.8h
    add     x9, x0, #(\low0 + 864)
    st1     {\r0\().h}[0], [x9], x10
    st1     {\r0\().h}[1], [x9], x10
    st1     {\r0\().h}[2], [x9]
    add     x9, x0, #(\low1 + 864)
    st1     {\r1\().h}[0], [x9], x10
    st1     {\r1\().h}[1], [x9], x10
    st1     {\r1\().h}[2], [x9]
    LOAD_FIXED_PAIR -722, -6844
    sqrdmulh v27.8h, \r0\().8h, v30.8h
    sqrdmulh v28.8h, \r1\().8h, v30.8h
    mul     \r0\().8h, \r0\().8h, v0.8h
    mul     \r1\().8h, \r1\().8h, v0.8h
    mls     \r0\().8h, v27.8h, v31.8h
    mls     \r1\().8h, v28.8h, v31.8h
    sub     \r0\().8h, v25.8h, \r0\().8h
    sub     \r1\().8h, v26.8h, \r1\().8h
    add     x9, x0, #\low0
    st1     {\r0\().h}[0], [x9], x10
    st1     {\r0\().h}[1], [x9], x10
    st1     {\r0\().h}[2], [x9]
    add     x9, x0, #\low1
    st1     {\r1\().h}[0], [x9], x10
    st1     {\r1\().h}[1], [x9], x10
    st1     {\r1\().h}[2], [x9]
.endm"""


def replace_macro(text: str, name: str, replacement: str) -> str:
    start = text.index(f".macro {name}")
    end = text.index(".endm", start) + len(".endm")
    return text[:start] + replacement + text[end:]


def main() -> None:
    text = BASE.read_text(encoding="utf-8")
    text = replace_macro(text, "FINISH_MAIN2", MAIN)
    text = replace_macro(text, "FINISH_TAIL2", TAIL)
    text = text.replace("gt864_inverse16_main_block_asm",
                        "gt864_inverse16_main_block_st1_asm")
    text = text.replace("gt864_inverse16_tail_block_asm",
                        "gt864_inverse16_tail_block_st1_asm")
    main_entry = "gt864_inverse16_main_block_st1_asm:\n_gt864_inverse16_main_block_st1_asm:\n"
    tail_entry = "gt864_inverse16_tail_block_st1_asm:\n_gt864_inverse16_tail_block_st1_asm:\n"
    assert text.count(main_entry) == 1 and text.count(tail_entry) == 1
    text = text.replace(main_entry, main_entry + "    mov     x10, #6\n", 1)
    text = text.replace(tail_entry, tail_entry + "    mov     x10, #2\n", 1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"generated={OUT}")
    print("dynamic_instruction_delta_finish=-640")


if __name__ == "__main__":
    main()
