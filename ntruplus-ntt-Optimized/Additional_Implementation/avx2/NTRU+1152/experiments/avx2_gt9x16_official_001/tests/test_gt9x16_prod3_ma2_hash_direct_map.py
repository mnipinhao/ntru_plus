#!/usr/bin/env python3
"""Independent invariants for the PROD3 MA2-to-hash-byte static map."""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "generated/gt9x16-prod3-ma2-hash-direct-map.json"
Q = 3457


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - 65536 if value >= 32768 else value


def mulhi(left: int, right: int) -> int:
    return (signed16(left) * signed16(right)) >> 16


def remove_scale4(value: int) -> int:
    low = signed16(value * 16379)
    high = mulhi(value, -901)
    result = signed16(high - mulhi(low, Q))
    return result + Q if result < 0 else result


def pack12(values: list[int]) -> bytes:
    result = bytearray()
    for index in range(0, len(values), 2):
        low, high = values[index:index + 2]
        result.extend((low & 255, (low >> 8) | ((high & 15) << 4), high >> 4))
    return bytes(result)


def main() -> int:
    document = json.loads(MAP.read_text())
    assert document["schema"] == "gt9x16-prod3-ma2-hash-direct-map/v1"
    coefficients = document["coefficient_map"]
    pairs = document["pair_map"]
    vectors = document["packing_oriented_vectors"]
    assert len(coefficients) == 1152
    assert [cell["official_coefficient"] for cell in coefficients] == list(range(1152))
    assert len({(cell["ma2"]["vector"], cell["ma2"]["lane"])
                for cell in coefficients}) == 1152
    assert len(pairs) == 576 and not any(pair["same_ma2_vector"] for pair in pairs)
    assert sum(pair["same_128bit_half"] for pair in pairs) == 0
    assert vectors == []

    byte_bits = {(byte, bit): [] for byte in range(1728) for bit in range(8)}
    for cell in coefficients:
        coefficient = cell["official_coefficient"]
        for contribution in cell["serializer"]["byte_contributions"]:
            coefficient_low, coefficient_high = contribution["coefficient_bits"]
            byte_low, byte_high = contribution["byte_bits"]
            assert coefficient_high - coefficient_low == byte_high - byte_low
            for offset in range(byte_high - byte_low + 1):
                byte_bits[(contribution["byte_index"], byte_low + offset)].append(
                    (coefficient, coefficient_low + offset))
    assert all(len(owners) == 1 for owners in byte_bits.values())

    by_ma2 = {(cell["ma2"]["vector"], cell["ma2"]["lane"]): cell
              for cell in coefficients}
    rng = random.Random(0xD1EC7)
    for _ in range(257):
        planes = [0] * 1152
        for (vector, lane), cell in by_ma2.items():
            low, high = cell["input_range_i16"]
            planes[16 * vector + lane] = rng.randint(low, high)
        serialized = [0] * 1152
        for (vector, lane), cell in by_ma2.items():
            serialized[cell["serializer"]["serialized_coefficient"]] = remove_scale4(
                planes[16 * vector + lane])
        control = pack12(serialized)
        direct = bytearray(1728)
        for pair in pairs:
            low_pos = pair["low"]
            high_pos = pair["high"]
            low = remove_scale4(planes[16 * low_pos["ma2_vector"] + low_pos["ma2_lane"]])
            high = remove_scale4(planes[16 * high_pos["ma2_vector"] + high_pos["ma2_lane"]])
            offset = pair["output_bytes"][0]
            direct[offset:offset + 3] = bytes(
                (low & 255, (low >> 8) | ((high & 15) << 4), high >> 4))
        assert bytes(direct) == control

    proof = document["scale_and_range_proof"]
    assert proof["post_inv4_range_i16"] == [-1998, 1998]
    assert proof["canonical_range"] == [0, 3456]
    assert proof["direct_sign_add_q_matches_official_pack"]
    assert proof["pack12_safe"]
    assert document["movement_ledger"]["H0-current"]["intermediate_stores"] == 216
    assert document["movement_ledger"]["H1-direct-official-block"]["intermediate_stores"] == 0
    assert document["movement_ledger"]["H2-packing-oriented"]["ma2_initial_loads_lower_bound"] is None
    assert not document["decision"]["direct_serializer_asm_authorized"]
    assert not document["decision"]["benchmark_authorized"]

    sources = document["source_sha256"]
    source_paths = {
        "prod2_map": ROOT / "generated/f0-prod2-ma2-map.json",
        "consumer_map": ROOT / "generated/f0-ma-consumer-map.json",
        "ma0_contract": ROOT / "generated/f0-ma0-adapter.json",
        "pinned_pack_s": ROOT / "upstream/supercop-avx2/pack.s",
        "pinned_pack_layout": ROOT / "generated/official-pack-layout.json",
    }
    for name, path in source_paths.items():
        assert sources[name] == hashlib.sha256(path.read_bytes()).hexdigest()

    print("PROD3 MA2 hash direct map: ownership, range, byte coverage, and 257 differentials passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
