#!/usr/bin/env python3
"""Exact M5U-B absorption, range, and optimistic instruction-cost gate."""

from __future__ import annotations

import json

Q = 3457
THETA = 9
ETA = pow(THETA, 96, Q)       # order 9
GAMMA = pow(THETA, 32, Q)     # order 27, GAMMA^3=ETA
INV9 = pow(9, -1, Q)
ROWS = 9
COLUMNS = 16
TILES = 36
SCALED_BANKS = 4              # two tops times components 1 and 2
BLOCKS_PER_BANK = 2
SCALED_BLOCKS = SCALED_BANKS * BLOCKS_PER_BANK
B0 = 26306
B12 = 5185
RSQ = 867
R = -147
NEG_QINV = -12929


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) % Q
             for j in range(len(b[0]))] for i in range(len(a))]


def diagonal(values: list[int]) -> list[list[int]]:
    return [[values[i] if i == j else 0 for j in range(len(values))]
            for i in range(len(values))]


def nonzeros(matrix: list[list[int]]) -> int:
    return sum(value % Q != 0 for row in matrix for value in row)


def is_monomial(matrix: list[list[int]]) -> bool:
    row_counts = [sum(value % Q != 0 for value in row) for row in matrix]
    col_counts = [sum(matrix[i][j] % Q != 0 for i in range(len(matrix)))
                  for j in range(len(matrix[0]))]
    return row_counts == [1] * len(matrix) and col_counts == [1] * len(matrix)


def montgomery_bound(bound: int) -> int:
    # Exact safe envelope for the signed -qinv/add reduction used by M5C.
    numerator = bound + 32768 * Q
    return (numerator + 65535) // 65536


def prove_family(top: str, residue: int, row: int, column: int) -> None:
    z = pow(THETA, residue + 6 * column + 96 * row, Q)
    if top == "alpha":
        z0, kappa = 9, 1
    else:
        z0, kappa = 3, 27
    tau = kappa * pow(THETA, 2 * column + 32 * row, Q) % Q
    assert pow(tau, 3, Q) * z0 % Q == z

    # The less aggressive 18-modulus family removes only the column exponent.
    z18 = pow(THETA, residue + 96 * row, Q)
    tau18 = pow(THETA, 2 * column, Q)
    assert pow(tau18, 3, Q) * z18 % Q == z

    # The complementary 32-modulus family removes only the row exponent.
    z32 = pow(THETA, residue + 6 * column, Q)
    tau32 = pow(THETA, 32 * row, Q)
    assert pow(tau32, 3, Q) * z32 % Q == z


def main() -> None:
    assert pow(ETA, 9, Q) == 1 and pow(ETA, 3, Q) != 1
    assert pow(GAMMA, 27, Q) == 1 and pow(GAMMA, 9, Q) != 1
    assert pow(GAMMA, 3, Q) == ETA

    # Orientation/permutation changes conjugate these matrices by monomial
    # matrices, which cannot change dense-vs-monomial classification.
    forward = [[pow(ETA, row * sample, Q) for sample in range(ROWS)]
               for row in range(ROWS)]
    inverse = [[INV9 * pow(ETA, -row * sample, Q) % Q
                for row in range(ROWS)] for sample in range(ROWS)]
    assert matmul(inverse, forward) == diagonal([1] * ROWS)

    conjugation = {}
    for component in (1, 2):
        row_scale = [pow(GAMMA, component * row, Q)
                     for row in range(ROWS)]
        pushed_to_input = matmul(matmul(inverse, diagonal(row_scale)), forward)
        assert nonzeros(pushed_to_input) == 81
        assert not is_monomial(pushed_to_input)
        conjugation[str(component)] = {
            "row_scale": [centered(x) for x in row_scale],
            "F9_inverse_D_F9_nonzeros": nonzeros(pushed_to_input),
            "monomial": False,
        }

    leaf_checks = 0
    z18_values = set()
    z32_values = set()
    for top, residue in (("alpha", 1), ("beta", 5)):
        for row in range(ROWS):
            for column in range(COLUMNS):
                prove_family(top, residue, row, column)
                z18_values.add(pow(THETA, residue + 96 * row, Q))
                z32_values.add(pow(THETA, residue + 6 * column, Q))
                leaf_checks += 1
    assert leaf_checks == 288
    assert len(z18_values) == 18 and len(z32_values) == 32

    # Direct two-constant schoolbook DAG.  All three wide expressions are R0;
    # one reduction makes R^-1, then RSQ plus one reduction returns R0.
    ranges = {}
    maximum = 0
    maximum_reduced = 0
    maximum_finished_accumulator = 0
    for top, z0 in (("alpha", 9), ("beta", 3)):
        accumulators = {
            "c0": B0 * B0 + 2 * z0 * B12 * B12,
            "c1": 2 * B0 * B12 + z0 * B12 * B12,
            "c2": 2 * B0 * B12 + B12 * B12,
        }
        assert max(accumulators.values()) < 2**31
        reduced = {name: montgomery_bound(value)
                   for name, value in accumulators.items()}
        assert max(reduced.values()) < 32768
        finished = {name: montgomery_bound(value * abs(RSQ))
                    for name, value in reduced.items()}
        add_finished = {
            name: montgomery_bound(value * abs(RSQ) + B0 * abs(R))
            for name, value in reduced.items()
        }
        maximum = max(maximum, *accumulators.values())
        maximum_reduced = max(maximum_reduced, *reduced.values())
        maximum_finished_accumulator = max(
            maximum_finished_accumulator,
            *(value * abs(RSQ) for value in reduced.values()),
            *(value * abs(RSQ) + B0 * abs(R) for value in reduced.values()))
        ranges[top] = {
            "z0": z0,
            "wide_R0_accumulator_abs_bounds": accumulators,
            "R_minus_1_abs_bounds": reduced,
            "BaseMul_R0_abs_bounds": finished,
            "BaseMulAdd_R0_abs_bounds": add_finished,
        }

    # Exact abstract Neon arithmetic ledger for the written schoolbook DAG.
    # One wide Montgomery reduction is uzp1,mul,smlal,smlal2,uzp2 = 5.
    baseline_cubic = 47
    finish_three = 21
    iso2_cubic = 37
    assert baseline_cubic + finish_three == 68
    assert iso2_cubic + finish_three == 58
    basemul_arithmetic_saved = TILES * (68 - 58)
    basemul_zeta_loads_removed = TILES
    iso2_constant_materializations = 2  # movi 9, then movi 3 by public branch
    optimistic_basemul_saved = (basemul_arithmetic_saved
                                + basemul_zeta_loads_removed
                                - iso2_constant_materializations)

    # Exact no-boundary fallback absorption: for each component-1/2 block,
    # merge the column-common delta into the eight existing s=1..8 twists,
    # add one s=0 mulmod, then apply eight nontrivial row factors: nine per
    # Forward block.  At the inverse boundary only the eight row factors are
    # new; the column-common factor commutes through inverse NTT9 and merges
    # into its existing final constants.
    forward_mulmods_per_scaled_block = 9
    inverse_mulmods_per_scaled_block = 8
    mulmods_per_forward = SCALED_BLOCKS * forward_mulmods_per_scaled_block
    mulmods_per_inverse = SCALED_BLOCKS * inverse_mulmods_per_scaled_block
    full_product_absorption_mulmods = 2 * mulmods_per_forward + mulmods_per_inverse
    full_product_absorption_arithmetic = 3 * full_product_absorption_mulmods
    iso2_net = full_product_absorption_arithmetic - optimistic_basemul_saved
    assert mulmods_per_forward == 72
    assert mulmods_per_inverse == 64
    assert full_product_absorption_mulmods == 208
    assert optimistic_basemul_saved == 394
    assert iso2_net == 230

    # Compare the four separable exponent-placement families.  These are
    # optimistic arithmetic/load deltas; omitted table loads only hurt them.
    family_ledger = {
        "FR0_288_moduli": {
            "tau": "1", "modulus_count": 288,
            "full_product_delta_instructions": 0,
        },
        "FRISO18_column_only": {
            "tau": "theta^(2*column)", "modulus_count": 18,
            "forward_extra_mulmods_each": 8,
            "inverse_extra_mulmods": 0,
            "optimistic_basemul_loads_saved": 18,
            "full_product_delta_instructions": 2 * 8 * 3 - 18,
        },
        "FRISO32_row_only": {
            "tau": "theta^(32*row)", "modulus_count": 32,
            "forward_extra_mulmods_each": 64,
            "inverse_extra_mulmods": 64,
            "optimistic_basemul_loads_saved": 32,
            "full_product_delta_instructions": 3 * 64 * 3 - 32,
        },
        "FRISO2_row_and_column": {
            "tau": "kappa*theta^(2*column+32*row)", "modulus_count": 2,
            "full_product_extra_mulmods": full_product_absorption_mulmods,
            "optimistic_basemul_instructions_saved": optimistic_basemul_saved,
            "full_product_delta_instructions": iso2_net,
        },
    }
    assert family_ledger["FRISO18_column_only"]["full_product_delta_instructions"] == 30
    assert family_ledger["FRISO32_row_only"]["full_product_delta_instructions"] == 544

    print(json.dumps({
        "gate": "gt864_friso2_absorption_cost",
        "status": "reject",
        "reason": "exact_zero_boundary_DAG_is_optimistically_230_instructions_worse",
        "field": {"q": Q, "theta": THETA, "eta": ETA, "gamma": GAMMA},
        "leaf_factorization_checks": leaf_checks,
        "row_factor_conjugation": conjugation,
        "two_constant_basemul": {
            "input_bounds": {"component0": B0, "component12": B12},
            "ranges": ranges,
            "maximum_wide_abs": maximum,
            "maximum_R_minus_1_abs": maximum_reduced,
            "maximum_finish_accumulator_abs": maximum_finished_accumulator,
            "baseline_arithmetic_per_tile": 68,
            "candidate_arithmetic_per_tile": 58,
            "arithmetic_saved_36_tiles": basemul_arithmetic_saved,
            "optimistic_total_saved_including_constants": optimistic_basemul_saved,
        },
        "absorption_DAG": {
            "scaled_blocks_per_transform": SCALED_BLOCKS,
            "forward_mulmods_per_scaled_block": forward_mulmods_per_scaled_block,
            "inverse_mulmods_per_scaled_block": inverse_mulmods_per_scaled_block,
            "mulmods_per_forward": mulmods_per_forward,
            "mulmods_per_inverse": mulmods_per_inverse,
            "two_forward_plus_inverse_mulmods": full_product_absorption_mulmods,
            "Algorithm10_instructions": full_product_absorption_arithmetic,
            "constant_loads_optimistically_omitted": True,
        },
        "family_ledger": family_ledger,
        "optimistic_full_product_net_regression_instructions": iso2_net,
        "new_coefficient_memory_boundaries": 0,
        "assembly_started": False,
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
