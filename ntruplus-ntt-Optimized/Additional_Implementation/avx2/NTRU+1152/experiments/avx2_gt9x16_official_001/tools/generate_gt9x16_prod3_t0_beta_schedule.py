#!/usr/bin/env python3
"""Lower T0 beta absorption to an exact frozen-PROD3 schedule and constants."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
STAGES = (("distance8", 8), ("distance4", 4),
          ("distance2", 2), ("distance1", 1))


def signed16(value: int) -> int:
    value &= 0xffff
    return value - 0x10000 if value >= 0x8000 else value


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def montgomery_constant(value: int) -> int:
    return centered(value * R)


def montgomery_reduce(value: int, constant: int) -> int:
    low = signed16(signed16(value * constant) * QINV)
    return (value * constant - low * Q) >> 16


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, contents: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != contents:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(contents, encoding="utf-8")


def emit_vector(lines: list[str], label: str, values: list[int]) -> None:
    if len(values) != 16:
        raise SystemExit(f"bad YMM constant width for {label}")
    lines.extend((".p2align 5", f"{label}:",
                  "  .word " + ", ".join(map(str, values))))


def packed(values: list[int], width: int) -> list[int]:
    result = [value for value in values for _ in range(width)]
    if len(result) != 16:
        raise SystemExit("bad packed constant geometry")
    return result


def stage_vectors(values: list[int]) -> list[tuple[str, list[int]]]:
    if len(values) == 1:
        return [("", packed(values, 16))]
    if len(values) == 2:
        return [("_lo", [values[0]] * 16), ("_hi", [values[1]] * 16)]
    if len(values) == 4:
        return [("_lo", packed(values[:2], 8)),
                ("_hi", packed(values[2:], 8))]
    if len(values) == 8:
        return [("_lo", packed(values[:4], 4)),
                ("_hi", packed(values[4:], 4))]
    raise SystemExit(f"unsupported stage width {len(values)}")


def interval_paths(value: object, prefix: str = "") -> list[tuple[str, list[int]]]:
    result: list[tuple[str, list[int]]] = []
    if (isinstance(value, list) and len(value) == 2 and
            all(isinstance(item, int) for item in value)):
        result.append((prefix, value))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            result.extend(interval_paths(item, f"{prefix}[{index}]"))
    elif isinstance(value, dict):
        for key, item in value.items():
            result.extend(interval_paths(item, f"{prefix}.{key}" if prefix else key))
    return result


def count_labels(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, re.MULTILINE))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--natural-audit", type=Path, required=True)
    parser.add_argument("--full-audit", type=Path, required=True)
    parser.add_argument("--producer-source", type=Path, required=True)
    parser.add_argument("--branch0-constants", type=Path, required=True)
    parser.add_argument("--branch1-constants", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--asm-constants", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    mapping = json.loads(args.map.read_text(encoding="utf-8"))
    scaled = json.loads(args.scaled_oracle.read_text(encoding="utf-8"))
    natural = json.loads(args.natural_audit.read_text(encoding="utf-8"))
    full_audit = json.loads(args.full_audit.read_text(encoding="utf-8"))
    source = args.producer_source.read_text(encoding="utf-8")
    b0_constants = args.branch0_constants.read_text(encoding="utf-8")
    b1_constants = args.branch1_constants.read_text(encoding="utf-8")

    if mapping["selected_candidate"]["name"] != "T0-BETA-TO-RADIX2":
        raise SystemExit("T0 absorption candidate changed")
    if mapping["chain_ledger_per_forward"]["delta"]["total"] != -8:
        raise SystemExit("T0 chain gate changed")
    if mapping["frozen_contract"]["qorder"] != "C1-natural-Q":
        raise SystemExit("Natural-Q is no longer frozen")
    if natural["component"]["producer_natural"]["instruction_count"] != 2819:
        raise SystemExit("frozen Natural-Q producer instruction count changed")
    required_source = (
        "PROD3_LOAD_TWIST \\branch,\\base,0,\\qblock,7",
        "PROD3_LOAD_TWIST \\branch,\\base,8,\\qblock,15",
        "PROD3_PASS_A 0,0,0", "PROD3_PASS_A 1,1152,3",
        "PROD3_PASS_B 0,0,0", "PROD3_PASS_B 1,1152,8",
    )
    if any(fragment not in source for fragment in required_source):
        raise SystemExit("frozen producer call geometry changed")

    # Current table geometry: 72 T0 zeta/qinv vectors per branch pair and one
    # shared set of 126 radix-2 zeta/qinv vectors.
    current_t0_vectors = (
        count_labels(b0_constants, r"^\.Lprod3_b0_r\d+_q\d+_twist(?:_qinv)?:$") +
        count_labels(b1_constants, r"^\.Lprod3_b1_r\d+_q\d+_twist(?:_qinv)?:$"))
    current_radix2_vectors = count_labels(
        b0_constants, r"^\.Lprod3_b0_p\d+_distance\d+(?:_lo|_hi)?_(?:zeta|qinv):$")
    current_aux_vectors = count_labels(
        b0_constants, r"^\.Lprod3_b0_ma2_q_mask:$")
    if (current_t0_vectors != 144 or current_radix2_vectors != 126 or
            current_aux_vectors != 1):
        raise SystemExit("current constant-table geometry changed")

    scaled_rows = {row["physical_row"]: row
                   for row in scaled["paper_adjusted_ntt16_rows"]}
    lines = ["/* Generated T0-BETA-TO-RADIX2 schedule constants; no ASM. */",
             ".section .rodata"]
    branch_schedules = []
    exact_constant_cases = 0
    candidate_alpha_vectors = 0
    candidate_radix2_vectors = 0

    for branch in mapping["factorization"]["branches"]:
        branch_id = branch["branch"]
        alpha_rows = branch["alpha_row_gauges_mod_q"]
        alpha_schedule = []
        for row, alpha in enumerate(alpha_rows):
            semantic_h = 5 * row % 9
            if alpha == 1:
                alpha_schedule.append({
                    "physical_row": row, "semantic_h": semantic_h,
                    "action": "raw-load", "chains_per_qblock": 0,
                    "qblocks": 4,
                })
                continue
            mont = montgomery_constant(alpha)
            qinv = signed16(mont * QINV)
            zeta_label = f".Lprod3_t0b_b{branch_id}_r{row}_alpha"
            qinv_label = f"{zeta_label}_qinv"
            emit_vector(lines, zeta_label, [mont] * 16)
            emit_vector(lines, qinv_label, [qinv] * 16)
            candidate_alpha_vectors += 2
            for value in range(-32768, 32768):
                if montgomery_reduce(value, mont) % Q != value * alpha % Q:
                    raise SystemExit("alpha Montgomery representation failed")
                exact_constant_cases += 1
            alpha_schedule.append({
                "physical_row": row, "semantic_h": semantic_h,
                "action": "four-qblock-montgomery", "chains_per_qblock": 1,
                "qblocks": 4, "factor_mod_q": alpha,
                "montgomery_signed": mont, "qinv_signed16": qinv,
                "zeta_label": zeta_label, "qinv_label": qinv_label,
                "memory_form_operands_per_chain": 2,
            })

        radix2_rows = []
        range_branch = mapping["range_proof"]["branches"][branch_id]
        range_rows = {row["physical_row"]: row
                      for row in range_branch["ntt16_rows"]}
        for row in range(9):
            stages = []
            original = scaled_rows[row]["adjusted_ntt16_stages"]
            mapped_stages = {entry["stage"]: entry
                             for entry in range_rows[row]["stages"]}
            for stage_name, distance in STAGES:
                ratio = branch["ntt16_beta_ratios"][stage_name]
                original_values = original[stage_name]["mod_q"]
                combined = [value * ratio % Q for value in original_values]
                if combined != mapped_stages[stage_name]["combined_twiddles_mod_q"]:
                    raise SystemExit("combined twiddle map changed")
                mont_values = [montgomery_constant(value) for value in combined]
                qinv_values = [signed16(value * QINV) for value in mont_values]
                emitted = []
                for suffix, vector in stage_vectors(mont_values):
                    label = f".Lprod3_t0b_b{branch_id}_p{row}_{stage_name}{suffix}_zeta"
                    emit_vector(lines, label, vector)
                    emitted.append(label)
                    candidate_radix2_vectors += 1
                for suffix, vector in stage_vectors(qinv_values):
                    label = f".Lprod3_t0b_b{branch_id}_p{row}_{stage_name}{suffix}_qinv"
                    emit_vector(lines, label, vector)
                    emitted.append(label)
                    candidate_radix2_vectors += 1
                for combined_value, mont in zip(combined, mont_values):
                    for value in range(-32768, 32768):
                        if (montgomery_reduce(value, mont) % Q !=
                                value * combined_value % Q):
                            raise SystemExit("combined Montgomery representation failed")
                        exact_constant_cases += 1
                stages.append({
                    "stage": stage_name, "distance": distance,
                    "beta_ratio_mod_q": ratio,
                    "original_twiddles_mod_q": original_values,
                    "combined_twiddles_mod_q": combined,
                    "montgomery_signed": mont_values,
                    "qinv_signed16": qinv_values,
                    "memory_operand_labels": emitted,
                    "chain_positions_changed": False,
                    "packing_geometry_changed": False,
                })
            radix2_rows.append({"physical_row": row, "stages": stages})
        branch_schedules.append({
            "branch": branch_id, "offset": branch["offset"],
            "pass_A_alpha_schedule": alpha_schedule,
            "pass_B_branch_specific_radix2": radix2_rows,
        })

    if candidate_alpha_vectors != 32 or candidate_radix2_vectors != 252:
        raise SystemExit("candidate constant-table vector count changed")

    intervals = interval_paths(mapping["range_proof"]["branches"])
    unsafe = [{"path": path, "interval": interval} for path, interval in intervals
              if interval[0] < -32768 or interval[1] > 32767]
    if unsafe:
        raise SystemExit(f"signed-i16 preoperation failure: {unsafe[0]}")

    current_producer = natural["component"]["producer_natural"]
    current_q_operands = full_audit["linked_machine_counts"][
        "prod3_persistent_aos_full"]["constant_memory_operands"]
    qorder_component = natural["component"]
    current_constant_operands = current_q_operands + (
        qorder_component["producer_natural"]["vpshufb"] -
        qorder_component["producer_current"]["vpshufb"])
    if current_constant_operands != 594:
        raise SystemExit("frozen producer constant-memory operand count changed")
    t0_operand_delta = -16
    candidate_constant_operands = current_constant_operands + t0_operand_delta
    current_table_vectors = (current_t0_vectors + current_radix2_vectors +
                             current_aux_vectors)
    candidate_table_vectors = candidate_alpha_vectors + candidate_radix2_vectors
    table_delta_bytes = 32 * (candidate_table_vectors - current_table_vectors)
    if table_delta_bytes != 416:
        raise SystemExit("constant table footprint delta changed")

    document = {
        "schema": "gt9x16-prod3-natural-q-t0-beta-schedule/v1",
        "checkpoint": "GT9X16-PROD3-NATURAL-Q-T0-BETA-SCHEDULE",
        "frozen_contract": {
            "qorder": "C1-natural-Q", "top_split_changed": False,
            "paper_R2_changed": False, "D_stage_order": ["D8", "D4", "D2", "D1"],
            "radix2_chain_positions_changed": False,
            "transform_scale": 4, "montgomery_r_exponent": 0,
            "range_repair_added": False,
        },
        "exact_schedule": {
            "candidate": "T0-BETA-TO-RADIX2",
            "pass_A": "row h=0 raw-load; other rows use one alpha_h Montgomery chain per qblock",
            "pass_B": "same chain positions and packing; select branch-specific w*g^(offset*d) constants",
            "branch_selector": "static straight-line labels; no runtime branch, lookup, or index",
            "branches": branch_schedules,
        },
        "montgomery_representation_proof": {
            "constant_formula": "centered((factor mod q) * 2^16 mod q)",
            "qinv_formula": "signed16(montgomery_constant * 12929)",
            "input_domain": "all 65536 signed-i16 values for every semantic alpha/combined constant occurrence",
            "exact_cases": exact_constant_cases,
            "same_scale": 4, "same_r_exponent": 0,
        },
        "montgomery_chain_ledger_per_forward": {
            "current": {"T0": 72, "NTT9": 80, "NTT16": 144, "total": 296},
            "candidate": {"alpha_normalization": 64, "NTT9": 80,
                          "combined_NTT16": 144, "total": 288},
            "delta": {"T0_or_alpha": -8, "NTT9": 0, "NTT16": 0, "total": -8},
            "encap_two_forward_delta": -16,
        },
        "constant_memory_operand_ledger_per_forward": {
            "current": {
                "T0": 144, "NTT16": 288,
                "other_unchanged": current_constant_operands - 144 - 288,
                "total": current_constant_operands,
            },
            "candidate": {
                "alpha_normalization": 128, "combined_NTT16": 288,
                "other_unchanged": current_constant_operands - 144 - 288,
                "total": candidate_constant_operands,
            },
            "delta": {"T0_or_alpha": -16, "NTT16": 0,
                      "other": 0, "total": -16},
            "new_explicit_constant_loads": 0,
            "new_table_selection_instructions": 0,
            "all_hot_twiddle_operands": "same RIP-relative memory-form positions",
        },
        "constant_table_footprint": {
            "current": {"T0_vectors": current_t0_vectors,
                        "shared_radix2_vectors": current_radix2_vectors,
                        "linked_auxiliary_vectors": current_aux_vectors,
                        "total_vectors": current_table_vectors,
                        "bytes": current_table_vectors * 32},
            "candidate": {"alpha_vectors": candidate_alpha_vectors,
                          "branch_specific_radix2_vectors": candidate_radix2_vectors,
                          "total_vectors": candidate_table_vectors,
                          "bytes": candidate_table_vectors * 32},
            "delta_vectors": candidate_table_vectors - current_table_vectors,
            "delta_bytes": table_delta_bytes,
            "interpretation": "runtime operands decrease; branch-specific radix2 tables add 416 linked rodata bytes after the control's retained 32-byte mask is counted",
        },
        "predicted_linked_machine_ledger_per_forward": {
            "basis": "frozen linked Natural-Q producer plus exact four-instruction Montgomery-chain deletion",
            "current": {
                "instructions": current_producer["instruction_count"],
                "vpmullw": current_producer["vpmullw"],
                "vpmulhw": current_producer["vpmulhw"],
                "barrett": current_producer["barrett_vpmulhrsw"],
                "data_loads": current_producer["data_loads"],
                "data_stores": current_producer["data_stores"],
                "routing": 432, "peak_live_ymm": 16,
            },
            "candidate": {
                "instructions": current_producer["instruction_count"] - 32,
                "vpmullw": current_producer["vpmullw"] - 8,
                "vpmulhw": current_producer["vpmulhw"] - 16,
                "barrett": current_producer["barrett_vpmulhrsw"],
                "data_loads": current_producer["data_loads"],
                "data_stores": current_producer["data_stores"],
                "routing": 432, "peak_live_ymm_upper_bound": 16,
            },
            "delta": {"instructions": -32, "vpmullw": -8,
                      "vpmulhw": -16, "vpsubw": -8,
                      "barrett": 0, "data_loads": 0, "data_stores": 0,
                      "routing": 0, "spill": 0},
            "text_byte_delta": None,
        },
        "range_and_pressure_gate": {
            "interval_nodes_checked": len(intervals),
            "all_preoperations_signed_i16": True,
            "candidate_global_i16": mapping["range_proof"]["candidate_global_i16"],
            "control_global_i16": mapping["range_proof"]["control_global_i16"],
            "new_reductions": 0, "new_register_temporaries": 0,
            "peak_live_ymm_upper_bound": 16,
        },
        "decision": {
            "eight_chains_disappear": True,
            "new_movement_debt": False,
            "constant_operand_penalty": False,
            "static_rodata_penalty_bytes": table_delta_bytes,
            "schedule_gate_passed": True,
            "next": "namespaced T0-BETA-TO-RADIX2 ASM correctness and linked audit",
            "asm_authorized": True, "benchmark_authorized": False,
            "native_kem_authorized": False,
        },
        "source_sha256": {name: sha256(path) for name, path in {
            "map": args.map, "scaled_oracle": args.scaled_oracle,
            "natural_audit": args.natural_audit,
            "full_audit": args.full_audit,
            "producer_source": args.producer_source,
            "branch0_constants": args.branch0_constants,
            "branch1_constants": args.branch1_constants,
        }.items()},
    }
    write(args.asm_constants, "\n".join(lines) + "\n", args.check)
    write(args.output, json.dumps(document, indent=2, sort_keys=True) + "\n",
          args.check)
    print("T0 beta schedule: -8 chains, -16 constant operands, +416 linked rodata bytes; ASM authorized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
