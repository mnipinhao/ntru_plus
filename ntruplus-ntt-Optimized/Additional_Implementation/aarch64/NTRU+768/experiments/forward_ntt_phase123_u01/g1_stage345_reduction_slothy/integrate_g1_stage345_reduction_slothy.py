#!/usr/bin/env python3
"""Integrate passing block1-3 schedules into full G1 and G1+S2 wrappers."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


EXP = Path(__file__).resolve().parent
U01 = EXP.parent
ROOT = U01.parents[1]
ASM_SLOTHY = ROOT / "asm/slothy/experiments/u01v3_g1_stage345_reduction"
ASM_GT = ROOT / "asm/gt/experiment"
TEST_ROOT = ROOT / "gt_test"
sys.path.insert(0, str(U01))

from generate_phase123_shared_prefix_v2 import PHASE123  # noqa: E402
from generate_phase123_shared_prefix_v3_block1_block01_fuse import (  # noqa: E402
    load_stage345_block,
)
from generate_u01v3_f0123_track_g import build_e3_stage345, emit_body_g1  # noqa: E402
from generate_u01v3_g1_fullpath import (  # noqa: E402
    emit_full_wrapper,
    emit_sentinel,
    transform_stage345_s2,
)


G1R = "poly_ntt_u01v3_g1_r123"
G1R_S2 = "poly_ntt_u01v3_g1_r123_s2"
LABEL_RE = re.compile(r"^\s*slothy_(?:start|end)_g1_stage345_block[0-3]_final_reduction:\s*$")


def instruction(line: str) -> str | None:
    code = line.split("//", 1)[0].strip()
    if (
        not code
        or code.startswith(".")
        or code.endswith(":")
        or code.startswith("/*")
        or code.startswith("*")
        or code.startswith("*/")
    ):
        return None
    return " ".join(code.lower().split())


def instruction_multiset(lines: list[str]) -> Counter[str]:
    return Counter(code for line in lines if (code := instruction(line)) is not None)


def load_scheduled_block(block: int, baseline: list[str]) -> list[str]:
    path = ASM_SLOTHY / f"block{block}_stage345_reduction.opt.s"
    if not path.exists():
        raise FileNotFoundError(path)
    lines = [line for line in path.read_text().splitlines() if not LABEL_RE.match(line)]
    if instruction_multiset(lines) != instruction_multiset(baseline):
        raise ValueError(f"block{block}: full-block instruction multiset changed")
    return lines


def emit_test() -> str:
    return f'''#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

void poly_ntt_u01v3_g1(poly *r, const poly *a);
void {G1R}(poly *r, const poly *a);
void {G1R_S2}(poly *r, const poly *a);
int {G1R}_abi_sentinel(poly *r, const poly *a);
int {G1R_S2}_abi_sentinel(poly *r, const poly *a);

static uint32_t state = 0x7123a55au;
static uint32_t next_u32(void)
{{
    state = state * 1664525u + 1013904223u;
    return state;
}}

static void fill_case(poly *a, int id)
{{
    const int bound = 3 * (NTRUPLUS_Q - 1);
    const int span = 2 * bound + 1;
    for (int i = 0; i < NTRUPLUS_N; i++) {{
        switch (id) {{
        case 0: a->coeffs[i] = 0; break;
        case 1: a->coeffs[i] = (int16_t)(i % 17); break;
        case 2: a->coeffs[i] = (int16_t)(NTRUPLUS_Q - 1 - (i % 31)); break;
        case 3: a->coeffs[i] = (int16_t)(bound - (i % 61)); break;
        default:
            a->coeffs[i] = (int16_t)((int)(next_u32() % (uint32_t)span) - bound);
            break;
        }}
    }}
}}

static int compare(const char *name, const poly *want, const poly *got)
{{
    int mismatches = 0;
    for (int i = 0; i < NTRUPLUS_N; i++) {{
        if (want->coeffs[i] != got->coeffs[i]) {{
            if (mismatches < 8)
                printf("%s mismatch[%d]: want=%d got=%d\\n", name, i,
                       want->coeffs[i], got->coeffs[i]);
            mismatches++;
        }}
    }}
    return mismatches;
}}

int main(void)
{{
    poly input, want, g1, r123, r123_inplace, combo, combo_inplace, sentinel;
    uint64_t r123_abi = 0, combo_abi = 0;
    int mismatches = 0;
    for (int t = 0; t < 260; t++) {{
        fill_case(&input, t < 4 ? t : 4);
        poly_ntt(&want, &input);
        poly_ntt_u01v3_g1(&g1, &input);
        {G1R}(&r123, &input);
        r123_inplace = input;
        {G1R}(&r123_inplace, &r123_inplace);
        {G1R_S2}(&combo, &input);
        combo_inplace = input;
        {G1R_S2}(&combo_inplace, &combo_inplace);
        r123_abi |= (uint64_t){G1R}_abi_sentinel(&sentinel, &input);
        mismatches += compare("g1", &want, &g1);
        mismatches += compare("r123", &want, &r123);
        mismatches += compare("r123_inplace", &want, &r123_inplace);
        mismatches += compare("r123_s2", &want, &combo);
        mismatches += compare("r123_s2_inplace", &want, &combo_inplace);
        mismatches += compare("r123_sentinel", &want, &sentinel);
        combo_abi |= (uint64_t){G1R_S2}_abi_sentinel(&sentinel, &input);
        mismatches += compare("r123_s2_sentinel", &want, &sentinel);
    }}
    printf("u01v3_g1_r123_abi_mask=0x%llx\\n", (unsigned long long)r123_abi);
    printf("u01v3_g1_r123_s2_abi_mask=0x%llx\\n", (unsigned long long)combo_abi);
    printf("u01v3_g1_r123_mismatches=%d\\n", mismatches);
    return mismatches == 0 && r123_abi == 0 && combo_abi == 0 ? 0 : 1;
}}
'''


def main() -> int:
    original0, original1, original2, _metadata = build_e3_stage345()
    original = [original0, original1, original2, load_stage345_block(3)]
    scheduled = [original0] + [load_scheduled_block(block, original[block]) for block in range(1, 4)]
    phase_lines = PHASE123.read_text().splitlines()
    body, _reports = emit_body_g1(phase_lines, *scheduled)

    transformed = []
    safe_sites = []
    kept_sites = []
    for block, lines in enumerate(scheduled):
        out, safe, kept = transform_stage345_s2(block, lines)
        transformed.append(out)
        safe_sites.extend(safe)
        kept_sites.extend(kept)
    if len(safe_sites) + len(kept_sites) != 32:
        raise ValueError(
            f"scheduled S2 coverage mismatch: {len(safe_sites)} safe + "
            f"{len(kept_sites)} kept"
        )
    combo_body, _combo_reports = emit_body_g1(phase_lines, *transformed)

    outputs = {
        ASM_GT / f"{G1R}.S": emit_full_wrapper(G1R, body, False),
        ASM_GT / f"{G1R}_dropin.S": emit_full_wrapper(G1R, body, True),
        ASM_GT / f"{G1R_S2}.S": emit_full_wrapper(G1R_S2, combo_body, False),
        ASM_GT / f"{G1R_S2}_dropin.S": emit_full_wrapper(G1R_S2, combo_body, True),
        ASM_GT / f"{G1R}_abi_sentinel.S": emit_sentinel(G1R, f"{G1R}_abi_sentinel"),
        ASM_GT / f"{G1R_S2}_abi_sentinel.S": emit_sentinel(
            G1R_S2, f"{G1R_S2}_abi_sentinel"
        ),
        TEST_ROOT / "test_u01v3_g1_reduction_slothy.c": emit_test(),
    }
    for path, text in outputs.items():
        path.write_text(text)
        print(path)

    (EXP / "g1_r123_s2_transform_audit.json").write_text(
        json.dumps(
            {
                "candidate": G1R_S2,
                "scheduled_blocks": [1, 2, 3],
                "unscheduled_blocks": [0],
                "safe_generic_sites": len(safe_sites),
                "kept_ext_str_sites": len(kept_sites),
                "dynamic_safe_sites_three_rows": 3 * len(safe_sites),
                "failures": 0,
                "sites": safe_sites,
                "kept_sites": kept_sites,
            },
            indent=2,
        )
        + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
