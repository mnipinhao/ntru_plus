#!/usr/bin/env python3
"""Search whether the current S4/S5 terminal can natively emit 070 M-prime.

The zero-extra proof deliberately grants each block every degree-independent
affine permutation of its four leaf-lane bits.  This is a superset of the
source/order/output gauges available from the current pair-packed S4/S5
permute/unpack topology.  The four existing deposit vpshufb masks remain fully
programmable.  If a target is unreachable even in this enlarged family, the
current terminal topology cannot obtain it merely by relabeling gauges/tables.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
import re
from pathlib import Path


def gf2_rank(rows: tuple[int, ...]) -> int:
    work = list(rows)
    pivot = 0
    for column in range(4):
        selected = next((index for index in range(pivot, 4)
                         if (work[index] >> column) & 1), None)
        if selected is None:
            continue
        work[pivot], work[selected] = work[selected], work[pivot]
        for index in range(4):
            if index != pivot and ((work[index] >> column) & 1):
                work[index] ^= work[pivot]
        pivot += 1
    return pivot


def affine_permutation(rows: tuple[int, ...], constant: int) -> tuple[int, ...]:
    result = []
    for value in range(16):
        output = constant
        for bit, row in enumerate(rows):
            output ^= ((row & value).bit_count() & 1) << bit
        result.append(output)
    return tuple(result)


def invert(permutation: tuple[int, ...]) -> tuple[int, ...]:
    result = [0] * len(permutation)
    for source, destination in enumerate(permutation):
        result[destination] = source
    return tuple(result)


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(left[right[index]] for index in range(len(right)))


def is_affine(permutation: tuple[int, ...]) -> tuple[bool, list[dict]]:
    rows = []
    valid = True
    for output_bit in range(4):
        constant = (permutation[0] >> output_bit) & 1
        coefficients = [
            ((permutation[1 << input_bit] >> output_bit) & 1) ^ constant
            for input_bit in range(4)
        ]
        for value, output in enumerate(permutation):
            predicted = constant
            for input_bit, coefficient in enumerate(coefficients):
                predicted ^= coefficient & ((value >> input_bit) & 1)
            if predicted != ((output >> output_bit) & 1):
                valid = False
                break
        rows.append({"constant": constant,
                     "coefficients_lsb_first": coefficients})
    return valid, rows


def algebraic_degrees(permutation: tuple[int, ...]) -> list[int]:
    result = []
    for output_bit in range(4):
        coefficients = [(permutation[value] >> output_bit) & 1
                        for value in range(16)]
        for input_bit in range(4):
            for mask in range(16):
                if (mask >> input_bit) & 1:
                    coefficients[mask] ^= coefficients[mask ^ (1 << input_bit)]
        result.append(max((mask.bit_count() for mask, coefficient
                           in enumerate(coefficients) if coefficient), default=0))
    return result


def cycles(permutation: tuple[int, ...]) -> list[list[int]]:
    seen = set()
    result = []
    for start in range(16):
        if start in seen:
            continue
        cycle = []
        value = start
        while value not in seen:
            seen.add(value)
            cycle.append(value)
            value = permutation[value]
        if len(cycle) > 1:
            result.append(cycle)
    return result


def deposit_mask_absorbable(permutation: tuple[int, ...]) -> bool:
    # Exact simplification of the current FR_PACKED_TO_PLANES symbolic proof:
    # its four vpshufb masks may independently exchange each adjacent word
    # pair, while the following dq/qdq unpacks and plane destinations stay.
    return all(permutation[2 * pair] in (2 * pair, 2 * pair + 1)
               and permutation[2 * pair + 1] in (2 * pair, 2 * pair + 1)
               and permutation[2 * pair] != permutation[2 * pair + 1]
               for pair in range(8))


def one_vpshufb(permutation: tuple[int, ...]) -> bool:
    return all(source // 8 == destination // 8
               for destination, source in enumerate(permutation))


def one_vpermq(permutation: tuple[int, ...]) -> bool:
    return (all(permutation[lane] % 4 == lane % 4 for lane in range(16))
            and all(len({permutation[4 * qword + offset] // 4
                         for offset in range(4)}) == 1 for qword in range(4))
            and len({permutation[4 * qword] // 4 for qword in range(4)}) == 4)


def one_vpermd(permutation: tuple[int, ...]) -> bool:
    return (all(permutation[2 * dword + 1] == permutation[2 * dword] + 1
                and permutation[2 * dword] % 2 == 0 for dword in range(8))
            and len({permutation[2 * dword] // 2 for dword in range(8)}) == 8)


def route_class(permutation: tuple[int, ...]) -> tuple[int, str]:
    if deposit_mask_absorbable(permutation):
        return 0, "existing-deposit-mask-relabel"
    if one_vpshufb(permutation):
        return 1, "one-vpshufb-after-deposit"
    if one_vpermq(permutation):
        return 1, "one-vpermq-after-deposit"
    if one_vpermd(permutation):
        return 1, "one-vpermd-after-deposit"
    return 2, "more-than-one-modeled-unary-route"


def affine_gauges():
    matrices = [rows for rows in itertools.product(range(16), repeat=4)
                if gf2_rank(rows) == 4]
    assert len(matrices) == 20160
    for rows in matrices:
        for constant in range(16):
            permutation = affine_permutation(rows, constant)
            yield rows, constant, permutation, invert(permutation)


def search_class(target: tuple[int, ...], gauges: list[tuple]) -> dict:
    best = None
    zero_gauges = 0
    for rows, constant, gauge, inverse_gauge in gauges:
        residual = compose(inverse_gauge, target)
        route = route_class(residual)
        if route[0] == 0:
            zero_gauges += 1
        candidate = (route[0], route[1], rows, constant, gauge, residual)
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    affine, matrix = is_affine(target)
    return {
        "target_permutation": list(target),
        "cycles": cycles(target),
        "is_gf2_affine": affine,
        "affine_rows_if_valid": matrix if affine else None,
        "output_algebraic_degrees": algebraic_degrees(target),
        "zero_extra_affine_gauges": zero_gauges,
        "best_modeled_residual_class": best[0],
        "best_modeled_residual_family": best[1],
        "best_affine_gauge": {
            "matrix_rows_lsb_first": list(best[2]),
            "constant": best[3],
            "permutation": list(best[4]),
        },
        "best_residual_permutation": list(best[5]),
    }


def csv_text(rows: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def macro_body(text: str, name: str) -> str:
    match = re.search(rf"^\s*\.macro\s+{re.escape(name)}\b(.*?)^\s*\.endm\s*$",
                      text, re.MULTILINE | re.DOTALL)
    if match is None:
        raise ValueError(f"missing selected macro {name}")
    return match.group(1)


def mnemonic_count(body: str, mnemonic: str) -> int:
    return len(re.findall(rf"^\s*{re.escape(mnemonic)}\b", body, re.MULTILINE))


def audit_selected_terminal(ntt: Path) -> dict:
    text = ntt.read_text()
    half = macro_body(text, "FR_MONT_HALF_PAIR")
    qword = macro_body(text, "FR_MONT_QWORD_PACKED")
    deposit = macro_body(text, "FR_PACKED_TO_PLANES")
    counts = {
        "s4_vperm2i128_per_pair": mnemonic_count(half, "vperm2i128"),
        "s5_vpunpcklqdq_per_pair": mnemonic_count(qword, "vpunpcklqdq"),
        "s5_vpunpckhqdq_per_pair": mnemonic_count(qword, "vpunpckhqdq"),
        "deposit_vpshufb_per_block": mnemonic_count(deposit, "vpshufb"),
        "deposit_dq_unpacks_per_block":
            mnemonic_count(deposit, "vpunpckldq") + mnemonic_count(deposit, "vpunpckhdq"),
        "deposit_qdq_unpacks_per_block":
            mnemonic_count(deposit, "vpunpcklqdq") + mnemonic_count(deposit, "vpunpckhqdq"),
    }
    expected = {
        "s4_vperm2i128_per_pair": 4,
        "s5_vpunpcklqdq_per_pair": 1,
        "s5_vpunpckhqdq_per_pair": 1,
        "deposit_vpshufb_per_block": 4,
        "deposit_dq_unpacks_per_block": 4,
        "deposit_qdq_unpacks_per_block": 4,
    }
    if counts != expected:
        raise ValueError(f"selected terminal topology changed: {counts}")
    selected = re.search(
        r"ntruplus768_ntt_m_avx2:(.*?)\.size\s+ntruplus768_ntt_m_avx2",
        text, re.DOTALL)
    if selected is None:
        raise ValueError("missing selected M Forward body")
    body = selected.group(1)
    calls = {
        "s4_pair_calls_per_tile": body.count("FR_MONT_HALF_PAIR"),
        "s5_pair_calls_per_tile": body.count("FR_MONT_QWORD_PACKED"),
        "deposit_calls_per_tile": body.count("FR_PACKED_TO_PLANES"),
    }
    if calls != {"s4_pair_calls_per_tile": 4,
                 "s5_pair_calls_per_tile": 4,
                 "deposit_calls_per_tile": 2}:
        raise ValueError(f"selected Forward call topology changed: {calls}")
    return {"macro_instruction_counts": counts, "selected_calls": calls,
            "status": "PASS"}


def build(search070: Path, ntt: Path) -> tuple[dict, str]:
    source = json.loads(search070.read_text())
    blocks = source["best_uniform_microkernel"]["blocks"]
    targets = [tuple(block["old_lane_for_each_new_lane"]) for block in blocks]
    unique_targets = list(dict.fromkeys(targets))
    gauges = list(affine_gauges())
    assert len(gauges) == 322560
    analyses = [search_class(target, gauges) for target in unique_targets]
    target_to_class = {target: index for index, target in enumerate(unique_targets)}
    multiplicities = [targets.count(target) for target in unique_targets]

    rows = []
    nonzero_blocks = 0
    modeled_ops = 0
    for block, target in zip(blocks, targets):
        index = target_to_class[target]
        analysis = analyses[index]
        zero = analysis["zero_extra_affine_gauges"] != 0
        if not zero:
            nonzero_blocks += 1
        modeled_ops += analysis["best_modeled_residual_class"] * 4
        rows.append({
            "new_block": block["new_block"],
            "old_block": block["old_block"],
            "branch": block["branch"],
            "k3": block["k3"],
            "q4": block["q4"],
            "permutation_class": index,
            "affine_target": analyses[index]["is_gf2_affine"],
            "zero_extra_in_enlarged_gauge": zero,
            "best_modeled_residual_class": analysis["best_modeled_residual_class"],
            "best_modeled_residual_family": analysis["best_modeled_residual_family"],
        })

    # A non-trivial residual affects four independent coefficient-plane YMMs.
    # AVX2 has one destination per vector instruction, so this is an optimistic
    # lower bound even before charging any cross-half/two-source complexity.
    lower_bound = 4 * nonzero_blocks
    tier = "T0_FREE" if lower_bound == 0 else (
        "T1_NEAR_FREE" if lower_bound <= 16 else "T2_EXPENSIVE")

    degree_profiles = {}
    for analysis, multiplicity in zip(analyses, multiplicities):
        key = tuple(analysis["output_algebraic_degrees"])
        degree_profiles[key] = degree_profiles.get(key, 0) + multiplicity

    result = {
        "schema": "ntruplus768-gt32-encap-mprime-terminal-071-v1",
        "experiment": "GT32-ENCAP-MPRIME-TERMINAL-071",
        "production_modified": False,
        "sources": {
            "search070": {"path": str(search070.resolve()),
                          "sha256": hashlib.sha256(search070.read_bytes()).hexdigest()},
            "ntt_m": {"path": str(ntt.resolve()),
                      "sha256": hashlib.sha256(ntt.read_bytes()).hexdigest()},
        },
        "selected_terminal_source_audit": audit_selected_terminal(ntt),
        "fixed_target": {
            "block_order_old_indices":
                source["best_uniform_microkernel"]["block_order_old_indices"],
            "uniform_q24_transpose_output_order":
                source["best_uniform_microkernel"]["transpose_output_order"],
            "uniform_q24_vpermq_immediates":
                source["best_uniform_microkernel"]["vpermq_immediates"],
        },
        "searched_terminal_family": {
            "current_pair_packed_topology": True,
            "lane_wise_s4_s5_arithmetic": "unchanged",
            "degree_independent_output_gauge":
                "all AGL(4,2), a superset of legal unpack/rejoin source, branch and output gauges",
            "affine_gauges_per_block": len(gauges),
            "gauge_independence":
                "granted independently per block; more permissive than the shared production loop",
            "deposit": "current dq/qdq topology with all four pshufb masks freely relabeled",
            "blend_accounting":
                "a non-affine residual needs a movement-producing instruction for each affected degree-plane output; blends are charged, not treated as a free gauge",
        },
        "permutation_classes": {
            "raw_distinct": len(unique_targets),
            "multiplicities": multiplicities,
            "algebraic_degree_profiles": [
                {"degrees": list(profile), "blocks": count}
                for profile, count in sorted(degree_profiles.items())
            ],
            "analyses": analyses,
        },
        "lower_bound": {
            "zero_extra_blocks": len(blocks) - nonzero_blocks,
            "nonzero_blocks": nonzero_blocks,
            "independent_degree_plane_outputs_per_block": 4,
            "optimistic_extra_vector_ops_per_forward": lower_bound,
            "eligibility_threshold": 16,
            "tier": tier,
            "proof_scope":
                "exact for current pair-packed affine output-gauge plus current deposit topology; the gauge search is an independent-per-block superset",
        },
        "modeled_route_score": {
            "optimistic_vector_op_score_per_forward": modeled_ops,
            "note":
                "selection aid only: unresolved more-than-one routes are scored as 2; this is neither an emitted route nor a universal lower bound over arbitrary non-affine AVX2 DAGs",
        },
        "decision": {
            "status": "NO_072_ASM" if tier == "T2_EXPENSIVE" else "OPEN_072_ASM",
            "reason":
                "even the optimistic movement lower bound exceeds the 16-op near-free eligibility threshold"
                if tier == "T2_EXPENSIVE" else
                "the terminal lower bound is inside the executable eligibility threshold",
            "q24_and_b3_reopen": False,
            "reopen":
                "only a non-affine S4/S5/deposit network that replaces mode-critical current movement at no extra cost, outside this affine current-topology family",
        },
    }
    return result, csv_text(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search070", required=True, type=Path)
    parser.add_argument("--ntt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--classes", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, classes = build(args.search070, args.ntt)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if args.output.read_text() != encoded or args.classes.read_text() != classes:
            raise SystemExit("071 generated evidence is stale")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded)
    args.classes.write_text(classes)


if __name__ == "__main__":
    main()
