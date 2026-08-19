#!/usr/bin/env python3
"""Exact algebra and first AVX2 gate for stopping GT32 at degree-8 leaves."""

from __future__ import annotations

import hashlib
import importlib.util
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
GT16 = EXPERIMENTS / "avx2_gt16_quadratic_official_001"
WAVES = {
    number: EXPERIMENTS / directory
    for number, directory in {
        11: "gt32_avx2_packing_superspace_011",
        12: "gt32_cross_r3_semantic_packet_012",
        13: "gt32_cross_r3_qword_semantic_packet_013",
        14: "gt32_cross_r3_qword_b3_inverse_range_014",
        15: "gt32_qword_kem_caller_closure_015",
        16: "gt32_qword_forward_asm_016",
        17: "gt32_degree_basis_commutation_017",
    }.items()
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GT = load_module("tile4_for_degree8_018", TOOLS / "generate_tile4.py")
Q, R = GT.Q, GT.R


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256(path)}


def ordinary_lambda(k3: int, q_index: int, branch: int) -> int:
    return GT.lambda_montgomery(k3, q_index, branch) * pow(R, -1, Q) % Q


def square_root(value: int) -> int:
    return next(candidate for candidate in range(Q)
                if candidate * candidate % Q == value % Q)


def poly_mul_mod_x8_mu(a: list[int], b: list[int], mu: int) -> list[int]:
    out = [0] * 8
    for i, av in enumerate(a):
        for j, bv in enumerate(b):
            degree = i + j
            if degree >= 8:
                out[degree - 8] += av * bv * mu
            else:
                out[degree] += av * bv
    return [value % Q for value in out]


def eval_mod_x2_r(poly: list[int], root: int) -> tuple[int, int]:
    even = sum(poly[2 * j] * pow(root, j, Q) for j in range(4)) % Q
    odd = sum(poly[2 * j + 1] * pow(root, j, Q) for j in range(4)) % Q
    return even, odd


def quadratic_mul(a: tuple[int, int], b: tuple[int, int], root: int) -> tuple[int, int]:
    a0, a1 = a
    b0, b1 = b
    # Rank-3 Karatsuba realization.
    p0 = a0 * b0 % Q
    p1 = a1 * b1 % Q
    p2 = (a0 + a1) * (b0 + b1) % Q
    return ((p0 + root * p1) % Q, (p2 - p0 - p1) % Q)


def factor_record(k3: int, branch: int, low_q: int) -> dict:
    high_q = low_q + 1
    lam = ordinary_lambda(k3, low_q, branch)
    neg_lam = ordinary_lambda(k3, high_q, branch)
    assert neg_lam == (-lam) % Q
    mu = lam * lam % Q
    sqrt_lam = square_root(lam)
    sqrt_neg_lam = square_root(neg_lam)
    roots = [sqrt_lam, -sqrt_lam % Q, sqrt_neg_lam, -sqrt_neg_lam % Q]
    assert len(set(roots)) == 4
    assert all(pow(root, (Q - 1) // 2, Q) == Q - 1 for root in roots)

    checks = 0
    for left_degree in range(8):
        for right_degree in range(8):
            a = [1 if i == left_degree else 0 for i in range(8)]
            b = [1 if i == right_degree else 0 for i in range(8)]
            product = poly_mul_mod_x8_mu(a, b, mu)
            for root in roots:
                assert eval_mod_x2_r(product, root) == quadratic_mul(
                    eval_mod_x2_r(a, root), eval_mod_x2_r(b, root), root)
                checks += 1
    return {
        "k3": k3,
        "branch": branch,
        "low_Q": low_q,
        "high_Q": high_q,
        "lambda": lam,
        "negative_lambda": neg_lam,
        "mu": mu,
        "quadratic_roots": roots,
        "all_quadratic_factors_irreducible": True,
        "monomial_product_factor_checks": checks,
    }


def macro_body(text: str, name: str) -> list[str]:
    match = re.search(rf"^\s*\.macro\s+{name}(?:\s[^\n]*)?\n(.*?)^\s*\.endm\s*$",
                      text, re.MULTILINE | re.DOTALL)
    assert match, name
    return [line.strip() for line in match.group(1).splitlines()
            if line.strip() and not line.lstrip().startswith("/*")]


def source_gate() -> dict:
    ntt = CLEAN / "ntt_m.s"
    inv = CLEAN / "invntt.s"
    bm = CLEAN / "basemul.s"
    text = ntt.read_text()
    macro = macro_body(text, "FR_MONT_QWORD_PACKED")
    assert len(macro) == 9
    selected = re.search(
        r"ntruplus768_ntt_m_avx2:(.*?)(?:\.size ntruplus768_ntt_m_avx2)",
        text, re.DOTALL,
    )
    assert selected
    calls_per_tile = selected.group(1).count("FR_MONT_QWORD_PACKED ")
    assert calls_per_tile == 4
    tiles = 6
    return {
        "sources": [artifact(ntt), artifact(inv), artifact(bm),
                    artifact(GT16 / "README.md"), artifact(GT16 / "STATUS.yml")],
        "selected_forward_S5_macro": "FR_MONT_QWORD_PACKED",
        "instructions_per_call": len(macro),
        "calls_per_256_byte_tile": calls_per_tile,
        "tiles_per_Forward": tiles,
        "S5_instructions_per_Forward": len(macro) * calls_per_tile * tiles,
        "S5_Montgomery_chains_per_Forward": calls_per_tile * tiles,
        "two_Forward_S5_instructions": 2 * len(macro) * calls_per_tile * tiles,
        "two_Forward_S5_Montgomery_chains": 2 * calls_per_tile * tiles,
        "terminal_plane_routing_not_included": True,
        "inverse_initial_S5_and_routing_not_credited": True,
    }


def coverage_registry() -> dict:
    evidence = []
    for number, path in WAVES.items():
        status = path / "STATUS.yml"
        readme = path / "README.md"
        assert status.exists() and readme.exists(), (number, path)
        evidence.extend([artifact(status), artifact(readme)])
    return {
        "evidence": evidence,
        "closed_or_narrowed": {
            "persistent_128bit_R3_semantics": "closed-012",
            "fixed_qword_R3_semantics": "exact-and-executable-loss-013-through-016",
            "pair_Hadamard_free_absorption": "closed-017",
            "persistent_expanded_K2": "capacity-stop-011",
        },
        "open": {
            "dynamic_stage_semantic_packet": "high-priority",
            "BaseMul_pair_native_packet_beyond_tested_L01_L02_nodes": "open",
            "streamed_evaluation_representation": "high-priority",
            "LHS_RHS_coupled_stream": "high-priority",
            "degree8_incomplete_NTT": "018-algebra-pass-executable-open",
            "mixed_width_stream": "secondary-open",
            "arbitrary_bilinear_basis": "technical-open-low-priority",
        },
        "census_warning": "011 enumerates representation classes; it is not executable closure of all 96 states",
    }


def build() -> dict:
    records = [factor_record(k3, branch, low_q)
               for k3 in range(3) for branch in range(2)
               for low_q in range(0, 32, 2)]
    assert len(records) == 96
    assert sum(record["monomial_product_factor_checks"] for record in records) == \
        96 * 8 * 8 * 4
    return {
        "schema": "ntruplus768-gt32-degree8-incomplete-ntt-018-v1",
        "experiment": "GT32-DEGREE8-INCOMPLETE-NTT-018",
        "production_modified": False,
        "assembly_emitted": False,
        "hypothesis": (
            "stop NTT32 before S5, retain 96 degree-8 leaves, and replace "
            "S5 + two quartic products + inverse-S5 with a native degree-8 BM"
        ),
        "post_011_coverage_registry": coverage_registry(),
        "coverage_correction": {
            "GT16_does_not_persist_a_degree8_ABI": True,
            "GT16_direction": "192 quartics split into 384 quadratic components",
            "degree8_direction": "192 quartics pair into 96 degree-8 components",
            "relationship": (
                "GT16 is a conjugated complete executable schedule for the same "
                "factor algebra, but not a direct persistent degree8 packet ABI"
            ),
            "remaining_gap": "delete work relative to GT16 split/QBM/merge rather than replay it",
        },
        "exact_algebra": {
            "degree8_leaves": 96,
            "quartic_pair_identity": "(x^4-lambda)(x^4+lambda)=x^8-lambda^2",
            "quadratic_factors_per_degree8_leaf": 4,
            "records": records,
            "total_exact_monomial_factor_checks": 96 * 8 * 8 * 4,
        },
        "bilinear_rank": {
            "dimension": 8,
            "maximal_components": 4,
            "Alder_Strassen_lower_bound_2n_minus_t": 12,
            "constructive_upper_bound": 12,
            "construction": "four irreducible quadratic products times rank 3",
            "exact_rank": 12,
            "arithmetic_acceleration_vs_known_quadratic_factorization": 0,
            "interpretation": (
                "degree-8 is not a lower-rank multiplication; any win must come "
                "from deleting S5/inverse-S5/routing or a better executable packet"
            ),
        },
        "current_boundary_credit": source_gate(),
        "decision": {
            "status": "algebra_pass_executable_packet_open",
            "emit_ASM": False,
            "next_gate": "synthesize one 16-leaf degree8 packet BM plus inverse entry",
            "requirements": [
                "whole 2F+B+I vector multiply uops do not increase",
                "both current Forward S5 layers are removed",
                "inverse S5/entry repair is removed rather than replayed inside BM",
                "peak live YMM <= 15 and no spills",
                "no new full-vector range checkpoint",
                "constructive schedule has at least 20-TSC-equivalent static margin",
            ],
            "stop_if": [
                "rank-12 evaluation/recombination recreates current S5 twice plus inverse S5",
                "degree8 packet needs a persistent representation above 16 YMM",
                "Montgomery/checkpoint work increases after crediting deleted S5 chains",
            ],
            "not_claimed": [
                "degree8 is faster",
                "degree16 is covered",
                "dynamic semantic packets or streamed LHS/RHS coupling are covered",
            ],
        },
    }


def main() -> None:
    output = EXPERIMENT / "generated" / "degree8_incomplete_ntt_gate.json"
    output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
