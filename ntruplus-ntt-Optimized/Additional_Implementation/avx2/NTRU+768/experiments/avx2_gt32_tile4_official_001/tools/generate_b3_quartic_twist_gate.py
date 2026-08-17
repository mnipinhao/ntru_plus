#!/usr/bin/env python3
"""Algebra gate for twisting every quartic leaf to y^4 - 1.

For q=3457, x is a fourth power in F_q iff x^((q-1)/gcd(4,q-1))=1.
The production lambda table is stored in Montgomery form, so this gate first
returns every entry to the ordinary field domain before applying the test.
"""

from __future__ import annotations

import json

import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_b3_quartic_twist_gate.json"


def centered(value: int) -> int:
    return gt.centered(value % gt.Q)


def fourth_root(value: int) -> int | None:
    # This exhaustive lookup is tiny (3457 elements) and also serves as an
    # independent constructive check of the subgroup criterion.
    target = value % gt.Q
    for candidate in range(gt.Q):
        if pow(candidate, 4, gt.Q) == target:
            return candidate
    return None


def main() -> None:
    inverse_r = pow(gt.R, -1, gt.Q)
    exponent = (gt.Q - 1) // 4
    records = []
    for branch in range(2):
        for k3 in range(3):
            for q_index in range(32):
                lambda_mont = gt.lambda_montgomery(k3, q_index, branch)
                value = lambda_mont % gt.Q * inverse_r % gt.Q
                criterion = pow(value, exponent, gt.Q)
                root = fourth_root(value)
                records.append({
                    "branch": branch,
                    "k3": k3,
                    "Q": q_index,
                    "lambda_montgomery": lambda_mont,
                    "lambda_ordinary": centered(value),
                    "fourth_power_criterion": centered(criterion),
                    "fourth_root": None if root is None else centered(root),
                    "twist_to_y4_minus_1_possible": root is not None,
                })

    eligible = [record for record in records
                if record["twist_to_y4_minus_1_possible"]]
    assert len(records) == 192
    assert not eligible
    assert {record["fourth_power_criterion"] for record in records} == {-1}

    # All entries have the same quotient-group character.  Ratios to one
    # reference lambda are therefore fourth powers, allowing normalization to
    # y^4-rho for a common rho, but not to y^4-1.
    reference = records[0]["lambda_ordinary"] % gt.Q
    ratio_records = []
    for record in records:
        value = record["lambda_ordinary"] % gt.Q
        ratio = value * pow(reference, -1, gt.Q) % gt.Q
        root = fourth_root(ratio)
        if root is None:
            raise AssertionError((record, ratio))
        ratio_records.append({
            "branch": record["branch"],
            "k3": record["k3"],
            "Q": record["Q"],
            "lambda_over_rho": centered(ratio),
            "tau": centered(root),
        })

    # Find a small signed representative of the same non-fourth-power coset.
    coset = [value for value in range(1, gt.Q)
             if pow(value, exponent, gt.Q) == gt.Q - 1]
    rho = min(coset, key=lambda value: abs(centered(value)))
    assert pow(rho, exponent, gt.Q) == gt.Q - 1
    assert centered(rho) == 2

    # If the common representative is rho=2, B3 can double each wrapped
    # accumulator with vpaddw instead of a four-instruction Montgomery chain.
    # Audit the frozen 10788 input envelope before the existing final center.
    forward_bound = 10788
    variable_product_bound = (
        (forward_bound * forward_bound + 65535) // 65536 + 1729
    )
    rho2_output_bounds = [
        2 * wrapped * variable_product_bound + direct * variable_product_bound
        for wrapped, direct in ((3, 1), (2, 2), (1, 3), (0, 4))
    ]
    assert max(rho2_output_bounds) < 32768

    # Merely replacing the existing CT constants cannot deliver the required
    # output-side diagonal.  One CT butterfly computes L +/- f*H, so its two
    # outputs inherit one common low-arm scale.  For degrees 1..3 the desired
    # tau_Q^c scales of any two distinct leaves cannot be equal (equality
    # would imply equal lambda_Q); all 192 production lambdas are distinct.
    current_ct_absorption = {
        "possible_by_constant_table_replacement_only": False,
        "reason": (
            "the desired tau_Q^c is a leaf-dependent output diagonal, while "
            "each current CT butterfly emits both outputs with one common "
            "low-arm scale"
        ),
        "production_lambda_entries_distinct": len({
            record["lambda_ordinary"] for record in records}) == len(records),
        "affected_degrees": [1, 2, 3],
        "consequence": (
            "extra output scaling chains or a different GS/DIF/conjugated "
            "Forward topology are required"
        ),
    }

    result = {
        "schema": "ntruplus768-gt32-b3-quartic-twist-gate-v1",
        "experiment": "GT32-B3-QUARTIC-TWIST-001",
        "field": {
            "q": gt.Q,
            "q_minus_1": gt.Q - 1,
            "gcd_4_q_minus_1": 4,
            "fourth_power_test_exponent": exponent,
            "criterion": "x is a fourth power iff x^864 == 1",
        },
        "production_lambda_audit": {
            "entries": len(records),
            "distinct_entries": len({record["lambda_ordinary"]
                                      for record in records}),
            "eligible_fourth_powers": len(eligible),
            "criterion_histogram": {"-1": len(records)},
            "all_are_non_fourth_powers": True,
            "records": records,
        },
        "requested_y4_minus_1_twist": {
            "required": "tau_Q^4=lambda_Q in F_q",
            "possible": False,
            "reason": (
                "all 192 production lambda_Q lie in the non-fourth-power "
                "coset: lambda_Q^864=-1"
            ),
            "forward_constant_absorption_reached": False,
            "inverse_constant_absorption_reached": False,
            "cyclic_B3_without_lambda_reached": False,
            "assembly_emitted": False,
        },
        "same_coset_relaxation": {
            "all_lambda_ratios_are_fourth_powers": True,
            "reference_rho": centered(reference),
            "smallest_signed_coset_representative": centered(rho),
            "ratio_root_records": ratio_records,
            "achievable_ring": "F_q[y]/(y^4-rho), with one common rho",
            "B3_rho2_DAG": {
                "current_lambda_chains_per_block": 3,
                "current_lambda_instructions_per_block": 12,
                "rho2_doublings_per_block": 3,
                "rho2_instructions_per_block": 3,
                "blocks": 12,
                "static_instruction_saving": 108,
                "variable_product_abs_bound": variable_product_bound,
                "precenter_coefficient_abs_bounds": rho2_output_bounds,
                "all_precenter_nodes_signed_i16_safe": True,
            },
            "current_Forward_CT_absorption": current_ct_absorption,
            "B3_effect": (
                "rho=2 makes the B3 wrapped-term operation cheap, but the "
                "required leaf-dependent producer twist is not obtainable by "
                "replacing constants in the current CT topology"
            ),
            "continuation": (
                "separate generator-only GS/DIF producer-topology gate; no "
                "assembly from the current-constants hypothesis"
            ),
        },
        "decision": "algebraic-hard-stop-before-assembly",
        "reopen_only_if": [
            "use an extension field containing fourth roots of lambda_Q",
            "change the transform decomposition so leaf lambda_Q are fourth powers",
            "prove a common-rho quartic multiply deletes a complete reduction chain",
            "generate a same-chain GS/DIF Forward and inverse that natively deliver rho=2 twist",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(result["decision"])


if __name__ == "__main__":
    main()
