#!/usr/bin/env python3
"""Enumerate and gate pure-permutation GT864 transform-domain tile ABIs."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


Q = 3457
THETA = 9                 # order 864, THETA^144 = alpha
ETA = pow(THETA, 96, Q)   # order 9
ALPHA = (-722) % Q
BETA = (1 - (-722)) % Q
ROWS = 9
COLUMNS = 16
LANES = 8
COMPONENTS = 3
TOPS = ("alpha", "beta")

P9_NATURAL = tuple(range(ROWS))
P9_ORIENTED = (0, 3, 6, 1, 4, 7, 8, 2, 5)
P16_NATURAL = tuple(range(COLUMNS))
P16_BIT_REVERSED = (0, 8, 4, 12, 2, 10, 6, 14,
                    1, 9, 5, 13, 3, 11, 7, 15)


@dataclass(frozen=True)
class Leaf:
    top: str
    row: int
    column: int


@dataclass(frozen=True)
class Candidate:
    name: str
    family: str
    groups: tuple[tuple[Leaf, ...], ...]
    ntt9_vector_mode: str
    bridge_shape: str
    output_routing: str
    tail_policy: str
    disposition: str


def logical_root(leaf: Leaf) -> int:
    residue = 1 if leaf.top == "alpha" else 5
    exponent = residue + 6 * leaf.column + 96 * leaf.row
    root = pow(THETA, exponent, Q)
    assert pow(root, 144, Q) == (ALPHA if leaf.top == "alpha" else BETA)
    return root


def fixed_row(name: str, p9: tuple[int, ...], p16: tuple[int, ...]) -> Candidate:
    groups = []
    for top in TOPS:
        for row in p9:
            for block in range(2):
                groups.append(tuple(
                    Leaf(top, row, column)
                    for column in p16[block * LANES:(block + 1) * LANES]
                ))
    return Candidate(
        name=name,
        family="fixed_row_column_batch",
        groups=tuple(groups),
        ntt9_vector_mode="across_registers_eight_columns_in_parallel",
        bridge_shape="two_8x8_main_tiles_plus_two_s8_vectors_per_top_component",
        output_routing="none; one output register is one physical tile component",
        tail_policy="s8 is the ninth input register, not an output-lane tail",
        disposition="retain_primary",
    )


def mixed_rotation(p9: tuple[int, ...], p16: tuple[int, ...]) -> Candidate:
    # This example exercises the full family.  A real a_c is selected only
    # after column-specific twist-table costs are known.
    rotations = tuple(column % ROWS for column in range(COLUMNS))
    groups = []
    for top in TOPS:
        for physical_row in p9:
            for block in range(2):
                groups.append(tuple(
                    Leaf(top, (physical_row + rotations[column]) % ROWS, column)
                    for column in p16[block * LANES:(block + 1) * LANES]
                ))
    return Candidate(
        name="mixed_lane_row_rotation_oriented_p16",
        family="lane_dependent_row_rotation",
        groups=tuple(groups),
        ntt9_vector_mode="across_registers_eight_columns_in_parallel",
        bridge_shape="same_as_fixed_row",
        output_routing="none if lambda_c is represented as lambda_c*eta^a_c",
        tail_policy="same_as_fixed_row",
        disposition="retain_conditional_on_twist_table_cost",
    )


def fixed_column() -> Candidate:
    groups = []
    for top in TOPS:
        for column in P16_NATURAL:
            groups.append(tuple(Leaf(top, row, column) for row in range(8)))
        for block in range(2):
            groups.append(tuple(
                Leaf(top, 8, column)
                for column in range(block * LANES, (block + 1) * LANES)
            ))
    return Candidate(
        name="fixed_column_with_row8_tail_tiles",
        family="fixed_column_row_lanes",
        groups=tuple(groups),
        ntt9_vector_mode="within_lanes_one_column_per_transform",
        bridge_shape="main R_c lanes already present after NTT16",
        output_routing="cross-lane radix3 routing plus row8 extraction",
        tail_policy="sixteen row8 scalars must be repacked into two BaseMul tiles",
        disposition="retain_secondary_requires_within_lane_ntt9_cost",
    )


def column_stream() -> Candidate:
    groups = []
    for top in TOPS:
        stream = [Leaf(top, row, column)
                  for column in P16_BIT_REVERSED
                  for row in P9_ORIENTED]
        groups.extend(tuple(stream[start:start + LANES])
                      for start in range(0, len(stream), LANES))
    return Candidate(
        name="oriented_column_stream_chunk8",
        family="mixed_column_stream",
        groups=tuple(groups),
        ntt9_vector_mode="within_lanes_or_scalar_column_stream",
        bridge_shape="no stable eight-column batch invariant",
        output_routing="nine-output column streams cross every eight-leaf tile boundary",
        tail_policy="implicit in stream, but forces cross-column tile assembly",
        disposition="reject_before_serializer_microbench",
    )


def validate(candidate: Candidate) -> tuple[str, str]:
    assert len(candidate.groups) == 36
    assert all(len(group) == LANES for group in candidate.groups)

    flat = [leaf for group in candidate.groups for leaf in group]
    expected = {Leaf(top, row, column)
                for top in TOPS
                for row in range(ROWS)
                for column in range(COLUMNS)}
    assert len(flat) == 288
    assert set(flat) == expected
    assert len(set(flat)) == 288

    # The three coefficient planes use the identical leaf map and differ only
    # by the SoA component offset inside each 24-coefficient tile.
    component_slots = set()
    for group, leaves in enumerate(candidate.groups):
        for lane, leaf in enumerate(leaves):
            for component in range(COMPONENTS):
                offset = 24 * group + 8 * component + lane
                component_slots.add((offset, leaf, component))
    assert len(component_slots) == 864
    assert {slot[0] for slot in component_slots} == set(range(864))

    roots = [logical_root(leaf) for leaf in flat]
    assert len(set(roots)) == 288

    # A pure permutation has a total inverse map.  BaseMul consumes the root in
    # the same group/lane, so no phase or arithmetic claim is hidden here.
    inverse = {leaf: physical for physical, leaf in enumerate(flat)}
    assert all(flat[inverse[leaf]] == leaf for leaf in expected)

    mapping = "\n".join(
        f"{physical},{leaf.top},{leaf.row},{leaf.column},{roots[physical]}"
        for physical, leaf in enumerate(flat)
    )
    zetas = ",".join(str(root) for root in roots)
    return (
        hashlib.sha256(mapping.encode("ascii")).hexdigest(),
        hashlib.sha256(zetas.encode("ascii")).hexdigest(),
    )


def main() -> None:
    assert pow(THETA, 864, Q) == 1
    assert pow(THETA, 432, Q) != 1
    assert pow(THETA, 288, Q) != 1
    assert pow(THETA, 144, Q) == ALPHA
    assert pow(ETA, 9, Q) == 1 and ETA != 1

    candidates = (
        fixed_row("fixed_row_natural", P9_NATURAL, P16_NATURAL),
        fixed_row("fixed_row_oriented_p16", P9_ORIENTED, P16_BIT_REVERSED),
        mixed_rotation(P9_ORIENTED, P16_BIT_REVERSED),
        fixed_column(),
        column_stream(),
    )

    print("gt864_transform_domain_tile_abi_search=pass")
    print(f"candidate_count={len(candidates)}")
    for candidate in candidates:
        mapping_hash, zeta_hash = validate(candidate)
        print(
            "candidate,"
            f"name={candidate.name},"
            f"family={candidate.family},"
            f"ntt9={candidate.ntt9_vector_mode},"
            f"routing={candidate.output_routing},"
            f"tail={candidate.tail_policy},"
            f"decision={candidate.disposition},"
            f"mapping_sha256={mapping_hash},"
            f"zeta_sha256={zeta_hash}"
        )
    print("shortlist=fixed_row_column_batch,lane_dependent_row_rotation,"
          "fixed_column_row_lanes")
    print("phase_claim=none; all candidates are pure leaf permutations")
    print("serializer_claim=none; structural obligations only")
    print("production_linked=0")


if __name__ == "__main__":
    main()
