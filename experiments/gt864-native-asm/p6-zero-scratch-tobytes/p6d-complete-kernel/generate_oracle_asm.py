#!/usr/bin/env python3
"""Wrap allocated P6-D1 regions in test-only AAPCS functions."""

from pathlib import Path

HERE = Path(__file__).resolve().parent


def body(path: Path, start: str, end: str) -> list[str]:
    text = path.read_text().splitlines()
    lo = next(i for i, x in enumerate(text) if x.strip() == start + ":") + 1
    hi = next(i for i, x in enumerate(text) if x.strip() == end + ":")
    return ["    " + x.split("//", 1)[0].strip() for x in text[lo:hi] if x.split("//", 1)[0].strip()]


def wrapper(name: str, allocated: str, start: str, end: str, copy_bytes: int, seed_bytes: int) -> list[str]:
    lines = [f".global {name}", f"{name}:", "    sub sp, sp, #640"]
    if seed_bytes:
        for off in range(0, seed_bytes - 7, 16):
            if off + 16 <= seed_bytes:
                lines += [f"    ldr q0, [x2, #{off}]", f"    str q0, [sp, #{off}]"]
        if seed_bytes & 15:
            off = seed_bytes & ~15
            lines += [f"    ldr x3, [x2, #{off}]", f"    str x3, [sp, #{off}]"]
    lines += [
        "    add x17, sp, #448",
        "    stp x19, x20, [x17, #0]", "    stp x21, x22, [x17, #16]",
        "    stp x23, x24, [x17, #32]", "    stp x25, x26, [x17, #48]",
        "    stp x27, x28, [x17, #64]", "    stp x29, x30, [x17, #80]",
        "    stp d8, d9, [x17, #96]", "    stp d10, d11, [x17, #112]",
        "    stp d12, d13, [x17, #128]", "    stp d14, d15, [x17, #144]",
        "    str x2, [sp, #608]", "    mov x29, x0", "    mov x30, x1",
    ]
    lines += body(HERE / allocated, start, end)
    lines += ["    ldr x3, [sp, #608]"]
    for off in range(0, copy_bytes - 7, 16):
        if off + 16 <= copy_bytes:
            lines += [f"    ldr q0, [sp, #{off}]", f"    str q0, [x3, #{off}]"]
    if copy_bytes & 15:
        off = copy_bytes & ~15
        lines += [f"    ldr x4, [sp, #{off}]", f"    str x4, [x3, #{off}]"]
    lines += [
        "    add x17, sp, #448",
        "    ldp d8, d9, [x17, #96]", "    ldp d10, d11, [x17, #112]",
        "    ldp d12, d13, [x17, #128]", "    ldp d14, d15, [x17, #144]",
        "    ldp x19, x20, [x17, #0]", "    ldp x21, x22, [x17, #16]",
        "    ldp x23, x24, [x17, #32]", "    ldp x25, x26, [x17, #48]",
        "    ldp x27, x28, [x17, #64]", "    ldp x29, x30, [x17, #80]",
        "    add sp, sp, #640", "    ret", "",
    ]
    return lines


lines = [".text", ".p2align 2"]
lines += wrapper("gt864_p6d_pair0_oracle", "producer.pair0.alloc.S", "gt864_p6d_pair0_start", "gt864_p6d_pair0_end", 216, 0)
lines += wrapper("gt864_p6d_pair1_oracle", "producer.pair1.alloc.S", "gt864_p6d_pair1_start", "gt864_p6d_pair1_end", 432, 216)
(HERE / "oracle.generated.S").write_text("\n".join(lines))
