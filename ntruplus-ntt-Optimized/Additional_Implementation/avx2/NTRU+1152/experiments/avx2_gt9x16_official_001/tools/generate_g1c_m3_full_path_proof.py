#!/usr/bin/env python3
"""Prove or reject M3 repair placements under the BMScale i16 contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
I16 = [-32768, 32767]
INPUT = [-13824, 13824]


def signed16(value: int) -> int:
    value %= 1 << 16
    return value - (1 << 16) if value >= 1 << 15 else value


def montgomery_reduce(value: int) -> int:
    low = signed16(signed16(value) * QINV)
    return (value - low * Q) >> 16


def exact_montgomery_range(interval: list[int], constant: int) -> list[int]:
    values = (montgomery_reduce(value * constant)
              for value in range(interval[0], interval[1] + 1))
    first = next(values)
    low = high = first
    for value in values:
        low = min(low, value)
        high = max(high, value)
    return [low, high]


def fits(interval: list[int]) -> bool:
    return I16[0] <= interval[0] and interval[1] <= I16[1]


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def propagate(row: dict, repair_after_d1_large: bool) -> dict:
    lanes = [INPUT[:] for _ in range(16)]
    records = []
    first_failure = None
    for distance in (1, 2, 4, 8):
        stage = row["adjusted_ntt16_stages"][f"distance{distance}"]
        constants = [centered(pow(zeta, -1, Q) * R)
                     for zeta in stage["mod_q"]]
        output: list[list[int] | None] = [None] * 16
        operations = []
        for block, base in enumerate(range(0, 16, 2 * distance)):
            for within in range(distance):
                left_index = base + within
                right_index = left_index + distance
                left, right = lanes[left_index], lanes[right_index]
                total = [left[0] + right[0], left[1] + right[1]]
                difference = [left[0] - right[1], left[1] - right[0]]
                twisted = exact_montgomery_range(difference, constants[block])
                output[left_index] = total
                output[right_index] = twisted
                operations.append((left_index, right_index, total, difference))
                if first_failure is None:
                    for name, interval in (("sum", total),
                                           ("difference", difference)):
                        if not fits(interval):
                            first_failure = {
                                "distance": distance,
                                "operation": name,
                                "physical_lanes": [left_index, right_index],
                                "interval": interval,
                            }
                            break
        lanes = [interval for interval in output if interval is not None]
        repair = None
        if distance == 1 and repair_after_d1_large:
            before = [lanes[index][:] for index in range(0, 16, 2)]
            for index in range(0, 16, 2):
                lanes[index] = exact_montgomery_range(lanes[index], centered(R))
            repair = {
                "semantic_stream": "D1 large/sum outputs",
                "physical_lanes": list(range(0, 16, 2)),
                "before": before,
                "after": [lanes[index] for index in range(0, 16, 2)],
                "identity": "Mont(x,R mod q) = x mod q; the Montgomery exponent is preserved",
            }
        records.append({
            "distance": distance,
            "pre_montgomery_overall": [
                min(min(total[0], difference[0])
                    for _, _, total, difference in operations),
                max(max(total[1], difference[1])
                    for _, _, total, difference in operations),
            ],
            "register_state_overall": [
                min(interval[0] for interval in lanes),
                max(interval[1] for interval in lanes),
            ],
            "all_pre_montgomery_fit_i16": all(
                fits(total) and fits(difference)
                for _, _, total, difference in operations),
            "repair": repair,
        })
    return {
        "stages": records,
        "first_failure": first_failure,
        "signed_i16_proved": first_failure is None,
    }


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--m3c2p-proof", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    scaled = json.loads(args.scaled_oracle.read_text())
    prior = json.loads(args.m3c2p_proof.read_text())
    rows = scaled["paper_adjusted_ntt16_rows"]
    d4_only = [propagate(row, False) for row in rows]
    d1_large = [propagate(row, True) for row in rows]
    if not all(item["first_failure"]["distance"] == 2 for item in d4_only):
        raise SystemExit("D4-only rejection no longer occurs first at D2")
    if not all(item["signed_i16_proved"] for item in d1_large):
        raise SystemExit("D1-large repair no longer closes the full path")

    document = {
        "schema": "gt-g1c-m3-full-path-proof/v1",
        "checkpoint": "G1C-M3C1-full-path-repair-placement-proof",
        "contract": {
            "each_raw_BMScale_lane": INPUT,
            "lane_independence": True,
            "signed_machine_arithmetic": "every vpaddw/vpsubw input result must fit signed i16 before execution",
        },
        "method": (
            "Sound interval propagation for independent BMScale lanes; every "
            "Montgomery node is enumerated over every integer in its input "
            "interval, not approximated by a floating-point bound."
        ),
        "selected_D4_tail_plan": {
            "status": "rejected-before-fusion",
            "reason": "The path can overflow at D2 before reaching the selected D4 repair boundary.",
            "rows": d4_only,
            "first_failure_all_rows": {
                "distance": 2,
                "operation": "sum",
                "interval": [-55296, 55296],
            },
        },
        "proved_conservative_alternative": {
            "status": "range-and-scale-proved",
            "placement": "Montgomery-by-identity on the D1 large/sum stream before D2",
            "rows": d1_large,
            "maximum_absolute_pre_montgomery_by_stage": {
                str(distance): max(
                    max(abs(item["stages"][stage]["pre_montgomery_overall"][0]),
                        abs(item["stages"][stage]["pre_montgomery_overall"][1]))
                    for item in d1_large)
                for stage, distance in enumerate((1, 2, 4, 8))
            },
            "scale_identity": "Mont(x,R mod q) = x mod q",
        },
        "prior_local_D8_proof": {
            "status": prior["decision"]["M3C2_P"],
            "scope": "conditional on already-valid signed-i16 D4 operands",
        },
        "authorization": {
            "D4_tail_identity_fusion": False,
            "M3_C0_C1_C2_full_path_benchmark": False,
            "next_required": "implement and price the proved D1-large identity placement; do not fuse at D4",
        },
        "source_sha256": {
            "scaled_oracle": digest(args.scaled_oracle),
            "m3c2p_proof": digest(args.m3c2p_proof),
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated M3 full-path proof is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
