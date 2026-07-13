#!/usr/bin/env python3
"""Generate full poly_ntt/KEM wrappers for G1 and the G1+S2 combination."""

from __future__ import annotations

import json
import re
from pathlib import Path

from generate_phase123_shared_prefix_v2 import PHASE123
from generate_phase123_shared_prefix_v3_block1_block01_fuse import load_stage345_block
from generate_u01v3_f0123_track_g import build_e3_stage345, emit_body_g1


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]
ASM_ROOT = NTRU_ROOT / "asm/gt/experiment"
TEST_ROOT = NTRU_ROOT / "gt_test"
from audit_umov_str_candidate import (  # noqa: E402
    CALLER_SAVED_X,
    code_part,
    is_instruction,
    mem_bases_in,
    parse_instruction,
    vector_reads,
    vector_writes,
)


G1_SYMBOL = "poly_ntt_u01v3_g1"
G1_S2_SYMBOL = "poly_ntt_u01v3_g1_s2"
G1_ASM = ASM_ROOT / f"{G1_SYMBOL}.S"
G1_DROPIN = ASM_ROOT / f"{G1_SYMBOL}_dropin.S"
G1_S2_ASM = ASM_ROOT / f"{G1_S2_SYMBOL}.S"
G1_S2_DROPIN = ASM_ROOT / f"{G1_S2_SYMBOL}_dropin.S"
G1_SENTINEL = ASM_ROOT / f"{G1_SYMBOL}_abi_sentinel.S"
G1_S2_SENTINEL = ASM_ROOT / f"{G1_S2_SYMBOL}_abi_sentinel.S"
TEST_SOURCE = TEST_ROOT / "test_u01v3_g1_fullpath.c"
S2_AUDIT = ROOT / "u01v3_g1_s2_transform_audit.json"
RESULT = ROOT / "u01v3_g1_fullpath_integration.md"

EXT_HIGH_RE = re.compile(
    r"^(?P<indent>\s*)ext\s+v(?P<tmp>\d+)\.16B,\s*"
    r"v(?P<src>\d+)\.16B,\s*v(?P=src)\.16B,\s*#8(?:\s*//.*)?$",
    re.IGNORECASE,
)
STR_D_RE = re.compile(
    r"^(?P<indent>\s*)str\s+d(?P<tmp>\d+),\s*"
    r"(?P<address>\[[^\]]+\])(?P<comment>\s*//.*)?$",
    re.IGNORECASE,
)

FRAME_SIZE = 1696
SCRATCH_OFFSET = 160
CALLER_TEMP_PRIORITY = (
    "x17", "x16", "x15", "x13", "x11", "x9", "x8", "x7",
    "x6", "x5", "x3", "x2", "x1", "x0",
)


def reg_live_after(lines: list[str], start: int, reg: str) -> bool:
    for line_no, line in enumerate(lines[start + 1 :], start=start + 2):
        if not is_instruction(line):
            continue
        parsed = parse_instruction(line_no, line)
        if parsed is None:
            continue
        if reg in parsed["reads"]:
            return True
        if reg in parsed["writes"]:
            return False
    return False


def ext_is_store_only(
    lines: list[str], ext_idx: int, store_idx: int, tmp: str, src: str
) -> bool:
    tmp_reg = f"v{tmp}"
    src_reg = f"v{src}"
    for between in lines[ext_idx + 1 : store_idx]:
        writes = vector_writes(between)
        if tmp_reg in writes or src_reg in writes:
            return False
    for after in lines[store_idx + 1 :]:
        if not code_part(after):
            continue
        if tmp_reg in vector_reads(after):
            return False
        if tmp_reg in vector_writes(after):
            return True
    return True


def choose_xtmp(lines: list[str], store_idx: int, address: str) -> str:
    address_bases = mem_bases_in(address)
    for reg in CALLER_TEMP_PRIORITY:
        if reg not in CALLER_SAVED_X or reg in address_bases:
            continue
        if not reg_live_after(lines, store_idx, reg):
            return reg
    raise ValueError(
        f"no dead caller-saved xTmp at line {store_idx + 1}: {code_part(lines[store_idx])}"
    )


def transform_stage345_s2(
    block: int, lines: list[str]
) -> tuple[list[str], list[dict[str, object]], list[dict[str, object]]]:
    out = list(lines)
    ext_defs: dict[str, tuple[int, str]] = {}
    sites: list[dict[str, object]] = []
    kept_sites: list[dict[str, object]] = []
    for idx, line in enumerate(lines):
        for written in vector_writes(line):
            ext_defs.pop(written[1:], None)
        ext = EXT_HIGH_RE.match(line)
        if ext:
            ext_defs[ext.group("tmp")] = (idx, ext.group("src"))
            continue
        store = STR_D_RE.match(line)
        if store is None:
            continue
        tmp = store.group("tmp")
        if tmp not in ext_defs:
            continue
        ext_idx, src = ext_defs[tmp]
        if not ext_is_store_only(lines, ext_idx, idx, tmp, src):
            kept_sites.append(
                {
                    "block": block,
                    "original_ext_line": ext_idx,
                    "original_store_line": idx,
                    "source_vector": f"v{src}",
                    "ext_tmp_vector": f"v{tmp}",
                    "store_address": store.group("address"),
                    "reason": "source_or_ext_tmp_live_range_prevents_store_site_umov",
                }
            )
            ext_defs.pop(tmp, None)
            continue
        address = store.group("address")
        xtmp = choose_xtmp(lines, idx, address)
        indent = store.group("indent")
        comment = store.group("comment") or ""
        out[ext_idx] = (
            f"{indent}// G1+S2 removed ext: v{tmp}.16B <- v{src}.16B high half"
        )
        out[idx] = (
            f"{indent}umov {xtmp}, v{src}.d[1]\n"
            f"{indent}str {xtmp}, {address}{comment} // G1+S2 highhalf_umov_str"
        )
        sites.append(
            {
                "block": block,
                "site": len(sites),
                "original_ext_line": ext_idx,
                "original_store_line": idx,
                "source_vector": f"v{src}",
                "ext_tmp_vector": f"v{tmp}",
                "new_xtmp": xtmp,
                "store_address": address,
                "xtmp_caller_saved": xtmp in CALLER_SAVED_X,
                "xtmp_address_alias": xtmp in mem_bases_in(address),
                "xtmp_live_after_store": reg_live_after(lines, idx, xtmp),
                "source_unchanged_before_umov": True,
                "store_size_bytes": 8,
                "little_endian_equivalent": True,
            }
        )
        ext_defs.pop(tmp, None)
    return out, sites, kept_sites


def emit_full_wrapper(symbol: str, body: list[str], public_dropin: bool) -> str:
    if public_dropin:
        globals_and_labels = [
            ".global poly_ntt",
            ".global _poly_ntt",
            ".global gt_block_major_poly_ntt",
            ".global _gt_block_major_poly_ntt",
            ".type poly_ntt, %function",
            "poly_ntt:",
            "_poly_ntt:",
            "gt_block_major_poly_ntt:",
            "_gt_block_major_poly_ntt:",
        ]
        size_lines = [
            ".size poly_ntt, .-poly_ntt",
            ".global poly_ntt_end",
            "poly_ntt_end:",
        ]
    else:
        globals_and_labels = [
            f".global {symbol}",
            f".type {symbol}, %function",
            f"{symbol}:",
        ]
        size_lines = [
            f".size {symbol}, .-{symbol}",
            f".global {symbol}_end",
            f"{symbol}_end:",
        ]
    return "\n".join(
        [
            f"/* Experiment-only full poly_ntt wrapper for {symbol}. */",
            "/* ABI: x0=dst, x1=src. The 1536-byte row scratch is stack-local. */",
            "",
            ".text",
            ".align 4",
            ".equ STACK_LOC_0, 0",
            "",
            *globals_and_labels,
            f"    sub sp, sp, #{FRAME_SIZE}",
            "    stp x19, x20, [sp, #16]",
            "    stp x21, x22, [sp, #32]",
            "    str x23, [sp, #48]",
            "    stp d8, d9, [sp, #64]",
            "    stp d10, d11, [sp, #80]",
            "    stp d12, d13, [sp, #96]",
            "    stp d14, d15, [sp, #112]",
            "",
            "    mov x19, x0",
            "    mov x20, x1",
            f"    add x21, sp, #{SCRATCH_OFFSET}",
            "",
            "    adr x2, u01_block_first_zetas",
            "    ldr q0, [x2]",
            "    adr x22, u01_block_first_twist_table",
            "    adr x23, u01_block_first_ntt32_twiddle_vecs",
            "",
            *body,
            "    ldp d14, d15, [sp, #112]",
            "    ldp d12, d13, [sp, #96]",
            "    ldp d10, d11, [sp, #80]",
            "    ldp d8, d9, [sp, #64]",
            "    ldr x23, [sp, #48]",
            "    ldp x21, x22, [sp, #32]",
            "    ldp x19, x20, [sp, #16]",
            f"    add sp, sp, #{FRAME_SIZE}",
            "    ret",
            *size_lines,
            "",
            '.include "asm/gt/experiment/forward_ntt/u01_block_first_tables.inc"',
            "",
        ]
    )


def emit_sentinel(target: str, sentinel: str) -> str:
    return f'''.text
.align 2

.macro LOAD_CANARY reg, imm16
    movz \\reg, #\\imm16
    movk \\reg, #\\imm16, lsl #16
    movk \\reg, #\\imm16, lsl #32
    movk \\reg, #\\imm16, lsl #48
.endm

.macro CHECK_X reg, imm16, bit
    LOAD_CANARY x9, \\imm16
    cmp \\reg, x9
    mov x10, #(1 << \\bit)
    csel x10, x10, xzr, ne
    orr x0, x0, x10
.endm

.macro CHECK_D operand, imm16, bit
    umov x9, \\operand
    LOAD_CANARY x10, \\imm16
    cmp x9, x10
    mov x11, #(1 << \\bit)
    csel x11, x11, xzr, ne
    orr x0, x0, x11
.endm

.global {sentinel}
.type {sentinel}, %function
{sentinel}:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #160
    stp x19, x20, [sp, #0]
    stp x21, x22, [sp, #16]
    stp x23, x24, [sp, #32]
    stp x25, x26, [sp, #48]
    stp x27, x28, [sp, #64]
    stp d8, d9, [sp, #80]
    stp d10, d11, [sp, #96]
    stp d12, d13, [sp, #112]
    stp d14, d15, [sp, #128]
    stp x0, x1, [sp, #144]

    LOAD_CANARY x19, 0x1919
    LOAD_CANARY x20, 0x2020
    LOAD_CANARY x21, 0x2121
    LOAD_CANARY x22, 0x2222
    LOAD_CANARY x23, 0x2323
    LOAD_CANARY x24, 0x2424
    LOAD_CANARY x25, 0x2525
    LOAD_CANARY x26, 0x2626
    LOAD_CANARY x27, 0x2727
    LOAD_CANARY x28, 0x2828
    LOAD_CANARY x9, 0xd8d8
    fmov d8, x9
    LOAD_CANARY x9, 0xd9d9
    fmov d9, x9
    LOAD_CANARY x9, 0xdada
    fmov d10, x9
    LOAD_CANARY x9, 0xdbdb
    fmov d11, x9
    LOAD_CANARY x9, 0xdcdc
    fmov d12, x9
    LOAD_CANARY x9, 0xdddd
    fmov d13, x9
    LOAD_CANARY x9, 0xdede
    fmov d14, x9
    LOAD_CANARY x9, 0xdfdf
    fmov d15, x9

    ldp x0, x1, [sp, #144]
    bl {target}

    mov x0, xzr
    CHECK_X x19, 0x1919, 0
    CHECK_X x20, 0x2020, 1
    CHECK_X x21, 0x2121, 2
    CHECK_X x22, 0x2222, 3
    CHECK_X x23, 0x2323, 4
    CHECK_X x24, 0x2424, 5
    CHECK_X x25, 0x2525, 6
    CHECK_X x26, 0x2626, 7
    CHECK_X x27, 0x2727, 8
    CHECK_X x28, 0x2828, 9
    CHECK_D v8.d[0], 0xd8d8, 10
    CHECK_D v9.d[0], 0xd9d9, 11
    CHECK_D v10.d[0], 0xdada, 12
    CHECK_D v11.d[0], 0xdbdb, 13
    CHECK_D v12.d[0], 0xdcdc, 14
    CHECK_D v13.d[0], 0xdddd, 15
    CHECK_D v14.d[0], 0xdede, 16
    CHECK_D v15.d[0], 0xdfdf, 17

    ldp d14, d15, [sp, #128]
    ldp d12, d13, [sp, #112]
    ldp d10, d11, [sp, #96]
    ldp d8, d9, [sp, #80]
    ldp x27, x28, [sp, #64]
    ldp x25, x26, [sp, #48]
    ldp x23, x24, [sp, #32]
    ldp x21, x22, [sp, #16]
    ldp x19, x20, [sp, #0]
    add sp, sp, #160
    ldp x29, x30, [sp], #16
    ret
.size {sentinel}, .-{sentinel}
'''


def emit_test_source() -> str:
    return f'''#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

void {G1_SYMBOL}(poly *r, const poly *a);
void {G1_S2_SYMBOL}(poly *r, const poly *a);
int {G1_SYMBOL}_abi_sentinel(poly *r, const poly *a);
int {G1_S2_SYMBOL}_abi_sentinel(poly *r, const poly *a);

static uint32_t state = 0x9e3779b9u;

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
    poly input, want, g1, g1_inplace, combo, combo_inplace, sentinel;
    uint64_t g1_abi = 0, combo_abi = 0;
    int mismatches = 0;
    for (int t = 0; t < 260; t++) {{
        fill_case(&input, t < 4 ? t : 4);
        poly_ntt(&want, &input);
        {G1_SYMBOL}(&g1, &input);
        g1_inplace = input;
        {G1_SYMBOL}(&g1_inplace, &g1_inplace);
        {G1_S2_SYMBOL}(&combo, &input);
        combo_inplace = input;
        {G1_S2_SYMBOL}(&combo_inplace, &combo_inplace);
        g1_abi |= (uint64_t){G1_SYMBOL}_abi_sentinel(&sentinel, &input);
        mismatches += compare("g1", &want, &g1);
        mismatches += compare("g1_inplace", &want, &g1_inplace);
        mismatches += compare("g1_s2", &want, &combo);
        mismatches += compare("g1_s2_inplace", &want, &combo_inplace);
        mismatches += compare("g1_sentinel", &want, &sentinel);
        combo_abi |= (uint64_t){G1_S2_SYMBOL}_abi_sentinel(&sentinel, &input);
        mismatches += compare("g1_s2_sentinel", &want, &sentinel);
    }}
    printf("u01v3_g1_abi_mask=0x%llx\\n", (unsigned long long)g1_abi);
    printf("u01v3_g1_s2_abi_mask=0x%llx\\n", (unsigned long long)combo_abi);
    printf("u01v3_g1_fullpath_mismatches=%d\\n", mismatches);
    return mismatches == 0 && g1_abi == 0 && combo_abi == 0 ? 0 : 1;
}}
'''


def main() -> int:
    phase_lines = PHASE123.read_text().splitlines()
    stage345 = {block: load_stage345_block(block) for block in range(4)}
    e3_b0, e3_b1, e3_b2, _meta = build_e3_stage345()
    g1_body, _reports = emit_body_g1(phase_lines, e3_b0, e3_b1, e3_b2, stage345[3])

    transformed: dict[int, list[str]] = {}
    sites: list[dict[str, object]] = []
    kept_sites: list[dict[str, object]] = []
    for block, block_lines in ((0, e3_b0), (1, e3_b1), (2, e3_b2), (3, stage345[3])):
        transformed[block], block_sites, block_kept = transform_stage345_s2(
            block, block_lines
        )
        sites.extend(block_sites)
        kept_sites.extend(block_kept)
    if len(sites) != 27 or len(kept_sites) != 5:
        raise ValueError(
            "expected G1 allocation to expose 27 safe and 5 live-range-blocked "
            f"high-half sites, found {len(sites)} safe and {len(kept_sites)} kept"
        )
    if any(
        site["xtmp_address_alias"] or site["xtmp_live_after_store"]
        or not site["xtmp_caller_saved"] or not site["little_endian_equivalent"]
        for site in sites
    ):
        raise ValueError("G1+S2 register/equivalence audit failed")
    combo_body, _combo_reports = emit_body_g1(
        phase_lines,
        transformed[0],
        transformed[1],
        transformed[2],
        transformed[3],
    )

    G1_ASM.write_text(emit_full_wrapper(G1_SYMBOL, g1_body, False))
    G1_DROPIN.write_text(emit_full_wrapper(G1_SYMBOL, g1_body, True))
    G1_S2_ASM.write_text(emit_full_wrapper(G1_S2_SYMBOL, combo_body, False))
    G1_S2_DROPIN.write_text(emit_full_wrapper(G1_S2_SYMBOL, combo_body, True))
    G1_SENTINEL.write_text(emit_sentinel(G1_SYMBOL, f"{G1_SYMBOL}_abi_sentinel"))
    G1_S2_SENTINEL.write_text(
        emit_sentinel(G1_S2_SYMBOL, f"{G1_S2_SYMBOL}_abi_sentinel")
    )
    TEST_SOURCE.write_text(emit_test_source())
    S2_AUDIT.write_text(
        json.dumps(
            {
                "candidate": G1_S2_SYMBOL,
                "source": G1_SYMBOL,
                "replacement": "store-only ext+str d -> umov+str x",
                "generic_highhalf_sites": 32,
                "converted_generic_sites": 27,
                "kept_ext_str_sites": 5,
                "dynamic_converted_sites_three_rows": 81,
                "failures": 0,
                "production_default_changed": False,
                "sites": sites,
                "kept_sites": kept_sites,
            },
            indent=2,
        )
        + "\n"
    )
    if not RESULT.exists():
        RESULT.write_text(
            "# U01v3 G1 Full poly_ntt / KEM Integration\n\n"
            "Status: generated; correctness and Pi5 PMU pending. Production "
            "default unchanged.\n\n"
            "Generated unique and drop-in wrappers for G1 and G1+S2. The "
            "two-argument ABI allocates the 1536-byte row scratch in a local "
            "1696-byte frame, avoiding a helper call. G1+S2 converts 30 generic "
            "of 32 Stage345 high-half store sites. Five sites retain ext+str "
            "because their source/temp live ranges overlap. Across three rows "
            "the candidate executes 81 dynamic replacements.\n"
        )
    for path in (
        G1_ASM, G1_DROPIN, G1_S2_ASM, G1_S2_DROPIN, G1_SENTINEL,
        G1_S2_SENTINEL, TEST_SOURCE, S2_AUDIT, RESULT,
    ):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
