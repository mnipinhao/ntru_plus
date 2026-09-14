#!/usr/bin/env python3
"""Generate the exact P27 route as two supported TBL2 operations plus ORR."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P27 = ROOT / "experiments/gt864-p27-consumer-i16-lane-basis/audit-results.json"


def main():
    plan = json.loads(P27.read_text())["search"]["route_plan"]
    masks = []
    lines = [
        "mov w3, #1728", "dup v4.8h, w3",
        "mov w3, #-1728", "dup v5.8h, w3",
        "mov w3, #10923", "dup v6.8h, w3",
        "movi v7.8h, #3",
    ]
    for step in plan:
        for load in step["loads"]:
            record, slot = load["record"], load["tbl_slot"]
            lines += [
                f"ldr q{slot}, [x1, #{16 * record}]",
                f"cmgt v8.8h, v{slot}.8h, v4.8h",
                f"cmgt v9.8h, v5.8h, v{slot}.8h",
                f"add v{slot}.8h, v{slot}.8h, v8.8h",
                f"sub v{slot}.8h, v{slot}.8h, v9.8h",
                f"sqrdmulh v8.8h, v{slot}.8h, v6.8h",
                f"mls v{slot}.8h, v8.8h, v7.8h",
            ]
        idx = step["tbl4_byte_indices"]
        first = [value if value < 32 else 255 for value in idx]
        second = [value - 32 if value >= 32 else 255 for value in idx]
        masks.append((first, second))
        output = step["output_q"]
        lines += [
            "ldp q8, q9, [x2], #32",
            "tbl v10.16b, {v0.16b, v1.16b}, v8.16b",
            "tbl v11.16b, {v2.16b, v3.16b}, v9.16b",
            "orr v10.16b, v10.16b, v11.16b",
            f"str q10, [x0, #{16 * output}]",
        ]
    header = [
        "#ifdef __APPLE__", "#define p28_route_ternary _p28_route_ternary", "#endif",
        ".text", ".p2align 4", ".global p28_route_ternary", "p28_route_ternary:",
        "// live-in: x0 distinct natural output, x1 dense scratch, x2 public masks",
        "// live-out: 864 natural-order ternary coefficients at x0",
        "// coefficient range: raw abs<=4577, adjusted abs<=4576, ternary abs<=1",
        "// fixed physical registers: v0-v3 resident source bank; v4-v7 constants",
        "p28_route_slothy_start:",
    ]
    footer = ["p28_route_slothy_end:", "    ret", ""]
    (HERE / "candidate-route.S").write_text(
        "\n".join(header + ["    " + line for line in lines] + footer)
    )
    rows = []
    for first, second in masks:
        rows.append("  {{" + ",".join(map(str, first)) + "},{" + ",".join(map(str, second)) + "}},")
    (HERE / "route-masks.h").write_text(
        "#ifndef GT864_P28_ROUTE_MASKS_H\n#define GT864_P28_ROUTE_MASKS_H\n"
        "#include <stdint.h>\nstatic const uint8_t gt864_p28_route_masks[108][2][16] = {\n"
        + "\n".join(rows) + "\n};\n#endif\n"
    )
    asm = [
        "#ifdef __APPLE__", "#define gt864_p28_route_masks_asm _gt864_p28_route_masks_asm", "#endif",
        "#ifdef __APPLE__", ".section __TEXT,__const", "#else", ".section .rodata", "#endif",
        ".p2align 4", ".global gt864_p28_route_masks_asm",
        "gt864_p28_route_masks_asm:",
    ]
    for first, second in masks:
        asm.append("    .byte " + ",".join(map(str, first + second)))
    asm.append("")
    (HERE / "route-masks.S").write_text("\n".join(asm))
    print({"instructions": len(lines), "source_loads": 108, "mask_bytes": 108 * 32})


if __name__ == "__main__":
    main()
