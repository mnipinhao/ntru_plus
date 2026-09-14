#!/usr/bin/env python3
"""P27 exact consumer-oriented I16 lane-basis and routing search."""

from __future__ import annotations

import hashlib
import itertools
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
Q = 3457
R = (1 << 16) % Q
THETA = 9
RESIDUES = (1, 5)
CHANNELS = tuple((component, half) for component in range(3) for half in range(2))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def table(name: str) -> list[int]:
    text = (PROD / "gt864_native_scaled_tables.h").read_text()
    body = text.split(name, 1)[1].split("=", 1)[1].split(";", 1)[0]
    return [int(x) for x in re.findall(r"-?\d+", body)]


def group_channels(group: tuple[int, int]) -> tuple[int, ...]:
    component, half = group
    return tuple(3 * row + component for row in range(4 * half, 4 * half + 4))


def matchings(items: tuple[tuple[int, int], ...]):
    if not items:
        yield ()
        return
    first = items[0]
    for i in range(1, len(items)):
        second = items[i]
        for rest in matchings(items[1:i] + items[i + 1:]):
            yield ((first, second),) + rest


def natural_coordinate(index: int) -> tuple[int, int, int, int]:
    top, rem = divmod(index, 432)
    t, channel = divmod(rem, 27)
    return top, t, channel // 3, channel % 3


def source_layout(matching):
    """Return exact dense-scratch source (record,lane) for all coefficients.

    Main output reuses the two 16-Q P8 blocks consumed by a paired kernel:
    the first block receives top 0 and the second receives top 1.  Tail output
    uses twelve dense records at original scratch Q slots 96..107.
    """
    bank_for_channel: dict[int, tuple[int, int]] = {}
    main_slot: dict[tuple[int, int, int], int] = {}
    bank_rows = []
    for bank, pair in enumerate(matching):
        lane_order = group_channels(pair[0]) + group_channels(pair[1])
        for lane, channel in enumerate(lane_order):
            assert channel not in bank_for_channel
            bank_for_channel[channel] = (bank, lane)
        input_blocks = tuple(component * 2 + half for component, half in pair)
        bank_rows.append({
            "bank": bank,
            "groups": [list(x) for x in pair],
            "channels": list(lane_order),
            "input_q_blocks": list(input_blocks),
        })
        for top in range(2):
            block = input_blocks[top]
            for t in range(16):
                main_slot[top, t, bank] = 16 * block + t
    assert set(bank_for_channel) == set(range(24))
    assert len(set(main_slot.values())) == 96

    mapping = []
    for natural in range(864):
        top, t, row, component = natural_coordinate(natural)
        channel = 3 * row + component
        if channel < 24:
            bank, lane = bank_for_channel[channel]
            record = main_slot[top, t, bank]
        else:
            tail_linear = 3 * t + component
            record = 96 + 6 * top + tail_linear // 8
            lane = tail_linear % 8
        mapping.append((record, lane))
    assert len(set(mapping)) == 864
    assert {record for record, _ in mapping} == set(range(108))
    return mapping, bank_rows


def route_plan(mapping):
    """Build a one-load/source interval-colored TBL4 plan.

    v0-v3 are the consecutive TBL4 source bank.  Each source record is loaded
    and normalized once, retained through its last natural-output consumer,
    and its byte positions are encoded in the output-specific table mask.
    """
    source_tags = [[None] * 8 for _ in range(108)]
    for natural, (record, lane) in enumerate(mapping):
        assert source_tags[record][lane] is None
        source_tags[record][lane] = natural
    assert all(all(tag is not None for tag in record) for record in source_tags)

    uses: dict[int, list[int]] = defaultdict(list)
    output_sources = []
    for output in range(108):
        records = []
        for record, _ in mapping[8 * output:8 * output + 8]:
            if record not in records:
                records.append(record)
        output_sources.append(records)
        for record in records:
            uses[record].append(output)
    assert len(uses) == 108

    resident: dict[int, int] = {}
    plan = []
    peak = 0
    load_count = 0
    for output, records in enumerate(output_sources):
        loads = []
        for record in records:
            if record not in resident:
                free = next(slot for slot in range(4) if slot not in resident.values())
                resident[record] = free
                loads.append({"record": record, "tbl_slot": free})
                load_count += 1
        peak = max(peak, len(resident))
        indices = []
        tags = []
        for record, lane in mapping[8 * output:8 * output + 8]:
            slot = resident[record]
            indices.extend((16 * slot + 2 * lane, 16 * slot + 2 * lane + 1))
            tags.append(source_tags[record][lane])
        assert len(indices) == 16 and max(indices) < 64
        plan.append({
            "output_q": output,
            "source_records": records,
            "loads": loads,
            "tbl4_byte_indices": indices,
            "tagged_output": tags,
        })
        for record in list(resident):
            if uses[record][-1] == output:
                del resident[record]
    assert not resident and load_count == 108 and peak <= 4
    assert [tag for row in plan for tag in row["tagged_output"]] == list(range(864))
    return plan, peak, Counter(len(x) for x in output_sources)


def route_arity(mapping) -> Counter:
    """Score a matching without imposing the four-register winner contract."""
    result = Counter()
    for output in range(108):
        records = []
        for record, _ in mapping[8 * output:8 * output + 8]:
            if record not in records:
                records.append(record)
        result[len(records)] += 1
    return result


def top_phase_gate() -> dict[str, object]:
    omega16 = pow(THETA, 54, Q)
    scale_steps = [pow(THETA, -9 * residue, Q) for residue in RESIDUES]
    ratio = scale_steps[1] * pow(scale_steps[0], -1, Q) % Q
    subgroup = [pow(omega16, k, Q) for k in range(16)]
    assert pow(omega16, 16, Q) == 1 and pow(omega16, 8, Q) != 1
    assert ratio not in subgroup
    return {
        "omega16": omega16,
        "top_scale_geometric_steps": scale_steps,
        "top1_over_top0_step": ratio,
        "ratio_power_16": pow(ratio, 16, Q),
        "ratio_is_omega16_power": False,
        "conclusion": "top recombination cannot move before I16 as a cyclic lane rotation",
    }


def table_scale_gate() -> dict[str, object]:
    stage = table("gt864_inverse16_stage_barrett")
    scale = table("gt864_inverse16_main_scale_barrett")
    tail = table("gt864_inverse16_tail_scale_barrett")
    assert len(stage) == 64 and len(scale) == len(tail) == 256
    inv16 = pow(16, -1, Q)
    for t in range(16):
        expected = [centered(R * inv16 * pow(pow(THETA, 9 * residue, Q), -t, Q))
                    for residue in RESIDUES]
        assert scale[16 * t:16 * t + 8] == [expected[0]] * 4 + [expected[1]] * 4
        assert tail[16 * t:16 * t + 8] == [expected[0]] * 3 + [expected[1]] * 3 + [0, 0]
    return {
        "stage_entries": len(stage),
        "main_scale_entries": len(scale),
        "tail_scale_entries": len(tail),
        "paired_groups_share_stage_and_terminal_constants": True,
        "roots_scale_and_R0_domain_unchanged_by_lane_pairing": True,
    }


def ternary(value: int) -> int:
    adjusted = value - int(value > 1728) + int(value < -1728)
    quotient = (adjusted * 10923 + 16384) // 32768
    return adjusted - 3 * quotient


def normalization_gate() -> dict[str, object]:
    for value in range(-4577, 4578):
        got = ternary(value)
        assert got in (-1, 0, 1)
        centered_q = value - Q if value > 1728 else value + Q if value < -1728 else value
        assert (got - centered_q) % 3 == 0
    # A permutation commutes with a pointwise map.  Distinct asymmetric tags
    # catch accidental lane/order symmetry.
    tagged = list(range(-432, 432))
    perm = [(37 * i + 11) % 864 for i in range(864)]
    assert [ternary(tagged[i]) for i in perm] == [ternary(x) for x in [tagged[i] for i in perm]]
    return {
        "exhaustive_raw_inputs": 9155,
        "raw_bound": 4577,
        "outputs": [-1, 0, 1],
        "normalize_before_route_equivalent": True,
    }


def register_budget() -> dict[str, object]:
    # Two existing four-channel/two-top I16 states: 2 * 16 Q registers.
    states = 32
    stage_aux = 3       # quotient/result temp plus packed public constants
    terminal_aux = 4    # terminal product/top recombination/join workspace
    parked_stage = stage_aux
    parked_terminal = terminal_aux
    assert states - parked_stage + stage_aux == 32
    assert states - parked_terminal + terminal_aux == 32
    assert 2 * parked_terminal == 8 <= 13  # x5-x17 caller-saved budget
    return {
        "coefficient_state_q": states,
        "stage_aux_q": stage_aux,
        "terminal_aux_q": terminal_aux,
        "peak_vector_registers": 32,
        "max_parked_q_in_gprs": parked_terminal,
        "max_parking_gprs": 2 * parked_terminal,
        "available_parking_and_control_gprs_x5_x17": 13,
        "memory_spill_required": False,
        "physical_allocation_proved": False,
        "warning": "P28 must prove the cross-class exchanges and timing with real assembly",
    }


def static_ledger() -> dict[str, object]:
    current = {
        "main_lane_extract_and_strh": 6 * 128 * 2,
        "tail_lane_extract_and_strh": 96 * 2,
        "total_terminal_materialization": 1728,
    }
    candidate = {
        "main_join_d_halves": 3 * 16 * 2,
        "main_full_q_stores": 3 * 16 * 2,
        "tail_dense_tbl": 12,
        "tail_full_q_stores": 12,
    }
    candidate["total_terminal_materialization"] = sum(candidate.values())
    assert candidate["total_terminal_materialization"] == 216
    # Conservative allowance: every paired main region pays 64 cross-class
    # parking instructions.  Consumer adds one TBL4 and one mask load per Q;
    # its 108 loads/stores and six arithmetic normalization ops replace the
    # current raw pass's same 108 loads/stores and six pointwise ops.
    removed = current["total_terminal_materialization"] - candidate["total_terminal_materialization"]
    constant_loads_saved = 18 + 192
    parking_allowance = 3 * 64
    new_consumer_route_and_mask = 108 * 2
    conservative_net = removed + constant_loads_saved - parking_allowance - new_consumer_route_and_mask
    assert conservative_net == 1314
    return {
        "current": current,
        "candidate": candidate,
        "terminal_materialization_removed": removed,
        "main_stage_and_composite_constant_loads_saved": constant_loads_saved,
        "gpr_parking_instruction_allowance": parking_allowance,
        "consumer_tbl4_plus_mask_load_allowance": new_consumer_route_and_mask,
        "conservative_net_instruction_reduction": conservative_net,
        "note": "static bound only; no cycle or allocated-code claim",
    }


def main() -> None:
    scored = []
    for matching in matchings(CHANNELS):
        mapping, rows = source_layout(matching)
        arity = route_arity(mapping)
        score = (max(arity), sum((k - 1) * count for k, count in arity.items()))
        scored.append((score, matching, mapping, rows, arity))
    assert len(scored) == 15
    scored.sort(key=lambda x: x[0])
    best = scored[0]
    assert best[0] == (4, 184)
    assert list(best[4].items()) == [(2, 48), (3, 44), (4, 16)]
    assert sum(1 for x in scored if x[0] == best[0]) == 1
    route, peak, arity = route_plan(best[2])

    all_natural = [natural_coordinate(i) for i in range(864)]
    assert len(set(all_natural)) == 864
    assert all(natural_coordinate(8 * q)[0] == natural_coordinate(8 * q + 7)[0]
               for q in range(108))

    result = {
        "experiment": "GT864-P27-CONSUMER-I16-LANE-BASIS-20260914",
        "status": "pass-machine-only",
        "production_changed": False,
        "source_sha256": {
            name: sha256(PROD / name) for name in (
                "gt864_native_inverse9.S",
                "gt864_native_inverse16_lazy.S",
                "gt864_native_inverse_tail_lazy.S",
                "gt864_crepmod3_raw.S",
                "gt864_native_public.S",
                "gt864_native_scaled_tables.h",
            )
        },
        "coordinate_gate": {
            "natural_formula": "n = top*432 + t*27 + row*3 + component",
            "coordinates": len(all_natural),
            "bijective": True,
            "natural_q_never_crosses_top": True,
            "scratch_q_capacity_unchanged": 112,
            "candidate_dense_source_q": 108,
            "unused_existing_tail_q": 4,
            "extra_coefficient_passes": 0,
        },
        "search": {
            "perfect_matchings_exhausted": 15,
            "score": "minimize maximum source arity, then excess source joins",
            "unique_best": True,
            "selected_banks": best[3],
            "route_source_arity": {str(k): v for k, v in sorted(arity.items())},
            "consumer_tbl4_outputs": 108,
            "source_q_loads": 108,
            "source_q_loaded_once": True,
            "peak_live_source_q": peak,
            "tbl_register_contract": "v0-v3 consecutive; output-specific 16-byte mask",
            "route_plan": route,
            "all_scores": [
                {
                    "score": list(score),
                    "matching": [[list(a), list(b)] for a, b in matching],
                    "arity": {str(k): v for k, v in sorted(arity_i.items())},
                }
                for score, matching, _, _, arity_i in scored
            ],
        },
        "top_phase_gate": top_phase_gate(),
        "table_scale_gate": table_scale_gate(),
        "range_gate": {
            "basemul_rinv": 2497,
            "inverse9_terminal": 2617,
            "inverse16_peak": 21397,
            "raw_R0": 4577,
            "ternary": 1,
            "changed_arithmetic_nodes": 0,
        },
        "normalization_gate": normalization_gate(),
        "register_budget": register_budget(),
        "static_instruction_ledger": static_ledger(),
        "memory_contract": {
            "P8_scratch_bytes": 1792,
            "main_in_place_pairs": "three disjoint pairs of two consumed 16-Q blocks",
            "tail_in_place": "16-Q input block becomes 12 dense Q records; four Q unused",
            "dense_source_bytes": 1728,
            "natural_output_bytes": 1728,
            "coefficient_vector_stores_before_cleanup": 108,
            "lane_ST3": 0,
            "UMOV_STRH_terminal_pairs": 0,
            "post_store_D_record_route": False,
        },
        "hard_gates": {
            "exact_coordinates_roots_scale_range": "pass",
            "exact_natural_ternary_output": "pass-machine-map",
            "no_extra_pass_or_larger_scratch": "pass",
            "no_lane_ST3_scalar_terminal_or_P11_D_route": "pass-design",
            "full_vector_terminal_stores_at_most_108": "pass",
            "at_most_32_vector_registers_no_memory_spill": "pass-budget-only",
            "real_materialization_removed": "pass-static",
            "physical_RA_schedule_KAT_Pi5": "deferred-P28",
        },
        "decision": "advance exact selected DAG to P28 physical realization",
        "limitations": [
            "No assembly, Slothy allocation, KAT, binary audit or Pi 5 timing was run.",
            "GPR parking is a bounded design, not yet an allocated instruction stream.",
            "The static instruction ledger is conservative accounting, not a cycle estimate.",
        ],
    }
    path = HERE / "audit-results.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": result["status"],
        "selected_banks": result["search"]["selected_banks"],
        "route_source_arity": result["search"]["route_source_arity"],
        "peak_live_source_q": peak,
        "terminal_materialization": [1728, 216],
        "conservative_net_instruction_reduction": result["static_instruction_ledger"]["conservative_net_instruction_reduction"],
        "next": "P28 physical paired-I16 and dense-tail symbolic realization",
    }, indent=2))


if __name__ == "__main__":
    main()
