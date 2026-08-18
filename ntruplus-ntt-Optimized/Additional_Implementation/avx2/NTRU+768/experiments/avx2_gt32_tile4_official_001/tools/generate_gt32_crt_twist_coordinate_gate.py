#!/usr/bin/env python3
"""Search CRT/leaf coordinates for a cheaper GT32 wide twist.

The searched representative family is
  k3'  = a*k3 + b*(k32 mod 3)                 (mod 3)
  k32' = c*k32 + d*k3                         (mod 32)
with a in Z3*, c odd.  Row/coordinate translations and branch swap are
quotiented because they only rename rows/leaves and cannot change
multiplicative separability or vector-constant cardinality.

The second part detects the non-affine carry phase caused by reducing the
CRT representative modulo 96.  A k-dependent cyclic input-row rotation can
remove that phase and makes the table exactly A[row]*B[k].  The gate then
accounts for where B[k] has to go; separability alone is not an acceleration
mechanism.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter

import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_crt_twist_coordinate_gate.json"
RHO3 = (-723) % gt.Q


def twist_table() -> list[list[list[int]]]:
    return [[[
        pow(gt.BRANCH_SCALE[branch], -(64 * row + 33 * k) % 96, gt.Q)
        * gt.R % gt.Q
        for k in range(32)
    ] for row in range(3)] for branch in range(2)]


def coordinate_map(a: int, b: int, c: int, d: int):
    forward = {}
    inverse = {}
    for row in range(3):
        for k in range(32):
            target = ((a * row + b * (k % 3)) % 3,
                      (c * k + d * row) % 32)
            if target in inverse:
                return None
            forward[row, k] = target
            inverse[target] = (row, k)
    return forward, inverse


def dft3_absorbable(rows: list[list[int]]) -> bool:
    targets = []
    for shift in range(3):
        targets.append((pow(RHO3, shift, gt.Q),
                        pow(RHO3, 2 * shift, gt.Q)))
    for permutation in itertools.permutations(range(3)):
        ok = True
        for k in range(32):
            base = rows[permutation[0]][k]
            inverse = pow(base, -1, gt.Q)
            ratio = (rows[permutation[1]][k] * inverse % gt.Q,
                     rows[permutation[2]][k] * inverse % gt.Q)
            if ratio not in targets:
                ok = False
                break
        if ok:
            return True
    return False


def candidate_metrics(a: int, b: int, c: int, d: int,
                      table: list[list[list[int]]]):
    mapping = coordinate_map(a, b, c, d)
    if mapping is None:
        return None
    forward, inverse = mapping
    ratio_cardinality = []
    separable = True
    absorbable = True
    constant_vectors = 0
    two_constant_vectors = 0
    identity_vectors = 0

    for branch in range(2):
        rows = [[table[branch][inverse[row, k][0]][inverse[row, k][1]]
                 for k in range(32)] for row in range(3)]
        for row in (1, 2):
            ratios = {
                rows[row][k] * pow(rows[0][k], -1, gt.Q) % gt.Q
                for k in range(32)
            }
            ratio_cardinality.append(len(ratios))
            separable &= len(ratios) == 1
        absorbable &= dft3_absorbable(rows)
        for row in range(3):
            for group in range(8):
                vector = rows[row][4 * group:4 * group + 4]
                cardinality = len(set(vector))
                constant_vectors += cardinality == 1
                two_constant_vectors += cardinality <= 2
                identity_vectors += all(value == gt.R for value in vector)

    # A DFT3 remains k-local only if the three original rows map to one k'.
    dft3_cross_k_debt = sum(
        len({forward[row, k][1] for row in range(3)}) - 1
        for k in range(32)
    )

    # Count length-2 NTT32 edges whose new row coordinate changes, plus edges
    # that no longer differ in exactly one physical k bit.  These are topology
    # debts, not cycle predictions.
    ntt32_cross_row_edges = 0
    ntt32_nonradix2_edges = 0
    for row in range(3):
        for bit in range(5):
            for k in range(32):
                if (k >> bit) & 1:
                    continue
                left = forward[row, k]
                right = forward[row, k ^ (1 << bit)]
                ntt32_cross_row_edges += left[0] != right[0]
                difference = left[1] ^ right[1]
                ntt32_nonradix2_edges += (
                    difference == 0 or (difference & (difference - 1)) != 0
                )

    return {
        "parameters": {"a": a, "b": b, "c": c, "d": d},
        "ratio_cardinality": ratio_cardinality,
        "ratio_complexity_sum": sum(ratio_cardinality),
        "multiplicatively_separable": separable,
        "DFT3_shift_or_column_permutation_absorbable": absorbable,
        "full_YMM_single_constant_vectors": constant_vectors,
        "full_YMM_at_most_two_constant_vectors": two_constant_vectors,
        "full_YMM_identity_vectors": identity_vectors,
        "DFT3_cross_k_debt": dft3_cross_k_debt,
        "NTT32_cross_row_edges": ntt32_cross_row_edges,
        "NTT32_nonradix2_edges": ntt32_nonradix2_edges,
    }


def ratios(table, branch, numerator, denominator):
    return [
        table[branch][numerator][k]
        * pow(table[branch][denominator][k], -1, gt.Q) % gt.Q
        for k in range(32)
    ]


def normalized_triplet(table, branch: int, k: int, rotation: int):
    values = [table[branch][(row + rotation) % 3][k]
              for row in range(3)]
    inverse = pow(values[0], -1, gt.Q)
    return tuple(value * inverse % gt.Q for value in values)


def carry_aware_separation(table):
    """Find one cyclic row rotation per k that aligns both branches.

    The reference is k=0.  Requiring the same rotation for both top-split
    branches is important: a branch-specific row permutation would add a new
    blend/repair boundary before the two NTT32 families.
    """
    reference = [normalized_triplet(table, branch, 0, 0)
                 for branch in range(2)]
    rotations = []
    for k in range(32):
        matches = [rotation for rotation in range(3)
                   if all(normalized_triplet(table, branch, k, rotation)
                          == reference[branch] for branch in range(2))]
        assert len(matches) == 1
        rotations.append(matches[0])

    branches = []
    for branch in range(2):
        b_values = [table[branch][rotations[k]][k] for k in range(32)]
        step_ratios = [
            b_values[k + 1] * pow(b_values[k], -1, gt.Q) % gt.Q
            for k in range(31)
        ]
        common_step, count = Counter(step_ratios).most_common(1)[0]
        exceptions = [index for index, value in enumerate(step_ratios)
                      if value != common_step]
        branches.append({
            "A_row_ratios": list(reference[branch]),
            "B_values": b_values,
            "B_common_linear_step": common_step,
            "B_common_step_count": count,
            "B_step_exception_edges": exceptions,
            "B_wrap_step": (
                b_values[0] * pow(b_values[-1], -1, gt.Q) % gt.Q
            ),
            "expected_inverse_branch_scale": (
                pow(gt.BRANCH_SCALE[branch], -1, gt.Q)
            ),
        })
        assert common_step == pow(gt.BRANCH_SCALE[branch], -1, gt.Q)
        assert count == 30
        assert exceptions == [0]

    # Current: 3 wide Montgomery chains plus the one-multiply DFT3, for
    # 2 branches * 8 groups.  Once separated, diag(A) needs two input
    # constant products plus the existing DFT3 multiply.  B then either costs
    # three output products, or is pushed into NTT32 and turns the currently
    # raw 16-butterfly S1 nonidentity in all six transforms.  Those 96 scalar
    # butterflies are packed as four YMM chains per tile, hence 24 vector
    # chains rather than 96 vector chains.
    current_wide = 48
    current_dft3 = 16
    separated_a_plus_dft3 = 48
    separated_b_at_dft_output = 48
    separated_b_in_ntt32_s1 = 6 * 4
    return {
        "status": "exactly-separable-by-carry-aware-row-rotation",
        "row_rotations_by_k": rotations,
        "rotation_definition": "new_row[i,k] = old_row[(i+rotation[k]) mod 3,k]",
        "branches": branches,
        "chain_accounting_per_forward": {
            "current_wide_twist": current_wide,
            "current_DFT3": current_dft3,
            "current_total": current_wide + current_dft3,
            "separated_A_plus_DFT3": separated_a_plus_dft3,
            "option_B_at_DFT3_output": separated_b_at_dft_output,
            "option_output_scaling_total": (
                separated_a_plus_dft3 + separated_b_at_dft_output
            ),
            "option_output_scaling_delta": (
                separated_a_plus_dft3 + separated_b_at_dft_output
                - current_wide - current_dft3
            ),
            "option_B_absorbed_into_NTT32_new_S1_vector_chains": separated_b_in_ntt32_s1,
            "option_B_absorbed_into_NTT32_new_S1_scalar_butterflies": 6 * 16,
            "option_NTT32_absorption_total": (
                separated_a_plus_dft3 + separated_b_in_ntt32_s1
            ),
            "option_NTT32_absorption_delta": (
                separated_a_plus_dft3 + separated_b_in_ntt32_s1
                - current_wide - current_dft3
            ),
        },
        "reason_B_is_not_free": (
            "B[k] is geometric with branch_scale^-1 on 30/31 linear edges, "
            "but has a CRT seam and is not a 32nd-root leaf permutation; "
            "pushing it into current N5 makes the identity S1 nonidentity"
        ),
    }


def main() -> None:
    table = twist_table()
    carry_separation = carry_aware_separation(table)
    current_ratios = {}
    for branch in range(2):
        current_ratios[str(branch)] = {}
        for row in (1, 2):
            values = ratios(table, branch, row, 0)
            current_ratios[str(branch)][f"row{row}_over_row0"] = {
                "unique": sorted(set(values)),
                "first_12": values[:12],
                "by_k_mod_3": {
                    str(residue): sorted({values[k] for k in range(32)
                                          if k % 3 == residue})
                    for residue in range(3)
                },
            }

    candidates = []
    total = 0
    for a in (1, 2):
        for b in range(3):
            for c in range(1, 32, 2):
                for d in range(32):
                    total += 1
                    metric = candidate_metrics(a, b, c, d, table)
                    if metric is not None:
                        candidates.append(metric)
    assert total == 3072
    assert len(candidates) == 1088

    hypotheses = {}
    for name, parameters in {
        "k3_plus_k32_mod3": (1, 1, 1, 0),
        "k3_minus_k32_mod3": (1, 2, 1, 0),
    }.items():
        candidate = candidate_metrics(*parameters, table)
        assert candidate is not None
        hypotheses[name] = candidate

    topology_preserving = [candidate for candidate in candidates
                           if candidate["DFT3_cross_k_debt"] == 0
                           and candidate["NTT32_cross_row_edges"] == 0
                           and candidate["NTT32_nonradix2_edges"] == 0]
    best_ratio = sorted(candidates, key=lambda candidate: (
        candidate["ratio_complexity_sum"],
        candidate["DFT3_cross_k_debt"],
        candidate["NTT32_cross_row_edges"],
        candidate["NTT32_nonradix2_edges"],
    ))[:16]

    summary = {
        "multiplicatively_separable": sum(
            candidate["multiplicatively_separable"] for candidate in candidates),
        "DFT3_absorbable": sum(
            candidate["DFT3_shift_or_column_permutation_absorbable"]
            for candidate in candidates),
        "improves_any_vector_to_single_constant": sum(
            candidate["full_YMM_single_constant_vectors"] > 0
            for candidate in candidates),
        "improves_any_vector_to_two_constants": sum(
            candidate["full_YMM_at_most_two_constant_vectors"] > 0
            for candidate in candidates),
        "topology_preserving_candidates": len(topology_preserving),
        "ratio_complexity_histogram": dict(sorted(Counter(
            candidate["ratio_complexity_sum"] for candidate in candidates
        ).items())),
    }
    assert summary["multiplicatively_separable"] == 0
    assert summary["DFT3_absorbable"] == 0
    assert summary["improves_any_vector_to_single_constant"] == 0
    assert summary["improves_any_vector_to_two_constants"] == 0
    assert len(topology_preserving) == 2
    for hypothesis in hypotheses.values():
        assert hypothesis["ratio_cardinality"] == [2, 2, 2, 2]
        assert hypothesis["NTT32_cross_row_edges"] == 240

    result = {
        "experiment": "GT32-CRT-TWIST-COORDINATE-001",
        "status": "structured-positive-no-current-N5-chain-win",
        "current_table": {
            "definition": (
                "T[branch,row,k] = branch_scale^(-(64*row+33*k mod 96))*R"
            ),
            "row_ratios": current_ratios,
            "wide_Montgomery_vector_chains_per_forward": 48,
            "GT_BLEND3_vpblendd_per_forward": 96,
        },
        "search_family": {
            "k3_prime": "a*k3 + b*(k32 mod 3) mod 3",
            "k32_prime": "c*k32 + d*k3 mod 32",
            "a": [1, 2],
            "b": [0, 1, 2],
            "c": "all 16 odd residues modulo 32",
            "d": "0..31",
            "raw_parameter_tuples": total,
            "bijective_coordinate_maps": len(candidates),
            "quotiented_symmetries": [
                "row translation/permutation phase",
                "k32 translation",
                "branch swap",
            ],
        },
        "summary": summary,
        "specific_hypotheses": hypotheses,
        "carry_aware_separation": carry_separation,
        "topology_preserving_candidates": topology_preserving,
        "best_ratio_complexity_candidates": best_ratio,
        "finding": {
            "current_twist_is_structured": True,
            "structure": (
                "three cyclic row-ratio triplets caused by the modulo-96 CRT "
                "representative seam; individual row ratios each use two values"
            ),
            "coordinate_family_makes_twist_separable": False,
            "coordinate_family_makes_twist_DFT3_absorbable": False,
            "coordinate_family_reduces_vector_constant_cardinality": False,
            "plus_minus_shear_moves_coupling_to_NTT32": (
                "both proposed shears retain two-valued ratios and create 240 "
                "cross-row NTT32 edges"
            ),
            "best_ratio_reduction_trade": (
                "ratio complexity 8 -> 6 is possible only with 64 DFT3 "
                "cross-k debt and nontrivial NTT32 geometry debt"
            ),
            "carry_aware_rotation_makes_twist_separable": True,
            "carry_aware_rotation_accelerates_current_N5": False,
        },
        "decision": {
            "assembly_emitted": False,
            "benchmark_run": False,
            "production_changed": False,
            "reason": (
                "the proposed affine shears only relocate coupling into NTT32 "
                "routing.  The exact carry-aware rotation does factor T=A*B, "
                "but A-scaled DFT3 plus either B output scaling or a newly "
                "nonidentity NTT32 S1 costs more chains than the current "
                "64-chain wide-twist-plus-DFT3 region"
            ),
        },
        "reopen_only_if": [
            "a non-affine exact coordinate family yields DFT3-absorbable ratios and executable NTT32 edges",
            "a joint DFT3-plus-NTT32 matrix factorization deletes at least one full Montgomery chain",
            "a wider ISA makes the introduced cross-row topology cheaper than current wide twist",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT.relative_to(gt.ROOT))
    print("decision: carry-aware separation exists, but current N5 gains no chain win")


if __name__ == "__main__":
    main()
