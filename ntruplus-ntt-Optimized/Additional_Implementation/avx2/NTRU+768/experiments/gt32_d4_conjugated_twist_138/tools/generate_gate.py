#!/usr/bin/env python3
"""Gate 138: exact D4 diagonal conjugation on the production GT32 DAG.

This is deliberately a generator-only gate.  It distinguishes scalar
factorizability from an AVX2-realizable TILE4 topology and accounts both the
generic 2F+B3 path and the actual Encap operand provenance.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


Q = 3457
NU = 2
R = (1 << 16) % Q
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
TILE4_GENERATOR = (
    REPO / "experiments/avx2_gt32_tile4_official_001/tools/generate_tile4.py"
)
D4_GATE = REPO / "experiments/gt32_d4_fixed_modulus_norm/generated/d4_fixed_modulus_norm.json"
QL2_ASM = REPO / "experiments/gt32_ql2_shared_convergence_103/generated/basemul_ql2.s"
OUT = ROOT / "generated/d4_conjugated_twist_gate.json"


def load_tile4():
    spec = importlib.util.spec_from_file_location("tile4_generator_138", TILE4_GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def inv(value: int) -> int:
    return pow(value % Q, Q - 2, Q)


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def fourth_roots(value: int) -> list[int]:
    roots = [x for x in range(1, Q) if pow(x, 4, Q) == value % Q]
    assert len(roots) == 4
    return roots


def pairs(stage: int):
    distance = 32 >> stage
    for base in range(0, 32, 2 * distance):
        for offset in range(distance):
            yield base + offset, base + offset + distance, base


def original_factor(tile4, stage: int, base: int) -> int:
    return pow(tile4.OMEGA32, tile4.forward_power(stage, base), Q)


def current_forward(tile4, values: list[int]) -> list[int]:
    values = values[:]
    for stage in range(1, 6):
        output = values[:]
        for low, high, base in pairs(stage):
            factor = original_factor(tile4, stage, base)
            product = factor * values[high] % Q
            output[low] = (values[low] + product) % Q
            output[high] = (values[low] - product) % Q
        values = output
    return values


def backward_conjugate(tile4, terminal: list[int], *, force_gs: bool) -> tuple[list[int], list[list[dict]]]:
    """Pull an output diagonal through CT butterflies exactly.

    CT is retained only when both output gauges match.  Otherwise the exact
    one-multiply identity is GS:

      diag(c,d) CT(w) = GS(d/c) diag(c,c*w).

    The returned input gauges can be folded into the existing frontend twist
    multiplications.  This greedy choice is forced wherever c != d.
    """
    gauges = terminal[:]
    by_stage: list[list[dict]] = [[] for _ in range(5)]
    for stage in range(5, 0, -1):
        before = gauges[:]
        records = []
        for low, high, base in pairs(stage):
            c, d = gauges[low], gauges[high]
            w = original_factor(tile4, stage, base)
            if c == d and not force_gs:
                kind = "CT"
                before[low] = c
                before[high] = c
                factor = w
            else:
                kind = "GS"
                before[low] = c
                before[high] = c * w % Q
                factor = d * inv(c) % Q
            records.append({
                "low_Q": low,
                "high_Q": high,
                "kind": kind,
                "candidate_factor": factor,
                "candidate_factor_centered": centered(factor),
            })
        gauges = before
        by_stage[stage - 1] = records
    return gauges, by_stage


def backward_conjugate_joint(tile4, terminals: list[list[int]]):
    """Conjugate while enforcing one CT/GS topology for all TILE4 degrees."""
    gauges = [row[:] for row in terminals]
    by_degree = [[[] for _ in range(5)] for _ in range(4)]
    for stage in range(5, 0, -1):
        before = [row[:] for row in gauges]
        records = [[] for _ in range(4)]
        for low, high, base in pairs(stage):
            w = original_factor(tile4, stage, base)
            kind = ("CT" if all(gauges[degree][low] == gauges[degree][high]
                                for degree in range(4)) else "GS")
            for degree in range(4):
                c, d = gauges[degree][low], gauges[degree][high]
                if kind == "CT":
                    before[degree][low] = c
                    before[degree][high] = c
                    factor = w
                else:
                    before[degree][low] = c
                    before[degree][high] = c * w % Q
                    factor = d * inv(c) % Q
                records[degree].append({
                    "low_Q": low,
                    "high_Q": high,
                    "kind": kind,
                    "candidate_factor": factor,
                    "candidate_factor_centered": centered(factor),
                })
        gauges = before
        for degree in range(4):
            by_degree[degree][stage - 1] = records[degree]
    return gauges, by_degree


def candidate_forward(values: list[int], input_gauges: list[int], stages: list[list[dict]]) -> list[int]:
    values = [x * g % Q for x, g in zip(values, input_gauges)]
    for records in stages:
        output = values[:]
        for record in records:
            low, high = record["low_Q"], record["high_Q"]
            factor = record["candidate_factor"]
            if record["kind"] == "CT":
                product = factor * values[high] % Q
                output[low] = (values[low] + product) % Q
                output[high] = (values[low] - product) % Q
            else:
                total = (values[low] + values[high]) % Q
                difference = (values[low] - values[high]) % Q
                output[low] = total
                output[high] = factor * difference % Q
        values = output
    return values


def prove_factorization(tile4, terminal: list[int], inputs: list[int], stages: list[list[dict]]) -> int:
    checks = 0
    for source in range(32):
        vector = [int(index == source) for index in range(32)]
        expected = [x * d % Q for x, d in zip(current_forward(tile4, vector), terminal)]
        actual = candidate_forward(vector, inputs, stages)
        assert actual == expected
        checks += 1
    return checks


def mont_product_bound(tile4, input_bound: int, factors: list[int]) -> int:
    mont = [centered(value * R) for value in factors]
    return tile4.product_bound(input_bound, mont)


def propagate_bounds(tile4, stages_by_degree: list[list[list[dict]]]) -> dict:
    """Conservative bound for one uniform-YMM topology.

    A TILE4 vector contains all four degrees.  A vector butterfly therefore
    uses GS if any c=1..3 lane needs GS; c=0 can use the same GS with factor 1.
    Factors remain lane-dependent table data, as in the existing code.
    """
    bounds = [[1728] * 32 for _ in range(4)]
    stage_reports = []
    for stage in range(1, 6):
        output = [row[:] for row in bounds]
        max_pre_add = 0
        max_product = 0
        gs_butterflies = 0
        ct_butterflies = 0
        for edge_index, (low, high, _) in enumerate(pairs(stage)):
            lane_records = [stages_by_degree[degree][stage - 1][edge_index]
                            for degree in range(4)]
            kind = "GS" if any(record["kind"] == "GS" for record in lane_records) else "CT"
            gs_butterflies += kind == "GS"
            ct_butterflies += kind == "CT"
            for degree, record in enumerate(lane_records):
                factor = record["candidate_factor"]
                if kind == "CT":
                    product = mont_product_bound(tile4, bounds[degree][high], [factor])
                    value = bounds[degree][low] + product
                    output[degree][low] = value
                    output[degree][high] = value
                    max_product = max(max_product, product)
                else:
                    pre_add = bounds[degree][low] + bounds[degree][high]
                    product = mont_product_bound(tile4, pre_add, [factor])
                    output[degree][low] = pre_add
                    output[degree][high] = product
                    max_pre_add = max(max_pre_add, pre_add)
                    max_product = max(max_product, product)
        bounds = output
        stage_reports.append({
            "stage": stage,
            "GS_scalar_butterflies_per_degree_upper": gs_butterflies,
            "CT_scalar_butterflies_per_degree_lower": ct_butterflies,
            "max_pre_multiply_add_abs_bound": max_pre_add,
            "max_product_abs_bound": max_product,
            "max_output_abs_bound": max(max(row) for row in bounds),
            "signed_int16_safe": max(max(row) for row in bounds) < 32768,
        })
    return {
        "input_abs_bound": 1728,
        "stages": stage_reports,
        "terminal_max_abs_bound": max(max(row) for row in bounds),
        "all_signed_int16_safe": all(row["signed_int16_safe"] for row in stage_reports),
    }


def vector_chain_count(stage: int) -> int:
    # Per tile in the current TILE4 realization.
    return 4 if stage <= 3 else 8


def main() -> None:
    tile4 = load_tile4()
    d4 = json.loads(D4_GATE.read_text())
    assert d4["field_proof"]["identity"] == "lambda_i=2*s_i^4"

    # Use production (k3,branch,Q) order, not the BaseMul transpose-table order.
    lambdas = []
    roots = []
    for k3 in range(3):
        for branch in range(2):
            tile_lambdas = [tile4.lambda_montgomery(k3, q_index, branch) % Q
                            for q_index in range(32)]
            assert len(set(tile_lambdas)) == 32
            tile_roots = [min(fourth_roots(value * inv(NU) % Q),
                              key=lambda root: abs(centered(root)))
                          for value in tile_lambdas]
            assert all(NU * pow(root, 4, Q) % Q == value
                       for root, value in zip(tile_roots, tile_lambdas))
            lambdas.append(tile_lambdas)
            roots.append(tile_roots)

    tile_reports = []
    total_basis_checks = 0
    aggregate_kind = {stage: {"CT": 0, "GS": 0} for stage in range(1, 6)}
    representative_stages = None
    for tile_index, tile_roots in enumerate(roots):
        terminals = [[pow(root, degree, Q) for root in tile_roots]
                     for degree in range(4)]
        input_gauges_by_degree, degree_stages = backward_conjugate_joint(
            tile4, terminals
        )
        degree_records = []
        for degree in range(4):
            terminal = terminals[degree]
            input_gauges = input_gauges_by_degree[degree]
            stages = degree_stages[degree]
            total_basis_checks += prove_factorization(tile4, terminal, input_gauges, stages)
            counts = {}
            for stage in range(1, 6):
                stage_counts = {kind: sum(record["kind"] == kind
                                          for record in stages[stage - 1])
                                for kind in ("CT", "GS")}
                counts[str(stage)] = stage_counts
                for kind in ("CT", "GS"):
                    aggregate_kind[stage][kind] += stage_counts[kind]
            degree_records.append({
                "degree": degree,
                "terminal_unique_scales": len(set(terminal)),
                "input_unique_scales": len(set(input_gauges)),
                "input_gauges_centered": [centered(value) for value in input_gauges],
                "stage_scalar_topologies": counts,
            })
        if representative_stages is None:
            representative_stages = degree_stages
        bounds = propagate_bounds(tile4, degree_stages)
        tile_reports.append({
            "tile": tile_index,
            "k3": tile_index // 2,
            "branch": tile_index % 2,
            "roots_centered": [centered(value) for value in tile_roots],
            "degrees": degree_records,
            "range": bounds,
        })

    # The exact scalar solution forces GS in every c=1 terminal butterfly.
    # Because c=0..3 share TILE4 vectors, the executable topology must also be
    # GS there.  Count full-width vector Montgomery chains, not scalar edges.
    current_per_tile = sum(vector_chain_count(stage) for stage in range(2, 6))
    candidate_per_tile = sum(vector_chain_count(stage) for stage in range(1, 6))
    assert current_per_tile == 24 and candidate_per_tile == 28
    added_per_forward = 6 * (candidate_per_tile - current_per_tile)
    assert added_per_forward == 24

    # B3 output D^-1 can reuse the existing per-coefficient R2 finalizer by
    # replacing its constants.  Q24 itself remains bit-for-bit unchanged.
    ql2_text = QL2_ASM.read_text()
    assert "finalizer" in ql2_text and "TILE4_BASEMUL_FUNCTION" in ql2_text
    b3_saved = 36
    generic_net = 2 * added_per_forward - b3_saved
    encap_decode_bridge = 36
    encap_net = added_per_forward + encap_decode_bridge - b3_saved

    all_ranges_safe = all(tile["range"]["all_signed_int16_safe"]
                          for tile in tile_reports)
    result = {
        "schema": "ntruplus768-gt32-d4-conjugated-twist-v1",
        "experiment": "GT32-D4-CONJUGATED-TWIST-TRANSPOSE-138",
        "status": "COMPLETE_STATIC_REJECT_NO_OPERATION_CLASS_DELETION",
        "production_modified": False,
        "assembly_emitted": False,
        "benchmark_run": False,
        "source_hashes": {
            TILE4_GENERATOR.name: hashlib.sha256(TILE4_GENERATOR.read_bytes()).hexdigest(),
            D4_GATE.name: hashlib.sha256(D4_GATE.read_bytes()).hexdigest(),
            QL2_ASM.name: hashlib.sha256(QL2_ASM.read_bytes()).hexdigest(),
        },
        "exact_algebra": {
            "q": Q,
            "normalized_modulus": NU,
            "tiles": 6,
            "leaves": 192,
            "identity": "lambda[tile,Q] = 2*s[tile,Q]^4",
            "output_diagonal": "D(s)=diag(1,s,s^2,s^3)",
            "butterfly_identity": "diag(c,d)*CT(w) = GS(d/c)*diag(c,c*w)",
            "basis_vector_checks": total_basis_checks,
            "all_checks_pass": total_basis_checks == 6 * 4 * 32,
        },
        "current_ntt32": {
            "S1": "raw CT, no Montgomery chain",
            "S2_to_S5": "CT with one high-arm Montgomery chain per butterfly",
            "full_width_vector_chains_per_tile": current_per_tile,
            "full_width_vector_chains_per_forward": 6 * current_per_tile,
        },
        "conjugated_ntt32": {
            "mathematically_exact": True,
            "input_diagonal_can_replace_existing_frontend_twist_constants": True,
            "reason": "the wide frontend already Montgomery-multiplies every deposited lane by a lane-dependent table",
            "TILE4_constraint": "all four quartic degrees in one YMM butterfly use one CT/GS topology",
            "root_choice_independent_topology": "S5 is forced by distinct lambda values; after S5 the c=0 gauges alone force GS through S4..S1",
            "forced_change": "S1 must become GS so its difference arm receives a lane-dependent Montgomery factor",
            "full_width_vector_chains_per_tile": candidate_per_tile,
            "full_width_vector_chains_per_forward": 6 * candidate_per_tile,
            "added_full_width_chains_per_forward": added_per_forward,
            "aggregate_scalar_topologies": {str(stage): counts for stage, counts in aggregate_kind.items()},
            "range_proof": {
                "all_tiles_signed_int16_safe": all_ranges_safe,
                "maximum_terminal_abs_bound": max(tile["range"]["terminal_max_abs_bound"]
                                                  for tile in tile_reports),
                "note": "conservative interval propagation; exact field equality does not rely on the bound",
            },
        },
        "terminal_absorption": {
            "normalized_B3_output_to_current_Q24": "replace the existing B3 R2 finalizer constants by R2*s^-c",
            "added_Montgomery_chains": 0,
            "Q24_arithmetic_changed": False,
            "Q24_routes_changed": False,
            "dynamic_constant_load_instruction_delta": 0,
            "rodata_growth_upper_bytes": 2304,
            "message_operand": "keep message Forward in current unnormalized M/QL2 form",
        },
        "complete_path_accounting": {
            "unit": "full-width vector Montgomery chains per polynomial path",
            "normalized_B3_credit": -b3_saved,
            "generic_two_forward_operands": {
                "Forward_conjugation_cost": 2 * added_per_forward,
                "B3_credit": -b3_saved,
                "terminal_inverse_diagonal": 0,
                "net_delta": generic_net,
            },
            "actual_Encap_provenance": {
                "r_Forward_conjugation_cost": added_per_forward,
                "h_Decode_normalization_bridge": encap_decode_bridge,
                "B3_credit": -b3_saved,
                "terminal_inverse_diagonal": 0,
                "net_delta": encap_net,
                "why_h_is_not_free": "the wire decoder has no existing arbitrary-constant Montgomery node to relabel",
            },
        },
        "route_and_register_accounting": {
            "standalone_D_transpose": 0,
            "new_physical_layout": False,
            "new_shuffle_family": 0,
            "peak_YMM": "not increased by the symbolic topology; GS uses the same low/high pair plus Montgomery temporaries",
            "important_cost": "24 new full-width S1 Montgomery chains per Forward, not routing",
        },
        "decision": {
            "generator_gate": "PASS",
            "mathematical_conjugation": "PASS",
            "range": "PASS" if all_ranges_safe else "FAIL",
            "assembly": "NOT_AUTHORIZED",
            "reason": "the complete path does not delete an operation class: generic 2F+B3 is +12 chains and actual Encap is +24 chains before any range-repair overhead",
            "scope_closed": "current TILE4 packing + one-multiply radix-2 CT/GS NTT32 + normalized D4 B3 + current Q24",
            "family_closed": False,
            "reopen_conditions": [
                "a frontend/NTT factorization that absorbs D(s) without adding the 24 S1 chains per Forward",
                "an h decoder that emits the normalized operand by replacing, not adding, a multiplication/reduction class",
                "an asymmetric raw-h/normalized-r tensor that retains the normalized B3 chain saving",
            ],
        },
        "tiles": tile_reports,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "basis_checks": total_basis_checks,
        "range_safe": all_ranges_safe,
        "added_chains_per_forward": added_per_forward,
        "generic_2F_B3_net_chains": generic_net,
        "actual_encap_net_chains": encap_net,
        "decision": result["status"],
    }, indent=2))


if __name__ == "__main__":
    main()
