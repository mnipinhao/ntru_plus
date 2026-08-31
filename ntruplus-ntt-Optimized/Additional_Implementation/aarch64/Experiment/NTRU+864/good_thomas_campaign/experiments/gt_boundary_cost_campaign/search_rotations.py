#!/usr/bin/env python3
"""M4.3 whole-vector-bundle search for conditional FR row rotations."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass

Q = 3457
THETA = 9
ETA = pow(THETA, 96, Q)
R = (1 << 16) % Q
ROWS = 9
COLUMNS = 16
TOP_RESIDUES = (1, 5)
FR_TRANSFORMS = 2 * 3 * 2  # top * degree-three component * column block
TWIST_MULMODS_PER_TRANSFORM = 8


@dataclass(frozen=True)
class Score:
    unique_bundles: int
    unique_up_to_sign: int
    exact_table_bytes: int
    signed_table_bytes: int
    vector_mulmods: int
    vector_constant_loads: int
    max_live_twist_vectors: int
    distinct_rotations: int


@dataclass(frozen=True)
class Candidate:
    name: str
    family: str
    rotations: tuple[int, ...]
    score: Score
    map_sha256: str
    constants_sha256: str


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def exponent_bundles(rotations: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    bundles = []
    for residue in TOP_RESIDUES:
        for block in range(2):
            effective = tuple(
                (residue + 6 * column + 96 * rotations[column]) % 864
                for column in range(block * 8, block * 8 + 8)
            )
            for power in range(1, 9):
                bundles.append(tuple((power * exponent) % 864
                                     for exponent in effective))
    return tuple(bundles)


def score(rotations: tuple[int, ...]) -> Score:
    bundles = exponent_bundles(rotations)
    signed_classes = {
        min(bundle, tuple((exponent + 432) % 864 for exponent in bundle))
        for bundle in bundles
    }
    return Score(
        unique_bundles=len(set(bundles)),
        unique_up_to_sign=len(signed_classes),
        exact_table_bytes=16 * len(set(bundles)),
        signed_table_bytes=16 * len(signed_classes),
        # Fixed by M4.4: rotation changes lambda constants, not the skeleton.
        vector_mulmods=FR_TRANSFORMS * TWIST_MULMODS_PER_TRANSFORM,
        vector_constant_loads=FR_TRANSFORMS * TWIST_MULMODS_PER_TRANSFORM,
        max_live_twist_vectors=1,
        distinct_rotations=len(set(rotations)),
    )


def validate_map(rotations: tuple[int, ...]) -> tuple[str, str]:
    physical_map = []
    constants = []
    for top, residue in enumerate(TOP_RESIDUES):
        for column in range(COLUMNS):
            rotation = rotations[column]
            lam = pow(THETA, residue + 6 * column, Q)
            effective_lam = lam * pow(ETA, rotation, Q) % Q
            before = {lam * pow(ETA, row, Q) % Q for row in range(ROWS)}
            after = {
                effective_lam * pow(ETA, physical, Q) % Q
                for physical in range(ROWS)
            }
            assert before == after
            for physical in range(ROWS):
                logical = (physical + rotation) % ROWS
                actual_root = effective_lam * pow(ETA, physical, Q) % Q
                expected_root = lam * pow(ETA, logical, Q) % Q
                assert actual_root == expected_root
                physical_map.append((top, physical, column, logical,
                                     actual_root))
            for power in range(1, ROWS):
                constants.append(centered(pow(effective_lam, power, Q) * R))
    map_text = "\n".join(",".join(map(str, row)) for row in physical_map)
    constant_text = ",".join(map(str, constants))
    return (
        hashlib.sha256(map_text.encode("ascii")).hexdigest(),
        hashlib.sha256(constant_text.encode("ascii")).hexdigest(),
    )


def make_candidate(name: str, family: str,
                   rotations: tuple[int, ...]) -> Candidate:
    map_hash, constant_hash = validate_map(rotations)
    return Candidate(name, family, rotations, score(rotations), map_hash,
                     constant_hash)


def main() -> None:
    assert pow(THETA, 864, Q) == 1
    assert pow(THETA, 432, Q) != 1
    assert pow(THETA, 144, Q) == (-722) % Q
    assert pow(ETA, 9, Q) == 1 and ETA != 1

    controls = [
        make_candidate("FR-0", "fixed_row", (0,) * COLUMNS),
        *(
            make_candidate(f"FR-global-{amount}", "global_rotation",
                           (amount,) * COLUMNS)
            for amount in range(1, ROWS)
        ),
    ]

    # Deterministic exploratory search.  Cost is evaluated on complete 8-lane
    # bundles; no scalar-constant count is used as a proxy.
    rng = random.Random(0x864)
    seeds = {
        tuple(column % ROWS for column in range(COLUMNS)),
        (0, 1, 2, 1, 2, 1, 1, 0, 1, 2, 0, 2, 0, 2, 2, 1),
    }
    for _ in range(100_000):
        seeds.add(tuple(rng.randrange(ROWS) for _ in range(COLUMNS)))
    # Hash/map validation is intentionally deferred until after ranking; doing
    # it for every random sample would make the campaign gate unnecessarily
    # slow without changing the cost search.
    ranked = sorted(
        ((score(rotations), rotations) for rotations in seeds),
        key=lambda item: (
            item[0].unique_bundles,
            item[0].unique_up_to_sign,
            item[0].distinct_rotations,
            item[1],
        ),
    )
    top_lane = [
        make_candidate(f"FR-lane-{index}", "lane_rotation", rotations)
        for index, (_, rotations) in enumerate(ranked[:8])
    ]
    payload = {
        "schema": 1,
        "fixed_skeleton": {
            "twist_vector_mulmods": FR_TRANSFORMS * 8,
            "twist_vector_loads": FR_TRANSFORMS * 8,
            "rotation_realization": "lambda_c_to_lambda_c_times_eta_pow_a_c",
            "output_map": "logical_row=(physical_row+a_c)_mod_9",
            "separate_permutation_stage": False,
        },
        "controls": [asdict(candidate) for candidate in controls],
        "top_lane_candidates": [asdict(candidate) for candidate in top_lane],
        "search_samples": len(seeds),
        "production_linked": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
