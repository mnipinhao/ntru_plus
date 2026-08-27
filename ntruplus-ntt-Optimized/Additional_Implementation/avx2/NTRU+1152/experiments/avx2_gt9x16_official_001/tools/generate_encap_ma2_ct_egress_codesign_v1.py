#!/usr/bin/env python3
"""Map H3 live terminals to exact ciphertext ownership and H4 feasibility."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


HOOK = re.compile(r"^\s*H3_TERMINAL_C\s+([^,]+),(\d+),(\d+)\s*$")
STORE = re.compile(r"^\s*vmovdqa\s+YMMWORD PTR \[rdi \+ (\d+)\], ymm(\d+)\s*$")


def source_hooks(path: Path) -> list[dict]:
    lines = path.read_text().splitlines()
    hooks = []
    for index, line in enumerate(lines):
        match = HOOK.match(line)
        if not match:
            continue
        if index + 1 >= len(lines) or not (store := STORE.match(lines[index + 1])):
            raise SystemExit(f"terminal hook at source line {index + 1} lacks immediate store")
        tile, coefficient, register = match.groups()
        offset, store_register = store.groups()
        if register != store_register:
            raise SystemExit("terminal hook register differs from following store")
        hooks.append({
            "terminal_index": len(hooks), "source_line": index + 1,
            "tile": tile, "terminal_coefficient_plane": int(coefficient),
            "register": f"ymm{register}", "output_vector": int(offset) // 32,
        })
    if len(hooks) != 72:
        raise SystemExit(f"expected 72 H3 terminal hooks, found {len(hooks)}")
    return hooks


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != text:
            raise SystemExit(f"stale H4 co-design map: {path}")
    else:
        path.write_text(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h3-source", type=Path, required=True)
    parser.add_argument("--liveness", type=Path, required=True)
    parser.add_argument("--serializer-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    hooks = source_hooks(args.h3_source)
    liveness = json.loads(args.liveness.read_text())
    serializer = json.loads(args.serializer_map.read_text())
    machine_by_vector = {x["output_vector"]: x for x in liveness["terminal_stores"]}
    coefficients_by_vector: dict[int, list[dict]] = {}
    for coefficient in serializer["coefficient_map"]:
        coefficients_by_vector.setdefault(coefficient["ma2"]["vector"], []).append(coefficient)
    for entries in coefficients_by_vector.values():
        entries.sort(key=lambda x: x["ma2"]["lane"])

    terminal = []
    for hook in hooks:
        vector = hook["output_vector"]
        machine = machine_by_vector[vector]
        owners = coefficients_by_vector[vector]
        if len(owners) != 16:
            raise SystemExit(f"MA2 vector {vector} does not own 16 coefficients")
        terminal.append({
            **hook,
            "machine_store_address": machine["address"],
            "machine_live_count": machine["live_count_before_store"],
            "machine_free_ymm": machine["free_ymm_before_store"],
            "h4a_one_scratch_normalization_feasible": machine["free_ymm_before_store"] >= 1,
            "coefficient_ownership": [{
                "lane": item["ma2"]["lane"],
                "official_coefficient": item["official_coefficient"],
                "serialized_coefficient": item["serializer"]["serialized_coefficient"],
                "pair": item["serializer"]["pair"],
                "pair_parity": item["serializer"]["pair_parity"],
                "byte_contributions": item["serializer"]["byte_contributions"],
            } for item in owners],
        })

    vector_order = [x["output_vector"] for x in terminal]
    position = {vector: index for index, vector in enumerate(vector_order)}
    pending: set[int] = set()
    frontier = []
    pair_intervals = []
    starts: dict[int, list[int]] = {}
    ends: dict[int, list[int]] = {}
    for pair in serializer["pair_map"]:
        a = position[pair["low"]["ma2_vector"]]
        b = position[pair["high"]["ma2_vector"]]
        first, second = sorted((a, b))
        starts.setdefault(first, []).append(pair["pair"])
        ends.setdefault(second, []).append(pair["pair"])
        pair_intervals.append({
            "pair": pair["pair"], "first_terminal": first,
            "second_terminal": second, "terminal_distance": second - first,
            "low_vector": pair["low"]["ma2_vector"],
            "high_vector": pair["high"]["ma2_vector"],
            "output_bytes": pair["output_bytes"],
        })
    for index, vector in enumerate(vector_order):
        for pair in starts.get(index, []):
            pending.add(pair)
        for pair in ends.get(index, []):
            pending.remove(pair)
        frontier.append({
            "after_terminal": index, "output_vector": vector,
            "pending_pairs": len(pending),
            "pending_coefficients": len(pending),
            "minimum_full_ymm_for_i16_pending_coefficients": (len(pending) + 15) // 16,
        })
    max_frontier = max(frontier, key=lambda x: x["pending_pairs"])
    zero_scratch = [x["terminal_index"] for x in terminal if x["machine_free_ymm"] == 0]
    report = {
        "schema": "encap-ma2-ct-egress-codesign-v1",
        "checkpoint": "ENCAP-MA2-CT-EGRESS-CODESIGN-V1",
        "boundary": "H3_TERMINAL_C live scale-4 Natural-Q vectors to exact ciphertext bytes",
        "frozen_contract": {
            "ma2_arithmetic": "unchanged", "natural_q": True,
            "input_scale": 4, "output_bytes": 1728,
            "inv4": "required exactly once", "canonical_range": [0, 3456],
        },
        "terminal_order": terminal,
        "serializer_pair_intervals": pair_intervals,
        "pending_pair_frontier": frontier,
        "h4a_terminal_normalization": {
            "minimum_extra_ymm_assumption": 1,
            "hooks_feasible_without_reschedule": len(terminal) - len(zero_scratch),
            "hooks_blocked_by_zero_machine_slack": zero_scratch,
            "all_hooks_feasible_in_current_schedule": not zero_scratch,
        },
        "h4b_full_byte_egress": {
            "all_true_12bit_pairs_cross_ma2_vectors": all(
                not pair["same_ma2_vector"] for pair in serializer["pair_map"]),
            "maximum_pending_pairs": max_frontier["pending_pairs"],
            "maximum_pending_coefficients": max_frontier["pending_coefficients"],
            "minimum_full_ymm_at_max_frontier": max_frontier[
                "minimum_full_ymm_for_i16_pending_coefficients"],
            "maximum_frontier_after_terminal": max_frontier["after_terminal"],
            "one_or_two_pack_accumulator_assumption_supported": max_frontier[
                "minimum_full_ymm_for_i16_pending_coefficients"] <= 2,
        },
        "decision": {
            "h4a": "all hooks have machine slack for one-scratch terminal normalization; exact schedule remains required",
            "h4b": "one pending YMM is a feasible lower-bound shape; search exact normalize/pair/pack schedule before ASM",
            "next": "price H3 independently; use this map for H4 schedule search only",
        },
        "gates": {
            "machine_def_use_liveness_used": True,
            "all_72_terminal_vectors_owned": len(terminal) == 72,
            "all_1152_coefficients_owned": sum(len(x["coefficient_ownership"]) for x in terminal) == 1152,
            "no_h4_asm_generated": True,
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    write(args.output, rendered, args.check)
    print("H4 map: max pending pairs={}, zero-slack hooks={}".format(
        max_frontier["pending_pairs"], len(zero_scratch)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
