#!/usr/bin/env python3
"""Exact static gate for Q24-native D01 h x M r -> M TMVP BaseMul."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated/tile4_encap_h_d01_mixed_tmvp_gate.json"
Q = 3457
R = 1 << 16


Word = tuple[int, int]  # (leaf, quartic degree)


def unpack(a: list[Word], b: list[Word], unit: int,
           high: bool) -> list[Word]:
    """AVX2 lane-local unpack at word/dword/qword granularity."""
    out: list[Word] = []
    for lane in range(2):
        aa = a[8 * lane:8 * lane + 8]
        bb = b[8 * lane:8 * lane + 8]
        achunks = [aa[index:index + unit] for index in range(0, 8, unit)]
        bchunks = [bb[index:index + unit] for index in range(0, 8, unit)]
        half = len(achunks) // 2
        indexes = range(half, len(achunks)) if high else range(half)
        for index in indexes:
            out.extend(achunks[index])
            out.extend(bchunks[index])
    assert len(out) == 16
    return out


def pair_interleave(blocked: list[Word]) -> list[Word]:
    """One lane-local vpshufb: [four d0][four d1] -> adjacent d01."""
    out: list[Word] = []
    for lane in range(2):
        words = blocked[8 * lane:8 * lane + 8]
        for index in range(4):
            out.extend((words[index], words[index + 4]))
    return out


def labels(words: list[Word]) -> list[str]:
    return [f"L{leaf}.c{degree}" for leaf, degree in words]


def main() -> None:
    # Four Q24 packet registers, each already corrected to four AoS quartics.
    source = [[(4 * packet + leaf, degree)
               for leaf in range(4) for degree in range(4)]
              for packet in range(4)]

    # First two stages of the existing four-way transpose.
    t0 = unpack(source[0], source[1], 1, False)
    t1 = unpack(source[0], source[1], 1, True)
    t2 = unpack(source[2], source[3], 1, False)
    t3 = unpack(source[2], source[3], 1, True)
    blocked = [
        unpack(t0, t2, 2, False),  # c0/c1, even physical leaf subset
        unpack(t0, t2, 2, True),   # c2/c3, even physical leaf subset
        unpack(t1, t3, 2, False),  # c0/c1, odd physical leaf subset
        unpack(t1, t3, 2, True),   # c2/c3, odd physical leaf subset
    ]
    interleaved = [pair_interleave(vector) for vector in blocked]

    # Current M planes are the complete 12-instruction transpose.  Applying
    # vpunpckl/hwd to its c0/c1 and c2/c3 planes must equal D01 interleaved.
    m0 = unpack(blocked[0], blocked[2], 4, False)
    m1 = unpack(blocked[0], blocked[2], 4, True)
    m2 = unpack(blocked[1], blocked[3], 4, False)
    m3 = unpack(blocked[1], blocked[3], 4, True)
    consumer_d = [
        unpack(m0, m1, 1, False), unpack(m2, m3, 1, False),
        unpack(m0, m1, 1, True), unpack(m2, m3, 1, True),
    ]
    assert interleaved == consumer_d
    for index, vector in enumerate(interleaved):
        degrees = (0, 1) if index in (0, 2) else (2, 3)
        assert all(vector[position][1] == degrees[position & 1]
                   for position in range(16))

    current_decode_route_per_block = 12
    blocked_decode_route_per_block = 8
    blocked_to_vpmaddwd_per_block = 4
    blocks = 12

    # Audited current production general MxM->M loop (objdump, excluding
    # prologue/epilogue and alignment NOPs).
    current_b3_loop = 134

    # A feasible zero-stack-spill schedule retains the four H vectors and the
    # reused U0/U2 low/high rows.  Three lambda-r planes use the public output
    # block as temporary storage, as current B3 already does for raw planes.
    candidate = {
        "input_loads_h_and_r": 8,
        "blocked_D_to_adjacent_pairs": 4,
        "three_lambda_Montgomery_chains": 12,
        "lambda_plane_output_scratch_stores": 3,
        # U0/U2 can be formed while their source r planes are resident (four
        # unpacks).  Each of U1/U3/U4/U5 needs one source reload followed by
        # low/high unpacks (four times three instructions): 4 + 12 = 16.
        "six_rows_low_high_including_required_source_loads": 16,
        "eight_two_dot_outputs": 24,
        "eight_unsigned_REDC16": 32,
        "eight_dword_compact_and_order": 16,
        "four_low_high_half_merges": 4,
        "four_R2_finalizer_chains": 16,
        "final_M_stores": 4,
        "pointer_loop_control": 7,
    }
    candidate_loop = sum(candidate.values())
    assert candidate_loop == 146

    # Consumer-ready D spends the four shuffles in Decode instead of B3.
    candidate_true_d_loop = candidate_loop - blocked_to_vpmaddwd_per_block
    assert candidate_true_d_loop == 142
    current_edge = blocks * current_decode_route_per_block + blocks * current_b3_loop
    blocked_edge = (blocks * blocked_decode_route_per_block
                    + blocks * candidate_loop)
    true_d_edge = (blocks * current_decode_route_per_block
                   + blocks * candidate_true_d_loop)
    assert blocked_edge == true_d_edge

    h_bound = 3456
    r_bound = 10788
    raw_dot_bound = 4 * h_bound * r_bound
    quotient_bound = (raw_dot_bound + R - 1) // R
    redc_abs_bound = quotient_bound + (Q - 1)
    r2_factor = 867
    post_r2_bound = ((redc_abs_bound * r2_factor + R - 1) // R
                     + (Q - 1))
    assert raw_dot_bound < (1 << 31)
    assert redc_abs_bound < (1 << 15)
    assert post_r2_bound < (1 << 15)

    report = {
        "schema": "ntruplus768-gt32-encap-h-d01-mixed-tmvp-b3-v1",
        "experiment": "ENCAP-H-D01-MIXED-TMVP-B3-001",
        "scope": "generator-only Q24(h)->D01 x M(r)->M edge gate",
        "frozen": [
            "Forward-r-to-current-M", "final-M-and-Q24-serializer",
            "quartic-ring-and-lambda-semantics", "Encap-caller-and-hash-glue",
        ],
        "physical_proof": {
            "q24_packet_registers": [labels(vector) for vector in source],
            "D01_blocked_after_8_transpose_instructions": [
                labels(vector) for vector in blocked],
            "D01_consumer_ready_after_4_vpshufb": [
                labels(vector) for vector in interleaved],
            "M_vpunpck_pair_view": [labels(vector) for vector in consumer_d],
            "consumer_ready_D_equals_vpunpck_view_of_M": True,
        },
        "gate_A_decoder": {
            "current_M_route_instructions_per_block": current_decode_route_per_block,
            "blocked_D_route_instructions_per_block": blocked_decode_route_per_block,
            "decoder_saving_per_polynomial": blocks * (
                current_decode_route_per_block - blocked_decode_route_per_block),
            "blocked_D_consumer_pair_shuffles_per_polynomial": blocks * blocked_to_vpmaddwd_per_block,
            "net_edge_representation_saving": 0,
            "interpretation": (
                "stopping after the word+dword transpose saves four qword "
                "unpacks, but vpmaddwd requires four lane-local pair shuffles"
            ),
        },
        "gate_B_complete_mixed_B3": {
            "current_general_MxM_to_M_loop_instructions": current_b3_loop,
            "candidate_blocked_DxM_to_M_loop_instructions": candidate_loop,
            "candidate_consumer_ready_DxM_to_M_loop_instructions": candidate_true_d_loop,
            "candidate_breakdown": candidate,
            "edge_instructions": {
                "current": current_edge,
                "blocked_D": blocked_edge,
                "consumer_ready_D": true_d_edge,
                "candidate_minus_current": blocked_edge - current_edge,
            },
            "mandatory_costs_that_the_proposal_omitted": [
                "six row vectors must be formed for both 8-leaf halves and four rows require source reloads",
                "each REDC16 half needs dword compaction and ordering",
                "two halves must merge before the full-width R2 finalizer",
                "three lambda-r planes cannot coexist with all inputs and reusable rows",
                "the general e0 output requires four R2 Montgomery finalizers",
            ],
        },
        "gate_C_register_schedule": {
            "ideal_all_inputs_lambda_rows_peak_ymm_lower_bound": 19,
            "ideal_all_resident_spill_free": False,
            "output_scratch_schedule_peak_ymm": 13,
            "output_scratch_vectors": 3,
            "stack_spills": 0,
            "reused_rows": ["U0-low/high", "U2-low/high"],
            "interpretation": "zero stack spill is feasible, but costs three lambda-plane stores",
        },
        "range": {
            "h_canonical_abs_bound": h_bound,
            "r_M_abs_bound": r_bound,
            "four_term_int32_bound": raw_dot_bound,
            "signed_int32_safe": True,
            "unsigned_REDC16_conservative_abs_bound": redc_abs_bound,
            "post_R2_conservative_abs_bound": post_r2_bound,
            "signed_int16_safe": True,
            "scale": "e0-times-e0-through-REDC16=e-1; mandatory-R2-finalizer-to-e0",
        },
        "decision": "static-hard-stop-before-assembly",
        "reason": [
            "Q24-native blocked D saves 48 decoder instructions but B3 repays the same 48 pair shuffles",
            "consumer-ready D costs the same 12-instruction route as current M",
            "complete zero-spill mixed TMVP edge is 96 instructions larger than current Decode-route plus B3",
            "the ideal all-resident schedule exceeds AVX2 by three YMM registers",
            "the executable 13-YMM schedule needs output-scratch lambda materialization",
        ],
        "assembly_emitted": False,
        "reopen_only_if": [
            "a decoder shuffle directly emits adjacent D pairs before the eight-instruction blocked transpose",
            "a REDC packs both 8-leaf halves without compact/order work",
            "the consumer accepts e-1 output and deletes all four R2 finalizers",
            "a wider ISA removes the register and half-merge constraints",
        ],
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "decoder_saving": report["gate_A_decoder"]["decoder_saving_per_polynomial"],
        "representation_net": report["gate_A_decoder"]["net_edge_representation_saving"],
        "candidate_minus_current": blocked_edge - current_edge,
        "peak_ymm": report["gate_C_register_schedule"]["output_scratch_schedule_peak_ymm"],
        "decision": report["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
