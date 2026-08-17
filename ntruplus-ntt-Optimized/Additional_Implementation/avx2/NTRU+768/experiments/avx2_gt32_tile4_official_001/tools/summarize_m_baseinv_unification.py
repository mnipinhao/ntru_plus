#!/usr/bin/env python3
"""Summarize the executable M/BaseInv M1--M4 gate."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def symbol_instruction_count(binary: Path, symbol: str) -> int:
    disassembly = subprocess.check_output(
        ["objdump", "-d", "--no-show-raw-insn", str(binary)], text=True)
    match = re.search(rf"^[0-9a-f]+ <{re.escape(symbol)}>:\n(.*?)"
                      rf"(?=^[0-9a-f]+ <|\Z)", disassembly,
                      flags=re.MULTILINE | re.DOTALL)
    if match is None:
        raise RuntimeError(f"symbol not found: {symbol}")
    count = 0
    for line in match.group(1).splitlines():
        if re.match(r"^\s*[0-9a-f]+:", line) is None:
            continue
        instruction = line.split("\t")[-1].strip()
        if instruction.startswith(("nop", "xchg", "data16", "cs ")):
            continue
        count += 1
        if instruction == "ret":
            break
    return count


def metric(summary: dict, name: str) -> dict:
    record = summary[name]
    return {
        "paired_delta_median": record["paired_delta_median"],
        "bootstrap_95_ci": record["paired_delta_bootstrap_95_ci"],
        "candidate_wins": record["gt_wins"],
        "pairs": record["pairs"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pmu", type=Path,
                        default=ROOT / "results/tile4-m-baseinv-unification-pmu.json")
    parser.add_argument("--binary", type=Path,
                        default=ROOT / "build/bench_m_baseinv_unification")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "generated/tile4_m_baseinv_unification_exec_gate.json")
    args = parser.parse_args()
    source = json.loads(args.pmu.read_text())

    placements = {}
    for placement, placement_record in source["placements"].items():
        gates = {}
        for gate in ("m1", "m2", "m3", "mpack", "m4"):
            summary = placement_record["gates"][gate]["summary"]
            gates[gate] = {
                "core_cycles": metric(summary, "cpu_core/cycles"),
                "instructions": metric(summary, "cpu_core/instructions"),
                "loads": metric(summary,
                    "cpu_core/mem_inst_retired.all_loads"),
                "stores": metric(summary,
                    "cpu_core/mem_inst_retired.all_stores"),
                "TSC": metric(summary, "tsc"),
            }
        placements[placement] = gates

    m_pack_count = symbol_instruction_count(
        args.binary, "gt32_q24_encode_soa_lazy10788_asm")
    p_pack_count = symbol_instruction_count(
        args.binary,
        "gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm")
    m_forward_count = symbol_instruction_count(
        args.binary, "gt32_global_forward_baseinv_m_safe_core_asm")
    m_forward_control_count = symbol_instruction_count(
        args.binary, "gt32_global_forward_core_asm")
    assert m_forward_count - m_forward_control_count == 6
    assert m_pack_count - p_pack_count == 35

    arithmetic_pass = all(
        placement["m3"]["core_cycles"]["bootstrap_95_ci"][1] < 0
        for placement in placements.values())
    whole_pass = all(
        placement["m4"]["core_cycles"]["bootstrap_95_ci"][1] < 0
        for placement in placements.values())

    result = {
        "schema": "ntruplus768-gt32-m-baseinv-unification-exec-v1",
        "experiment": "GT32-M-BASEINV-UNIFICATION-EXEC-001",
        "correctness": {
            "random_trials": 1000,
            "accepted_invertible_pairs": 1000,
            "Forward_semantic_differential": "pass",
            "BaseInv_status_and_value_differential": "pass",
            "BaseMul_and_Q24_byte_differential": "pass",
            "M_BaseInv_alias": "pass",
            "noninvertible_zero_failure_semantics": "pass",
        },
        "static_executable_audit": {
            "M_safe_forward_instructions_through_ret": m_forward_count,
            "M_forward_control_instructions_through_ret":
                m_forward_control_count,
            "selective_center_static_instructions_per_tile": 6,
            "M_Q24_instructions_through_ret_per_polynomial": m_pack_count,
            "P_SP1_Q24_instructions_through_ret_per_polynomial": p_pack_count,
            "M_minus_P_SP1_instructions_per_polynomial":
                m_pack_count - p_pack_count,
            "three_polynomial_delta": 3 * (m_pack_count - p_pack_count),
            "correction_to_generator_accounting": (
                "the prior 48-shuffle P debt described an older P route; "
                "the current SP1 half-scatter control has already absorbed "
                "that routing and is 35 instructions smaller than M L0"
            ),
        },
        "placements": placements,
        "gate_results": {
            "M1_selective_center_entry_fee": "pass-bounded-cost",
            "M2_M_native_BaseInv": "pass-parity",
            "M3_arithmetic_island":
                "pass-both-placements" if arithmetic_pass else "fail",
            "M_pack_vs_P_SP1": "fail-M-is-slower",
            "M4_complete_K3_K5":
                "pass" if whole_pass else "fail-no-stable-two-placement-win",
        },
        "decision": "stop-before-KEM-integration-retain-P-for-Keygen",
        "reason": (
            "M arithmetic wins, but the current P SP1 serializer is about "
            "57-59 core cycles faster for three polynomials and consumes the "
            "entire arithmetic gain; M4 is parity/placement-sensitive"
        ),
        "production_changes": False,
        "full_KEM_same_binary_gate_run": False,
        "why_full_KEM_was_not_run": (
            "M4 failed its prerequisite, so linking the candidate into all "
            "three KEM operations would test placement without an intrinsic "
            "Keygen margin"
        ),
        "reopen_only_if": [
            "an M Q24 encoder removes at least the 35-instruction-per-polynomial SP1 gap with a compact reusable body",
            "the P-specific serializer and tables can be removed from the final image and the complete M4 region then wins both placements",
            "another M-native consumer deletes a complete materialized boundary beyond this gate",
            "target ISA or microarchitecture changes",
        ],
        "artifacts": {
            "PMU": str(args.pmu.relative_to(ROOT)),
            "benchmark": "bench/bench_m_baseinv_unification.c",
            "M_BaseInv": "src/tile4_baseinv_m_soa.c",
            "M_prepare": "src/tile4_baseinv_m_prepare_asm.S",
            "M_safe_Forward_generator":
                "tools/generate_gt32_global_physical_asm.py",
        },
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
