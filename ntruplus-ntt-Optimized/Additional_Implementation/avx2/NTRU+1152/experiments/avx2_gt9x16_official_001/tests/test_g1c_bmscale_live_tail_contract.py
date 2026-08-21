#!/usr/bin/env python3
"""Validate the G1C BMScale live-tail scheduling and direct inverse algebra."""

import json
import random
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
TRIALS = 10003
experiment = Path(__file__).resolve().parents[1]
contract = json.loads((experiment / "generated/g1c-bmscale-live-tail-contract.json").read_text())
inverse = json.loads((experiment / "generated/g1c-adjusted-inverse-head.json").read_text())
layout = json.loads((experiment / "generated/gt9x16-pipeline-layout.json").read_text())


def signed16(value):
    value %= 1 << 16
    return value - (1 << 16) if value >= (1 << 15) else value


def montgomery_reduce(value):
    low = signed16(signed16(value) * QINV)
    return (value - low * Q) >> 16


assert contract["schema"] == "gt-g1c-bmscale-live-tail/v1"
cutpoints = contract["official_live_result_cutpoints"]
assert cutpoints["early"]["results"] == {"c0": "ymm5", "c1": "ymm6", "c2": "ymm7"}
assert cutpoints["late"]["results"] == {"c3": "ymm1"}
assert cutpoints["arithmetic_changed"] is False
assert cutpoints["all_ymm_registers_touched_by_function"] == 16

arithmetic = contract["gt_bmscale_arithmetic_contract"]
assert arithmetic["input_layout"] == "gt_row_terminal_lane"
assert arithmetic["row_blocks"] == 18
assert arithmetic["operand_transform_scales"] == [4, 4]
assert arithmetic["output_transform_scale"] == 16
assert arithmetic["output_montgomery_r_exponent"] == -1
cell_by_key = {
    (cell["branch"], cell["gt_row_physical_trit_reversed"],
     cell["ntt16_lane_physical_bit_reversed"]): cell
    for cell in layout["cells"]
}
for row_contract in arithmetic["rows"]:
    cells = [cell_by_key[(row_contract["branch"], row_contract["physical_row"], lane)]
             for lane in range(16)]
    assert row_contract["factor_mod_q_by_lane"] == [cell["factor_mod_q"] for cell in cells]
    assert row_contract["factor_montgomery_signed_by_lane"] == [
        cell["basemul_factor_montgomery"] for cell in cells]
    assert row_contract["factor_qinv_signed16_by_lane"] == [
        cell["basemul_factor_qinv_signed16"] for cell in cells]

materialized = contract["materialized_persistent_pair_path"]
assert materialized["routing_instructions_per_terminal_pair"] == 6
assert materialized["routing_instructions_per_row"] == 12
assert materialized["routing_instructions_full_transform"] == 216
assert materialized["faithful_schedule_minimum_extra_memory"]["full_transform_temporary_stores"] == 18
assert materialized["faithful_schedule_minimum_extra_memory"]["full_transform_temporary_loads"] == 18

live = contract["live_direct_inverse_path"]
assert live["edge_input_loads"] == 0
assert live["post_inverse_d1_stores_per_row"] == 4
assert live["materialized_BMScale_to_inverse_seam"] is False
assert live["designed_peak_live_ymm_upper_bound"] == 13
assert contract["selection"]["selected"] == "C2-L"

rng = random.Random(0xC2B1152)
checks = 0
for direct, row in zip(contract["direct_inverse_rows"], inverse["rows"]):
    assert direct["physical_row"] == row["physical_row"]
    inverse_twiddles = row["inverse_distance1_twiddle_mod_q"]
    alternating_mod = direct["inverse_twiddle_alternating_mod_q"]
    alternating_mont = direct["inverse_twiddle_alternating_montgomery_signed"]
    alternating_qinv = direct["inverse_twiddle_alternating_qinv_signed16"]
    for pair, inverse_twiddle in enumerate(inverse_twiddles):
        assert alternating_mod[2 * pair] == inverse_twiddle
        assert alternating_mod[2 * pair + 1] == -inverse_twiddle % Q
    for value, mont, qinv in zip(alternating_mod, alternating_mont, alternating_qinv):
        assert mont % Q == value * R % Q
        assert qinv == signed16(mont * QINV)
    for _ in range(TRIALS):
        lanes = [rng.randrange(Q) for _ in range(16)]
        swapped = [lanes[index ^ 1] for index in range(16)]
        sums = [(left + right) % Q for left, right in zip(lanes, swapped)]
        differences = [(left - right) % Q for left, right in zip(lanes, swapped)]
        twisted = [montgomery_reduce(signed16(value) * constant) % Q
                   for value, constant in zip(differences, alternating_mont)]
        output = [sums[index] if index % 2 == 0 else twisted[index]
                  for index in range(16)]
        for pair, zeta_inverse in enumerate(inverse_twiddles):
            even = lanes[2 * pair]
            odd = lanes[2 * pair + 1]
            assert output[2 * pair] == (even + odd) % Q
            assert output[2 * pair + 1] == zeta_inverse * (even - odd) % Q
        checks += 16

gate = contract["prototype_gate"]
assert gate["linked_C2_L_asm_authorized"] is True
assert gate["must_preserve_official_bmscale_arithmetic"] is True
assert gate["must_not_add_standalone_converter"] is True
assert gate["cycles"] is None
print(f"G1C2 contract: Official c0/c1/c2→c3 cutpoints, C2-L zero-seam schedule, {checks} lane checks passed")
