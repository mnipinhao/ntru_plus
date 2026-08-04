#!/usr/bin/env python3
"""Generate and validate the Round 4 weighted GT(3,16) pre-kernel contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

Q = 3457
N = 768
D = 4
ZETA = 22
ZETA_ORDER = 576
PHI = 2735
PHI_INV = 723
OMEGA96 = 675
OMEGA48 = pow(OMEGA96, 2, Q)
OMEGA16 = pow(OMEGA48, 3, Q)
OMEGA3 = pow(OMEGA48, 16, Q)
VERTICAL_REVISION = "76a0c183f73fb008a808c0c3ebe97af8415ecad5"

HERE = Path(__file__).resolve().parent.parent
REPO = next(p for p in (HERE, *HERE.parents) if (p / ".git").exists())
ROUND3_REFERENCE = REPO / (
    "ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/"
    "experiments/avx2_gt_rewrite_official_001/generated/reference-tables.json"
)
VERTICAL_PREFIX = REPO / (
    "ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/"
    "experiments/gt_ntt"
)
VERTICAL_FILES = (
    "gt_ntt_frontend_stage12_soa.S",
    "gt_ntt_stage345_soa.s",
    "gt_ntt_tables.c",
    "gt_basemul_layout_asm.S",
    "gt_baseinv_native.c",
    "gt_baseinv_native_prepare_asm.S",
    "gt_invntt_fused_soa.S",
    "gt_invntt_ntt32_soa.s",
    "gt_invntt_postprocess_soa.s",
    "gt_invntt_soa.c",
    "gt_invntt_soa_tables.inc",
    "gt_native_pack_asm.S",
    "gt_native_pack.c",
)


def mod_inv(x: int) -> int:
    return pow(x, -1, Q)


def centered(x: int) -> int:
    x %= Q
    return x - Q if x > (Q - 1) // 2 else x


def sqrt_all(value: int) -> list[int]:
    return [x for x in range(1, Q) if x * x % Q == value]


def roots48(value: int) -> list[int]:
    return [x for x in range(1, Q) if pow(x, 48, Q) == value]


def discrete_logs() -> dict[int, int]:
    result: dict[int, int] = {}
    value = 1
    for exponent in range(ZETA_ORDER):
        result[value] = exponent
        value = value * ZETA % Q
    assert len(result) == ZETA_ORDER
    return result


LOG = discrete_logs()


def input_crt(i3: int, i16: int) -> int:
    return (16 * i3 + 33 * i16) % 48


def output_crt(k3: int, k16: int) -> int:
    return (16 * k3 + 3 * k16) % 48


def branch_specs() -> list[dict[str, int]]:
    result = []
    for top, gamma in enumerate((PHI, PHI_INV)):
        betas = sqrt_all(gamma)
        assert len(betas) == 2 and (betas[0] + betas[1]) % Q == 0
        # Preserve the old F=2/F=22 half first, then its sibling branch.
        preferred = 2 if top == 0 else 22
        preferred_beta = mod_inv(pow(preferred, 48, Q))
        betas.sort(key=lambda beta: beta != preferred_beta)
        for split, beta in enumerate(betas):
            result.append({"branch": 2 * top + split, "top": top,
                           "gamma": gamma, "beta": beta})
    return result


def weight_matrix(factor: int, sign: int = -1) -> list[list[int]]:
    return [[pow(factor, sign * input_crt(i3, i16), Q)
             for i16 in range(16)] for i3 in range(3)]


def factor_weight_matrix(factor: int, beta: int, sign: int = -1) -> dict[str, Any]:
    full = weight_matrix(factor, sign)
    row = [full[i3][0] for i3 in range(3)]
    column = [full[0][i16] for i16 in range(16)]
    residual = [[full[i3][i16] * mod_inv(row[i3] * column[i16] % Q) % Q
                 for i16 in range(16)] for i3 in range(3)]
    wrap = []
    for i3 in range(3):
        wrap_row = []
        for i16 in range(16):
            raw = 16 * i3 + 33 * i16
            index = raw % 48
            quotient = (raw - index) // 48
            correction = pow(beta, sign * quotient, Q)
            assert full[i3][i16] == (
                pow(factor, sign * 16 * i3, Q)
                * pow(factor, sign * 33 * i16, Q)
                * correction) % Q
            wrap_row.append({"index": index, "quotient": quotient,
                             "correction": centered(correction)})
        wrap.append(wrap_row)
    covered = sum(value == 1 for values in residual for value in values)
    return {
        "full_weight": [[centered(x) for x in values] for values in full],
        "row_factor": [centered(x) for x in row],
        "column_factor": [centered(x) for x in column],
        "residual_correction": [
            [centered(x) for x in values] for values in residual
        ],
        "wrap": wrap,
        "rank1_covered_entries": covered,
        "rank1_covered_percent": 100.0 * covered / 48.0,
        "residual_distinct_constants": len({
            x for values in residual for x in values if x != 1
        }),
        "residual_nonidentity_entries": 48 - covered,
    }


def candidate_record(spec: dict[str, int], factor: int) -> dict[str, Any]:
    matrix = factor_weight_matrix(factor, spec["beta"])
    inverse_matrix = factor_weight_matrix(factor, spec["beta"], 1)
    constants = {
        x % Q for source in (matrix, inverse_matrix)
        for rows in source["full_weight"] for x in rows
    }
    cheap = {1, Q - 1, OMEGA3, mod_inv(OMEGA3)}
    cheap.update(pow(OMEGA16, exponent, Q) for exponent in range(16))
    cheap_hits = sum((x % Q) in cheap for source in (matrix, inverse_matrix)
                     for rows in source["full_weight"] for x in rows)
    return {
        "F": factor,
        "F_centered": centered(factor),
        "F_exponent_base22": LOG[factor],
        "residual_nonidentity_entries": matrix["residual_nonidentity_entries"],
        "residual_distinct_constants": matrix["residual_distinct_constants"],
        "cheap_weight_entries": cheap_hits,
        "distinct_full_weights": len(constants),
        "max_centered_weight_abs": max(abs(centered(x)) for x in constants),
    }


def select_roots(specs: list[dict[str, int]]) -> tuple[list[list[dict[str, Any]]],
                                                        list[dict[str, Any]]]:
    all_candidates = []
    for spec in specs:
        candidates = [candidate_record(spec, factor)
                      for factor in roots48(mod_inv(spec["beta"]))]
        assert len(candidates) == 48
        candidates.sort(key=lambda c: (
            c["residual_nonidentity_entries"],
            -c["cheap_weight_entries"],
            c["residual_distinct_constants"],
            c["distinct_full_weights"],
            c["max_centered_weight_abs"],
            c["F_exponent_base22"],
        ))
        all_candidates.append(candidates)

    def mask(record: dict[str, Any]) -> int:
        result = 0
        for sign in (-1, 1):
            for row in weight_matrix(record["F"], sign):
                for value in row:
                    result |= 1 << value
        return result

    # Exhaust all 48^4 joint choices.  Meet-in-the-middle bitsets make the
    # 5,308,416 constant-union comparisons exact rather than relying on a
    # local shortlist that could discard a globally reusable root.
    pairs01 = [(left, right, mask(left) | mask(right))
               for left in all_candidates[0] for right in all_candidates[1]]
    pairs23 = [(left, right, mask(left) | mask(right))
               for left in all_candidates[2] for right in all_candidates[3]]
    best_key = None
    best_combo = None
    for left0, left1, left_mask in pairs01:
        for right0, right1, right_mask in pairs23:
            combo = (left0, left1, right0, right1)
            union_count = (left_mask | right_mask).bit_count()
            key = (
                sum(r["residual_nonidentity_entries"] for r in combo),
                union_count,
                (2 * union_count + 63) // 64,
                -sum(r["cheap_weight_entries"] for r in combo),
                sum(r["max_centered_weight_abs"] for r in combo),
                tuple(r["F_exponent_base22"] for r in combo),
            )
            if best_key is None or key < best_key:
                best_key = key
                best_combo = combo
    assert best_combo is not None
    return all_candidates, [dict(record) for record in best_combo]


def component_records(specs: list[dict[str, int]], selected: list[dict[str, Any]],
                      official_index: list[int]) -> list[dict[str, Any]]:
    official_position = {exponent: slot
                         for slot, exponent in enumerate(official_index)}
    records = []
    for spec, root in zip(specs, selected):
        fexp = root["F_exponent_base22"]
        for k3 in range(3):
            for k16 in range(16):
                k = output_crt(k3, k16)
                alpha_exp = (12 * k - fexp) % ZETA_ORDER
                alpha = pow(ZETA, alpha_exp, Q)
                assert pow(alpha, 48, Q) == spec["beta"]
                records.append({
                    "slot": len(records),
                    "branch": spec["branch"],
                    "top": spec["top"],
                    "k3": k3,
                    "k16": k16,
                    "frequency": k,
                    "alpha": centered(alpha),
                    "alpha_exp": alpha_exp,
                    "official_slot": official_position[alpha_exp],
                    "repr_scale": 1,
                    "repr_scale_exp": 0,
                    "montgomery_power": 0,
                    "range": [-1728, 1728],
                    "word_formula": "((branch*3+k3)*4+degree)*16+k16",
                })
    assert len(records) == 192
    assert sorted(r["alpha_exp"] for r in records) == sorted(official_index)
    assert sorted(r["official_slot"] for r in records) == list(range(192))
    return records


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def constant_stream(specs: list[dict[str, int]], sign: int,
                    prefix: str) -> bytes:
    lines = ["/* Generated by tools/generate_gt16.py; do not edit. */",
             ".section .rodata", ".p2align 5"]
    for spec in specs:
        matrix = weight_matrix(spec["F"], sign)
        for row, values in enumerate(matrix):
            lines.append(f".globl {prefix}_b{spec['branch']}_r{row}")
            lines.append(f"{prefix}_b{spec['branch']}_r{row}:")
            lines.append("\t.short " + ", ".join(str(centered(x)) for x in values))
    return ("\n".join(lines) + "\n").encode()


def derive() -> dict[str, bytes]:
    round3 = json.loads(ROUND3_REFERENCE.read_text(encoding="utf-8"))
    official_index = round3["official_index"]
    assert len(official_index) == 192
    assert pow(ZETA, ZETA_ORDER, Q) == 1
    assert pow(ZETA, ZETA_ORDER // 2, Q) == Q - 1
    assert PHI * PHI_INV % Q == 1
    assert pow(OMEGA48, 48, Q) == 1 and pow(OMEGA48, 24, Q) == Q - 1
    assert sorted(input_crt(a, b) for a in range(3) for b in range(16)) == list(range(48))
    assert sorted(output_crt(a, b) for a in range(3) for b in range(16)) == list(range(48))

    specs = branch_specs()
    all_candidates, selected = select_roots(specs)
    for spec, root in zip(specs, selected):
        assert pow(root["F"], 48, Q) == mod_inv(spec["beta"])
        spec.update({"F": root["F"],
                     "F_exponent_base22": root["F_exponent_base22"]})
    components = component_records(specs, selected, official_index)

    branches = {
        "q": Q,
        "ring": "x^768-x^384+1",
        "terminal_degree": D,
        "factorization": "special-R2 then standard-R2 then weighted-GT(3,16)",
        "branches": specs,
        "ntt16_rows": {"per_beta_branch": 12, "per_top_branch": 24,
                       "full_transform": 48, "inverse_full_transform": 48},
    }
    roots = {
        "selection_policy": "exhaustive-joint-search-over-48^4-forward-and-inverse-root-combinations",
        "candidate_count_per_branch": 48,
        "all": [{"branch": spec["branch"], "beta": spec["beta"],
                 "candidates": candidates}
                for spec, candidates in zip(specs, all_candidates)],
    }
    selected_roots = {
        "selected": [{**spec, **root}
                     for spec, root in zip(specs, selected)],
        "warning": "static AVX2 cost is not established by this algebraic score",
    }
    factorizations = []
    inverse_factorizations = []
    for spec in specs:
        factorizations.append({
            "branch": spec["branch"], "beta": spec["beta"], "F": spec["F"],
            **factor_weight_matrix(spec["F"], spec["beta"]),
        })
        inverse_factorizations.append({
            "branch": spec["branch"], "beta": spec["beta"], "F": spec["F"],
            **factor_weight_matrix(spec["F"], spec["beta"], 1),
        })

    scale_nodes = []
    for component in components:
        common = {key: component[key] for key in
                  ("slot", "alpha_exp", "repr_scale_exp",
                   "montgomery_power", "range")}
        scale_nodes.append({
            **common,
            "add_sub": "requires-identical-repr-scale",
            "basemul_compensation": "s^-1=1",
            "baseinv_compensation": "s^2=1",
            "encode_compare_unscale": "s^-1=1",
        })

    forward_schedule = {
        "orders": ["DFT3-first", "NTT16-first"],
        "input_crt": [[input_crt(i3, i16) for i16 in range(16)]
                      for i3 in range(3)],
        "output_crt": [[output_crt(k3, k16) for k16 in range(16)]
                       for k3 in range(3)],
        "omega3": centered(OMEGA3),
        "omega16": centered(OMEGA16),
        "full_ntt16_invocations": 48,
        "standalone_preweight_pass": "forbidden-production-diagnostic-only",
        "output_layout": "[branch][k3][degree][k16]",
    }
    inverse_schedule = {
        "orders": ["inverse-NTT16-first", "inverse-DFT3-first"],
        "normalization": mod_inv(48),
        "postweight": "F^i compiled into inverse execution constants",
        "full_inverse_ntt16_invocations": 48,
        "postweight_factorizations": inverse_factorizations,
    }
    fusion = {
        "schema_version": 1,
        "scope": "full 768-coefficient transform",
        "explicit_twist_multiplies": 4 * 4 * 48,
        "standalone_twist_pass_in_candidate": 0,
        "absorbed_existing_multiplies": "requires-row-kernel instruction selection",
        "absorbed_but_reduction_lost": "requires-per-layer range schedule",
        "residual_required_vector_modmul_lower_bound": 48,
        "residual_lower_bound_reason": (
            "canonical s=1 needs one weight/modified-stage vector multiply per horizontal row "
            "in addition to the three nonidentity cyclic NTT16 stages"
        ),
        "deferred_output_scales": 0,
        "new_reductions_required": "requires-per-layer range schedule",
        "constant_vector_loads": "requires-tile selection",
        "distinct_preweight_constants": len({
            x % Q for spec in specs for row in weight_matrix(spec["F"])
            for x in row
        }),
        "distinct_combined_forward_inverse_weight_constants": len({
            x % Q for spec in specs for sign in (-1, 1)
            for row in weight_matrix(spec["F"], sign) for x in row
        }),
        "decision": "math-compiled-static-avx2-accounting-pending",
    }
    vertical_instructions = 2026.260
    ntt16_row_floor = {
        "partner_permutations": 4,
        "low_high_replication_blends": 8,
        "modular_multiply_instructions": 16,
        "signed_combine_instructions": 8,
        "total": 36,
    }
    horizontal_ntt16_floor = 48 * ntt16_row_floor["total"]
    dft3_floor = 16 * 11
    mandatory_io_floor = 48 + 48
    full_floor = horizontal_ntt16_floor + dft3_floor + mandatory_io_floor
    floor_improvement = 100.0 * (vertical_instructions - full_floor) / vertical_instructions
    static_cost = {
        "comparison": "horizontal-GT16-full-graph-vs-frozen-vertical-GT32-native",
        "scope": "single-transform-per-YMM canonical-s=1 schedule proposed for Round 4",
        "floor_assumptions": [
            "packed-int16 Montgomery constant multiply requires four AVX2 instructions",
            "each horizontal stage requires one partner permutation and two low/high replication blends",
            "signed combine uses the optimistic two-instruction sign-plus-add form",
            "three cyclic stages are nonidentity and weighted canonical input requires one additional vector multiply per row",
            "all radix-2, packing, correction, normalization, and control work is omitted from the floor",
        ],
        "reopen_condition": (
            "a concrete fixed-control AVX2 construction must invalidate at least one floor assumption "
            "and demonstrate a full-graph floor below 1924.947 instructions"
        ),
        "full_ntt16_rows_counted": 48,
        "frozen_vertical_champion": {
            "dynamic_instructions_per_forward": vertical_instructions,
            "source": "tracked BENCHMARK_RESULTS.md row2q2-lazy result",
        },
        "optimistic_horizontal_instruction_floor": {
            "per_ntt16_row": ntt16_row_floor,
            "all_48_ntt16_rows": horizontal_ntt16_floor,
            "sixteen_vector_dft3_groups": dft3_floor,
            "mandatory_48_loads_plus_48_stores": mandatory_io_floor,
            "not_yet_counted": ["special-R2", "standard-R2", "input-packing",
                                "branch-specific-corrections", "normalization",
                                "loop-or-call-control"],
            "total_before_unaccounted_work": full_floor,
            "optimistic_improvement_percent": floor_improvement,
        },
        "required_tiles": ["tile-by-row", "tile-by-degree", "tile-by-branch-pair"],
        "register_gate": {"steady_state_data_ymm_max": 10,
                          "total_live_ymm_max": 15,
                          "emergency_temporary_reserved": 1,
                          "spill_allowed": False},
        "measure_before_asm": ["shuffle-uops", "multiply-uops", "loads-stores",
                               "range-reset-cost", "code-bytes", "constant-bytes",
                               "constant-cache-lines", "uop-cache-footprint",
                               "in-place-scratch-traffic"],
        "five_percent_floor_required": 0.95 * vertical_instructions,
        "five_percent_gate": "fail",
        "status": "stop-horizontal-single-ymm-row-before-avx2",
    }
    range_metadata = {
        "input_small": [-3, 4],
        "canonical_scalar_nodes": [-1728, 1728],
        "orders_requiring_independent_trace": ["DFT3-first", "NTT16-first"],
        "note": "canonical scalar range is proved; lazy per-layer AVX2 bounds remain a prekernel gate",
    }
    champion = {
        "source_revision": VERTICAL_REVISION,
        "source_prefix": str(VERTICAL_PREFIX.relative_to(REPO)),
        "files": {name: sha256(VERTICAL_PREFIX / name) for name in VERTICAL_FILES},
        "native_abi": "frozen tracked vertical GT(3,32) source closure",
    }
    decision = {
        "math": "pass",
        "root_search": "pass-all-48-roots-per-branch",
        "crt_wrap": "pass-full-3x16-matrices-generated",
        "official_192_leaf_mapping": "pass",
        "representation_scale_typecheck": "pass-canonical-s-equals-1",
        "scalar_forward_inverse_polymul": "evaluated-by-tests/test_scalar_gt16.py",
        "static_economics": "fail-optimistic-floor-improves-only-%.3f-percent" % floor_improvement,
        "avx2_kernel_authorized": False,
        "decision": "stop-round4-prekernel-horizontal-single-ymm-gt16",
    }

    outputs: dict[str, Any] = {
        "generated/gt16-branches.json": branches,
        "generated/gt16-all-root-candidates.json": roots,
        "generated/gt16-selected-roots.json": selected_roots,
        "generated/gt16-explicit-preweights.json": {
            "diagnostic_only": True,
            "branches": factorizations,
        },
        "generated/gt16-factorization.json": {
            "input_formula": "(16*i3+33*i16) mod 48",
            "output_formula": "(16*k3+3*k16) mod 48",
            "components": components,
        },
        "generated/gt16-residual-corrections.json": {
            "branches": factorizations,
        },
        "generated/gt16-forward-schedule.json": forward_schedule,
        "generated/gt16-inverse-schedule.json": inverse_schedule,
        "generated/gt16-basemul-scales.json": {
            "law": "out_scale=s requires compensation s^-1 for two s-scaled inputs",
            "slots": scale_nodes,
        },
        "generated/gt16-baseinv-scales.json": {
            "law": "out_scale=s requires compensation s^2 after inversion",
            "slots": scale_nodes,
        },
        "generated/gt16-range-metadata.json": range_metadata,
        "generated/gt16-live-range-estimate.json": static_cost["register_gate"],
        "generated/vertical-champion-manifest.json": champion,
        "results/round4-twist-fusion-accounting.json": fusion,
        "results/round4-static-cost.json": static_cost,
        "results/round4-prekernel-decision.json": decision,
    }
    serialized = {name: json_bytes(value) for name, value in outputs.items()}
    serialized["generated/gt16-forward-constants.inc"] = constant_stream(
        specs, -1, "gt16_forward_weight")
    serialized["generated/gt16-inverse-constants.inc"] = constant_stream(
        specs, 1, "gt16_inverse_weight")
    manifest = {name: hashlib.sha256(content).hexdigest()
                for name, content in serialized.items()}
    serialized["generated/manifest.json"] = json_bytes({
        "schema_version": 1,
        "official_revision": "0c249d5828b90e8dd5de2c8405323d5ee2a0ce41",
        "round3_parent": "c0969e7",
        "artifacts": manifest,
    })
    return serialized


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = derive()
    stale = []
    for relative, content in outputs.items():
        path = HERE / relative
        if args.check:
            if not path.exists() or path.read_bytes() != content:
                stale.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    if stale:
        raise SystemExit("stale generated artifacts:\n" + "\n".join(stale))
    print(f"gt16-generated-check=passed artifacts={len(outputs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
