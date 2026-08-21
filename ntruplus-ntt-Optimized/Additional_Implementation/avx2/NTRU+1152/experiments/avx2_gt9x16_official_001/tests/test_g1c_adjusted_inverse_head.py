#!/usr/bin/env python3
"""Validate the G1C adjusted inverse distance-1 oracle independently."""

import json
import random
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
TRIALS = 10003
experiment = Path(__file__).resolve().parents[1]
oracle = json.loads((experiment / "generated/g1c-adjusted-inverse-head.json").read_text())
layout = json.loads((experiment / "generated/gt9x16-pipeline-layout.json").read_text())

assert oracle["schema"] == "gt-g1c-adjusted-inverse-head/v1"
assert oracle["factorization_boundary"]["official_source_level6_reused"] is False
assert oracle["factorization_boundary"]["standalone_conversion"] is False
assert oracle["butterfly"]["montgomery_r_exponent_change"] == 0
assert oracle["proof"]["component_butterflies"] == 576
assert oracle["proof"]["input_cells_covered_once"] == 1152
assert oracle["proof"]["output_cells_covered_once"] == 1152

inputs = []
outputs = []
cell_by_key = {
    (cell["branch"], cell["gt_row_physical_trit_reversed"],
     cell["ntt16_lane_physical_bit_reversed"]): cell
    for cell in layout["cells"]
}
for butterfly in oracle["butterflies"]:
    inputs.extend(butterfly["input_positions_i16"].values())
    outputs.extend(butterfly["output_positions_i16"].values())
    branch = butterfly["branch"]
    row = butterfly["physical_row"]
    coefficient = butterfly["terminal_coefficient"]
    lanes = butterfly["physical_lanes"]
    cells = [cell_by_key[(branch, row, lane)] for lane in lanes]
    assert butterfly["frequency_q"] == [cell["ntt16_frequency_q"] for cell in cells]
    assert butterfly["factor_roots_mod_q"] == [cell["factor_mod_q"] for cell in cells]
    assert butterfly["official_component_positions_i16"] == [
        cell["positions"][coefficient]["official"]["position_i16"] for cell in cells]
assert sorted(inputs) == list(range(1152))
assert sorted(outputs) == list(range(1152))

rng = random.Random(0x61C1152)
checks = 0


def signed16(value):
    value %= 1 << 16
    return value - (1 << 16) if value >= (1 << 15) else value


def montgomery_reduce(value):
    low = signed16(signed16(value) * QINV)
    return (value - low * Q) >> 16


for row in oracle["rows"]:
    forward = row["forward_distance1_twiddle_mod_q"]
    inverse = row["inverse_distance1_twiddle_mod_q"]
    montgomery = row["inverse_distance1_twiddle_montgomery_signed"]
    qinv = row["inverse_distance1_twiddle_qinv_signed16"]
    for zeta, zeta_inverse, mont, low_constant in zip(forward, inverse, montgomery, qinv):
        assert zeta * zeta_inverse % Q == 1
        assert mont % Q == zeta_inverse * R % Q
        assert low_constant == signed16(mont * QINV)
        cases = [(-1728, -1728), (-1728, 1728), (1728, -1728),
                 (1728, 1728), (0, 0)]
        cases.extend((rng.randrange(Q), rng.randrange(Q)) for _ in range(TRIALS))
        for left, right in cases:
            even = (left + zeta * right) % Q
            odd = (left - zeta * right) % Q
            recovered_left = (even + odd) % Q
            recovered_right = zeta_inverse * (even - odd) % Q
            assert recovered_left == 2 * left % Q
            assert recovered_right == 2 * right % Q
            assert montgomery_reduce(signed16(even - odd) * mont) % Q == recovered_right
            checks += 1

for contract in oracle["range_contracts"].values():
    assert contract["all_intermediates_fit_signed_i16"]
    assert contract["extra_reduction_required"] is False
    for interval in (contract["sum_output"], contract["difference_before_montgomery"],
                     contract["twisted_difference_overall"]):
        assert -32768 <= interval[0] <= interval[1] <= 32767

gate = oracle["prototype_gate"]
assert gate["inverse_distance1_asm_authorized"] is True
assert gate["linked_BMScale_tail_plus_inverse_head_authorized"] is False
assert gate["cycles"] is None
print(f"G1C1 inverse distance1: 576 component butterflies, {checks} algebra trials, scale and i16 ranges passed")
