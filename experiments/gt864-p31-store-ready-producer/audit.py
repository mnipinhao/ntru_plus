#!/usr/bin/env python3
"""Reproduce the P29/P31 static instruction and routing audit."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def opcodes(path):
    counts = Counter()
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith((".", "#", "//")) or line.endswith(":"):
            continue
        line = line.split("//", 1)[0].strip()
        if line:
            counts[line.split()[0].lower()] += 1
    return counts


p28 = opcodes(ROOT / "experiments/gt864-p28s-timing/candidate-main.timing.S")
p29_route = opcodes(ROOT / "experiments/gt864-p29-direct-st3/candidate-main-route.alloc.S")
tail = opcodes(ROOT / "experiments/gt864-p29-direct-st3/candidate-tail.alloc.S")
pair2 = opcodes(HERE / "candidate-pair2.alloc.S")
pair1 = opcodes(HERE / "candidate-pair1.alloc.S")

p29 = p28 + p28 + p28 + p29_route + tail
p31 = p28 + pair2 + pair1 + tail
delta = {name: p31[name] - p29[name] for name in sorted(set(p29) | set(p31))
         if p31[name] != p29[name]}

result = {
    "status": "static_pass_timing_reject",
    "instruction_count": {
        "p29_runtime_kernel_sum": sum(p29.values()),
        "p31_runtime_kernel_sum": sum(p31.values()),
        "delta": sum(p31.values()) - sum(p29.values()),
        "p31_components": {
            "pair0_p28": sum(p28.values()),
            "pair2": sum(pair2.values()),
            "pair1": sum(pair1.values()),
            "tail_p29": sum(tail.values()),
        },
        "opcode_delta_p31_minus_p29": delta,
    },
    "memory_boundary": {
        "removed_q_load_instructions": 32,
        "removed_q_store_instructions": 32,
        "coefficient_scratch_bytes_removed": 1536,
        "retained_b2_high_d_store_instructions": 32,
        "retained_b2_high_d_load_instructions": 32,
        "full_vector_st3_4h": pair2["st3"] + pair1["st3"],
        "lane_st3": 0,
        "coefficient_spill": 0,
    },
    "object_text_bytes_pi5": {
        "pair0_p28": 3364,
        "pair2": 6000,
        "pair1": 4848,
        "tail_p29": 3136,
    },
    "slothy": {
        "root": "/Users/chenpinhao/slothy",
        "allow_spills": False,
        "allocation": "pass for both producers and all bounded windows",
        "timing_mode": "functional no-reordering allocation; measured final objects on Pi 5",
    },
}
(HERE / "static-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
