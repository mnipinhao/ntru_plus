#!/usr/bin/env python3
"""Replay the serializer V2 ownership and 12-bit byte contract."""

from __future__ import annotations

import importlib.util
import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_generator():
    path = ROOT / "tools/generate_scale1_r_serializer_v2_packet_map.py"
    spec = importlib.util.spec_from_file_location("serializer_v2_map", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pack12(coefficients: list[int]) -> bytes:
    out = bytearray()
    for low, high in zip(coefficients[0::2], coefficients[1::2]):
        out += bytes((low & 255, ((low >> 8) | (high << 4)) & 255,
                      (high >> 4) & 255))
    return bytes(out)


def main() -> int:
    generator = load_generator()
    machine = json.loads((ROOT / "generated/wire-monotone-machine-wire-layout.json").read_text())
    record = json.loads((ROOT / "generated/scale1-r-serializer-v2-packet-map.json").read_text())
    assert len(record["packets"]) == 9
    assert record["instruction_budget"]["candidate_minus_current_full"] == -144
    assert record["liveness"]["expected_peak_ymm"] == 14
    assert sum(packet["crosses_gt_branch"] for packet in record["packets"]) == 1

    source_to_wire = machine["source_to_wire"]
    rng = random.Random(0x5356325041434B45)
    for trial in range(1003):
        wire = ([0] * 1152 if trial == 0 else
                [4095] * 1152 if trial == 1 else
                [rng.randrange(3457) for _ in range(1152)])
        state = [0] * 1152
        for source, wire_index in enumerate(source_to_wire):
            state[source] = wire[wire_index]
        actual = bytearray()
        for packet in record["packets"]:
            low_quartet, high_quartet = packet["tile_state_vectors"]
            low = [state[16 * vector:16 * vector + 16] for vector in low_quartet]
            high = [state[16 * vector:16 * vector + 16] for vector in high_quartet]
            vectors = generator.official_inputs(low, high)
            coefficients = [vectors[register][lane]
                            for lane in range(16) for register in range(8)]
            lo, hi = packet["wire_coefficients"]
            assert coefficients == wire[lo:hi + 1]
            actual += pack12(coefficients)
        assert actual == pack12(wire)
    print("scale-1 serializer V2 packet map: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
