#!/usr/bin/env python3
"""Generate the isolated compact-wide-frontend executable gate."""

from __future__ import annotations

import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXP = HERE.parent
NTRU = EXP.parent.parent
BASE = NTRU / "experiments" / "avx2_gt32_tile4_official_001"
GENERATED = EXP / "generated"


COMPACT = r'''
.macro EMIT_FRONTEND_WIDE_COMPACT_U3
.p2align 5
.globl gt32_tile4_frontend_wide_raw_compact_u3_asm
.type gt32_tile4_frontend_wide_raw_compact_u3_asm,@function
.Ltile4_frontend_wide_raw_compact_u3_start:
gt32_tile4_frontend_wide_raw_compact_u3_asm:
	leaq .Ltile4_frontend_wide_twist_qinv(%rip), %rdx
	leaq .Ltile4_frontend_wide_twist_factor(%rip), %rcx
	vmovdqa .Ltile4_q(%rip), %ymm15
	movl $2, %r8d
.p2align 5
.Ltile4_frontend_wide_compact_u3_loop:
	FRONTEND_WIDE_ITER_0 0
	FRONTEND_WIDE_ITER_1 32
	FRONTEND_WIDE_ITER_2 64
	addq $96, %rsi
	decl %r8d
	jne .Ltile4_frontend_wide_compact_u3_loop
	/* Groups six and seven retain shapes zero and one. */
	FRONTEND_WIDE_ITER_0 0
	FRONTEND_WIDE_ITER_1 32
	vzeroupper
	ret
.globl gt32_tile4_frontend_wide_raw_compact_u3_active_end
gt32_tile4_frontend_wide_raw_compact_u3_active_end:
	/* Generator-owned fixed fill; audited against the 3917-byte control. */
	.fill 1445,1,0x90
.size gt32_tile4_frontend_wide_raw_compact_u3_asm,.-gt32_tile4_frontend_wide_raw_compact_u3_asm
.endm
'''


def minimal_period(values: list[int]) -> int:
    for period in range(1, len(values) + 1):
        if all(values[i] == values[i % period] for i in range(len(values))):
            return period
    raise AssertionError


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    schedule_source = BASE / "generated" / "tile4_frontend_wide.inc"
    schedule = schedule_source.read_text()
    shapes = [int(v) for v in re.findall(r"FRONTEND_WIDE_ITER_(\d)\s+\d+", schedule)]
    if shapes != [0, 1, 2, 0, 1, 2, 0, 1]:
        raise RuntimeError(f"unexpected production schedule: {shapes}")
    period = minimal_period(shapes)
    audit = {
        "schema": "ntruplus768-gt32-compact-frontend-shape-audit-v1",
        "iterations": [
            {"iteration": i, "source_displacement": 32 * i,
             "shape": shape, "twist_bytes": [192 * i, 192 * i + 191],
             "destination_displacement": 32 * i}
            for i, shape in enumerate(shapes)
        ],
        "shape_sequence": shapes,
        "minimum_period": period,
        "requested_periods": {
            str(p): {"legal_repeating_body": period <= p and p % period == 0}
            for p in (1, 2, 4)
        },
        "selected": {
            "body": "U3",
            "loop_iterations": 2,
            "tail": "U2",
            "reason": "the fixed-immediate/register orientation has exact period three",
        },
    }
    (GENERATED / "shape_audit.json").write_text(json.dumps(audit, indent=2) + "\n")

    for name in ("tile4_frontend_fixed.inc", "tile4_frontend_wide.inc",
                 "tile4_constants.inc"):
        (GENERATED / name).write_bytes((BASE / "generated" / name).read_bytes())

    source = (BASE / "src" / "tile4_asm.S").read_text()
    marker = "/* N5: contiguous quartic loads and qword-granular Good--Thomas blends. */"
    source = source.replace(marker, COMPACT + "\n" + marker, 1)
    before_control = ".p2align 5\n.globl gt32_tile4_frontend_wide_raw_asm"
    source = source.replace(
        before_control,
        "#ifdef GT32_COMPACT_FIRST\n\tEMIT_FRONTEND_WIDE_COMPACT_U3\n#endif\n" + before_control,
        1,
    )
    after_control = ".size gt32_tile4_frontend_wide_raw_asm,.-gt32_tile4_frontend_wide_raw_asm"
    source = source.replace(
        after_control,
        after_control + "\n#ifndef GT32_COMPACT_FIRST\n\tEMIT_FRONTEND_WIDE_COMPACT_U3\n#endif",
        1,
    )
    (GENERATED / "tile4_compact_gate.S").write_text(source)

    bench = (BASE / "bench" / "bench_frontend_f1.c").read_text()
    bench = bench.replace(
        "enum { WORDS = GT32_TILE4_POLY_WORDS, SAMPLES = 20 };",
        "extern void gt32_tile4_frontend_wide_raw_compact_u3_asm(int16_t *, const int16_t *);\n\n"
        "enum { WORDS = GT32_TILE4_POLY_WORDS, SAMPLES = 20 };",
        1,
    )
    bench = bench.replace("gt32_tile4_frontend_wide_raw_f1_asm",
                          "gt32_tile4_frontend_wide_raw_compact_u3_asm")
    (GENERATED / "bench_compact_frontend.c").write_text(bench)
    print(json.dumps(audit["selected"], indent=2))


if __name__ == "__main__":
    main()
