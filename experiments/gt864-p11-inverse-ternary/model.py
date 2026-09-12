#!/usr/bin/env python3
"""Exact P11 scratch coordinate, ternary arithmetic and cost model."""

import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
AUDIT = ROOT / "experiments/gt864-native-asm/inverse-p3b-producer-center/producer-layout-audit.json"


def oracle(x: int) -> int:
    centered = (x + 1728) % 3457 - 1728
    return (centered + 1) % 3 - 1


def candidate(x: int) -> int:
    high = -int(x > 1728)
    low = -int(x < -1728)
    adjusted = x + high - low
    quotient = (adjusted * 10923 + 16384) // 32768
    return adjusted - 3 * quotient


audit = json.loads(AUDIT.read_text())
main = audit["inverse16_lazy"]["groups"]
tail = audit["inverse_tail_lazy"]["groups"]

# The public wrapper adds component*2 + half*24 to x0 for main calls.
# Each source contributes four lanes.  P11 writes that D to scratch[half][k].
main_scratch = {}
for component in range(3):
    for half in range(2):
        for group in main:
            for chunk in (group[:4], group[4:]):
                start = chunk[0]["byte_offset"]
                assert [r["lane"] for r in chunk] == list(range(4))
                assert [r["byte_offset"] for r in chunk] == [start + 6 * i for i in range(4)]
                k = start // 54
                key = (component, half, k)
                assert key not in main_scratch
                main_scratch[key] = [
                    (r["byte_offset"] + 2 * component + 24 * half) // 2 for r in chunk
                ]

# Tail x0 is output+48.  Each source contributes the row-8 component triplet.
tail_scratch = {}
for group in tail:
    for chunk in (group[:3], group[3:]):
        start = chunk[0]["byte_offset"]
        assert [r["lane"] for r in chunk] == list(range(3))
        assert [r["byte_offset"] for r in chunk] == [start + 2 * i for i in range(3)]
        k = (48 + start) // 54
        assert k not in tail_scratch
        tail_scratch[k] = [(48 + r["byte_offset"]) // 2 for r in chunk]

assert len(main_scratch) == 3 * 2 * 32
assert len(tail_scratch) == 32

seen = []
for k in range(32):
    for row in range(8):
        half, lane = divmod(row, 4)
        for component in range(3):
            got = main_scratch[(component, half, k)][lane]
            want = 27 * k + 3 * row + component
            assert got == want, (k, row, component, got, want)
            seen.append(got)
    for component in range(3):
        got = tail_scratch[k][component]
        want = 27 * k + 24 + component
        assert got == want, (k, component, got, want)
        seen.append(got)

assert sorted(seen) == list(range(864))

for x in range(-4577, 4578):
    assert candidate(x) == oracle(x), x

report = {
    "status": "pass",
    "coordinate_map": {
        "coefficients": len(seen),
        "unique": len(set(seen)),
        "main_records": len(main_scratch),
        "tail_records": len(tail_scratch),
        "formula": "natural_index = 27*k + 3*row + component",
    },
    "range": {
        "exhaustive_inputs": 9155,
        "raw_bound": 4577,
        "adjusted_bound": 4576,
        "output": [-1, 0, 1],
    },
    "memory": {
        "scratch_bytes": 1792,
        "added_coefficient_passes": 0,
        "main_store": "192 STR D across six calls",
        "tail_store": "32 STR D",
        "route": "32 full ST3 plus row8 STR S/ST1 H",
    },
    "instruction_ledger": {
        "baseline_umov_strh": 1728,
        "candidate_producer_str_d": 224,
        "baseline_p8_body": 864,
        "candidate_route_body": 1216,
        "delta_before_loop_scaffolding": -1152,
    },
}
(P / "proof.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
