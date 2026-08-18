#!/usr/bin/env python3
"""Generate the GT32 four-instance twiddle-major static gate.

This script reads the selected GT Clean frontend tables but never edits or
links production sources.  It proves the proposed data/table permutation and
emits the static AVX2 accounting used to decide whether an ASM probe is legal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


VECTOR_WORDS = 16
QWORD_WORDS = 4
INSTANCES = 16
ROLES = 3
BATCH = 4


def parse_table(source: str, label: str) -> list[int]:
    match = re.search(
        rf"^{re.escape(label)}:\n(?P<body>.*?)(?=^\s*\.section )",
        source,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise ValueError(f"table label not found: {label}")
    values: list[int] = []
    for line in match.group("body").splitlines():
        line = line.strip()
        if not line.startswith(".short"):
            continue
        values.extend(int(value) for value in line[6:].split(","))
    return values


def vectors(values: list[int]) -> list[list[int]]:
    if len(values) % VECTOR_WORDS:
        raise ValueError(f"table has {len(values)} words, not whole YMMs")
    return [
        values[offset : offset + VECTOR_WORDS]
        for offset in range(0, len(values), VECTOR_WORDS)
    ]


def scalar_qwords(vector: list[int]) -> list[int]:
    result: list[int] = []
    for qword in range(4):
        group = vector[qword * QWORD_WORDS : (qword + 1) * QWORD_WORDS]
        if len(set(group)) != 1:
            raise ValueError(f"factor qword is not replicated: {group}")
        result.append(group[0])
    return result


def table_vector_index(instance: int, role: int) -> int:
    # The selected frontend emits two independent DFT3 instances per
    # iteration.  Its wide table is [instance0.X/Y/Z, instance1.X/Y/Z, ...].
    return instance * ROLES + role


def compact_table(table: list[list[int]]) -> tuple[list[list[int]], list[dict]]:
    if len(table) != INSTANCES * ROLES:
        raise ValueError(f"expected 48 table vectors, got {len(table)}")
    compact: list[list[int]] = []
    manifest: list[dict] = []
    for batch_start in range(0, INSTANCES, BATCH):
        for role in range(ROLES):
            source_indices = [
                table_vector_index(instance, role)
                for instance in range(batch_start, batch_start + BATCH)
            ]
            packed = [
                value
                for index in source_indices
                for value in scalar_qwords(table[index])
            ]
            if len(packed) != VECTOR_WORDS:
                raise AssertionError("compact vector is not one YMM")
            compact.append(packed)
            manifest.append(
                {
                    "batch_instances": list(range(batch_start, batch_start + BATCH)),
                    "role": role,
                    "source_vector_indices": source_indices,
                    "values": packed,
                }
            )
    return compact, manifest


def transpose_mapping() -> dict:
    # R_i contains lanes R_i[4*j+k].  T_k packs the same k from all four
    # instances: T_k[4*i+j] = R_i[4*j+k].
    direct = []
    inverse = []
    for k in range(4):
        lanes = []
        for i in range(4):
            for j in range(4):
                lanes.append({"source_register": i, "source_lane": 4 * j + k})
        direct.append(lanes)
    for i in range(4):
        lanes = []
        for j in range(4):
            for k in range(4):
                lanes.append({"source_register": k, "source_lane": 4 * i + j})
        inverse.append(lanes)
    return {"direct": direct, "inverse": inverse}


def apply_mapping(inputs: list[list[int]], mapping: list[list[dict]]) -> list[list[int]]:
    return [
        [inputs[item["source_register"]][item["source_lane"]] for item in output]
        for output in mapping
    ]


def prove_lane_products(
    original: list[list[int]], compact: list[list[int]], manifest: list[dict]
) -> int:
    mapping = transpose_mapping()["direct"]
    checks = 0
    for compact_vector, item in zip(compact, manifest):
        source_indices = item["source_vector_indices"]
        source_data = [
            [10000 * source_index + lane for lane in range(VECTOR_WORDS)]
            for source_index in source_indices
        ]
        transposed = apply_mapping(source_data, mapping)
        old_products = [
            [source_data[i][lane] * original[index][lane] for lane in range(16)]
            for i, index in enumerate(source_indices)
        ]
        new_products = [
            [transposed[k][lane] * compact_vector[lane] for lane in range(16)]
            for k in range(4)
        ]
        recovered = apply_mapping(new_products, transpose_mapping()["inverse"])
        if recovered != old_products:
            raise AssertionError(f"lane product proof failed for {item}")
        checks += 64
    return checks


def instruction_accounting() -> dict:
    batches = INSTANCES // BATCH
    compact_groups = batches * ROLES
    # A constructive current-layout transpose uses, per four-register role:
    #   4 VPSHUFB + 4 VPERMD + 4 VPUNPCKQDQ + 4 VPERM2I128 = 16.
    transpose_instructions = 16
    current_constant_operands = INSTANCES * ROLES * 2
    compact_explicit_loads = compact_groups * 2
    input_transposes = compact_groups
    output_transposes = batches * ROLES
    return {
        "per_frontend": {
            "independent_dft3_instances": INSTANCES,
            "current_active_table_bytes": current_constant_operands * 32,
            "compact_active_table_bytes": compact_explicit_loads * 32,
            "table_byte_saving": (current_constant_operands - compact_explicit_loads) * 32,
            "current_qinv_factor_memory_operands": current_constant_operands,
            "compact_qinv_factor_explicit_loads": compact_explicit_loads,
            "constant_load_reduction": current_constant_operands - compact_explicit_loads,
            "montgomery_vector_multiply_count_change": 0,
        },
        "constructive_transpose_network": {
            "instructions_per_four_register_role": transpose_instructions,
            "stages": [
                {"instruction": "vpshufb", "count": 4},
                {"instruction": "vpermd", "count": 4, "requires_live_index_vector": True},
                {"instruction": "vpunpcklqdq/vpunpckhqdq", "count": 4},
                {"instruction": "vperm2i128", "count": 4},
            ],
        },
        "scenarios": {
            "current_producer_and_current_consumer": {
                "input_transpose_instructions": input_transposes * transpose_instructions,
                "output_repair_instructions": output_transposes * transpose_instructions,
                "explicit_constant_load_instructions": compact_explicit_loads,
                "net_extra_instructions":
                    (input_transposes + output_transposes) * transpose_instructions
                    + compact_explicit_loads,
                "eligible_for_asm": False,
                "reason": "table-load saving is dominated by two full transpose boundaries",
            },
            "current_producer_persistent_twiddle_major_consumer": {
                "input_transpose_instructions": input_transposes * transpose_instructions,
                "output_repair_instructions": 0,
                "explicit_constant_load_instructions": compact_explicit_loads,
                "net_extra_instructions": input_transposes * transpose_instructions
                + compact_explicit_loads,
                "eligible_for_asm": False,
                "reason": "producer still pays twelve explicit four-register transpose networks",
            },
            "producer_and_consumer_native": {
                "input_transpose_instructions": 0,
                "output_repair_instructions": 0,
                "explicit_constant_load_instructions": compact_explicit_loads,
                "net_extra_instructions": compact_explicit_loads,
                "memory_operand_reduction": current_constant_operands - compact_explicit_loads,
                "eligible_for_asm": False,
                "reason": "requires a producer liveness proof before assembly",
                "reopen_condition": [
                    "frontend directly produces four-instance same-role packets",
                    "peak live YMM <= 15 with no spills or role materialization",
                    "NTT32 and terminal consumers retain the layout without a global repair",
                    "caller-weighted model predicts at least 20 core-cycle saving",
                ],
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ntt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source = args.ntt.read_text()
    raw_tables = {
        "qinv": vectors(parse_table(source, ".Ltile4_frontend_wide_twist_qinv")),
        "factor": vectors(parse_table(source, ".Ltile4_frontend_wide_twist_factor")),
    }
    generated = {}
    proof_checks = 0
    for name, table in raw_tables.items():
        compact, manifest = compact_table(table)
        proof_checks += prove_lane_products(table, compact, manifest)
        generated[name] = {
            "original_vectors": len(table),
            "compact_vectors": len(compact),
            "manifest": manifest,
        }

    result = {
        "experiment": "GT32-TWIDDLE-MAJOR-SIMD-001",
        "status": "generator_only_static_stop",
        "production_modified": False,
        "source": str(args.ntt.resolve()),
        "source_sha256": hashlib.sha256(args.ntt.read_bytes()).hexdigest(),
        "layout": {
            "input": "R_i[4*j+k]",
            "output": "T_k[4*i+j] = R_i[4*j+k]",
            "instances_per_batch": BATCH,
            "dft3_roles": ROLES,
        },
        "proof": {
            "lane_product_checks": proof_checks,
            "qinv_and_factor_exact": True,
            "inverse_mapping_exact": True,
            "montgomery_chain_count_unchanged": True,
        },
        "tables": generated,
        "cost": instruction_accounting(),
        "decision": {
            "current_abi": "hard_stop_before_assembly",
            "persistent_layout": "hard_stop_with_current_producer",
            "producer_native": "reopen_after_register_liveness_and_full-consumer proof",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
