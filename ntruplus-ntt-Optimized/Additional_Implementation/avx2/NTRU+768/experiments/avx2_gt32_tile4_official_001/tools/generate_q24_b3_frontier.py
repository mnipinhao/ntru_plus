#!/usr/bin/env python3
"""Generate the benchmark-only Q24 Decode2 -> first scale-B3 frontier."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
Q24 = ROOT / "generated/tile4_q24_codec.json"
OUT_JSON = ROOT / "generated/tile4_q24_b3_frontier_gate.json"
OUT_ASM = ROOT / "generated/tile4_q24_b3_frontier.inc"


def main() -> None:
    packets = json.loads(Q24.read_text())["packets_detail"]
    assert len(packets) == 48

    groups: list[dict] = []
    seen_blocks: list[int] = []
    asm = ["/* Generated Q24 Decode2 -> scale-B3 groups; do not edit. */"]
    for group in range(12):
        records = packets[4 * group:4 * group + 4]
        blocks = {record["destination_vector"] // 4 for record in records}
        assert len(blocks) == 1
        block = blocks.pop()
        registers = [record["destination_vector"] % 4
                     for record in records]
        assert sorted(registers) == [0, 1, 2, 3]
        seen_blocks.append(block)

        compact_records = []
        asm.extend(["", f"/* wire group {group} -> B3 block {block} */",
                    "vmovdqa .Lq24_b3_low12(%rip), %ymm13"])
        for base in ("rsi", "rdx"):
            for record in records:
                destination = 5 + record["destination_vector"] % 4
                asm.append(
                    "Q24_B3_DECODE_PACKET "
                    f"{record['low_load_offset']},"
                    f"{record['high_load_offset']},"
                    f"{int(record['low_load_safe12'])},"
                    f"{int(record['high_load_safe12'])},"
                    f"{record['mask_label']},{base},ymm{destination}"
                )
                compact_records.append({
                    "packet": record["packet"],
                    "destination_register": destination,
                    "base": base,
                    "low": record["low_load_offset"],
                    "high": record["high_load_offset"],
                    "safe_low": record["low_load_safe12"],
                    "safe_high": record["high_load_safe12"],
                    "mask": record["mask_label"],
                })
            asm.append("Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8")
            outputs = "ymm1,ymm2,ymm3,ymm4" if base == "rsi" \
                else "ymm9,ymm10,ymm11,ymm12"
            asm.append(
                "Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8," + outputs
            )
        asm.append(f"Q24_B3_SCALE_BLOCK {128 * block},{32 * block}")
        groups.append({
            "wire_group": group,
            "b3_block": block,
            "output_byte_offset": 128 * block,
            "lambda_byte_offset": 32 * block,
            "packet_register_bijection": registers,
            "decode_records": compact_records,
        })

    assert sorted(seen_blocks) == list(range(12))
    assert seen_blocks == [0, 1, 9, 8, 4, 5, 11, 10, 6, 7, 3, 2]

    # Current Decode2 writes 4 planes per operand/block; B3 immediately
    # reloads the same 8 planes.  The stream keeps both sets in registers.
    materialized_stores = 2 * 12 * 4
    consumer_reloads = 12 * 8
    removed_materialization_ops = materialized_stores + consumer_reloads

    # Current decoder: four persistent vpmaxuw chains plus one final fold per
    # input.  Streaming frees those registers by reducing each four-packet
    # group to a public failure mask before B3.  This adds 18 instructions per
    # operand over the current validity path.  B3 clobbers the low12 register,
    # so ten additional low12 reloads are required.  Twenty-two additional
    # qm1 memory operands are folded into the validity instructions.
    validity_instruction_debt = 36
    low12_reload_instruction_debt = 10
    instruction_saving_lower_bound = (
        removed_materialization_ops
        - validity_instruction_debt
        - low12_reload_instruction_debt
    )
    additional_qm1_memory_operands = 22
    net_memory_operands_removed = (
        removed_materialization_ops
        - low12_reload_instruction_debt
        - additional_qm1_memory_operands
    )

    result = {
        "schema": "ntruplus768-gt32-q24-b3-frontier-v1",
        "experiment": "GT32-Q24-DECODE2-B3-FRONTIER-001",
        "scope": "Q24 Decode(c,f) -> first scale-B3 only; hinv unchanged",
        "proof": {
            "q24_packets_per_frontier": 4,
            "quartics_per_b3_block": 16,
            "wire_groups": 12,
            "b3_blocks": 12,
            "wire_group_to_b3_block": seen_blocks,
            "block_mapping_bijective": True,
            "quartic_products_independent_across_blocks": True,
            "lambda_selected_by_b3_block": True,
            "scale": "e0-times-e0-to-e-minus1",
            "range_contract": "unchanged-canonical-Q24-input-to-B3",
        },
        "register_plan": {
            "ymm0": "q",
            "ymm1_to_ymm4": "decoded-c coefficient planes / B3 A",
            "ymm5_to_ymm8": "packet decode / A*qinv temporaries",
            "ymm9_to_ymm12": "decoded-f coefficient planes / B3 B",
            "ymm13_to_ymm15": "low12/decode temporaries then B3 temporaries",
            "peak_ymm": 16,
            "spill_required": False,
            "persistent_vector_validity_state": False,
            "failure_state": "public fixed-scan GPR accumulator",
        },
        "memory_accounting": {
            "decode2_private_soa_stores_removed": materialized_stores,
            "b3_input_reloads_removed": consumer_reloads,
            "materialization_vector_memory_ops_removed":
                removed_materialization_ops,
            "materialization_bytes_removed": 6144,
            "additional_low12_vector_loads": low12_reload_instruction_debt,
            "additional_qm1_memory_operands":
                additional_qm1_memory_operands,
            "net_memory_operands_removed_lower_bound":
                net_memory_operands_removed,
        },
        "instruction_accounting": {
            "materialization_instructions_removed":
                removed_materialization_ops,
            "streaming_validity_instruction_debt":
                validity_instruction_debt,
            "low12_reload_instruction_debt":
                low12_reload_instruction_debt,
            "dynamic_instruction_saving_lower_bound":
                instruction_saving_lower_bound,
            "B3_arithmetic_sequence_changed": False,
            "Q24_packet_math_changed": False,
        },
        "groups": groups,
        "assembly_eligible": instruction_saving_lower_bound >= 128,
        "decision": "emit-benchmark-only-streaming-probe",
        "continuation_gate": {
            "minimum_saving_tsc": 30,
            "minimum_negative_launch_fraction": 0.90,
            "bootstrap_95ci_upper_below_zero": True,
            "full_first_product_word_exact": True,
            "no_spill": True,
        },
        "hard_stop_if_probe_fails": (
            "stop-decap-micro-optimization-and-shift-to-keygen-encap"
        ),
    }
    assert result["assembly_eligible"]
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")
    OUT_ASM.write_text("\n".join(asm) + "\n")
    print(json.dumps({
        "decision": result["decision"],
        "blocks": seen_blocks,
        "materialization_ops_removed": removed_materialization_ops,
        "instruction_saving_lower_bound": instruction_saving_lower_bound,
        "peak_ymm": 16,
    }))


if __name__ == "__main__":
    main()
