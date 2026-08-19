#!/usr/bin/env python3
"""Generator-only gate for BaseMul-selected quartic degree bases.

The selected GT32 transform is a length-32 transform applied independently to
each of the four quartic degrees.  This gate proves that a degree basis change
commutes with both the exact selected Forward matrix and its inverse, audits
the selected Clean boundaries, and accounts for the explicit T/T^-1 work that
commutation can move but cannot delete.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
ROOT = EXPERIMENTS.parent
REPO = ROOT.parents[3]
CLEAN = REPO.parent / "ntru_plus" / "ntruplus-ntt-Optimized" / \
    "Additional_Implementation" / "avx2" / "NTRU+768" / "clean" / \
    "avx2-gt32-clean"
TOOLS = EXPERIMENTS / "avx2_gt32_tile4_official_001" / "tools"
PRIOR009 = EXPERIMENTS / "gt32_joint_transform_basis_009"
PRIOR010 = EXPERIMENTS / "gt32_joint_transform_superspace_010"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GT = load_module("tile4_for_degree_basis_017", TOOLS / "generate_tile4.py")
Q = GT.Q


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256(path)}


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) % Q
             for j in range(len(b[0]))] for i in range(len(a))]


def matvec(a: list[list[int]], x: list[int]) -> list[int]:
    return [sum(row[j] * x[j] for j in range(len(x))) % Q for row in a]


def inverse(a: list[list[int]]) -> list[list[int]]:
    n = len(a)
    work = [[a[i][j] % Q for j in range(n)] +
            [1 if i == j else 0 for j in range(n)] for i in range(n)]
    for col in range(n):
        pivot = next(row for row in range(col, n) if work[row][col])
        work[col], work[pivot] = work[pivot], work[col]
        scale = pow(work[col][col], -1, Q)
        work[col] = [(v * scale) % Q for v in work[col]]
        for row in range(n):
            if row == col:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [(work[row][j] - factor * work[col][j]) % Q
                             for j in range(2 * n)]
    return [row[n:] for row in work]


def butterfly_pairs(stage: int) -> list[tuple[int, int]]:
    distance = 32 >> stage
    return [(group + lane, group + lane + distance)
            for group in range(0, 32, 2 * distance)
            for lane in range(distance)]


def forward_matrix() -> list[list[int]]:
    columns: list[list[int]] = []
    for source in range(32):
        state = [1 if i == source else 0 for i in range(32)]
        for stage in range(1, 6):
            distance = 32 >> stage
            for low, high in butterfly_pairs(stage):
                if stage == 1:
                    factor = 1
                else:
                    group = (low // (2 * distance)) * (2 * distance)
                    factor = pow(GT.OMEGA32, GT.forward_power(stage, group), Q)
                product = state[high] * factor % Q
                state[low], state[high] = ((state[low] + product) % Q,
                                           (state[low] - product) % Q)
        columns.append(state)
    matrix = [[columns[j][i] for j in range(32)] for i in range(32)]
    inverse(matrix)  # Exact nonsingularity check.
    return matrix


def apply_leaf(matrix: list[list[int]], state: list[list[int]]) -> list[list[int]]:
    return [matvec(matrix, plane) for plane in state]


def apply_degree(matrix: list[list[int]], state: list[list[int]]) -> list[list[int]]:
    return [[sum(matrix[out][degree] * state[degree][leaf]
                 for degree in range(4)) % Q
             for leaf in range(32)] for out in range(4)]


def determinant_nonzero(matrix: list[list[int]]) -> bool:
    inverse(matrix)
    return True


BASES = {
    "identity": [[1, 0, 0, 0], [0, 1, 0, 0],
                 [0, 0, 1, 0], [0, 0, 0, 1]],
    "H02_13": [[1, 0, 1, 0], [1, 0, -1, 0],
               [0, 1, 0, 1], [0, 1, 0, -1]],
    "H01_23": [[1, 1, 0, 0], [1, -1, 0, 0],
               [0, 0, 1, 1], [0, 0, 1, -1]],
    "H03_12": [[1, 0, 0, 1], [1, 0, 0, -1],
               [0, 1, 1, 0], [0, 1, -1, 0]],
}


def normalized(matrix: list[list[int]]) -> list[list[int]]:
    return [[value % Q for value in row] for row in matrix]


def operation_floor(matrix: list[list[int]]) -> dict:
    supports = [sum(value % Q != 0 for value in row) for row in matrix]
    nonunit_rows = sum(support != 1 for support in supports)
    # Each two-term row needs at least one vector add/sub.  This is exact for
    # the pair-Hadamard families and deliberately ignores coefficient scaling.
    assert all(support in (1, 2) for support in supports)
    return {
        "row_supports": supports,
        "vector_add_sub_lower_bound_per_16_leaf_block": nonunit_rows,
        "coefficient_scale_operations_ignored": True,
    }


def commutation_proof(leaf_matrix: list[list[int]], leaf_inverse: list[list[int]],
                      basis: list[list[int]]) -> dict:
    basis = normalized(basis)
    forward_checks = 0
    inverse_checks = 0
    for degree in range(4):
        for leaf in range(32):
            state = [[0] * 32 for _ in range(4)]
            state[degree][leaf] = 1
            assert apply_degree(basis, apply_leaf(leaf_matrix, state)) == \
                apply_leaf(leaf_matrix, apply_degree(basis, state))
            forward_checks += 1
            assert apply_degree(basis, apply_leaf(leaf_inverse, state)) == \
                apply_leaf(leaf_inverse, apply_degree(basis, state))
            inverse_checks += 1
    return {
        "forward_basis_vectors": forward_checks,
        "inverse_basis_vectors": inverse_checks,
        "exact_mod_q": True,
        "interpretation": "T commutes with leaf NTT and inverse; it is movable, not free",
    }


def family() -> list[list[list[int]]]:
    seen: set[tuple[tuple[int, ...], ...]] = set()
    result = []
    for name in ("H02_13", "H01_23", "H03_12"):
        base = BASES[name]
        for order in itertools.permutations(range(4)):
            for signs in itertools.product((1, -1), repeat=4):
                matrix = [[signs[row] * base[order[row]][col] for col in range(4)]
                          for row in range(4)]
                key = tuple(tuple(value % Q for value in row) for row in matrix)
                if key not in seen:
                    seen.add(key)
                    result.append(matrix)
    return result


def macro_body(text: str, name: str) -> list[str]:
    match = re.search(rf"^\s*\.macro\s+{name}[^\n]*\n(.*?)^\s*\.endm\s*$",
                      text, re.MULTILINE | re.DOTALL)
    assert match, name
    return [line.strip() for line in match.group(1).splitlines()
            if line.strip() and not line.lstrip().startswith("/*")]


def source_audit() -> dict:
    ntt = CLEAN / "ntt_m.s"
    bm = CLEAN / "basemul.s"
    inv = CLEAN / "invntt.s"
    lines = macro_body(ntt.read_text(), "FR_PACKED_TO_BM_REGS")
    mnemonics = [line.split()[0] for line in lines]
    assert len(lines) == 12
    assert not ({"vpaddw", "vpsubw"} & set(mnemonics))
    assert "ntruplus768_basemul_scale_m_avx2" in bm.read_text()
    assert "ntruplus768_invntt_m_avx2" in inv.read_text()
    return {
        "sources": [artifact(ntt), artifact(bm), artifact(inv)],
        "forward_terminal_macro": "FR_PACKED_TO_BM_REGS",
        "terminal_instruction_count": len(lines),
        "terminal_mnemonics": mnemonics,
        "terminal_degree_add_sub": 0,
        "selected_BM": "ntruplus768_basemul_scale_m_avx2",
        "selected_inverse": "ntruplus768_invntt_m_avx2",
        "axis_finding": (
            "NTT32 and inverse butterflies mix the 32-leaf axis independently "
            "for each quartic degree; terminal degree handling is routing-only"
        ),
    }


def prior_accounting() -> dict:
    status = (PRIOR009 / "STATUS.yml").read_text()
    required = [
        "complete_loop_instructions_per_16_quartics: 114",
        "vector_multiply_uops_per_16_quartics: 63",
        "Hybrid_compute_only_floor_per_block: 105",
        "maximum_BM_credit_across_12_blocks: 108",
        "two_Forward_plus_inverse_transform_debt: 144",
        "Hybrid_vector_multiply_uops_per_block: 61",
    ]
    assert all(item in status for item in required)
    return {
        "sources": [
            artifact(PRIOR009 / "STATUS.yml"),
            artifact(PRIOR009 / "generated/joint_transform_basis_gate.json"),
            artifact(PRIOR010 / "STATUS.yml"),
            artifact(PRIOR010 / "generated/joint_transform_superspace_gate.json"),
        ],
        "current_B3_instructions_per_block": 114,
        "current_B3_vector_multiply_uops_per_block": 63,
        "known_Hybrid_compute_floor_per_block": 105,
        "known_Hybrid_vector_multiply_uops_per_block": 61,
        "maximum_known_BM_credit_whole_polynomial": 108,
    }


def build() -> dict:
    leaf = forward_matrix()
    leaf_inv = inverse(leaf)
    assert matmul(leaf, leaf_inv) == [[1 if i == j else 0 for j in range(32)]
                                         for i in range(32)]
    candidates = []
    for name, matrix in BASES.items():
        normalized_matrix = normalized(matrix)
        inv = inverse(normalized_matrix)
        candidates.append({
            "name": name,
            "matrix": normalized_matrix,
            "inverse": inv,
            "invertible": determinant_nonzero(normalized_matrix),
            "forward_and_inverse_commutation": commutation_proof(leaf, leaf_inv, matrix),
            "input_formation": operation_floor(normalized_matrix),
            "output_undo": operation_floor(inv),
            "inverse_contains_inv2": any(pow(2, -1, Q) in row for row in inv),
        })

    signed_family = family()
    # Row permutations/signs preserve the tensor-axis proof and pair-support
    # floor.  Check every member is invertible and has the same executable
    # support; the representative matrices above carry the 128-vector exact
    # Forward/inverse checks.
    for matrix in signed_family:
        inverse(normalized(matrix))
        assert operation_floor(normalized(matrix))[
            "vector_add_sub_lower_bound_per_16_leaf_block"] == 4

    blocks = 12
    per_operand = 4
    input_two_operands = 2 * per_operand * blocks
    output_undo = 4 * blocks
    boundary_floor = input_two_operands + output_undo
    known_credit = 108
    assert boundary_floor == 144 and boundary_floor > known_credit
    return {
        "schema": "ntruplus768-gt32-degree-basis-commutation-017-v1",
        "experiment": "GT32-DEGREE-BASIS-COMMUTATION-017",
        "production_modified": False,
        "assembly_emitted": False,
        "question": (
            "can BaseMul-selected quartic linear forms be retained across "
            "Forward/BM/inverse so their formation and repair disappear?"
        ),
        "source_audit": source_audit(),
        "exact_selected_leaf_transform": {
            "dimension": 32,
            "forward_inverse_identity": True,
            "acts_independently_on_quartic_degrees": True,
        },
        "candidate_bases": candidates,
        "signed_row_permutation_pair_hadamard_family": {
            "unique_matrices": len(signed_family),
            "representative_exact_forward_basis_checks": 3 * 128,
            "representative_exact_inverse_basis_checks": 3 * 128,
            "family_invertibility_and_support_checks": len(signed_family),
            "commutation_inherited_by_signed_row_permutation": True,
            "all_pass": True,
        },
        "prior_009_010": prior_accounting(),
        "optimistic_cost_floor": {
            "blocks_of_16_leaves": blocks,
            "two_input_basis_formations": input_two_operands,
            "output_inverse_basis_undo": output_undo,
            "total_vector_add_sub_floor": boundary_floor,
            "inverse_inv2_scaling_cost_charged": 0,
            "routing_load_store_loop_cost_charged": 0,
            "maximum_known_BM_credit": known_credit,
            "minimum_whole_island_delta": boundary_floor - known_credit,
            "known_multiply_uop_delta_per_block": -2,
            "interpretation": (
                "even the optimistic pair-Hadamard boundary floor loses by 36 "
                "instructions before inverse-2 scaling or delivery costs"
            ),
        },
        "decision": {
            "status": "static_hard_stop_current_degree_basis_absorption",
            "emit_ASM": False,
            "closed_scope": [
                "pair-Hadamard H01|23, H02|13 and H03|12 degree bases",
                "all signed output-row permutations of those bases",
                "claim that current Forward final butterflies provide degree forms for free",
                "claim that current inverse first butterflies consume degree forms for free",
            ],
            "not_closed": [
                "arbitrary dense or non-pair bilinear bases",
                "a producer that natively emits the selected degree forms",
                "a downstream consumer that natively accepts transformed coefficients",
                "a changed leaf decomposition that mixes the quartic-degree axis",
            ],
            "reason": [
                "the current transform and degree basis operate on orthogonal tensor axes",
                "commutation moves T and T^-1 but does not delete either",
                "the selected terminal is routing-only and exposes no reusable degree add/sub",
                "the optimistic 144-instruction boundary floor exceeds the known 108-instruction BM credit",
                "the known arithmetic changes only 63 to 61 vector multiply uops per block",
            ],
            "reopen_only_if": [
                "explicit T plus T^-1 cost is removed by producer/consumer native semantics",
                "a new basis deletes more multiply/reduction uops than its executable formation floor",
                "no Montgomery chain or range checkpoint is added",
                "the transform decomposition changes so an existing butterfly mixes quartic degrees",
            ],
        },
    }


def main() -> None:
    output = EXPERIMENT / "generated" / "degree_basis_commutation_gate.json"
    output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
