#!/usr/bin/env python3
"""Search an Encap-specific M' leaf order with a uniform Q24 microkernel."""

from __future__ import annotations

import argparse
import csv
import io
import itertools
import json
import random
from functools import lru_cache
from pathlib import Path


QPERMS = tuple(itertools.permutations(range(4)))
IDENTITY = tuple(range(16))
CURRENT_PSHUFB_WORDS = (0, 4, 1, 5, 2, 6, 3, 7,
                         8, 12, 9, 13, 10, 14, 11, 15)


def unpack_dwords(a: list, b: list, high: bool) -> list:
    result = []
    for half in (0, 8):
        start = half + (4 if high else 0)
        result += a[start:start + 2] + b[start:start + 2]
        result += a[start + 2:start + 4] + b[start + 2:start + 4]
    return result


def unpack_qwords(a: list, b: list, high: bool) -> list:
    result = []
    for half in (0, 8):
        start = half + (4 if high else 0)
        result += a[start:start + 4] + b[start:start + 4]
    return result


def transpose4(vectors: list[list]) -> list[list]:
    s0, s1, s2, s3 = vectors
    # Same 16-bit 4x16 transpose used by the selected Q24 body.
    def unpack_words(a: list, b: list, high: bool) -> list:
        result = []
        for half in (0, 8):
            start = half + (4 if high else 0)
            for index in range(start, start + 4):
                result += (a[index], b[index])
        return result
    t0, t1 = unpack_words(s0, s1, False), unpack_words(s0, s1, True)
    t2, t3 = unpack_words(s2, s3, False), unpack_words(s2, s3, True)
    a0, a1 = unpack_dwords(t0, t2, False), unpack_dwords(t0, t2, True)
    a2, a3 = unpack_dwords(t1, t3, False), unpack_dwords(t1, t3, True)
    return [unpack_qwords(a0, a2, False), unpack_qwords(a0, a2, True),
            unpack_qwords(a1, a3, False), unpack_qwords(a1, a3, True)]


def apply_qperm(words: list, permutation: tuple[int, ...]) -> list:
    result = []
    for source in permutation:
        result += words[4 * source:4 * source + 4]
    return result


def qperm_immediate(permutation: tuple[int, ...]) -> int:
    return sum(source << (2 * destination)
               for destination, source in enumerate(permutation))


def load_groups(mapping_csv: Path) -> list[list[tuple[int, int]]]:
    rows = list(csv.DictReader(mapping_csv.open()))
    groups = []
    for group in range(12):
        selected = sorted((row for row in rows
                           if int(row["packet"]) // 4 == group),
                          key=lambda row: int(row["target_coefficient"]))
        if len(selected) != 64:
            raise ValueError("mapping CSV does not contain twelve 64-word groups")
        groups.append([(int(row["degree"]), int(row["lane"]))
                       for row in selected])
    return groups


def load_group_metadata(mapping_json: Path) -> tuple[list[dict], list[tuple]]:
    document = json.loads(mapping_json.read_text())
    groups = document["groups"]
    seeds = []
    for group in groups:
        output_order = tuple(packet["transpose_output"]
                             for packet in group["packets"])
        qperms = tuple(tuple((packet["vpermq_imm"] >> (2 * lane)) & 3
                             for lane in range(4))
                       for packet in group["packets"])
        seeds.append((output_order, *qperms))
    return groups, seeds


def template_mapping(parameters: tuple) -> tuple[tuple[int, int], ...]:
    vectors = [[(degree, lane) for lane in range(16)] for degree in range(4)]
    outputs = transpose4(vectors)
    output_order = parameters[0]
    qperms = parameters[1:]
    result = []
    for packet in range(4):
        result += apply_qperm(outputs[output_order[packet]], qperms[packet])
    return tuple(result)


def required_lane_permutation(template: tuple[tuple[int, int], ...],
                              target: list[tuple[int, int]]) -> tuple[int, ...]:
    permutation: list[int | None] = [None] * 16
    for source, wanted in zip(template, target):
        degree, new_lane = source
        wanted_degree, old_lane = wanted
        if degree != wanted_degree:
            raise ValueError("template changes coefficient degree")
        if permutation[new_lane] not in (None, old_lane):
            raise ValueError("template is not a leaf bijection")
        permutation[new_lane] = old_lane
    if any(value is None for value in permutation):
        raise ValueError("incomplete lane permutation")
    return tuple(int(value) for value in permutation)


def deposit_network(vectors: list[list]) -> list[list]:
    r4 = unpack_dwords(vectors[0], vectors[2], False)
    r5 = unpack_dwords(vectors[0], vectors[2], True)
    r6 = unpack_dwords(vectors[1], vectors[3], False)
    r7 = unpack_dwords(vectors[1], vectors[3], True)
    return [unpack_qwords(r4, r6, False), unpack_qwords(r4, r6, True),
            unpack_qwords(r5, r7, False), unpack_qwords(r5, r7, True)]


INPUTS = [[(register, lane) for lane in range(16)] for register in range(4)]
CURRENT_POST_SHUFFLE = [[vector[lane] for lane in CURRENT_PSHUFB_WORDS]
                        for vector in INPUTS]
CURRENT_DEPOSIT_OUTPUT = deposit_network(CURRENT_POST_SHUFFLE)
DEPOSIT_ROUTE = deposit_network(INPUTS)


def mask_absorbable(permutation: tuple[int, ...]) -> bool:
    """Can block-specific pshufb masks realize M' at unchanged instruction count?"""
    target = [[CURRENT_DEPOSIT_OUTPUT[degree][permutation[lane]]
               for lane in range(16)] for degree in range(4)]
    required: list[list[tuple[int, int] | None]] = [[None] * 16 for _ in range(4)]
    for degree in range(4):
        for lane in range(16):
            register, slot = DEPOSIT_ROUTE[degree][lane]
            required[register][slot] = target[degree][lane]
    return all(required[register][lane] is not None
               and required[register][lane][0] == register
               and required[register][lane][1] // 8 == lane // 8
               for register in range(4) for lane in range(16))


def one_vpshufb(permutation: tuple[int, ...]) -> bool:
    return all(source // 8 == destination // 8
               for destination, source in enumerate(permutation))


def one_vpermq(permutation: tuple[int, ...]) -> bool:
    return (all(permutation[lane] % 4 == lane % 4 for lane in range(16))
            and all(len({permutation[4 * qword + offset] // 4
                         for offset in range(4)}) == 1 for qword in range(4))
            and len({permutation[4 * qword] // 4 for qword in range(4)}) == 4)


def one_vpermd(permutation: tuple[int, ...]) -> bool:
    return (all(permutation[2 * dword + 1] == permutation[2 * dword] + 1
                and permutation[2 * dword] % 2 == 0 for dword in range(8))
            and len({permutation[2 * dword] // 2 for dword in range(8)}) == 8)


def two_qperm_pshufb(permutation: tuple[int, ...]) -> bool:
    for qperm in QPERMS:
        inverse = {4 * qperm[qword] + offset: 4 * qword + offset
                   for qword in range(4) for offset in range(4)}
        if all(inverse[permutation[lane]] // 8 == lane // 8
               for lane in range(16)):
            return True
        if all(permutation[4 * qword + offset] // 8 == qperm[qword] // 2
               for qword in range(4) for offset in range(4)):
            return True
    return False


@lru_cache(maxsize=None)
def route_class(permutation: tuple[int, ...]) -> tuple[int, str]:
    if mask_absorbable(permutation):
        return 0, "existing-deposit-mask-relabel"
    if one_vpshufb(permutation):
        return 1, "one-vpshufb-after-deposit"
    if one_vpermq(permutation):
        return 1, "one-vpermq-after-deposit"
    if one_vpermd(permutation):
        return 1, "one-vpermd-after-deposit"
    if two_qperm_pshufb(permutation):
        return 2, "two-op-qperm-pshufb-family"
    return 3, "outside-modeled-two-op-one-source-family"


def evaluate(parameters: tuple, groups: list[list[tuple[int, int]]]) -> tuple:
    template = template_mapping(parameters)
    permutations = [required_lane_permutation(template, group) for group in groups]
    classes = [route_class(permutation) for permutation in permutations]
    costs = [item[0] for item in classes]
    # The first fields drive search; trailing data makes equal minima stable.
    score = (sum(costs), max(costs), sum(cost != 0 for cost in costs),
             len(set(permutations)))
    return score, permutations, classes


def coordinate_descent(start: tuple, groups: list[list[tuple[int, int]]]) -> tuple:
    current = start
    current_score = evaluate(current, groups)[0]
    changed = True
    while changed:
        changed = False
        for coordinate in range(5):
            best, best_score = current, current_score
            for choice in QPERMS:
                proposal = list(current)
                proposal[coordinate] = choice
                proposal_tuple = tuple(proposal)
                score = evaluate(proposal_tuple, groups)[0]
                if (score, proposal_tuple) < (best_score, best):
                    best, best_score = proposal_tuple, score
            if best != current:
                current, current_score = best, best_score
                changed = True
    return current


def search(groups: list[list[tuple[int, int]]], seeds: list[tuple],
           random_starts: int) -> list[tuple]:
    rng = random.Random(0x0704D505249)
    starts = list(seeds)
    for _ in range(random_starts):
        starts.append(tuple(rng.choice(QPERMS) for _ in range(5)))
    minima = {coordinate_descent(start, groups) for start in starts}
    return sorted(minima, key=lambda item: (evaluate(item, groups)[0], item))


def render_rows(best: tuple, groups: list[list[tuple[int, int]]],
                metadata: list[dict]) -> tuple[list[dict], list[dict]]:
    _, permutations, classes = evaluate(best, groups)
    block_rows = []
    lane_rows = []
    for new_block, (old_group, permutation, route) in enumerate(
            zip(metadata, permutations, classes)):
        old_block = int(old_group["block"])
        block_rows.append({
            "new_block": new_block,
            "old_block": old_block,
            "old_tile": old_block // 2,
            "branch": int(old_group["branch"]),
            "k3": int(old_group["k3"]),
            "q4": int(old_group["q4"]),
            "modeled_extra_ops_per_degree_plane": route[0],
            "route_class": route[1],
            "old_lane_for_each_new_lane": list(permutation),
        })
        for new_lane, old_lane in enumerate(permutation):
            lane_rows.append({
                "new_block": new_block,
                "new_lane": new_lane,
                "old_block": old_block,
                "old_lane": old_lane,
                "lambda_source_word": 16 * old_block + old_lane,
            })
    return block_rows, lane_rows


def csv_text(rows: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def build(mapping_csv: Path, mapping_json: Path,
          random_starts: int) -> tuple[dict, str]:
    groups = load_groups(mapping_csv)
    metadata, seeds = load_group_metadata(mapping_json)
    minima = search(groups, seeds, random_starts)
    best = minima[0]
    best_score, _, best_classes = evaluate(best, groups)
    block_rows, lane_rows = render_rows(best, groups, metadata)

    # A common physical relabel composes every group signature with the same
    # bijection and therefore cannot collapse distinct signatures.
    signatures = {tuple(group) for group in groups}
    block_order = [row["old_block"] for row in block_rows]
    old_to_new = {old: new for new, old in enumerate(block_order)}
    tile_store_schedule = []
    for old_tile in range(6):
        destinations = [old_to_new[2 * old_tile], old_to_new[2 * old_tile + 1]]
        tile_store_schedule.append({
            "old_tile": old_tile,
            "new_blocks": destinations,
            "new_256_byte_base": min(destinations) // 2,
            "q4_swapped": destinations[0] > destinations[1],
        })
    modeled_per_poly = 4 * sum(item[0] for item in best_classes)
    result = {
        "schema": "ntruplus768-gt32-encap-mprime-layout-070-v1",
        "search": {
            "uniform_microkernel_family":
                "4x16 transpose + packet-output permutation + four vpermq permutations",
            "parameter_space": "24^5 = 191102976 uniform packet templates",
            "method": "all 12 production seeds plus deterministic multi-start coordinate descent",
            "random_starts": random_starts,
            "local_minima_found": len(minima),
            "static_score_is_not_cycle_veto": True,
        },
        "global_uniform_lane_relabel": {
            "possible": len(signatures) == 1,
            "distinct_current_group_signatures": len(signatures),
            "proof": "composition by one common bijection preserves unequal group signatures",
        },
        "best_uniform_microkernel": {
            "score": {
                "modeled_ops_per_degree_plane_sum_over_blocks": best_score[0],
                "maximum_block_class": best_score[1],
                "nonzero_route_blocks": best_score[2],
                "distinct_lane_permutations": best_score[3],
            },
            "transpose_output_order": list(best[0]),
            "vpermq_qword_permutations": [list(value) for value in best[1:]],
            "vpermq_immediates": [qperm_immediate(value) for value in best[1:]],
            "block_order_old_indices": block_order,
            "blocks": block_rows,
        },
        "consumer_effect": {
            "q24_body": "one uniform four-packet body in a twelve-iteration loop",
            "b3_arithmetic": "unchanged; lambda and lambda_qinv tables relabeled by lane_rows",
            "complete_M_materialization": False,
            "decoder_h": "inverse uniform packet mapping can land directly in M'; executable proof not run",
        },
        "forward_cost": {
            "current_loop_uses_one_shared_deposit_shape": True,
            "zero_extra_mask_relabel_blocks": sum(item[0] == 0 for item in best_classes),
            "non_absorbable_blocks": sum(item[0] != 0 for item in best_classes),
            "modeled_extra_vector_ops_per_forward_polynomial": modeled_per_poly,
            "two_forward_polynomials_in_encap": 2,
            "modeled_extra_vector_ops_for_r_and_m": 2 * modeled_per_poly,
            "note": "class 3 is a modeled floor outside the tested two-op one-source family, not a universal AVX2 lower bound",
            "tile_store_schedule": tile_store_schedule,
        },
        "decision": {
            "status": ("STATIC_LAYOUT_PASS" if best_score[0] == 0
                       else "NO_ASM_CONTINUATION"),
            "reason": ("a uniform Q24 template is compatible with every block "
                       "through the current Forward deposit masks"
                       if best_score[0] == 0 else
                       "no searched uniform template is compatible with the "
                       "current shared Forward deposit by table/store relabel alone"),
            "best_candidate_still_requires_block_dependent_lane_routing":
                best_score[0] != 0,
            "reopen": ("write the bounded executable ABI gate"
                       if best_score[0] == 0 else
                       "only with a jointly redesigned Forward terminal whose "
                       "existing S4/S5 movement constructs these block-dependent "
                       "permutations without new operations"),
        },
        "top_local_minima": [
            {
                "score": list(evaluate(item, groups)[0]),
                "transpose_output_order": list(item[0]),
                "vpermq_immediates": [qperm_immediate(value) for value in item[1:]],
            }
            for item in minima[:16]
        ],
        "bijections": {
            "blocks": sorted(block_order) == list(range(12)),
            "lane_rows": len(lane_rows) == 192,
            "lambda_source_words": len({row["lambda_source_word"] for row in lane_rows}) == 192,
        },
    }
    if not all(result["bijections"].values()):
        raise ValueError("M' mapping is not bijective")
    return result, csv_text(lane_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping-csv", required=True, type=Path)
    parser.add_argument("--mapping-json", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--lanes", required=True, type=Path)
    parser.add_argument("--random-starts", type=int, default=512)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, lanes = build(args.mapping_csv, args.mapping_json, args.random_starts)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if args.output.read_text() != text or args.lanes.read_text() != lanes:
            raise SystemExit("070 generated evidence is stale")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
    args.lanes.write_text(lanes)


if __name__ == "__main__":
    main()
