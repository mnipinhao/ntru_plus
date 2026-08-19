#!/usr/bin/env python3
"""Emit executable-layout and conservative range obligations for experiment 032."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


Q = 3457
SIGNED16_LIMIT = 32768


def label_shorts(source: str, label: str) -> list[int]:
    """Read .short values from one object-local constant section."""
    marker = f"{label}:"
    if marker not in source:
        raise ValueError(f"missing assembly label {label}")
    tail = source.split(marker, 1)[1]
    block_lines: list[str] = []
    for line in tail.splitlines():
        stripped = line.strip()
        if stripped.startswith(".section") or (
                stripped.startswith(".L") and stripped.endswith(":")):
            break
        block_lines.append(line)
    block = "\n".join(block_lines)
    values: list[int] = []
    for line in block.splitlines():
        if ".short" in line:
            values.extend(int(value) for value in
                          re.findall(r"-?\d+", line.split(".short", 1)[1]))
    if not values:
        raise ValueError(f"no .short values at {label}")
    return values


def ceil_div(value: int, divisor: int) -> int:
    return (value + divisor - 1) // divisor


def mont_bound(a_bound: int, factor_bound: int) -> int:
    """Conservative bound for the selected signed 16-bit Montgomery DAG.

    vpmulhw(a,factor) is bounded by ceil(|a*factor|/2^16), while the
    q*low(a*qinv) correction high word is bounded by ceil(q/2).
    """
    return ceil_div(a_bound * factor_bound, 1 << 16) + ceil_div(Q, 2)


def build_result(root: Path) -> tuple[dict[str, object], dict[str, int]]:
    basemul = (root / "basemul.s").read_text()
    ntt = (root / "ntt.s").read_text()
    ntt_m = (root / "ntt_m.s").read_text()

    output_macro = basemul.split(
        " .macro TILE4_OUTPUT_SOA_LATE_RSQ_ADD_M", 1)[1].split(
            " .endm", 1)[0]
    expected_offsets = ["0(%r10)", "32(%r10)", "64(%r10)", "96(%r10)"]

    # Bind the proof to the constants in the currently selected production
    # frontend and progressive-M core, rather than the obsolete 10788 proof.
    top_factor = max(abs(value) for value in label_shorts(
        ntt, ".Ltile4_frontend_zeta_top_raw"))
    twist_factor = max(abs(value) for value in label_shorts(
        ntt, ".Ltile4_frontend_wide_twist_factor"))
    omega_factor = max(abs(value) for value in label_shorts(
        ntt, ".Ltile4_frontend_omega3_factor"))
    stage_factors = [
        max(abs(value) for value in label_shorts(
            ntt_m, ".Ltile4_fwd_s2_factor")),
        max(abs(value) for value in label_shorts(
            ntt_m, ".Ltile4_fwd_s3_factor")),
        max(abs(value) for value in label_shorts(
            ntt_m, ".Ltile4_fwd_s4_pair_factor")),
        max(abs(value) for value in label_shorts(
            ntt_m, ".Ltile4_fwd_s5_pair_factor")),
    ]
    lambda_factor = max(abs(value) for value in label_shorts(
        basemul, ".Ltile4_bm_lambda"))
    rsq_factor = max(abs(value) for value in label_shorts(
        basemul, ".Ltile4_bm_rsq"))

    coefficient_bound = 1
    top_bound = coefficient_bound + top_factor * coefficient_bound
    twist_bound = mont_bound(top_bound, twist_factor)
    omega_bound = mont_bound(2 * twist_bound, omega_factor)
    frontend_bound = max(3 * twist_bound, 2 * twist_bound + omega_bound)
    forward_stages = [frontend_bound, 2 * frontend_bound]  # frontend, raw S1
    for factor in stage_factors:
        previous = forward_stages[-1]
        forward_stages.append(previous + mont_bound(previous, factor))
    forward_bound = forward_stages[-1]

    decoded_h_bound = Q - 1
    product_bound = mont_bound(decoded_h_bound, forward_bound)
    b3_raw_bounds = [
        mont_bound(3 * product_bound, lambda_factor) + product_bound,
        mont_bound(2 * product_bound, lambda_factor) + 2 * product_bound,
        mont_bound(product_bound, lambda_factor) + 3 * product_bound,
        4 * product_bound,
    ]
    b3_final_bounds = [mont_bound(value, rsq_factor)
                       for value in b3_raw_bounds]
    sum_bounds = [value + forward_bound for value in b3_final_bounds]
    maximum = max(sum_bounds)

    contract = {
        "GT32_032_FORWARD_BOUND": forward_bound,
        "GT32_032_SUM_BOUND": maximum,
    }
    proof: dict[str, object] = {
        "schema": "ntruplus768-gt32-encap-b3-addm-032-proof-v2",
        "experiment": "GT32-ENCAP-B3-ADDM-032",
        "baseline": "031 four-polynomial Encap",
        "production_modified": False,
        "layout": {
            "B3_output": "M private SoA, four degree planes per 16-leaf tile",
            "m_input": "same M private SoA produced by the same Forward",
            "degree_plane_offsets": [0, 32, 64, 96],
            "candidate_m_offsets_match": all(
                offset in output_macro for offset in expected_offsets),
            "permutation_repair": 0,
        },
        "scale": {
            "B3_general_output_exponent": 0,
            "m_forward_exponent": 0,
            "sum_exponent": 0,
        },
        "range": {
            "method": "conservative absolute-value propagation over selected assembly DAG",
            "signed_montgomery_bound": "ceil(A*F/65536)+ceil(3457/2)",
            "selected_factors": {
                "top_raw": top_factor,
                "frontend_twist": twist_factor,
                "frontend_omega3": omega_factor,
                "S2_S3_S4_S5": stage_factors,
                "B3_lambda": lambda_factor,
                "B3_R2": rsq_factor,
            },
            "forward_stage_bounds": {
                "top_split": top_bound,
                "twist": twist_bound,
                "omega3_product": omega_bound,
                "frontend_DFT3": frontend_bound,
                "S1_raw": forward_stages[1],
                "S2": forward_stages[2],
                "S3": forward_stages[3],
                "S4": forward_stages[4],
                "S5_M_terminal": forward_stages[5],
            },
            "decoded_h_bound": decoded_h_bound,
            "single_runtime_product_bound": product_bound,
            "B3_raw_degree_bounds": b3_raw_bounds,
            "B3_final_degree_bounds": b3_final_bounds,
            "sum_degree_bounds": sum_bounds,
            "maximum": maximum,
            "signed_int16_no_wrap": maximum < SIGNED16_LIMIT,
            "obsolete_contract": {
                "forward_bound": 10788,
                "sum_bound": 12699,
                "status": "contradicted by current selected executable",
                "first_observed_counterexample": 12882,
            },
            "Q24_reducer_contract": "full signed int16 (exhaustively proven by Q24 generator)",
        },
        "serialization": {
            "candidate_packer": "ntruplus768_pack_m_highrange12699_avx2",
            "note": "symbol name is stale; body tail-jumps to full-signed-int16 reducer",
            "required_result": "byte-exact Encodeq((h_hat circle r_hat + m_hat) mod q)",
            "executable_differential_required": True,
        },
        "operation_delta": {
            "removed_B3_result_reloads": 48,
            "removed_standalone_sum_stores": 48,
            "removed_vector_bytes": 3072,
            "m_loads_remain": 48,
            "vpaddw_remain": 48,
            "B3_final_stores_remain_and_store_sum": 48,
        },
    }
    return proof, contract


def render_header(contract: dict[str, int]) -> str:
    lines = [
        "/* Generated by tools/generate_proof.py; do not edit. */",
        "#ifndef GT32_ENCAP_B3_ADDM_032_RANGE_CONTRACT_H",
        "#define GT32_ENCAP_B3_ADDM_032_RANGE_CONTRACT_H",
        "",
    ]
    lines.extend(f"#define {name} {value}" for name, value in contract.items())
    lines.extend(["", "#endif", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--header", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    proof, contract = build_result(args.root)
    data = json.dumps(proof, indent=2, sort_keys=True) + "\n"
    header = render_header(contract)
    if args.check:
        if args.output.read_text() != data or args.header.read_text() != header:
            raise SystemExit("proof or generated range contract is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)
        args.header.write_text(header)


if __name__ == "__main__":
    main()
