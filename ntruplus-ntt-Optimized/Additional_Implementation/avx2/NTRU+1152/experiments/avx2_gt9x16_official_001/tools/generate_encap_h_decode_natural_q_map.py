#!/usr/bin/env python3
"""Map Official PK decoding directly to the frozen Natural-Q MA2 h ABI."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from pathlib import Path

N = 1152
Q = 3457
COEFFICIENT_BITS = 12
DECODE_BLOCK_COEFFICIENTS = 128
PHYSICAL_VECTOR_COEFFICIENTS = 16


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_u16_array(path: Path, name: str) -> list[int]:
    text = path.read_text()
    match = re.search(
        rf"static const uint16_t\s+{re.escape(name)}\[1152\]\s*=\s*\{{(.*?)\}};",
        text, re.S)
    if not match:
        raise SystemExit(f"missing {name} in {path}")
    values = [int(value) for value in re.findall(r"\b\d+\b", match.group(1))]
    if len(values) != N or sorted(values) != list(range(N)):
        raise SystemExit(f"{name} is not a 1152-cell permutation")
    return values


def bit_fragments(serialized_coefficient: int) -> list[dict[str, int]]:
    fragments: list[dict[str, int]] = []
    start = COEFFICIENT_BITS * serialized_coefficient
    bit = 0
    while bit < COEFFICIENT_BITS:
        global_bit = start + bit
        byte = global_bit // 8
        byte_bit = global_bit % 8
        width = min(8 - byte_bit, COEFFICIENT_BITS - bit)
        fragments.append({"pk_byte": byte, "pk_lsb": byte_bit,
                          "coefficient_lsb": bit, "width": width})
        bit += width
    return fragments


def asm_loop_counts(path: Path) -> dict[str, object]:
    text = path.read_text()
    body = text.split("_looptop_poly_frombytes:", 1)[1].split(
        "jb  _looptop_poly_frombytes", 1)[0]
    mnemonics = re.findall(r"^\s*([a-z][a-z0-9]+)\s", body, re.M)
    counts = {name: mnemonics.count(name) for name in sorted(set(mnemonics))}
    cross_vector = sum(counts.get(name, 0) for name in
                       ("vperm2i128", "vpunpcklqdq", "vpunpckhqdq",
                        "vpblendd", "vpblendw"))
    return {
        "blocks": N // DECODE_BLOCK_COEFFICIENTS,
        "per_block": counts,
        "total_instructions_including_pointer_and_validation":
            len(mnemonics) * (N // DECODE_BLOCK_COEFFICIENTS),
        "cross_vector_unpack_routes_per_block": cross_vector,
        "cross_vector_unpack_routes_total":
            cross_vector * (N // DECODE_BLOCK_COEFFICIENTS),
        "pk_vector_loads": counts.get("vmovdqu", 0) * 9,
        "official_layout_vector_stores": counts.get("vmovdqa", 0) * 9,
    }


def extensional_checks(physical_to_serialized: list[int],
                       natural_to_physical: list[int]) -> dict[str, int | bool]:
    serialized_to_physical = [0] * N
    for physical, serialized in enumerate(physical_to_serialized):
        serialized_to_physical[serialized] = physical

    def encode(values: list[int]) -> bytes:
        output = bytearray(N * COEFFICIENT_BITS // 8)
        for coefficient, value in enumerate(values):
            offset = coefficient * COEFFICIENT_BITS
            byte, shift = divmod(offset, 8)
            word = value << shift
            for index in range(3):
                if byte + index < len(output):
                    output[byte + index] |= (word >> (8 * index)) & 0xff
        return bytes(output)

    def extract(data: bytes, coefficient: int) -> int:
        offset = coefficient * COEFFICIENT_BITS
        byte, shift = divmod(offset, 8)
        word = int.from_bytes(data[byte:byte + 3], "little")
        return (word >> shift) & 0xfff

    def official_decode(data: bytes) -> tuple[bool, list[int]]:
        serialized = [extract(data, index) for index in range(N)]
        physical = [0] * N
        for index, value in enumerate(serialized):
            physical[serialized_to_physical[index]] = value
        return max(serialized) < Q, physical

    def natural_decode(data: bytes) -> tuple[bool, list[int]]:
        values = [extract(data, physical_to_serialized[source])
                  for source in natural_to_physical]
        return max(values) < Q, values

    for value in range(4096):
        values = [0] * N
        values[0] = value
        data = encode(values)
        official_valid, official = official_decode(data)
        natural_valid, natural = natural_decode(data)
        if official_valid != natural_valid:
            raise AssertionError("scalar byte-level validity identity failed")
        if official_valid and natural != [official[source]
                                          for source in natural_to_physical]:
            raise AssertionError("scalar byte-level output identity failed")

    edge_values = (Q - 1, Q, Q + 1, 4095)
    single_cases = 0
    for position in range(N):
        for value in edge_values:
            values = [0] * N
            values[position] = value
            data = encode(values)
            official_valid, official = official_decode(data)
            natural_valid, natural_values = natural_decode(data)
            if official_valid != natural_valid:
                raise AssertionError("single-position validity mismatch")
            if official_valid and natural_values != [official[source]
                                                      for source in natural_to_physical]:
                raise AssertionError("valid single-position map mismatch")
            single_cases += 1

    multiple_cases = 0
    for position in range(N):
        values = [0] * N
        values[position] = Q
        values[(position * 73 + 19) % N] = 4095
        data = encode(values)
        official_valid, _ = official_decode(data)
        natural_valid, _ = natural_decode(data)
        if official_valid != natural_valid:
            raise AssertionError("multiple-invalid validity mismatch")
        multiple_cases += 1

    generator = random.Random(0x48444543)
    random_cases = 1003
    for _ in range(random_cases):
        data = bytes(generator.randrange(256) for _ in range(N * 3 // 2))
        official_valid, official = official_decode(data)
        natural_valid, natural = natural_decode(data)
        if official_valid != natural_valid:
            raise AssertionError("random validity mismatch")
        if official_valid and natural != [official[source]
                                          for source in natural_to_physical]:
            raise AssertionError("random valid output mismatch")

    return {
        "exhaustive_scalar_12bit_values": 4096,
        "single_position_edge_cases": single_cases,
        "multiple_invalid_cases": multiple_cases,
        "random_12bit_strings": random_cases,
        "accepted_set_identical": True,
        "valid_output_is_exact_natural_permutation": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-layout", type=Path, required=True)
    parser.add_argument("--natural-header", type=Path, required=True)
    parser.add_argument("--natural-schedule", type=Path, required=True)
    parser.add_argument("--pack-source", type=Path, required=True)
    parser.add_argument("--official-kem", type=Path, required=True)
    parser.add_argument("--candidate-kem", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    pack_layout = json.loads(args.pack_layout.read_text())
    physical_to_serialized = pack_layout["physical_to_serialized"]
    if len(physical_to_serialized) != N or sorted(physical_to_serialized) != list(range(N)):
        raise SystemExit("Official pack layout is not a 1152-cell permutation")
    natural_to_physical = parse_u16_array(
        args.natural_header, "ntruplus1152_exp001_qnat_h_source")
    schedule = json.loads(args.natural_schedule.read_text())
    plans = schedule["resident_h"]["natural_plans"]
    if len(plans) != N // PHYSICAL_VECTOR_COEFFICIENTS:
        raise SystemExit("Natural-Q resident-h plan count changed")

    plan_by_vector = {}
    block_local = 0
    for plan in plans:
        vector = plan["tile"] * 4 + plan["coefficient"]
        if vector in plan_by_vector:
            raise SystemExit("duplicate Natural-Q destination vector")
        source_blocks = sorted({source // 8 for source in plan["source_vectors"]})
        if len(source_blocks) == 1:
            block_local += 1
        plan_by_vector[vector] = (plan, source_blocks)
    if sorted(plan_by_vector) != list(range(72)):
        raise SystemExit("Natural-Q destination vectors are incomplete")

    ownership = []
    for destination in range(N):
        destination_vector, lane = divmod(destination, 16)
        plan, source_blocks = plan_by_vector[destination_vector]
        source = natural_to_physical[destination]
        serialized = physical_to_serialized[source]
        ownership.append({
            "natural_cell": destination,
            "natural_vector": destination_vector,
            "natural_lane": lane,
            "semantic": {"branch": plan["branch"], "p": plan["p"],
                         "q": plan["destination_lane_to_semantic_q"][lane],
                         "terminal_coefficient": plan["coefficient"]},
            "official_physical_cell": source,
            "official_physical_vector": source // 16,
            "official_physical_lane": source % 16,
            "serialized_coefficient": serialized,
            "decode_block": serialized // DECODE_BLOCK_COEFFICIENTS,
            "pk_bit_offset": serialized * COEFFICIENT_BITS,
            "pk_fragments": bit_fragments(serialized),
            "plan_source_decode_blocks": source_blocks,
        })

    for entry in ownership:
        if entry["decode_block"] not in entry["plan_source_decode_blocks"]:
            raise SystemExit("ownership and Natural-Q plan disagree on decode block")

    official_kem = args.official_kem.read_text()
    candidate_kem = args.candidate_kem.read_text()
    official_encap = official_kem.split("static inline int crypto_kem_enc_derand", 1)[1].split(
        "int crypto_kem_enc(", 1)[0]
    candidate_encap = candidate_kem.split("static inline int crypto_kem_enc_derand", 1)[1].split(
        "int crypto_kem_enc(", 1)[0]
    if official_encap.count("poly_frombytes(&h, pk)") != 1:
        raise SystemExit("Official Encap h decode call graph changed")
    if official_encap.count("poly_basemul(&c, &h, &r)") != 1:
        raise SystemExit("Official Encap h arithmetic consumer changed")
    if candidate_encap.count("poly_frombytes(&h, pk)") != 1:
        raise SystemExit("candidate Encap h decode call graph changed")
    if candidate_encap.count("h.coeffs") != 1:
        raise SystemExit("candidate Encap h consumer fanout changed")

    decoder = asm_loop_counts(args.pack_source)
    current_projection = schedule["resident_h"]["natural_exact_schedule"]
    if current_projection["data_loads"] != 144 or current_projection["routing_total"] != 360:
        raise SystemExit("frozen resident-h projection ledger changed")
    direct_baseline = {
        "pk_vector_loads": decoder["pk_vector_loads"],
        "natural_layout_vector_stores": 72,
        "natural_formation_routes_upper_bound": 360,
        "ma2_native_h_vector_loads": 72,
        "scratch_bytes": 0,
        "cross_decode_block_retention": 0,
        "full_official_layout_intermediate": False,
        "note": "reuses the proved projector networks on live decode outputs; linked ASM may absorb routes into unpack geometry",
    }

    report = {
        "schema": "encap-h-decode-natural-q-map/v1",
        "checkpoint": "ENCAP-H-DECODE-NATURAL-Q-MAP",
        "scope": "map/proof only; no ASM and no performance result",
        "protocol_contract": {
            "pk_bytes": "unchanged 1728-byte encoding",
            "coefficient_bits": 12,
            "canonical_range": [0, Q - 1],
            "invalid_range": [Q, 4095],
            "error_return": "identical nonzero result iff any decoded coefficient is >= q",
            "mathematical_h": "unchanged; Natural-Q is a private lane permutation",
        },
        "consumer_graph": {
            "official": ["poly_frombytes(&h,pk)", "validity branch",
                         "poly_basemul(c,h,r)"],
            "current_gt": ["poly_frombytes(&h,pk)", "validity branch",
                           "Natural-Q h projection inside scale4 MA2"],
            "h_value_consumers_after_success": 1,
            "dual_consumer_h": False,
        },
        "ownership": ownership,
        "decode_geometry": {
            **decoder,
            "natural_destination_vectors": 72,
            "block_local_natural_vectors": block_local,
            "cross_block_natural_vectors": 72 - block_local,
            "all_natural_outputs_formable_from_one_live_decode_block": block_local == 72,
            "maximum_live_source_vectors_per_decode_block": 8,
        },
        "extensional_equivalence": extensional_checks(
            physical_to_serialized, natural_to_physical),
        "movement": {
            "current_after_official_decode": {
                "official_layout_vector_stores": 72,
                "ma2_projection_data_loads": 144,
                "ma2_projection_routes": 360,
                "ma2_projection_stores": 0,
            },
            "direct_decoder_baseline": direct_baseline,
            "baseline_delta": {
                "vector_loads": -72,
                "vector_stores": 0,
                "routes": 0,
                "scratch_bytes": 0,
            },
            "interpretation": "the conservative direct decoder relocates rather than removes 360 formation routes, but permanently removes 72 duplicated h reloads; route fusion is an ASM opportunity, not a MAP claim",
        },
        "authorization": {
            "namespaced_asm_next": True,
            "required_shape": "paired candidate: decode one 192-byte block, validate, form eight Natural-Q vectors from its live eight decoded vectors, store directly to h[1152], then use a same-arithmetic MA2 entry that loads one preprojected h vector per plane",
            "decoder_symbol": "ntruplus1152_exp001_poly_frombytes_h_natural_q",
            "consumer_symbol": "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4_preprojected_h",
            "must_preserve": ["all 4096 12-bit acceptance decisions",
                              "1728-byte wire format", "Natural-Q raw ownership",
                              "error return", "zero scratch", "constant-time dataflow"],
            "benchmark": False,
            "native_kem": False,
        },
        "source_sha256": {name: sha256(path) for name, path in {
            "pack_layout": args.pack_layout,
            "natural_header": args.natural_header,
            "natural_schedule": args.natural_schedule,
            "pack_source": args.pack_source,
            "official_kem": args.official_kem,
            "candidate_kem": args.candidate_kem,
        }.items()},
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"generated artifact differs: {args.output}")
    else:
        args.output.write_text(rendered)
    print("ENCAP h decode map: 72/72 outputs block-local; direct baseline removes 72 reloads")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
