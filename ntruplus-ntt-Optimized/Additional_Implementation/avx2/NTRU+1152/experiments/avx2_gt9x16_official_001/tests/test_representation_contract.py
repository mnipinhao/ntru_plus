#!/usr/bin/env python3
"""Validate normalized component identity, physical ABIs, scales, and costs."""

import json
from pathlib import Path

experiment = Path(__file__).resolve().parents[1]
contract = json.loads((experiment / "generated/gt9x16-pipeline-layout.json").read_text())
cost = json.loads((experiment / "generated/gt9x16-representation-cost-matrix.json").read_text())
lifecycle = json.loads((experiment / "generated/ntt-domain-lifecycle-audit.json").read_text())

assert len(contract["cells"]) == 288
assert contract["physical_row_to_mathematical_p"] == [0, 3, 6, 1, 4, 7, 2, 5, 8]
assert contract["physical_lane_to_mathematical_q"] == [0, 8, 4, 12, 2, 10, 6, 14,
                                                        1, 9, 5, 13, 3, 11, 7, 15]
positions = {name: [] for name in ("official", "gt_row_terminal_lane",
                                    "gt_terminal_row_lane", "persistent_pair_sd")}
hybrid_forward = []
hybrid_inverse = []
for cell in contract["cells"]:
    assert cell["ntt9_frequency_p"] == contract["physical_row_to_mathematical_p"][
        cell["gt_row_physical_trit_reversed"]]
    assert cell["ntt16_frequency_q"] == contract["physical_lane_to_mathematical_q"][
        cell["ntt16_lane_physical_bit_reversed"]]
    assert cell["factor_polynomial"]["constant_term_mod_q"] == (-cell["factor_mod_q"]) % 3457
    assert set(cell["value_contract_ids"].values()) <= set(contract["value_contracts"])
    for terminal in cell["positions"]:
        for name in positions:
            positions[name].append(terminal[name]["position_i16"])
        hybrid = terminal["terminal_to_inverse_pair_hybrid"]
        hybrid_forward.append(hybrid["forward_and_arithmetic_input_position_i16"])
        hybrid_inverse.append(hybrid["arithmetic_output_and_inverse_position_i16"])
for name, mapped in positions.items():
    assert sorted(mapped) == list(range(1152)), name
assert hybrid_forward == positions["gt_row_terminal_lane"]
assert hybrid_inverse == positions["persistent_pair_sd"]
assert contract["value_contracts"]["resident-r0"]["scale_r_exponent"] == 0
assert contract["value_contracts"]["inverse-feed-rminus1"]["scale_r_exponent"] == -1
assert contract["value_contracts"]["kem-small-forward-r0"]["transform_scale"] == 1
assert contract["value_contracts"]["resident-r0"]["transform_scale"] == 1
assert contract["value_contracts"]["inverse-feed-rminus1"]["transform_scale"] == 1
assert contract["transform_scale_policy"]["paper_scaled_r3r3"] == 4
assert lifecycle["boundaries"]["scaled_basemul_inverse_feed"]["output_scale_r_exponent"] == -1
assert lifecycle["boundaries"]["inverse_load"]["expected_input_scale_r_exponent"] == -1
assert lifecycle["audit_conclusion"]["baseinv_has_denominator_side_channel"]
assert lifecycle["audit_conclusion"]["standalone_full_layout_passes"] == 0
assert not cost["standalone_full_layout_pass_allowed"]
assert cost["candidates"]["B_persistent_pair"]["basemul_boundary_routing_full_transform"] == 432
assert cost["candidates"]["C_terminal_to_inverse_pair_hybrid"]["basemul_boundary_routing_full_transform"] == 144
print("NTT-domain representation contract: 288 components, 1152 physical cells, scales and ABI costs passed")
