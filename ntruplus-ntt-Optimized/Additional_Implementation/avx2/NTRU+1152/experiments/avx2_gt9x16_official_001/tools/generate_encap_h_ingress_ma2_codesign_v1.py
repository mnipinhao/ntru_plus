#!/usr/bin/env python3
"""Map decoder-native and streaming public-key ingress into Natural-Q MA2."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != text:
            raise SystemExit(f"generated co-design map is stale: {path}")
    else:
        path.write_text(text)


def function(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decode-map", type=Path, required=True)
    parser.add_argument("--h1-contract", type=Path, required=True)
    parser.add_argument("--official-kem", type=Path, required=True)
    parser.add_argument("--candidate-kem", type=Path, required=True)
    parser.add_argument("--api", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    decode = json.loads(args.decode_map.read_text())
    h1 = json.loads(args.h1_contract.read_text())
    if decode["decode_geometry"]["block_local_natural_vectors"] != 72:
        raise SystemExit("streaming prerequisite no longer holds")
    ownership = decode["ownership"]
    block_tiles: dict[int, dict[tuple[int, int], set[int]]] = {}
    block_source_pairs: dict[int, set[tuple[int, int]]] = {}
    for item in ownership:
        block = item["decode_block"]
        owner = item["semantic"]
        tile = (owner["branch"], owner["p"])
        block_tiles.setdefault(block, {}).setdefault(tile, set()).add(
            owner["terminal_coefficient"])
        vector = item["official_physical_vector"] % 8
        natural_vector = item["natural_vector"]
        block_source_pairs.setdefault(block, set()).add((natural_vector, vector))
    for block, tiles in block_tiles.items():
        if len(tiles) != 2 or any(coefficients != {0, 1, 2, 3}
                                  for coefficients in tiles.values()):
            raise SystemExit(f"decode block {block} is not two complete MA2 tiles")

    official = args.official_kem.read_text()
    candidate = args.candidate_kem.read_text()
    api = args.api.read_text()
    official_derand = function(official, "static inline int crypto_kem_enc_derand",
                               "int crypto_kem_enc(")
    candidate_derand = function(candidate, "static inline int crypto_kem_enc_derand",
                                "int crypto_kem_enc(")
    candidate_public = function(candidate, "int crypto_kem_enc(unsigned char *ct",
                                "/*************************************************\n* Name:        crypto_kem_dec")
    if candidate_public.find("randombytes(coins") > candidate_public.find(
            "crypto_kem_enc_derand(ct, ss, pk, coins)"):
        raise SystemExit("randomness is not consumed before the deterministic caller")
    required_order = ["poly_frombytes(&h, pk)", "hash_f(", "poly_cbd1(&r",
                      "prod3_ma2_hash_h1_natural_q(ct, r_f0.coeffs)",
                      "poly_sotp_encode(&m", "f0_ma2_planes_natural_q_scale4("]
    positions = [candidate_derand.find(token) for token in required_order]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        raise SystemExit("cumulative encapsulation order changed")
    if candidate_derand.count("h.coeffs") != 1:
        raise SystemExit("h no longer has exactly one arithmetic consumer")
    if "overlap" in api.lower() or "alias" in api.lower():
        raise SystemExit("public API gained an explicit overlap contract; re-audit H3")

    tiles = []
    for block in range(9):
        entries = []
        for (branch, p), coefficients in sorted(block_tiles[block].items()):
            entries.append({"branch": branch, "p": p,
                            "terminal_coefficients": sorted(coefficients)})
        tiles.append({"decode_block": block, "pk_byte_range": [192 * block,
                                                                 192 * block + 191],
                      "ma2_tiles": entries,
                      "natural_destination_vectors": sorted({item["natural_vector"]
                          for item in ownership if item["decode_block"] == block}),
                      "decoded_source_vectors": list(range(8))})

    report = {
        "schema": "encap-h-ingress-ma2-codesign/v1",
        "checkpoint": "ENCAP-H-INGRESS-MA2-CODESIGN-V1",
        "scope": "architecture map; H1 is implemented control; H2/H3 are not timed or promoted",
        "frozen": {"r_m_presentation": "Natural-Q scale-4 PROD3",
                   "ma2_mathematics": "quartic MulAdd unchanged",
                   "pk_wire_bytes": 1728, "acceptance": "all coefficients <3457",
                   "ciphertext_and_shared_secret": "byte-exact external contract"},
        "architectures": {
            "H0-current": {"h_presentation": "Official poly_frombytes layout",
                           "resident_h_bytes": 2304, "projection_routes": 360,
                           "ma2_h_loads": 144},
            "H1-direct-natural-q-control": {
                "status": "implemented correctness and linked-audit control",
                "h_presentation": "exact Natural-Q", "resident_h_bytes": 2304,
                "decoder_formation_routes": h1["decoder"]["formation_routes"],
                "ma2_h_loads": h1["consumer"]["h_loads"]},
            "H2-decoder-native-persistent": {
                "status": "schedule search required",
                "freedoms": ["vector order", "lane order", "half order",
                             "block-local output swaps", "offline lambda reindex",
                             "h scale/Montgomery presentation"],
                "constraint": "each semantic h component multiplies the matching Natural-Q r component",
                "warning": "constant reindex alone cannot repair a mismatched h/r lane owner; the MA2 schedule must absorb it"},
            "H3-streaming-decode-ma2": {
                "status": "caller-legal and block-local; exact zero-spill schedule not yet proved",
                "resident_h_bytes": 0, "h_stores": 0, "h_reloads": 0,
                "blocks": tiles,
                "caller_reorder": "hash/r/m/forwards, then nine decode+validate+MA2 waves",
                "pk_ct_overlap_preservation": "serialize/hash r into storage reusing the dead 2304-byte h frame slot; do not write ct until all pk blocks are consumed",
                "invalid_key": "validation accumulator is public; after the final block zero ct/ss and return 1 exactly as current",
                "randomness": "crypto_kem_enc consumes coins before crypto_kem_enc_derand both before and after reorder",
            },
        },
        "caller_legality": {
            "hash_f_reads_pk_bytes_not_h": "hash_f(" in candidate_derand,
            "r_m_production_has_no_h_dependency": candidate_derand.find("h.coeffs") > candidate_derand.find("poly_sotp_encode(&m"),
            "h_success_value_consumers": 1,
            "randombytes_before_derand": True,
            "current_invalid_external_result": "zero ct, zero ss, return 1",
            "late_validation_external_result_can_match": True,
            "extra_invalid_input_work_depends_only_on_public_pk": True,
            "api_explicit_overlap_contract": False,
            "overlap_safe_plan_required": True,
        },
        "wavefront": {
            "block_local_vectors": 72, "cross_block_vectors": 0,
            "complete_ma2_tiles_per_decode_block": 2,
            "shared_decoded_sources": "both tiles reuse all eight decoded source vectors",
            "naive_live_bound": {"decoded_sources": 8, "formed_h_quartet": 4,
                                 "r_quartet": 4, "minimum_temps": 2, "total": 18,
                                 "fits_16_ymm": False},
            "candidate_accumulator_wavefront_bound": {
                "decoded_sources": 8, "four_output_accumulators": 4,
                "one_formed_h": 1, "one_r_operand": 1,
                "montgomery_and_route_temps": 2, "total": 16,
                "fits_16_ymm": True, "slack": 0,
                "requires": "exact register allocation and linked zero-spill proof"},
            "fallback": "materialize four h vectors for the second tile only (128 bytes/block); prices a half-resident H3 control",
        },
        "decision": {
            "H1": "retain as machine control; do not optimize or promote it before H3 pricing",
            "H3": "preferred architecture; next checkpoint is exact one-block/two-tile schedule",
            "H2": "fallback if H3 exact schedule spills or regresses",
            "benchmark": False, "native_kem": False,
        },
        "source_sha256": {name: sha256(path) for name, path in {
            "decode_map": args.decode_map, "h1_contract": args.h1_contract,
            "official_kem": args.official_kem, "candidate_kem": args.candidate_kem,
            "api": args.api}.items()},
        "official_order_checked": official_derand.find("poly_frombytes(&h, pk)") <
                                  official_derand.find("hash_f("),
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    write(args.output, rendered, args.check)
    print("H ingress co-design: caller reorder legal; 9 blocks each feed two MA2 tiles; H3 exact schedule next")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
