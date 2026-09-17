#!/usr/bin/env python3
"""Exact ternary reachable-range proof for gate 130's S3 GS pre-add."""

from __future__ import annotations

import argparse
import json
import sys
from itertools import product
from pathlib import Path

Q = 3457
I16_MAX = 32767
OMEGA3_MONT = -886


def load_tile4(root: Path):
    tools = root / "experiments/avx2_gt32_tile4_official_001/tools"
    sys.path.insert(0, str(tools))
    import generate_tile4 as gt
    return gt


def frontend_value(gt, branch: int, k3: int, logical_q: int,
                   values: tuple[int, ...]) -> int:
    scale = gt.BRANCH_SCALE[branch]
    twisted = []
    for n3 in range(3):
        low, high = values[2 * n3:2 * n3 + 2]
        top = low - 722 * high if branch == 0 else low + 723 * high
        power = (64 * n3 + 33 * logical_q) % 96
        factor = gt.centered(pow(scale, -power, gt.Q) * gt.R)
        twisted.append(gt.montgomery_fixed(top, factor))
    a_value, p_value, q_value = twisted
    omega_value = gt.montgomery_fixed(p_value - q_value, OMEGA3_MONT)
    return (
        a_value + p_value + q_value,
        a_value - q_value + omega_value,
        a_value - p_value - omega_value,
    )[k3]


def leaf_record(gt, branch: int, k3: int, logical_q: int) -> dict:
    outcomes = []
    for values in product((-1, 0, 1), repeat=6):
        outcomes.append((frontend_value(gt, branch, k3, logical_q, values), values))
    minimum = min(outcomes, key=lambda item: item[0])
    maximum = max(outcomes, key=lambda item: item[0])
    return {
        "Q": logical_q,
        "minimum": minimum[0],
        "maximum": maximum[0],
        "argmin": list(minimum[1]),
        "argmax": list(maximum[1]),
        "reachable_value_count": len({item[0] for item in outcomes}),
    }


def coefficient_indices(logical_q: int, coefficient: int) -> list[int]:
    base = 4 * logical_q + coefficient
    # GT_BLEND3 rotates the three 128-word source groups before the three
    # twist/DFT3 inputs.  This is the source-group order for twist inputs
    # n3=0,1,2 at each Q residue.
    blend_orders = (
        (0, 2, 1),
        (1, 0, 2),
        (2, 1, 0),
        (0, 2, 1),
    )
    group = logical_q // 4
    xyz_sources = ((group + 0) % 3, (group + 1) % 3, (group + 2) % 3)
    result = []
    for xyz_index in blend_orders[logical_q % 4]:
        source_group = xyz_sources[xyz_index]
        result.extend((base + 128 * source_group,
                       base + 384 + 128 * source_group))
    return result


def build(root: Path) -> tuple[dict, list[int]]:
    gt = load_tile4(root)
    records = []
    worst = None
    leaf_cache = {}
    for branch in range(2):
        for k3 in range(3):
            for logical_q in range(32):
                leaf_cache[(branch, k3, logical_q)] = leaf_record(
                    gt, branch, k3, logical_q)
            for residue in range(4):
                q_values = [residue + 4 * vector for vector in range(8)]
                for kind, signs in (
                    ("sum", [1] * 8),
                    ("difference", [1, -1, 1, -1, 1, -1, 1, -1]),
                ):
                    minimum = sum(
                        leaf_cache[(branch, k3, q)]["minimum" if sign > 0 else "maximum"] * sign
                        for q, sign in zip(q_values, signs)
                    )
                    maximum = sum(
                        leaf_cache[(branch, k3, q)]["maximum" if sign > 0 else "minimum"] * sign
                        for q, sign in zip(q_values, signs)
                    )
                    item = {
                        "branch": branch, "k3": k3,
                        "S3_packet_lane": residue, "kind": kind,
                        "logical_Q_support": q_values,
                        "minimum": minimum, "maximum": maximum,
                        "max_abs": max(abs(minimum), abs(maximum)),
                        "signed_i16_safe": minimum >= -32768 and maximum <= I16_MAX,
                    }
                    records.append(item)
                    if worst is None or item["max_abs"] > worst["max_abs"]:
                        worst = item

    assert worst is not None
    witness = [0] * 768
    signs = ([1] * 8 if worst["kind"] == "sum" else
             [1, -1, 1, -1, 1, -1, 1, -1])
    witness_terms = []
    for logical_q, sign in zip(worst["logical_Q_support"], signs):
        leaf = leaf_cache[(worst["branch"], worst["k3"], logical_q)]
        values = leaf["argmax" if sign > 0 else "argmin"]
        indices = coefficient_indices(logical_q, 0)
        for index, value in zip(indices, values):
            assert witness[index] == 0
            witness[index] = value
        reached = frontend_value(gt, worst["branch"], worst["k3"], logical_q,
                                 tuple(values))
        witness_terms.append({
            "Q": logical_q, "sign": sign, "frontend_value": reached,
            "coefficient_indices": indices, "coefficient_values": values,
        })
    reached_preadd = sum(term["sign"] * term["frontend_value"]
                         for term in witness_terms)
    assert reached_preadd == worst["maximum"]
    wrapped = ((reached_preadd + 32768) & 0xFFFF) - 32768
    assert (wrapped - reached_preadd) % Q != 0

    unsafe = [record for record in records if not record["signed_i16_safe"]]
    result = {
        "schema": "ntruplus768-gt32-s3gs-ternary-reachable-range-v1",
        "experiment": "GT32-S3GS-REACHABLE-RANGE-131",
        "production_modified": False,
        "input_contract": "768 independent coefficients in {-1,0,1}",
        "method": {
            "leaf_enumeration": "exact 3^6 assignments per (branch,k3,Q)",
            "support_decomposition": "the eight Q leaves use disjoint six-coefficient supports",
            "S1_S2_property": "all paths feeding S3 packet 0 are identity CT add/sub paths",
            "composition": "exact extrema add because supports are disjoint",
        },
        "records": records,
        "unsafe_record_count": len(unsafe),
        "worst": worst,
        "witness": {
            "nonzero_coefficients": sum(value != 0 for value in witness),
            "terms": witness_terms,
            "mathematical_preadd": reached_preadd,
            "vpaddw_result": wrapped,
            "error": wrapped - reached_preadd,
            "error_mod_q": (wrapped - reached_preadd) % Q,
        },
        "decision": "candidate-130-closed-for-ternary-forward-input",
        "reason": "an exactly reachable S3 GS pre-add exceeds signed int16 and wraps by a nonzero residue modulo q",
        "reopen_condition": "change the factorization/producer so this GS pre-add is absent or reduced; do not add back the deleted checkpoint",
    }
    return result, witness


def render_header(witness: list[int]) -> str:
    entries = [(index, value) for index, value in enumerate(witness) if value]
    lines = [
        "/* Generated by tools/prove.py; do not edit. */",
        "#ifndef GT32_131_WITNESS_H", "#define GT32_131_WITNESS_H",
        "#include <stddef.h>", "#include <stdint.h>",
        "struct gt32_131_assignment { uint16_t index; int16_t value; };",
        "static const struct gt32_131_assignment gt32_131_witness[] = {",
    ]
    lines.extend(f"\t{{{index}, {value}}}," for index, value in entries)
    lines.extend([
        "};", "static const size_t gt32_131_witness_count =",
        "\tsizeof gt32_131_witness / sizeof gt32_131_witness[0];",
        "#endif", "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, witness = build(args.root.resolve())
    json_text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    header_text = render_header(witness)
    if args.check:
        if args.json.read_text() != json_text or args.header.read_text() != header_text:
            raise SystemExit("generated gate 131 artifacts are stale")
    else:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json_text)
        args.header.write_text(header_text)
    print(json.dumps({
        "worst": result["worst"],
        "unsafe_record_count": result["unsafe_record_count"],
        "witness_preadd": result["witness"]["mathematical_preadd"],
        "witness_vpaddw": result["witness"]["vpaddw_result"],
        "decision": result["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
