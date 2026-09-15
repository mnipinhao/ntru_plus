#!/usr/bin/env python3
"""Machine-check P29's equal-half banks and direct natural ST3 layout."""

from collections import Counter
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GROUPS = tuple((component, half) for component in range(3) for half in range(2))
SELECTED = (((0, 0), (1, 0)), ((0, 1), (1, 1)), ((2, 0), (2, 1)))
RECORD_BASE = {(0, 0): 0, (1, 0): 32, (0, 1): 16, (1, 1): 48, (0, 2): 64, (1, 2): 80}


def group_channels(group):
    component, half = group
    return tuple(3 * row + component for row in range(4 * half, 4 * half + 4))


def matchings(items):
    if not items:
        yield ()
        return
    first = items[0]
    for index in range(1, len(items)):
        for rest in matchings(items[1:index] + items[index + 1:]):
            yield ((first, items[index]),) + rest


def natural(index):
    top, rem = divmod(index, 432)
    t, channel = divmod(rem, 27)
    return top, t, channel // 3, channel % 3


def producer_map(matching):
    result = {}
    for producer, pair in enumerate(matching):
        for channel in group_channels(pair[0]) + group_channels(pair[1]):
            result[channel] = producer
    for channel in range(24, 27):
        result[channel] = 3
    return result


def direct_q_impossibility():
    rows = []
    for matching in matchings(GROUPS):
        producers = producer_map(matching)
        arity = Counter()
        for output_q in range(108):
            used = {
                producers[3 * natural(index)[2] + natural(index)[3]]
                for index in range(8 * output_q, 8 * output_q + 8)
            }
            arity[len(used)] += 1
        rows.append({
            "matching": matching,
            "arity": dict(sorted(arity.items())),
            "fragments": sum(key * value for key, value in arity.items()),
            "single_producer_q": arity[1],
        })
    assert len(rows) == 15
    assert all(row["single_producer_q"] == 0 for row in rows)
    assert min(row["fragments"] for row in rows) == 292
    return rows


def selected_source(top, t, channel):
    for bank, pair in enumerate(SELECTED):
        lanes = group_channels(pair[0]) + group_channels(pair[1])
        if channel in lanes:
            return RECORD_BASE[top, bank] + t, lanes.index(channel)
    raise ValueError(channel)


def st3_gate():
    tagged_records = [[None] * 8 for _ in range(96)]
    for top in range(2):
        for t in range(16):
            for channel in range(24):
                record, lane = selected_source(top, t, channel)
                tag = top * 432 + t * 27 + channel
                assert tagged_records[record][lane] is None
                tagged_records[record][lane] = tag
    assert all(all(value is not None for value in record) for record in tagged_records)

    output = []
    for top in range(2):
        for t in range(16):
            for half in range(2):
                rows = range(4 * half, 4 * half + 4)
                # Architectural ST3.4h order: lane0 of each register, then lane1, ...
                for row in rows:
                    for component in range(3):
                        record, lane = selected_source(top, t, 3 * row + component)
                        output.append(tagged_records[record][lane])
            output.extend(top * 432 + t * 27 + channel for channel in range(24, 27))
    assert output == list(range(864))
    return {
        "selected_matching": SELECTED,
        "main_records": 96,
        "full_st3_4h_stores": 64,
        "tail_exact_groups": 32,
        "tagged_coordinates": len(output),
        "natural_order_exact": True,
    }


def ternary(value):
    adjusted = value - int(value > 1728) + int(value < -1728)
    quotient = (adjusted * 10923 + 16384) // 32768
    return adjusted - 3 * quotient


def normalization_gate():
    for value in range(-4577, 4578):
        got = ternary(value)
        assert got in (-1, 0, 1)
        centered = value - 3457 if value > 1728 else value + 3457 if value < -1728 else value
        assert (got - centered) % 3 == 0
    return {"inputs": 9155, "raw_bound": 4577, "outputs": [-1, 0, 1]}


def static_cost():
    baseline = {"main": 841, "tail": 542, "route": 1304}
    candidate = {
        "main": 841,
        # Remove 96 INS + 12 dense STR; add 8 setup + 32*(6 normalize + 4 exact store).
        "tail_upper_bound": 542 - 108 + 8 + 32 * 10,
        # setup/pointer 7 + 32*(3 LDR + 18 normalize + 3 EXT + 2 ST3 + 1 ADD) + RET
        "main_route_upper_bound": 7 + 32 * 27 + 1,
    }
    baseline_total = 3 * baseline["main"] + baseline["tail"] + baseline["route"]
    candidate_total = 3 * candidate["main"] + candidate["tail_upper_bound"] + candidate["main_route_upper_bound"]
    assert baseline_total == 4369
    assert candidate_total == 4157
    return {
        "baseline_executable_upper": baseline_total,
        "candidate_executable_upper": candidate_total,
        "instruction_upper_delta": candidate_total - baseline_total,
        "removed": {"tbl": 216, "orr_route": 108, "route_mask_q_loads": 216, "route_mask_bytes": 3456},
        "added": {"full_st3_4h": 64, "lane_st3": 0},
        "note": "Counts include terminal control; real generated/assembled counts supersede this upper bound.",
    }


result = {
    "experiment": "GT864-P29-DIRECT-ST3-20260915",
    "direct_no_communication_gate": {
        "status": "impossible",
        "reason": "every natural Q depends on at least two sequential producers for all 15 pairings",
        "matchings": direct_q_impossibility(),
    },
    "st3_hybrid_gate": st3_gate(),
    "normalization_gate": normalization_gate(),
    "static_cost": static_cost(),
    "decision": "pass_to_symbolic_assembly",
}
(HERE / "audit-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({
    "direct": result["direct_no_communication_gate"]["status"],
    "st3": result["st3_hybrid_gate"],
    "cost": result["static_cost"],
}, indent=2))
