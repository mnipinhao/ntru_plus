#!/usr/bin/env python3
"""Generate a compact three-stream progressive-P Q24 serializer probe."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "generated/tile4_q24_p_encode_gate.json"
ASM = ROOT / "generated/tile4_q24_pack3_compact.inc"
META = ROOT / "generated/tile4_q24_pack3_compact_gate.json"


def emit_group(group: dict, label: str) -> list[str]:
    block = group["P_block"]
    halves = group["source_halves"]
    orientations: list[int] = []
    residuals: list[str | None] = []
    for register in range(4, 8):
        swaps = tuple(bool(halves[f"ymm{register}.{half}"]["swap_qwords"])
                      for half in ("low", "high"))
        orientations.append(int(swaps == (True, True)))
        residuals.append(
            f".Lq24_p_half_mask_{int(swaps[0])}{int(swaps[1])}"
            if swaps in ((False, True), (True, False)) else None)

    lines = [f"{label}:"]
    for lane in range(4):
        lines.append(f"\tvmovdqu {128 * block + 32 * lane}(%rsi), %ymm{lane}")
    lines.append(
        "\tQ24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7," +
        ",".join(map(str, orientations)))
    for register, mask in zip(range(4, 8), residuals):
        if mask is not None:
            lines.append(f"\tvpshufb {mask}(%rip), %ymm{register}, %ymm{register}")
    lines.append("\tQ24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7")
    for store in group["packet_stores"]:
        low_register, low_half = store["low_source"]
        high_register, high_half = store["high_source"]
        packet = store["packet"]
        lines.append(
            "\tQ24_STORE_SCATTER_PACKET "
            f"%ymm{low_register},%xmm{low_register},{low_half},"
            f"%ymm{high_register},%xmm{high_register},{high_half},"
            f"{24 * packet},{int(packet == 47)}")
    lines.append("\tret")
    return lines


def main() -> None:
    source = json.loads(SOURCE.read_text())
    groups = source["D2_half_native_scatter"]["groups"]
    lines = [
        "/* Generated compact three-stream TF1 schedule. */",
        ".macro Q24_ENCODE_P_SOA_PACK3_COMPACT_BODY",
        "\tpushq %r12",
        "\tpushq %r13",
        "\tpushq %r14",
        "\tpushq %r15",
        "\tmovq %rdi, %r10",
        "\tmovq %rsi, %r11",
        "\tmovq %rdx, %r12",
        "\tmovq %rcx, %r13",
        "\tmovq %r8, %r14",
        "\tmovq %r9, %r15",
    ]
    for index in range(len(groups)):
        label = f".Lq24_pack3_group_{index}_\\@"
        for out_reg, in_reg in (("r10", "r11"), ("r12", "r13"),
                                ("r14", "r15")):
            lines.extend([
                f"\tmovq %{out_reg}, %rdi",
                f"\tmovq %{in_reg}, %rsi",
                f"\tcall {label}",
            ])
    lines.extend([
        "\tjmp .Lq24_pack3_done_\\@",
    ])
    for index, group in enumerate(groups):
        lines.extend(emit_group(group, f".Lq24_pack3_group_{index}_\\@"))
    lines.extend([
        ".Lq24_pack3_done_\\@:",
        "\tpopq %r15",
        "\tpopq %r14",
        "\tpopq %r13",
        "\tpopq %r12",
        ".endm",
        "",
    ])
    ASM.write_text("\n".join(lines))

    dynamic_overhead = {
        "callee_saved_push_pop": 8,
        "pointer_preservation_moves": 6,
        "per_group_stream_moves": 72,
        "per_group_calls_and_returns": 72,
        "terminal_jump": 1,
    }
    META.write_text(json.dumps({
        "schema": "ntruplus768-gt32-q24-pack3-compact-v1",
        "experiment": "GT32-KEYGEN-Q24-PACK3-P2-001",
        "control": "three calls to reusable TF1 serializer",
        "candidate": "twelve shared TF1 group bodies, each called for h/f/hinv",
        "streams": 3,
        "groups": 12,
        "serializer_arithmetic_changed": False,
        "wire_mapping_changed": False,
        "range_or_scale_changed": False,
        "tripled_unrolled_body": False,
        "expected_code_footprint": "approximately one TF1 body plus dispatch",
        "dynamic_control_overhead": dynamic_overhead,
        "dynamic_control_overhead_total": sum(dynamic_overhead.values()),
        "instructions_eliminated": {
            "duplicate_constant_loads": 4,
            "intermediate_vzeroupper": 2,
        },
        "acceleration_mechanism": "cross-stream latency overlap only",
        "assembly_eligible": True,
        "implementation": {
            "candidate_symbol_bytes": 4723,
            "tf1_symbol_bytes": 4276,
            "tripled_body_avoided": True,
        },
        "correctness": {
            "random_trials": 1000,
            "byte_exact_three_stream_output": "pass",
        },
        "benchmark": {
            "iterations": 10000,
            "paired_repeats": 20,
            "normal": {
                "core_cycle_delta": 52.330,
                "core_cycle_bootstrap_95_ci": [40.447, 70.346],
                "candidate_wins": "1/20",
                "instruction_delta": 165.915,
                "load_delta": 37.348,
                "store_delta": 43.192,
                "tsc_delta": 35.180,
            },
            "reversed": {
                "core_cycle_delta": 62.058,
                "core_cycle_bootstrap_95_ci": [38.832, 80.640],
                "candidate_wins": "4/20",
                "instruction_delta": 177.688,
                "load_delta": 38.460,
                "store_delta": 44.030,
                "tsc_delta": 37.040,
            },
        },
        "continuation_gate": "at least 60 core cycles saving in both placements",
        "gate_result": "hard-stop",
        "decision": [
            "compact shared code footprint does not create useful cross-stream overlap",
            "group call-return and pointer dispatch retire more work than three reusable TF1 calls",
            "do not run whole Keygen or SUPERcop",
            "retain TF1 as the local three-polynomial serializer control",
        ],
        "reopen_only_if": [
            "one packet kernel consumes all three streams without per-group calls or tripled code",
            "a downstream consumer removes another complete materialized boundary",
            "target ISA or microarchitecture changes",
        ],
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
