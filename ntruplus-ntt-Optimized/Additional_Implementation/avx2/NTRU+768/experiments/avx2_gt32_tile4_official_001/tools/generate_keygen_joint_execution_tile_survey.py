#!/usr/bin/env python3
"""Audit and gate narrow Keygen T16/T32 execution-ABI families.

This is not a leaf-permutation search.  It distinguishes an I/O loop tile
from a genuinely simultaneous arithmetic tile, audits the exact Official and
current-P implementations, and scores only the four bounded families proposed
by KEYGEN-JOINT-ABI-EXECUTION-TILE-SURVEY.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated/tile4_keygen_joint_execution_tile_survey.json"
OFFICIAL = ROOT.parents[1]
PRODUCTION_BINARY = ROOT / "build/bench_keygen_production"


def require_order(text: str, first: str, second: str, description: str) -> None:
    left = text.find(first)
    right = text.find(second, left + len(first))
    if left < 0 or right < 0 or left >= right:
        raise SystemExit(f"failed source-order audit: {description}")


def symbol_ranges(binary: Path) -> dict[str, tuple[int, int]]:
    result = {}
    for line in subprocess.check_output(["nm", "-S", str(binary)],
                                        text=True).splitlines():
        fields = line.split()
        if len(fields) == 4 and re.fullmatch(r"[0-9a-fA-F]+", fields[0]):
            result[fields[3]] = (int(fields[0], 16), int(fields[1], 16))
    return result


def disassembly(binary: Path) -> list[tuple[int, str, str]]:
    text = subprocess.check_output(
        ["objdump", "-d", "-M", "att", str(binary)], text=True)
    result = []
    pattern = re.compile(
        r"\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*"
        r"([a-z][a-z0-9]*)\s*(.*)")
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            result.append((int(match.group(1), 16), match.group(2),
                           match.group(3)))
    return result


def resource_record(instructions: list[tuple[int, str, str]]) -> dict:
    # XMM/YMM names alias the same physical AVX register file.
    registers = sorted({int(number) for _, _, operands in instructions
                        for number in re.findall(r"%[xy]mm(\d+)", operands)})
    return {
        "static_instructions": len(instructions),
        "vector_multiply_instructions": sum(
            mnemonic.startswith("vpmul") or mnemonic == "vpmaddwd"
            for _, mnemonic, _ in instructions),
        "shuffle_instructions": sum(
            mnemonic.startswith(("vpshuf", "vperm", "vpunpck", "vpblend",
                                 "vextract", "vinsert"))
            for _, mnemonic, _ in instructions),
        "stack_referencing_instructions": sum(
            "%rsp" in operands for _, _, operands in instructions),
        "YMM_registers_referenced": registers,
        "YMM_register_count": len(registers),
    }


def linked_resources() -> dict:
    if not PRODUCTION_BINARY.exists():
        raise SystemExit(f"missing production audit binary: {PRODUCTION_BINARY}")
    ranges = symbol_ranges(PRODUCTION_BINARY)
    listing = disassembly(PRODUCTION_BINARY)
    names = [
        "gt32_p_baseinv_direct_avx2",
        "gt_basemul_native_asm_avx2",
        "gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm",
    ]
    result = {}
    for name in names:
        start, size = ranges[name]
        instructions = [item for item in listing
                        if start <= item[0] < start + size]
        result[name] = {"address": start, "size_bytes": size,
                        **resource_record(instructions)}
    return result


def main() -> None:
    official_baseinv_path = OFFICIAL / "asm/baseinv.s"
    official_basemul_path = OFFICIAL / "asm/basemul.s"
    official_pack_path = OFFICIAL / "asm/pack.s"
    current_bm_path = OFFICIAL / "experiments/gt_ntt/gt_basemul_layout_asm.S"
    current_q24_path = ROOT / "src/tile4_q24_codec_asm.S"

    official_baseinv = official_baseinv_path.read_text()
    official_basemul = official_basemul_path.read_text()
    official_pack = official_pack_path.read_text()
    current_bm = current_bm_path.read_text()
    current_q24 = current_q24_path.read_text()

    # Official BaseInv completes and stores batch A before loading batch B.
    require_order(official_baseinv,
                  "vmovdqu %ymm8, (%rsi)",
                  "vmovdqa 128(%rdx), %ymm2",
                  "Official BaseInv A store precedes B load")
    # Official BaseMul likewise finishes c0..c3 for A before moving to B.
    require_order(official_basemul,
                  "vmovdqa %ymm1, 96(%rdi)",
                  "vmovdqa 96(%rsi), %ymm1",
                  "Official BaseMul A store precedes B load")
    # Official pack is a real eight-input-vector execution tile.
    require_order(official_pack,
                  "vmovdqa 224(%rsi), %ymm7",
                  "vpmulhw %ymm15, %ymm0",
                  "Official Q24 loads eight YMM before reduction")
    # Current SP1 already overlaps the next four-vector block with this tail.
    require_order(current_q24,
                  "vpmulhrsw %ymm13, \\d, %ymm3",
                  "vmovdqu \\n0(%rsi), %ymm8",
                  "SP1 quotient precedes next-block preload")
    require_order(current_q24,
                  "vmovdqu \\n3(%rsi), %ymm11",
                  "vpmullw %ymm15, %ymm0, %ymm0",
                  "SP1 preload precedes current correction")

    linked = linked_resources()
    baseinv_linked = linked["gt32_p_baseinv_direct_avx2"]
    bm_linked = linked["gt_basemul_native_asm_avx2"]
    q24_linked = linked[
        "gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm"]
    assert baseinv_linked["YMM_register_count"] == 16
    assert baseinv_linked["stack_referencing_instructions"] > 0
    assert bm_linked["YMM_register_count"] == 16
    assert bm_linked["stack_referencing_instructions"] == 0
    assert q24_linked["YMM_register_count"] == 15
    assert q24_linked["stack_referencing_instructions"] == 0
    assert "All eight input vectors stay resident" in current_bm

    p_prime = json.loads(
        (ROOT / "generated/tile4_p_prime_joint_abi_survey.json").read_text())
    assert p_prime["best_static_result"][
        "whole_K3_K5_static_instruction_delta_floor"] == -30

    # A two-way outer-loop unroll can remove scalar loop-control work, but it
    # cannot shorten any vector critical tail.  These are deliberately upper
    # bounds: current compiled BaseInv has add/add/cmp/jne per T16 batch; the
    # native BM macro has five pointer adds plus decl/jne.
    baseinv_control_saving_per_call = 6 * 4
    bm_control_saving_per_call = 6 * 7
    two_baseinv_control_saving = 2 * baseinv_control_saving_per_call
    two_bm_control_saving = 2 * bm_control_saving_per_call
    scalar_control_ceiling = (two_baseinv_control_saving
                              + two_bm_control_saving)
    assert scalar_control_ceiling == 132

    references = {
        "BaseInv": {
            "BI0_current_P": {
                "semantic_tile": "T16",
                "compiled_resources": baseinv_linked,
                "observation": "all 16 YMM referenced and vector stack temporaries present",
            },
            "BI1_Official_exact": {
                "outer_IO_tile": "T32/256-byte loop",
                "arithmetic_tile": "two sequential T16 batches",
                "simultaneous_AB_interleave": False,
                "evidence": "batch-A output and determinant are stored before batch-B input loads",
                "YMM_peak": 16,
            },
            "BI2_Official_derived_P": {
                "status": "measured-hard-stop-reference",
                "twoF_twoBI_core_cycle_regression": {"normal": 43.56,
                                                      "reversed": 51.67},
                "through_twoBM_core_cycle_regression": {"normal": 44.45,
                                                         "reversed": 63.07},
            },
        },
        "BaseMul": {
            "BM0_current_P": {
                "semantic_tile": "T16",
                "compiled_resources": bm_linked,
                "all_eight_inputs_resident": True,
                "YMM_peak": 16,
            },
            "BM1_Official": {
                "outer_IO_tile": "T32/256-byte loop",
                "arithmetic_tile": "two sequential T16 batches",
                "simultaneous_AB_interleave": False,
                "materialized_R2_pass": True,
            },
            "BM2_B3_typed": {
                "status": "existing-arithmetic-parity-reference",
                "new_formula_search": False,
            },
        },
        "Q24": {
            "Q0_current_P_SP1": {
                "semantic_tile": "T16 current plus T16 next-block preload",
                "effective_load_overlap": "T32",
                "compiled_resources": q24_linked,
                "preload_registers": ["ymm8", "ymm9", "ymm10", "ymm11"],
                "YMM_peak": 15,
            },
            "Q1_Official": {
                "execution_tile": "T32/eight input YMM to six output YMM",
                "all_eight_inputs_loaded_before_reduction": True,
            },
        },
    }

    families = [
        {
            "id": "F0-current-P-T16",
            "role": "control",
            "Forward": "current progressive-P",
            "BaseInv": "BI0 current-P T16",
            "BaseMul": "BM0 current-P T16",
            "Q24": "Q0 SP1 already overlaps the next T16 block",
            "eligible": True,
        },
        {
            "id": "F1-current-P-T32",
            "role": "same-semantic-order execution-tiling candidate",
            "BaseInv": "genuine A/B interleave exceeds 16 YMM; sequential pair is only loop unroll",
            "BaseMul": "genuine A/B interleave exceeds 16 YMM; sequential pair is only loop unroll",
            "Q24": "already implemented by SP1 next-block preload",
            "vector_arithmetic_delta": 0,
            "vector_critical_tail_delta": 0,
            "scalar_loop_control_instruction_ceiling": -scalar_control_ceiling,
            "resource_relevant_vector_instruction_delta": 0,
            "candidate_peak_YMM_lower_bound": 17,
            "spill_free_peak_at_most_15": False,
            "eligible": False,
        },
        {
            "id": "F2-Official-inspired-paired-Q",
            "role": "metadata-compatible pair grouping",
            "BaseInv": "Official already pairs equal metadata but clobbers/reloads constants between sequential T16 batches",
            "BaseMul": "Official already pairs equal metadata but completes/stores A before loading B",
            "Q24": "no better complete schedule than the already active SP1 T32 overlap is established",
            "global_transpose": False,
            "vector_arithmetic_delta": 0,
            "vector_critical_tail_delta": 0,
            "eligible": False,
        },
        {
            "id": "F3-best-P-prime-T32",
            "role": "top-four prior P-prime placements plus T32",
            "P_prime_winners": p_prime["best_static_result"]["winners"],
            "P_prime_three_Q24_shuffle_delta": -30,
            "T32_new_vector_work_removed": 0,
            "T32_vector_critical_tail_delta": 0,
            "scalar_loop_control_instruction_ceiling": -scalar_control_ceiling,
            "resource_relevant_vector_instruction_delta": -30,
            "complete_reduction_or_materialization_removed": False,
            "candidate_peak_YMM_lower_bound": 17,
            "spill_free_peak_at_most_15": False,
            "eligible": False,
        },
    ]

    output = {
        "schema": "ntruplus768-keygen-joint-execution-tile-survey-v1",
        "experiment": "KEYGEN-JOINT-ABI-EXECUTION-TILE-SURVEY-001",
        "status": "static-hard-stop-no-assembly",
        "kernels_remain_independent": True,
        "sources_audited": [
            str(official_baseinv_path.relative_to(OFFICIAL)),
            str(official_basemul_path.relative_to(OFFICIAL)),
            str(official_pack_path.relative_to(OFFICIAL)),
            str(current_bm_path.relative_to(OFFICIAL)),
            "src/tile4_q24_codec_asm.S",
            "build/bench_keygen_production",
        ],
        "central_correction": {
            "claim": "Official BaseInv and BaseMul use a T32 arithmetic tile",
            "verdict": False,
            "actual": "their outer loop consumes 256 bytes, but the two T16 arithmetic batches are sequential and separated by full stores",
            "true_T32_reference": "Official Q24; current P-SP1 already implements next-block T32 load overlap",
        },
        "cost_vector": ["vector-multiply", "shuffle", "load", "store",
                        "critical-tail", "peak-live-YMM"],
        "references": references,
        "families": families,
        "hard_constraints": {
            "no_kernel_fusion": True,
            "no_global_transpose": True,
            "peak_YMM_at_most": 15,
            "no_spill": True,
            "no_new_Montgomery_chain_without_consumer_chain_deletion": True,
            "exact_range_and_scale_proof": True,
        },
        "promotion_filter": {
            "one_complete_reduction_or_materialization_removed": False,
            "at_least_100_resource_relevant_instructions_removed": False,
            "at_least_50_local_core_cycle_headroom_modeled": False,
            "reason": "the apparent 132-instruction T32 saving is scalar loop control with zero vector critical-tail reduction; the only vector-work saving remains the prior 30 Q24 shuffles",
        },
        "decision": [
            "do-not-emit-T32-BaseInv-or-BaseMul-ASM",
            "do-not-repeat-P-prime-layout-search",
            "retain-current-P-T16-arithmetic-and-SP1-Q24",
            "treat-Official-T32-BaseInv-and-BM-as-outer-loop-unroll-not-common-execution-ABI",
        ],
        "reopen_only_if": [
            "a T32 schedule proves peak at most 15 YMM with no spill or reload/recomputation debt",
            "two-batch scheduling deletes vector arithmetic or shortens a measured vector critical tail",
            "a new representation removes a complete reduction or materialized pass",
            "target ISA supplies additional vector registers",
        ],
        "twisting": {
            "status": "deferred",
            "condition": "only after an execution family passes; net Montgomery chain count must be nonpositive",
        },
    }
    OUT.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({
        "output": str(OUT),
        "central_correction": output["central_correction"],
        "eligible_candidates": [family["id"] for family in families
                                if family["eligible"] and family["role"] != "control"],
        "status": output["status"],
    }, indent=2))


if __name__ == "__main__":
    main()
