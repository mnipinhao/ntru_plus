#!/usr/bin/env python3
"""Generate the coefficient-domain to MA2-F0 producer contract."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != text:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--range-proof", type=Path, required=True)
    parser.add_argument("--kem-source", type=Path, required=True)
    parser.add_argument("--cbd-source", type=Path, required=True)
    parser.add_argument("--producer-source", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    mapping = json.loads(args.map.read_text())
    ranges = json.loads(args.range_proof.read_text())
    kem = args.kem_source.read_text()
    cbd = args.cbd_source.read_text()
    producer = args.producer_source.read_text()
    required_kem = ("poly_cbd1(&r", "poly_sotp_encode(&m", "poly_ntt(&r)",
                    "poly_ntt(&m)")
    if any(token not in kem for token in required_kem):
        raise SystemExit("pinned encapsulation producer sequence changed")
    if ".global poly_cbd1" not in cbd or ".global poly_sotp_encode" not in cbd:
        raise SystemExit("pinned coefficient producers changed")
    forbidden = ("poly_ntt", "official_to_f0")
    if any(token in producer for token in forbidden):
        raise SystemExit("F0 producer source crosses an Official representation")

    minimum = [None] * 1152
    maximum = [None] * 1152
    owners = [None] * 1152
    for vector in mapping["f0_vectors"]:
        if vector["scale"] != {"transform": 4, "montgomery_r_exponent": 0}:
            raise SystemExit("F0 scale contract changed")
        for lane in vector["lanes"]:
            position = lane["f0_position_i16"]
            minimum[position], maximum[position] = lane["exact_f0_range_i16"]
            owners[position] = lane["semantic_owner"]
    if any(value is None for value in minimum + maximum + owners):
        raise SystemExit("F0 contract is not a complete 1152-cell map")

    physical_p = mapping["frozen_semantic_contract"]["physical_p_order"]
    physical_q = mapping["frozen_semantic_contract"]["physical_q_order"]
    if physical_p != [0, 3, 6, 1, 4, 7, 8, 2, 5]:
        raise SystemExit("F0 physical-P order changed")
    if len(set(physical_q)) != 16:
        raise SystemExit("F0 physical-Q order is not a permutation")

    document = {
        "checkpoint": "F0-PROD0",
        "parameter": 1152,
        "entry": "ntruplus1152_exp001_f0_forward_for_ma2",
        "input_roles": {
            "F0_R": {"producer": "poly_cbd1", "coefficient_range": [-1, 1]},
            "F0_M": {"producer": "poly_sotp_encode", "coefficient_range": [-1, 1]},
        },
        "shared_core_authorized": True,
        "input_abi": {
            "actual_caller_alignment_bytes": 32,
            "alias": "output-equals-input-supported",
            "length_i16": 1152,
        },
        "output_abi": {
            "owner": "(branch,p,q,terminal_coefficient)",
            "physical_p_order": physical_p,
            "physical_q_order": physical_q,
            "scale": 4,
            "montgomery_r_exponent": 0,
            "global_range_i16": [min(minimum), max(maximum)],
            "per_cell_ranges_in_header": str(args.header),
            "consumer": "F0-MA2",
        },
        "pipeline": ["existing top split arithmetic", "GT adapter/pre-twist",
                     "paper R2 NTT9", "persistent D1 NTT16",
                     "materialized F0 ABI"],
        "forbidden_boundaries": ["Official poly_ntt", "Official-to-F0 adapter"],
        "current_debt": {
            "performance_status": "unpriced-correctness-first",
            "pair_input_bytes": 576,
            "pair_output_bytes": 576,
            "split_bytes": 2304,
            "coefficient_adapter_bytes": 288,
            "zero_copy_required": False,
        },
        "range_proof_summary": [
            {key: row[key] for key in ("physical_row", "frequency_p",
                                       "input_range", "overall_final_range")}
            for row in ranges["adjusted_ntt16_full"]
        ],
        "source_sha256": {
            "map": sha256(args.map),
            "range_proof": sha256(args.range_proof),
            "kem": sha256(args.kem_source),
            "cbd": sha256(args.cbd_source),
            "producer": sha256(args.producer_source),
        },
    }
    json_text = json.dumps(document, indent=2, sort_keys=True) + "\n"
    header_lines = [
        "#ifndef NTRUPLUS1152_EXP001_F0_PROD0_RANGES_H",
        "#define NTRUPLUS1152_EXP001_F0_PROD0_RANGES_H",
        "#include <stdint.h>",
        "static const int16_t ntruplus1152_exp001_f0_prod0_min[1152] = {",
    ]
    for offset in range(0, 1152, 16):
        header_lines.append("  " + ",".join(map(str, minimum[offset:offset + 16])) + ",")
    header_lines.append("};")
    header_lines.append("static const int16_t ntruplus1152_exp001_f0_prod0_max[1152] = {")
    for offset in range(0, 1152, 16):
        header_lines.append("  " + ",".join(map(str, maximum[offset:offset + 16])) + ",")
    header_lines.extend(["};", "#endif", ""])
    write(args.json, json_text, args.check)
    write(args.header, "\n".join(header_lines), args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
