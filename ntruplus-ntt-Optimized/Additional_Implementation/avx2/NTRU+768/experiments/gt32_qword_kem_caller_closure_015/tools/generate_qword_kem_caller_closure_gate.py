#!/usr/bin/env python3
"""Exact KEM-caller closure gate for the qword-semantic Forward from 013."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
ROOT = EXPERIMENTS.parent
PARENT = EXPERIMENTS / "gt32_cross_r3_qword_semantic_packet_013"
RANGE014 = EXPERIMENTS / "gt32_cross_r3_qword_b3_inverse_range_014"
PARENT_JSON = PARENT / "generated/qword_semantic_packet_gate.json"
RANGE014_JSON = RANGE014 / "generated/qword_b3_inverse_range_gate.json"
RANGE014_TOOL = RANGE014 / "tools/generate_qword_b3_inverse_range_gate.py"
PACK = ROOT / "pack.s"
BASEMUL = ROOT / "basemul.s"
ENCAP = ROOT / "encap.c"
DECAP = ROOT / "decap.c"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


R14 = load_module("qword_range014_for_015", RANGE014_TOOL)
GT = R14.GT
Q = GT.Q


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256(path)}


def macro_body(text: str, name: str) -> str:
    match = re.search(
        rf"^\s*\.macro\s+{re.escape(name)}[^\n]*\n(.*?)^\s*\.endm\s*$",
        text, re.MULTILINE | re.DOTALL,
    )
    assert match, name
    return match.group(1)


Interval = tuple[int, int]


def peak(interval: Interval) -> int:
    return max(abs(interval[0]), abs(interval[1]))


def add(a: Interval, b: Interval) -> Interval:
    return a[0] + b[0], a[1] + b[1]


def scale_interval(interval: Interval, count: int) -> Interval:
    return interval[0] * count, interval[1] * count


def edge(name: str, interval: Interval) -> dict:
    return {
        "edge": name,
        "interval": list(interval),
        "abs_bound": peak(interval),
        "signed_int16_safe": -32768 <= interval[0] <= interval[1] <= 32767,
    }


def reduce9(value: int) -> int:
    """Exact vpmulhrsw(9), vpmullw(q), vpsubw sequence."""
    quotient = (value * 9 + (1 << 14)) >> 15
    assert -32768 <= quotient <= 32767
    return GT.signed16(value - GT.signed16(quotient * Q))


def canonical_after_reduce9(value: int) -> int:
    reduced = reduce9(value)
    return reduced + Q if reduced < 0 else reduced


def q24_reducer_proof(lo: int, hi: int) -> dict:
    records = [(value, reduce9(value), canonical_after_reduce9(value))
               for value in range(lo, hi + 1)]
    max_residual = max(abs(record[1]) for record in records)
    canonical_min = min(record[2] for record in records)
    canonical_max = max(record[2] for record in records)
    congruent = all((record[0] - record[1]) % Q == 0 for record in records)
    canonical = all(0 <= record[2] < Q for record in records)
    return {
        "input_interval": [lo, hi],
        "exact_scalar_inputs_checked": hi - lo + 1,
        "max_reduced_abs_bound": max_residual,
        "canonical_output_interval": [canonical_min, canonical_max],
        "mod_q_congruence": congruent,
        "canonical_after_existing_sign_fix": canonical,
        "unchanged_Q24_sequence_closes": congruent and canonical,
    }


def general_b3_leaf(bound_a: int, bound_b: int, lambda_factor: int) -> dict:
    product = R14.variable_mont_interval(bound_a * bound_b)
    edges = [edge("variable_mont_product", product)]
    outputs = []
    for coefficient, (wrapped_count, direct_count) in enumerate(
            ((3, 1), (2, 2), (1, 3), (0, 4))):
        if wrapped_count:
            wrapped = scale_interval(product, wrapped_count)
            edges.append(edge(f"c{coefficient}.wrapped_sum_before_lambda", wrapped))
            lam = R14.fixed_mont_interval(
                wrapped[0], wrapped[1], lambda_factor)
            edges.append(edge(f"c{coefficient}.lambda_product", lam))
        else:
            lam = (0, 0)
        raw = add(lam, scale_interval(product, direct_count))
        edges.append(edge(f"c{coefficient}.raw_output", raw))
        rsq = R14.fixed_mont_interval(raw[0], raw[1], 867)
        edges.append(edge(f"c{coefficient}.RSQ_output", rsq))
        outputs.append(rsq)
    return {
        "input_abs_bounds": [bound_a, bound_b],
        "lambda_factor": lambda_factor,
        "edges": edges,
        "output_intervals": [list(value) for value in outputs],
        "output_abs_bounds": [peak(value) for value in outputs],
        "all_edges_int16_safe": all(item["signed_int16_safe"] for item in edges),
    }


def source_audit() -> dict:
    pack = PACK.read_text()
    basemul = BASEMUL.read_text()
    encap = ENCAP.read_text()
    decap = DECAP.read_text()
    lazy_reduce = macro_body(pack, "Q24_LAZY_QUAD_REDUCE")
    equal_body = re.search(
        r"ntruplus768_equal_m_modq12699_avx2:(.*?)^\s*\.size",
        pack, re.MULTILINE | re.DOTALL).group(1)
    assert "vpmulhrsw" in lazy_reduce and "vpmullw" in lazy_reduce \
        and "vpsubw" in lazy_reduce
    assert "jmp ntruplus768_pack_m_lazy10788_avx2" in pack
    assert "vpmulhrsw" in equal_body and "vpmullw" in equal_body \
        and "vpsubw" in equal_body
    assert "TILE4_OUTPUT_SOA_LATE_RSQ" in basemul
    assert "ntruplus768_basemul_general_m_avx2" in encap
    assert "ntruplus768_pack_m_highrange12699_avx2" in encap
    assert "ntruplus768_basemul_general_m_avx2" in decap
    assert "ntruplus768_pack_m_centered_avx2" in decap
    assert "ntruplus768_equal_m_modq12699_avx2" in decap
    return {
        "sources": [artifact(PARENT_JSON), artifact(RANGE014_JSON),
                    artifact(PACK), artifact(BASEMUL), artifact(ENCAP),
                    artifact(DECAP)],
        "current_lazy_Q24_reducer": ["vpmulhrsw 9", "vpmullw q", "vpsubw"],
        "current_equality_reducer": ["vpmulhrsw 9", "vpmullw q", "vpsubw"],
        "general_B3_finalizer": "Montgomery RSQ on all four coefficient planes",
        "caller_correction": (
            "Neither Encap nor the two post-inverse Decap Forward callsites "
            "feed the current inverse."
        ),
    }


def build() -> dict:
    terminal = R14.terminal_bounds()
    terminal_max = max(terminal.values())
    canonical_bound = Q - 1
    full_reducer = q24_reducer_proof(-32768, 32767)
    terminal_reducer = q24_reducer_proof(-terminal_max, terminal_max)

    encap_leaves = []
    encap_all_b3_safe = True
    encap_add_safe = True
    encap_sum_lo, encap_sum_hi = 0, 0
    encap_b3_max = [0, 0, 0, 0]
    encap_sum_max = [0, 0, 0, 0]

    decap_leaves = []
    decap_sub_safe = True
    decap_all_b3_safe = True
    decap_centered_pack_safe = True
    decap_sub_interval_global = (0, 0)
    decap_b3_max = [0, 0, 0, 0]
    equality_difference_global = (0, 0)

    for branch in range(2):
        for k3 in range(3):
            for physical_q in range(32):
                forward_bound = terminal[branch, k3, physical_q]
                lam = GT.lambda_montgomery(k3, physical_q, branch)

                # Encap: decoded h (canonical) times candidate Forward(r),
                # followed by addition of candidate Forward(m).
                eb3 = general_b3_leaf(canonical_bound, forward_bound, lam)
                sums = []
                for coefficient, output in enumerate(eb3["output_intervals"]):
                    total = add(tuple(output), (-forward_bound, forward_bound))
                    sums.append(total)
                    encap_b3_max[coefficient] = max(
                        encap_b3_max[coefficient], peak(tuple(output)))
                    encap_sum_max[coefficient] = max(
                        encap_sum_max[coefficient], peak(total))
                    encap_sum_lo = min(encap_sum_lo, total[0])
                    encap_sum_hi = max(encap_sum_hi, total[1])
                    encap_add_safe &= -32768 <= total[0] <= total[1] <= 32767
                encap_all_b3_safe &= eb3["all_edges_int16_safe"]
                encap_leaves.append({
                    "branch": branch, "k3": k3, "physical_Q": physical_q,
                    "forward_abs_bound": forward_bound,
                    "general_B3": eb3,
                    "B3_plus_m_intervals": [list(value) for value in sums],
                })

                # Decap: decoded c minus candidate Forward(m), multiplied by
                # decoded hinv.  The general RSQ output feeds centered Q24.
                subtraction = (-forward_bound, canonical_bound + forward_bound)
                decap_sub_interval_global = (
                    min(decap_sub_interval_global[0], subtraction[0]),
                    max(decap_sub_interval_global[1], subtraction[1]))
                decap_sub_safe &= -32768 <= subtraction[0] \
                    and subtraction[1] <= 32767
                db3 = general_b3_leaf(peak(subtraction), canonical_bound, lam)
                decap_all_b3_safe &= db3["all_edges_int16_safe"]
                for coefficient, output in enumerate(db3["output_intervals"]):
                    output = tuple(output)
                    decap_b3_max[coefficient] = max(
                        decap_b3_max[coefficient], peak(output))
                    decap_centered_pack_safe &= output[0] >= -(Q - 1) \
                        and output[1] <= Q - 1
                    difference = add(output, (-forward_bound, forward_bound))
                    equality_difference_global = (
                        min(equality_difference_global[0], difference[0]),
                        max(equality_difference_global[1], difference[1]))
                decap_leaves.append({
                    "branch": branch, "k3": k3, "physical_Q": physical_q,
                    "forward_abs_bound": forward_bound,
                    "c_minus_mhat_interval": list(subtraction),
                    "general_B3": db3,
                })

    encap_sum_reducer = q24_reducer_proof(encap_sum_lo, encap_sum_hi)
    equality_sub_safe = (-32768 <= equality_difference_global[0]
                         <= equality_difference_global[1] <= 32767)
    equality_reducer = q24_reducer_proof(*equality_difference_global)

    encap_zero_cost = (terminal_reducer["unchanged_Q24_sequence_closes"]
                       and encap_all_b3_safe and encap_add_safe
                       and encap_sum_reducer["unchanged_Q24_sequence_closes"])
    decap_zero_cost = (decap_sub_safe and decap_all_b3_safe
                       and decap_centered_pack_safe and equality_sub_safe
                       and equality_reducer["unchanged_Q24_sequence_closes"])
    all_zero_cost = encap_zero_cost and decap_zero_cost

    return {
        "schema": "gt32-qword-kem-caller-closure-v1",
        "experiment": "GT32-QWORD-KEM-CALLER-CLOSURE-015",
        "production_modified": False,
        "assembly_emitted": False,
        "source_audit": source_audit(),
        "Q24_reduce9_contract": {
            "full_signed_int16": full_reducer,
            "candidate_Forward_terminal": terminal_reducer,
        },
        "encap": {
            "dataflow": [
                "F013(r) -> unchanged lazy Q24",
                "decoded h x F013(r) -> unchanged general B3",
                "general B3 + F013(m) -> unchanged high-range Q24",
            ],
            "leaf_records": encap_leaves,
            "general_B3_all_edges_int16_safe": encap_all_b3_safe,
            "general_B3_output_abs_bounds_by_coefficient": encap_b3_max,
            "B3_plus_m_abs_bounds_by_coefficient": encap_sum_max,
            "B3_plus_m_global_interval": [encap_sum_lo, encap_sum_hi],
            "poly_add_signed_int16_safe": encap_add_safe,
            "ciphertext_Q24_reducer": encap_sum_reducer,
            "zero_extra_instruction_closure": encap_zero_cost,
        },
        "decap": {
            "dataflow": [
                "decoded c - F013(m) -> unchanged general B3",
                "general B3 -> unchanged centered Q24",
                "recovered rhat - F013(derived r) -> unchanged native equality",
            ],
            "leaf_records": decap_leaves,
            "c_minus_mhat_global_interval": list(decap_sub_interval_global),
            "poly_sub_signed_int16_safe": decap_sub_safe,
            "general_B3_all_edges_int16_safe": decap_all_b3_safe,
            "general_B3_output_abs_bounds_by_coefficient": decap_b3_max,
            "centered_Q24_input_contract_met": decap_centered_pack_safe,
            "native_equality_difference_interval": list(equality_difference_global),
            "native_equality_vpsubw_safe": equality_sub_safe,
            "native_equality_reducer": equality_reducer,
            "zero_extra_instruction_closure": decap_zero_cost,
        },
        "decision": {
            "status": "kem_caller_zero_cost_closure_pass" if all_zero_cost
                      else "kem_caller_range_hard_stop",
            "encap_assembly_eligible": encap_zero_cost,
            "decap_forward_assembly_eligible": decap_zero_cost,
            "inverse_014_blocks_current_KEM_callsites": False,
            "next": "GT32-QWORD-FORWARD-ASM-016" if all_zero_cost
                    else "stop before ASM and isolate the failing caller edge",
            "GT_Clean_modified": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
