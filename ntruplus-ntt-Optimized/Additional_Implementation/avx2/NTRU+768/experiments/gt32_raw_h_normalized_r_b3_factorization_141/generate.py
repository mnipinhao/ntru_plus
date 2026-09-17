#!/usr/bin/env python3
"""Static/oracle gate for RAW-H / NORMALIZED-R asymmetric B3 cuts.

This does not benchmark or generate assembly.  It checks the semantic cuts of
the existing four-register Q24 transpose and accounts for routing that must be
paid either by the decoder or by the B3 consumer.
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

Q = 3457
GROUPS = 12
LANES = 16


def unpack(a: list[int], b: list[int], elem_words: int, high: bool) -> list[int]:
    """Exact AVX2 unpack semantics, independently in each 128-bit half."""
    out: list[int] = []
    elems_per_half = 8 // elem_words
    begin = elems_per_half // 2 if high else 0
    end = elems_per_half if high else elems_per_half // 2
    for half in range(2):
        base = half * 8
        for element in range(begin, end):
            lo = base + element * elem_words
            hi = lo + elem_words
            out.extend(a[lo:hi])
            out.extend(b[lo:hi])
    assert len(out) == 16
    return out


def transpose_stage(rows: list[list[int]], stage: int) -> list[list[int]]:
    """Exact word/dword/qword layer used by Q24_TRANSPOSE/TILE4_TRANSPOSE."""
    a, b, c, d = rows
    if stage == 0:
        return [unpack(a, b, 1, False), unpack(a, b, 1, True),
                unpack(c, d, 1, False), unpack(c, d, 1, True)]
    if stage == 1:
        return [unpack(a, c, 2, False), unpack(a, c, 2, True),
                unpack(b, d, 2, False), unpack(b, d, 2, True)]
    if stage == 2:
        return [unpack(a, c, 4, False), unpack(a, c, 4, True),
                unpack(b, d, 4, False), unpack(b, d, 4, True)]
    raise ValueError(stage)


def apply_stages(rows: list[list[int]], n: int) -> list[list[int]]:
    out = [row[:] for row in rows]
    for stage in range(n):
        out = transpose_stage(out, stage)
    return out


def finish_from_cut(rows: list[list[int]], cut: int) -> list[list[int]]:
    out = [row[:] for row in rows]
    for stage in range(cut, 3):
        out = transpose_stage(out, stage)
    return out


def center(x: int) -> int:
    return x - Q if x > Q // 2 else x


def quartic(a: list[int], b: list[int], lam: int) -> list[int]:
    out = [0] * 4
    for i in range(4):
        for j in range(4):
            degree = i + j
            factor = 1
            if degree >= 4:
                degree -= 4
                factor = lam
            out[degree] = (out[degree] + factor * a[i] * b[j]) % Q
    return out


def macro(source: str, name: str) -> str:
    match = re.search(
        rf"(?ms)^\s*\.macro {re.escape(name)}(?: .*?)?\n(.*?)^\s*\.endm$",
        source,
    )
    if not match:
        raise RuntimeError(f"macro not found: {name}")
    return match.group(1)


def main() -> None:
    rng = random.Random(141)
    here = Path(__file__).resolve().parent
    production = here.parent.parent
    pack_source = (production / "pack.s").read_text()
    b3_source = (production / "basemul.s").read_text()
    transpose = macro(pack_source, "Q24_TRANSPOSE")
    decode_reg = macro(pack_source, "Q24_DECODE_REG")
    decode_soa = macro(pack_source, "Q24_DECODE_SOA_BODY")
    input_a_soa = macro(b3_source, "TILE4_INPUT_A_SOA")
    input_a_aos = macro(b3_source, "TILE4_INPUT_A_AOS")
    transpose_routes = sum(
        line.lstrip().startswith("vpunpck") for line in transpose.splitlines()
    )
    decode_groups = sum(
        line.lstrip().startswith("Q24_TRANSPOSE ") for line in decode_soa.splitlines()
    )
    assert transpose_routes == 12
    assert decode_groups == GROUPS
    assert "Q24_TRANSPOSE" not in input_a_soa
    assert "TILE4_TRANSPOSE" in input_a_aos
    assert not any(op in decode_reg for op in ("vpmulhrsw", "vpmullw", "vpmulhw"))
    oracle_cases = 0
    canonicality_cases = 0
    raw_center_cases = 0

    # Every cut followed by the missing stages reaches the same B3 input.
    for _ in range(2000):
        rows = [[rng.randrange(0, Q) for _ in range(LANES)] for _ in range(4)]
        final = apply_stages(rows, 3)
        for cut in range(4):
            state = apply_stages(rows, cut)
            assert finish_from_cut(state, cut) == final
            assert max(max(row) for row in state) == max(max(row) for row in rows)
            oracle_cases += 1

    # Canonicality is accumulated immediately after 12-bit extraction.  A
    # later permutation cannot alter the maximum or the invalid predicate.
    for _ in range(2000):
        rows = [[rng.randrange(0, 4096) for _ in range(LANES)] for _ in range(4)]
        invalid = any(x >= Q for row in rows for x in row)
        for cut in range(4):
            state = apply_stages(rows, cut)
            assert any(x >= Q for row in state for x in row) == invalid
            canonicality_cases += 1

    # The current decoder stores canonical, non-centred residues.  B3 already
    # consumes those residues.  Centering h would be congruent but does not
    # delete a current operation because no such centering exists today.
    for _ in range(10000):
        h = [rng.randrange(0, Q) for _ in range(4)]
        r = [rng.randrange(-10788, 10789) % Q for _ in range(4)]
        lam = rng.randrange(0, Q)
        assert quartic(h, r, lam) == quartic([center(x) for x in h], r, lam)
        raw_center_cases += 1

    cuts = []
    names = ["RAW_PACKET", "P1_WORD", "P2_DWORD", "M_SOA"]
    for cut, name in enumerate(names):
        decoder_routes_per_group = 4 * cut
        b3_routes_per_group = 4 * (3 - cut)
        cuts.append(
            {
                "presentation": name,
                "decoder_route_instructions": GROUPS * decoder_routes_per_group,
                "b3_route_instructions": GROUPS * b3_routes_per_group,
                "total_route_instructions": GROUPS
                * (decoder_routes_per_group + b3_routes_per_group),
                "modular_reductions_deleted": 0,
                "peak_ymm_upper_bound": 16,
                "zero_spill_feasible": True,
            }
        )

    report = {
        "experiment": 141,
        "title": "RAW-H / NORMALIZED-R ASYMMETRIC B3 FACTORIZATION",
        "facts": {
            "decoded_h_range": [0, Q - 1],
            "decoded_h_is_centered": False,
            "decoder_modular_reductions": 0,
            "canonicality_before_transpose": True,
            "current_b3_already_accepts_raw_h": True,
            "groups": GROUPS,
            "source_audit": {
                "q24_transpose_routes_per_group": transpose_routes,
                "decode_groups": decode_groups,
                "decode_reg_has_modular_multiply": False,
                "current_b3_soa_input_has_transpose": False,
                "aos_b3_input_requires_transpose": True,
            },
        },
        "oracle": {
            "cut_completion_cases": oracle_cases,
            "canonicality_cases": canonicality_cases,
            "raw_vs_centered_b3_cases": raw_center_cases,
            "status": "PASS",
        },
        "cuts": cuts,
        "constant_absorption": {
            "possible_for_mod_q_representative_change": True,
            "useful_operation_deleted": False,
            "possible_for_remaining_lane_permutation": False,
            "reason": "A diagonal lane-wise constant cannot implement a non-identity lane permutation.",
        },
        "decision": {
            "executable_candidate": False,
            "status": "STATIC_NO_OPERATION_CLASS_DELETION",
            "reason": "All legal cuts move the same 144 dynamic routing instructions between decode and B3; current decode has no reduction/centering to absorb.",
            "reopen": "A new asymmetric tensor must consume a pre-transpose packet presentation without recreating the missing 144-route layer, or delete a separate B3 Montgomery/reduction class.",
        },
    }

    generated = here / "generated"
    generated.mkdir(exist_ok=True)
    (generated / "report.json").write_text(json.dumps(report, indent=2) + "\n")

    lines = [
        "# Experiment 141 generated result",
        "",
        "| cut | decoder routes | B3 routes | total | reductions deleted | peak YMM |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in cuts:
        lines.append(
            f"| {item['presentation']} | {item['decoder_route_instructions']} | "
            f"{item['b3_route_instructions']} | {item['total_route_instructions']} | "
            f"{item['modular_reductions_deleted']} | {item['peak_ymm_upper_bound']} |"
        )
    lines += [
        "",
        "Result: **STATIC_NO_OPERATION_CLASS_DELETION**.",
        "",
        "The current decoder already preserves canonical raw h residues; it does not center or reduce them. "
        "Moving the three transpose layers merely transfers 144 dynamic routes from decode to B3.",
    ]
    (generated / "REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
