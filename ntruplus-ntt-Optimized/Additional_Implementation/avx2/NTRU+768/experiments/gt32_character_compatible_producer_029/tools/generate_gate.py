#!/usr/bin/env python3
"""Gate zero-new-chain producer scaling against the exact DFT3 characters."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "avx2_gt16_quadratic_official_001"
HEADER = SOURCE / "generated" / "quadratic-constants.h"
Q = 3457
R = (1 << 16) % Q
RINV = pow(R, -1, Q)
HIGH = {2, 3, 6, 7, 10, 11, 14, 15}
BRV3 = (0, 4, 2, 6, 1, 5, 3, 7)


def center(x: int) -> int:
    x %= Q
    return x-Q if x > Q//2 else x


def inv(x: int) -> int:
    return pow(x % Q, -1, Q)


def table(text: str, pattern: str, count: int) -> list[int]:
    match = re.search(pattern + r".*?= \{(.*?)\n\};", text, re.S)
    if not match:
        raise RuntimeError(pattern)
    values = [int(x) for x in re.findall(r"-?\d+", match.group(1))]
    if len(values) != count:
        raise RuntimeError((pattern, len(values), count))
    return values


def propagate(scales: list[list[int]]) -> list[list[int]]:
    after = [[0]*16 for _ in range(48)]
    for k3 in range(3):
        for position, k16 in enumerate(BRV3):
            low = 16*k3+k16
            for destination in (16*k3+2*position, 16*k3+2*position+1):
                after[destination] = scales[low][:]
    scales = after
    for length in (4, 8, 16):
        half = length//2
        after = [row[:] for row in scales]
        for k3 in range(3):
            for start in range(0, 16, length):
                for index in range(half):
                    low = 16*k3+start+index
                    high = low+half
                    after[low] = scales[low][:]
                    after[high] = scales[low][:]
        scales = after
    return scales


def normalized(values: tuple[int, int, int]) -> tuple[int, int, int]:
    common = inv(values[0])
    return tuple(x*common % Q for x in values)


def main() -> None:
    text = HEADER.read_text()
    flat = table(text, r"round4c_merge_mont\[48\]\[16\]", 48*16)
    weights = [[center(flat[16*v+j]*RINV) for j in range(16)]
               for v in range(48)]
    terminal_weight = propagate(weights)
    roots = sorted(x for x in range(1, Q)
                   if pow(x, 3, Q) == 1 and x != 1)
    characters = {(1, 1, 1), (1, roots[0], roots[1]),
                  (1, roots[1], roots[0])}
    classes = []
    seen = set()
    for lane in sorted(HIGH):
        w = tuple(terminal_weight[16*k][lane] % Q for k in range(3))
        if w in seen:
            continue
        seen.add(w)
        w_norm = normalized(w)
        # A diagonal producer relabel alpha scales p and m together.  Hence
        # the sum lane sees alpha and the difference lane sees alpha/w.
        # Both are DFT3 characters iff w itself is a character (characters
        # form a group under component-wise multiplication/division).
        classes.append({
            "lanes": [x for x in sorted(HIGH)
                      if tuple(terminal_weight[16*k][x] % Q
                               for k in range(3)) == w],
            "terminal_merge_weight": [center(x) for x in w],
            "normalized_merge_weight": [center(x) for x in w_norm],
            "merge_weight_is_character": w_norm in characters,
            "zero_chain_diagonal_producer_solution_exists": w_norm in characters,
        })
    complete_solution = all(item["merge_weight_is_character"] for item in classes)
    assert not complete_solution
    result = {
        "experiment": "GT32-CHARACTER-COMPATIBLE-PRODUCER-029",
        "required_conditions": {
            "sum_ratio": "alpha must be a DFT3 character",
            "difference_ratio": "alpha / merge_weight must be a DFT3 character",
            "equivalent_test": "merge_weight must itself be a DFT3 character",
        },
        "classes": classes,
        "all_lane_classes_have_zero_chain_solution": complete_solution,
        "producer_provenance": {
            "Forward": {
                "existing_constant_chain": "round4c_forward_preweight_mont",
                "constant_relabel_possible": True,
                "result": "fails_simultaneous_sum_and_difference_character_condition",
            },
            "Decode": {
                "existing_constant_chain": None,
                "constant_relabel_possible": False,
                "result": "nontrivial_alpha_requires_new_runtime_or_prepared_work",
            },
            "BaseInv": {
                "existing_output_scaling_may_be_foldable": True,
                "result": "same_diagonal_scaling_obstruction_as_Forward",
            },
            "prepared_key": {
                "result": "separate_time_memory_API_not_zero_cost_standard_KEM_producer",
            },
        },
        "decision": {
            "status": "static_stop_zero_new_chain_diagonal_producer_character_family",
            "assembly_eligible": False,
            "reason": (
                "Not every terminal merge-weight class is a DFT3 character. A free "
                "diagonal producer relabel scales both bilinear products and "
                "therefore cannot make both the sum and weighted-difference "
                "coordinates character-compatible. Selective difference-only "
                "scaling requires the rank-two output mix already proved by 026A."
            ),
            "open": [
                "non_diagonal_coupled_producer_that_deletes_an_operation_class",
                "prepared_key_time_memory_representation",
                "new_producer_with_an_existing_selective_difference_chain",
            ],
        },
    }
    out = ROOT / "generated" / "producer_character_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(out)


if __name__ == "__main__":
    main()
