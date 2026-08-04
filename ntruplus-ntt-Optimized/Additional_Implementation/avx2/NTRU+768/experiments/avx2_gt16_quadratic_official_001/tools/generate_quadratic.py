#!/usr/bin/env python3
"""Generate the Round 4C quadratic-terminal contract and static gates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

Q = 3457
R = 1 << 16
QINV = pow(Q, -1, R)
CENTER = (Q - 1) // 2
OMEGA48 = pow(675, 2, Q)
OMEGA16 = pow(OMEGA48, 3, Q)
OMEGA3 = pow(OMEGA48, 16, Q)
HERE = Path(__file__).resolve().parent.parent
REPO = next(p for p in HERE.parents if (p / ".git").exists())
HORIZONTAL = HERE.parent / "avx2_gt16_native_official_001"
VERTICAL = HERE.parent / "avx2_gt16_vertical_official_001"
COMPONENTS_FILE = HORIZONTAL / "generated/gt16-factorization.json"
BENCHMARK_FILE = HERE.parent / "gt_ntt/BENCHMARK_RESULTS.md"

FROZEN_FORWARD = 2026.260
FROZEN_QBM = 1523.549
FROZEN_INVERSE_SURROGATE = 4731.420
FROZEN_CHAIN = 17784.325
FROZEN_CHAIN_GATE = 0.95 * FROZEN_CHAIN
VERTICAL_CORE = 1884


def centered(x: int) -> int:
    x %= Q
    return x - Q if x > CENTER else x


def legendre(x: int) -> int:
    value = pow(x % Q, (Q - 1) // 2, Q)
    return -1 if value == Q - 1 else value


def multiplicative_order(x: int) -> int:
    value = 1
    for order in range(1, Q):
        value = value * x % Q
        if value == 1:
            return order
    raise AssertionError("nonzero field element has no order")


def square_roots(x: int) -> list[int]:
    return [candidate for candidate in range(1, Q)
            if candidate * candidate % Q == x % Q]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def mont_constant(value: int) -> tuple[int, int]:
    mont = centered(value * R)
    qinv = signed16((mont & 0xFFFF) * QINV)
    return mont, qinv


def constant_header(factors: dict[str, Any]) -> str:
    branches = json.loads(
        (HORIZONTAL / "generated/gt16-branches.json").read_text()
    )["branches"]
    by_vector: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for factor in factors["factors"]:
        by_vector.setdefault((factor["k3"], factor["k16"]), []).append(factor)
    split_rows = []
    split_qinv_rows = []
    weight_rows = []
    weight_qinv_rows = []
    merge_rows = []
    merge_qinv_rows = []
    for k3 in range(3):
        for k16 in range(16):
            records = sorted(by_vector[(k3, k16)],
                             key=lambda item: (item["branch"], item["sign_index"]))
            roots = [next(r for r in records
                          if r["branch"] == branch and r["sign_index"] == 0)["sqrt_alpha"] % Q
                     for branch in range(4)]
            split_values = []
            weight_values = []
            merge_values = []
            for root in roots:
                split_values.extend((root, root, -root, -root))
                weight_values.extend((1, root, 1, -root))
                inv = pow(root, -1, Q)
                merge_values.extend((inv, inv, inv, inv))
            def encoded(values: list[int]) -> tuple[list[int], list[int]]:
                pairs = [mont_constant(value % Q) for value in values]
                return [p[0] for p in pairs], [p[1] for p in pairs]
            split_m, split_q = encoded(split_values)
            weight_m, weight_q = encoded(weight_values)
            merge_m, merge_q = encoded(merge_values)
            split_rows.append(split_m)
            split_qinv_rows.append(split_q)
            weight_rows.append(weight_m)
            weight_qinv_rows.append(weight_q)
            merge_rows.append(merge_m)
            merge_qinv_rows.append(merge_q)

    def array(name: str, rows: list[list[int]]) -> list[str]:
        result = [f"static const int16_t {name}[48][16] __attribute__((aligned(32))) = {{"]
        result.extend("    {" + ", ".join(f"{x:6d}" for x in row) + "}," for row in rows)
        result.append("};")
        return result
    lines = [
        "#ifndef ROUND4C_GENERATED_CONSTANTS_H",
        "#define ROUND4C_GENERATED_CONSTANTS_H",
        "", "#include <stdint.h>", "",
    ]
    for name, rows in (
        ("round4c_split_mont", split_rows),
        ("round4c_split_qinv", split_qinv_rows),
        ("round4c_weight_mont", weight_rows),
        ("round4c_weight_qinv", weight_qinv_rows),
        ("round4c_merge_mont", merge_rows),
        ("round4c_merge_qinv", merge_qinv_rows),
    ):
        lines.extend(array(name, rows))
        lines.append("")
    inverse_twiddles = []
    for length in (4, 8, 16):
        for index in range(length // 2):
            inverse_twiddles.append(pow(OMEGA16, -index * (16 // length), Q))
    inverse_mont = [mont_constant(value)[0] for value in inverse_twiddles]
    inverse_qinv = [mont_constant(value)[1] for value in inverse_twiddles]
    norm_mont, norm_qinv = mont_constant(pow(16, -1, Q))
    lines.append("static const int16_t round4c_inv16_twiddle_mont[14] __attribute__((aligned(32))) = {")
    lines.append("    " + ", ".join(str(x) for x in inverse_mont) + ",")
    lines.append("};")
    lines.append("static const int16_t round4c_inv16_twiddle_qinv[14] __attribute__((aligned(32))) = {")
    lines.append("    " + ", ".join(str(x) for x in inverse_qinv) + ",")
    lines.append("};")
    lines.append(f"static const int16_t round4c_inv16_norm_mont = {norm_mont};")
    lines.append(f"static const int16_t round4c_inv16_norm_qinv = {norm_qinv};")
    omega3_mont, omega3_qinv = mont_constant(OMEGA3)
    lines.append(f"static const int16_t round4c_inv3_omega_mont = {omega3_mont};")
    lines.append(f"static const int16_t round4c_inv3_omega_qinv = {omega3_qinv};")
    lines.append("")
    inverse3 = pow(3, -1, Q)
    postweight_rows = []
    postweight_qinv_rows = []
    for i3 in range(3):
        for i16 in range(16):
            natural = (16 * i3 + 33 * i16) % 48
            values = []
            for branch in branches:
                value = inverse3 * pow(branch["F"], natural, Q) % Q
                values.extend((value,) * 4)
            encoded = [mont_constant(value) for value in values]
            postweight_rows.append([item[0] for item in encoded])
            postweight_qinv_rows.append([item[1] for item in encoded])
    lines.extend(array("round4c_inv48_postweight_mont", postweight_rows))
    lines.append("")
    lines.extend(array("round4c_inv48_postweight_qinv", postweight_qinv_rows))
    lines.append("")

    def scalar_array(name: str, values: list[int]) -> None:
        pairs = [mont_constant(value % Q) for value in values]
        lines.append(
            f"static const int16_t {name}_mont[{len(values)}] = {{" +
            ", ".join(str(pair[0]) for pair in pairs) + "};"
        )
        lines.append(
            f"static const int16_t {name}_qinv[{len(values)}] = {{" +
            ", ".join(str(pair[1]) for pair in pairs) + "};"
        )

    # The quadratic merge leaves scale 2*R^-1.  Omitting the two standard-R2
    # inv2 multiplies makes both top residues carry scale 4*R^-1; the final
    # constants remove that common scale while completing the special R2.
    scalar_array("round4c_inv_beta", [pow(branches[index]["beta"], -1, Q)
                                      for index in (0, 2)])
    inverse_scale = (R % Q) * pow(4, -1, Q) % Q
    inverse_delta = pow(2735 - 723, -1, Q)
    scalar_array("round4c_final_merge", [
        inverse_scale,
        inverse_delta * inverse_scale % Q,
        2735 * inverse_delta * inverse_scale % Q,
    ])
    lines.append("static const int16_t round4c_branch_f[4] = {" +
                 ", ".join(str(branch["F"]) for branch in branches) + "};")
    lines.append("static const int16_t round4c_branch_beta[4] = {" +
                 ", ".join(str(branch["beta"]) for branch in branches) + "};")
    lines.append("")
    lines.extend(["#endif", ""])
    return "\n".join(lines)


def quartic_lambda_source() -> str:
    components = json.loads(COMPONENTS_FILE.read_text())["components"]
    by_key = {(c["branch"], c["k3"], c["k16"]): c["alpha"] % Q
              for c in components}
    # The frozen ASM GT_MONT_LAMBDA consumes Montgomery-form lambda.
    values = [centered(by_key[(branch, k3, k16)] * R)
              for branch in range(4) for k3 in range(3) for k16 in range(16)]
    qinv = [signed16((value & 0xFFFF) * QINV) for value in values]
    def array(name: str, data: list[int]) -> list[str]:
        lines = [f"const int16_t {name}[192] __attribute__((aligned(32))) = {{"]
        for offset in range(0, 192, 16):
            lines.append("    " + ", ".join(f"{x:6d}" for x in data[offset:offset + 16]) + ",")
        lines.append("};")
        return lines
    lines = ["#include <stdint.h>", ""]
    lines.extend(array("gt_native_lambda", values))
    lines.append("")
    lines.extend(array("gt_native_lambda_qinv", qinv))
    lines.append("")
    lines.extend(array("gt_soa_lambda", values))
    lines.append("")
    lines.extend(array("gt_soa_lambda_qinv", qinv))
    lines.append("")
    return "\n".join(lines)


def choose_vector_signs(vector: list[dict[str, Any]]) -> tuple[list[int], dict[str, Any]]:
    """Exhaust all 2^4 root orientations for one (k3,k16) vector."""
    candidates = []
    for mask in range(16):
        roots = []
        lanes = []
        for branch, component in enumerate(vector):
            roots_pair = square_roots(component["alpha"])
            root = roots_pair[(mask >> branch) & 1]
            roots.append(root)
            lanes.extend((centered(root), centered(root),
                          centered(-root), centered(-root)))
        transitions = sum((lanes[i] < 0) != (lanes[i - 1] < 0)
                          for i in range(1, 16))
        candidates.append(((transitions, tuple(lanes), mask), roots, lanes))
    candidates.sort(key=lambda item: item[0])
    best = candidates[0]
    tied_primary = sum(c[0][:2] == best[0][:2] for c in candidates)
    return best[1], {
        "mask": best[0][2],
        "sign_transitions": best[0][0],
        "constant_lanes": best[2],
        "primary_score_ties": tied_primary,
        "search_space": 16,
        "note": "root negation swaps the plus/minus factors; both constants remain present",
    }


def factorization() -> dict[str, Any]:
    source = json.loads(COMPONENTS_FILE.read_text())["components"]
    by_key = {(c["k3"], c["k16"], c["branch"]): c for c in source}
    vectors = []
    factors = []
    for k3 in range(3):
        for k16 in range(16):
            quartet = [by_key[(k3, k16, branch)] for branch in range(4)]
            roots, score = choose_vector_signs(quartet)
            vector_factors = []
            for branch, (component, root) in enumerate(zip(quartet, roots)):
                alpha = component["alpha"] % Q
                assert root * root % Q == alpha
                assert legendre(alpha) == 1
                assert pow(alpha, (Q - 1) // 4, Q) == Q - 1
                assert legendre(root) == -1 and legendre(-root) == -1
                assert multiplicative_order(alpha) == 576
                for sign_index, sign in enumerate((1, -1)):
                    record = {
                        "quadratic_slot": len(factors),
                        "quartic_slot": component["slot"],
                        "official_quartic_slot": component["official_slot"],
                        "branch": branch,
                        "k3": k3,
                        "k16": k16,
                        "sign_index": sign_index,
                        "factor_sign": sign,
                        "alpha": centered(alpha),
                        "sqrt_alpha": centered(root),
                        "quadratic_modulus_r": centered(sign * root),
                        "representation_scale": 1,
                        "montgomery_power": 0,
                        "input_range": [-3456, 3456],
                        "lane0": 4 * branch + 2 * sign_index,
                        "lane1": 4 * branch + 2 * sign_index + 1,
                    }
                    factors.append(record)
                    vector_factors.append(record["quadratic_slot"])
            vectors.append({"k3": k3, "k16": k16,
                            "sign_search": score,
                            "quadratic_slots": vector_factors})
    assert len(factors) == 384 and len(vectors) == 48
    assert sorted(f["lane0"] for f in factors[:8]) == list(range(0, 16, 2))
    return {
        "field": {"q": Q, "q_mod_4": Q % 4, "minus_one_square": legendre(-1) == 1},
        "layout": {
            "batch": "k3",
            "vector": "k16",
            "lane": "4*branch + 2*sign_index + quadratic_degree",
            "pair_local_to_128_bit_half": True,
        },
        "quartic_components": 192,
        "quadratic_components": 384,
        "vectors": vectors,
        "factors": factors,
    }


def signed16(x: int) -> int:
    x &= 0xFFFF
    return x - 0x10000 if x & 0x8000 else x


def mont32(x: int) -> int:
    m = signed16((x & 0xFFFF) * QINV)
    assert (x - m * Q) % R == 0
    return (x - m * Q) // R


def range_metadata() -> dict[str, Any]:
    split_bound = 2 * CENTER
    c0_bound = 2 * split_bound * CENTER
    c1_bound = 2 * split_bound * split_bound
    assert c1_bound < 2**31 and split_bound < 32768

    # For each low word, y is affine in the 16-bit quotient of x.  Checking
    # the minimum and maximum legal quotient is exact over the full interval.
    minimum = 10**9
    maximum = -10**9
    for low in range(R):
        first = (-c1_bound - low + R - 1) // R
        last = (c1_bound - low) // R
        for high in {first, last}:
            x = high * R + low
            if -c1_bound <= x <= c1_bound:
                value = mont32(x)
                minimum = min(minimum, value)
                maximum = max(maximum, value)
    assert -32768 not in range(-split_bound, split_bound + 1)
    return {
        "canonical_input_bound": CENTER,
        "split_lazy_bound": split_bound,
        "weighted_operand_bound": CENTER,
        "c0_vpmaddwd_bound": c0_bound,
        "c1_vpmaddwd_bound": c1_bound,
        "signed_int32_safe": c1_bound < 2**31,
        "negative_32768_excluded": True,
        "five_instruction_montgomery32": {
            "qinv": QINV,
            "sequence": ["vpmullw-qinv", "vpand-lowword", "vpmaddwd-q",
                         "vpsubd", "vpsrad-16"],
            "exact_input_interval": [-c1_bound, c1_bound],
            "exact_output_interval": [minimum, maximum],
            "output_fits_int16": -32768 <= minimum <= maximum <= 32767,
            "output_scale": "R^-1",
        },
    }


def static_schedules(ranges: dict[str, Any]) -> dict[str, Any]:
    split = ["vpshufb-duplicate-low", "vpshufb-duplicate-high",
             "vpmullw-s", "vpmulhw-s", "vpmulhw-q", "vpsubw-mont",
             "vpaddw-signed-pairs"]
    merge = ["vpshufb-duplicate-plus", "vpshufb-duplicate-minus",
             "vpaddw-sum", "vpsubw-difference", "vpmullw-inv-s",
             "vpmulhw-inv-s", "vpmulhw-q", "vpsubw-mont",
             "vpshufb-quartic-order"]
    mont32_ops = ranges["five_instruction_montgomery32"]["sequence"]
    preweight = [
        "load-a", "load-b",
        "vpmullw-r", "vpmulhw-r", "vpmulhw-q", "vpsubw-weighted-b",
        "vpshufb-swap-b-pairs", "vpmaddwd-c0", "vpmaddwd-c1",
        *[f"c0-{op}" for op in mont32_ops],
        *[f"c1-{op}" for op in mont32_ops],
        "vpackssdw-c0-c1", "vpshufb-interleave-pairs", "store-output",
    ]
    assert len(preweight) == 22
    postmultiply = [
        "load-a", "load-b", "vpshufb-swap-b-pairs",
        "vpmaddwd-c0-unweighted", "vpmaddwd-c1",
        "vpshufb-isolate-a1", "vpshufb-isolate-b1", "vpmaddwd-a1b1",
        *[f"c0-{op}" for op in mont32_ops],
        *[f"c1-{op}" for op in mont32_ops],
        *[f"a1b1-{op}" for op in mont32_ops],
        "vpmullw-rminus1", "vpmulhw-rminus1", "vpmulhw-q",
        "vpsubw-weighted-a1b1", "vpaddw-c0-correction",
        "vpackssdw-c0-c1", "vpshufb-interleave-pairs", "store-output",
    ]
    assert len(postmultiply) == 31
    asymmetric_qbm = [
        "load-a", "load-b-normal", "load-b-weighted",
        "vpshufb-swap-b-pairs", "vpmaddwd-c0", "vpmaddwd-c1",
        *[f"c0-{op}" for op in mont32_ops],
        *[f"c1-{op}" for op in mont32_ops],
        "vpackssdw-c0-c1", "vpshufb-interleave-pairs", "store-output",
    ]
    assert len(asymmetric_qbm) == 19
    candidates = {
        "QBM-PREWEIGHT": {
            "per_vector_ops": preweight,
            "vectors": 48,
            "instructions": 48 * len(preweight),
            "peak_live_ymm": 11,
            "expanded_operand": False,
        },
        "QBM-POSTMULTIPLY": {
            "per_vector_ops": postmultiply,
            "vectors": 48,
            "instructions": 48 * len(postmultiply),
            "peak_live_ymm": 13,
            "expanded_operand": False,
        },
        "QBM-ASYMMETRIC-DUAL": {
            "per_vector_ops": asymmetric_qbm,
            "qbm_instructions": 48 * len(asymmetric_qbm),
            "right_precompute_ops_per_vector": 5,
            "right_precompute_instructions": 48 * 5,
            "instructions": 48 * (len(asymmetric_qbm) + 5),
            "peak_live_ymm": 10,
            "expanded_operand": True,
            "expanded_bytes": 1536,
        },
    }
    selected = min(candidates, key=lambda name: candidates[name]["instructions"])
    assert selected == "QBM-PREWEIGHT"
    return {
        "split": {"per_vector_ops": split, "vectors_per_forward": 48,
                  "instructions_per_forward": 48 * len(split),
                  "standalone_traversal": 0, "peak_live_ymm": 6},
        "merge": {"per_vector_ops": merge, "vectors_per_inverse": 48,
                  "instructions_per_inverse": 48 * len(merge),
                  "standalone_traversal": 0, "peak_live_ymm": 6,
                  "inv2_absorbed_into_inverse_normalization": True},
        "qbm_candidates": candidates,
        "selected": selected,
        "abi_invariants": ["quadratic pairs are adjacent",
                           "no pair crosses a 128-bit half",
                           "fixed public addresses and loop bounds",
                           "YMM15 remains available"],
    }


def consumer_estimates() -> dict[str, Any]:
    return {
        "serialization": {
            "to_official": "merge+canonicalize+Official permutation+pack must be one pass",
            "from_official": "unpack+Official permutation+split must be one pass",
            "modq_compare": "pairwise quadratic lanes may compare directly after fixed centering",
            "gate": "requires direct benchmark before integration",
            "standalone_quadratic_wire_format_allowed": False,
        },
        "baseinv": {
            "formula": "(a0-a1*x)/(a0^2-r*a1^2)",
            "norms": 384,
            "vector_norm_frontend_optimistic_instructions": 48 * 10,
            "vector_multiplyback_optimistic_instructions": 48 * 5,
            "scalar_batch_inversion_count": 384,
            "failure_semantics": "any zero norm => fixed-work failure and zero output",
            "gate": "static estimate only; keygen benchmark required",
        },
    }


def decision(schedules: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    split = schedules["split"]["instructions_per_forward"]
    qbm = schedules["qbm_candidates"][schedules["selected"]]["instructions"]
    merge = schedules["merge"]["instructions_per_inverse"]
    candidate_kernel = 2 * (VERTICAL_CORE + split) + qbm + merge + VERTICAL_CORE
    frozen_kernel = 2 * FROZEN_FORWARD + FROZEN_QBM + FROZEN_INVERSE_SURROGATE
    common = FROZEN_CHAIN - frozen_kernel
    projected_chain = common + candidate_kernel
    gate_pass = projected_chain < FROZEN_CHAIN_GATE
    accounting = {
        "comparison": "static candidate regions plus frozen dynamic-instruction surrogate",
        "round4b_hypothetical_terminal_boundary": {
            "old_edges": {
                "forward_a.vertical_to_quartic_bm": 288,
                "forward_b.vertical_to_quartic_bm": 288,
                "quartic_bm": FROZEN_QBM,
                "inverse.quartic_bm_to_vertical": 288,
            },
            "old_total": 3 * 288 + FROZEN_QBM,
            "new_edges": {
                "forward_a.fused_split": split,
                "forward_b.fused_split": split,
                "quadratic_bm": qbm,
                "inverse.fused_merge": merge,
            },
            "new_total": 2 * split + qbm + merge,
            "saving": 3 * 288 + FROZEN_QBM - (2 * split + qbm + merge),
        },
        "frozen": {
            "two_forward": 2 * FROZEN_FORWARD,
            "quartic_bm": FROZEN_QBM,
            "inverse_surrogate": FROZEN_INVERSE_SURROGATE,
            "kernel_subtotal": frozen_kernel,
            "complete_chain": FROZEN_CHAIN,
            "residual_common": common,
        },
        "candidate": {
            "two_vertical_forward_cores": 2 * VERTICAL_CORE,
            "two_fused_splits": 2 * split,
            "quadratic_bm": qbm,
            "fused_merge": merge,
            "vertical_inverse_floor": VERTICAL_CORE,
            "kernel_subtotal": candidate_kernel,
            "projected_complete_chain": projected_chain,
        },
        "five_percent_gate": FROZEN_CHAIN_GATE,
        "static_gate": "pass" if gate_pass else "fail",
        "projected_improvement_percent": 100 * (FROZEN_CHAIN - projected_chain) / FROZEN_CHAIN,
        "limitations": [
            "1884 is an optimistic vertical inverse symmetry floor, not an inverse execution trace",
            "4731.420 is the tracked hybrid inverse dynamic count, not a same-binary Round 4C measurement",
            "instruction projection does not predict cycles or frontend behavior",
            "serialization and 384-norm baseinv have separate mandatory gates",
        ],
    }
    status = "intrinsic-terminal-cycle-gate-pass" if gate_pass else "stop-quadratic-terminal-before-avx2"
    result = {
        "status": status,
        "selected_qbm": schedules["selected"],
        "assembly_authorized": False,
        "intrinsics_prototype_authorized": gate_pass,
        "intrinsics_prototype_completed": gate_pass,
        "direct_terminal_cycle_gate": {
            "status": "pass" if gate_pass else "not-run",
            "old_tsc_median": 601.868 if gate_pass else None,
            "new_tsc_median": 553.028 if gate_pass else None,
            "improvement_percent": 8.11474 if gate_pass else None,
            "environment": "local Intel Core Ultra 7 155H, powersave governor",
        },
        "production_changed": False,
        "reason": (
            "The exact benchmark-only terminal boundary clears the direct 5% cycle gate, "
            "but the inverse term is still only a symmetry floor and serialization/baseinv "
            "are not closed. Assembly remains unauthorized."
            if gate_pass else
            "The consumer-complete static floor does not clear 95% of the frozen chain."
        ),
        "next_gate": (
            "concrete executable paired vertical inverse trace, followed by direct "
            "serialization and baseinv caller benchmarks"
        ),
    }
    return accounting, result


def artifacts() -> dict[Path, Any]:
    factors = factorization()
    ranges = range_metadata()
    schedules = static_schedules(ranges)
    chain, result = decision(schedules)
    manifest = {
        "round": "4C",
        "parent": "a8f713c",
        "sources": {
            str(COMPONENTS_FILE.relative_to(REPO)): sha256(COMPONENTS_FILE),
            str((VERTICAL / "generated/vertical-forward-schedule.json").relative_to(REPO)): sha256(VERTICAL / "generated/vertical-forward-schedule.json"),
            str(BENCHMARK_FILE.relative_to(REPO)): sha256(BENCHMARK_FILE),
            str((HERE / "src/qbm_intrinsic.c").relative_to(REPO)): sha256(HERE / "src/qbm_intrinsic.c"),
            str((HERE / "src/inverse_stage1_intrinsic.c").relative_to(REPO)): sha256(HERE / "src/inverse_stage1_intrinsic.c"),
            str((HERE / "src/transpose_intrinsic.c").relative_to(REPO)): sha256(HERE / "src/transpose_intrinsic.c"),
            str((HERE.parent / "gt_ntt/gt_basemul_layout_asm.S").relative_to(REPO)): sha256(HERE.parent / "gt_ntt/gt_basemul_layout_asm.S"),
        },
        "production_files_modified": [],
    }
    return {
        HERE / "generated/quadratic-factorization.json": factors,
        HERE / "generated/quadratic-constants.h": constant_header(factors),
        HERE / "generated/quartic-lambda.c": quartic_lambda_source(),
        HERE / "generated/quadratic-range-metadata.json": ranges,
        HERE / "generated/qbm-static-schedules.json": schedules,
        HERE / "generated/source-manifest.json": manifest,
        HERE / "results/round4c-chain-floor.json": chain,
        HERE / "results/round4c-decision.json": result,
        HERE / "results/round4c-consumer-estimates.json": consumer_estimates(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    values = artifacts()
    if args.check:
        for path, value in values.items():
            expected = value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True) + "\n"
            assert path.exists(), f"missing {path}"
            assert path.read_text() == expected, f"stale {path}"
        print("quadratic terminal generated artifacts are current")
        return 0
    for path, value in values.items():
        if isinstance(value, str):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)
        else:
            write_json(path, value)
    print(f"wrote {len(values)} Round 4C artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
