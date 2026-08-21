#!/usr/bin/env python3
"""Audit the Official BMScale/BaseInv inverse sink before G1C assembly work."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = 3457
R = (1 << 16) % Q
INV288 = pow(288, -1, Q)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(text: str, fragment: str, source: Path) -> None:
    if fragment not in text:
        raise SystemExit(f"required Official contract disappeared from {source}: {fragment!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--basemul", type=Path, required=True)
    parser.add_argument("--invntt", type=Path, required=True)
    parser.add_argument("--baseinv", type=Path, required=True)
    parser.add_argument("--poly", type=Path, required=True)
    parser.add_argument("--edge-oracle", type=Path, required=True)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    basemul = args.basemul.read_text()
    invntt = args.invntt.read_text()
    baseinv = args.baseinv.read_text()
    poly = args.poly.read_text()
    edge_oracle = json.loads(args.edge_oracle.read_text())
    scaled = json.loads(args.scaled_oracle.read_text())

    for fragment in (".global poly_basemul_scale", "vmovdqa %ymm2,   (%rdi)",
                     "vmovdqa %ymm3, 32(%rdi)", "vmovdqa %ymm4, 64(%rdi)",
                     "vmovdqa %ymm5, 96(%rdi)", "add $128, %rdi"):
        require(basemul, fragment, args.basemul)
    for fragment in ("_looptop_start_6543:", "#level6", "#level5",
                     "vmovdqa 224(%rdi), %ymm10", "vpblendw $0xAA",
                     "vpmulhrsw %ymm1, %ymm11, %ymm3"):
        require(invntt, fragment, args.invntt)
    level6 = invntt.split("#level6", 1)[1].split("#level5", 1)[0]
    if "#store" in level6 or "%ymm3,     (%rdi)" in level6:
        raise SystemExit("Official inverse unexpectedly materializes the level6/level5 seam")
    for fragment in (".global poly_baseinv_1", "vmovdqu %ymm8, (%rsi)",
                     "vmovdqa %ymm2,   (%rdi)", "vmovdqa %ymm5, 96(%rdi)"):
        require(baseinv, fragment, args.baseinv)
    for fragment in ("__m256i den[18];", "poly_baseinv_1(r, den, a);",
                     "if(fqinv_batch(den))", "poly_baseinv_2(r, den);",
                     "fqmul_neg(r1", "fqmul_neg(r3", "secure_clear(den, sizeof den)"):
        require(poly, fragment, args.poly)

    edges = {edge["id"]: edge for edge in edge_oracle["edges"]}
    bm_edge = edges["F5.bmscale-store-to-inverse-head"]
    bi_edge = edges["F5.baseinv-store-to-inverse-head"]
    if bm_edge["scale_relation"]["montgomery_r_exponent"] != -1:
        raise SystemExit("G1 BMScale R exponent changed")
    if bi_edge["scale_relation"]["BaseInv_output_transform_scale"] != "1/4":
        raise SystemExit("G1 BaseInv scale changed")
    if scaled["scale_ledger"]["decapsulation_inverse_path"]["standalone_scale_pass"] is not False:
        raise SystemExit("scaled inverse ledger changed")

    official_norm = INV288 * R * R % Q
    resident_r0_norm = INV288 * R % Q
    baseinv_quarter_norm = 4 * resident_r0_norm % Q
    if (official_norm, resident_r0_norm, baseinv_quarter_norm) != (3424, 1764, 142):
        raise SystemExit("normalization arithmetic changed")

    document = {
        "schema": "gt-g1c-inverse-sink-audit/v1",
        "checkpoint": "G1C0-official-sink-and-baseinv-algebraic-closure",
        "parameter": 1152,
        "official_bmscale_to_inverse": {
            "layout": "terminal-major four degree-4 coefficient vectors per block",
            "store_offsets_bytes": [0, 32, 64, 96],
            "block_stride_bytes": 128,
            "blocks": 18,
            "output_montgomery_r_exponent": -1,
            "standalone_converter_count": 0,
            "C1_store_only_credit_available_against_official": False,
            "reason": "Official BMScale already stores exactly the layout consumed by its inverse level6 loads",
        },
        "official_inverse_level6_head": {
            "input_offsets_bytes": [0, 32, 64, 96, 128, 160, 192, 224],
            "input_vectors": 8,
            "terminal_blocks_per_iteration": 2,
            "sum_vectors": 4,
            "difference_vectors": 4,
            "montgomery_difference_chains": 4,
            "barrett_sum_chains": 4,
            "word_routing_instructions": 16,
            "materialized_store_before_level5": False,
        },
        "baseinv_den18_lifetime": {
            "phase_1": "poly_baseinv_1 emits four adjugate vectors and one denominator vector per block",
            "den_vectors": 18,
            "phase_boundary": "fqinv_batch inverts the complete den[18] array",
            "phase_2": "poly_baseinv_2 applies each inverted denominator to four vectors",
            "phase_2_sign_pattern": [1, -1, 1, -1],
            "lifetime_rule": "preserve all den[18] values and the phase boundary; no per-block early destruction",
            "failure_and_clear": "zero output on inversion failure; clear den[18] on both paths",
        },
        "baseinv_homogeneity": {
            "adjugate_degree": 3,
            "denominator_degree": 4,
            "inverse_denominator_degree": -4,
            "base_inverse_output_degree": -1,
            "relations": ["adj(g*A)=g^3*adj(A)", "den(g*A)=g^4*den(A)",
                          "BaseInv(g*A)=g^-1*BaseInv(A)"],
            "identity_component_gauge": True,
        },
        "inverse_normalization_mod_q": {
            "q": Q,
            "R_mod_q": R,
            "inverse_288_mod_q": INV288,
            "official_Rminus1_input": official_norm,
            "resident_R0_input": resident_r0_norm,
            "BaseInv_quarter_scale_R0_input": baseinv_quarter_norm,
            "scalar_normalization_closed": True,
        },
        "prototype_gate": {
            "G1C_M_C0": "Official zero-conversion control",
            "G1C_M_C1": "not-built: store-order-only has no standalone-converter credit against Official",
            "G1C_M_C2": "pending adjusted inverse level6 component/twiddle/range oracle",
            "G1C_I": "scalar normalization and den[18] lifetime closed; adjusted inverse head remains pending",
            "asm_authorized": False,
            "cycles": None,
            "rule": "do not report G1C credit or add it to G1B debt before a linked tail+head prototype exists",
        },
        "source_sha256": {
            "official_basemul": sha256(args.basemul),
            "official_invntt": sha256(args.invntt),
            "official_baseinv": sha256(args.baseinv),
            "official_poly": sha256(args.poly),
            "g1_edge_oracle": sha256(args.edge_oracle),
            "scaled_r3r3_oracle": sha256(args.scaled_oracle),
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated G1C inverse-sink audit is stale")
        return 0
    args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
