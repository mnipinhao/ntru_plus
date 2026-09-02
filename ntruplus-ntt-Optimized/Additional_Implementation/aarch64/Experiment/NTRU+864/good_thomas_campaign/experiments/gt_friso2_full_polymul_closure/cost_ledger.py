#!/usr/bin/env python3
"""Whole-product lower-bound ledger using already measured CF0/B1 evidence."""

import json

forward_absorption_instructions = 292
forward_absorption_cycles = 398.678
basemul_instruction_saving = 361
basemul_cycle_saving = 334.194
inverse_row_mulmods = 64
algorithm10_instructions = 3

inverse_arithmetic_instructions = inverse_row_mulmods * algorithm10_instructions
pre_inverse_cycle_deficit = 2 * forward_absorption_cycles - basemul_cycle_saving
static_lower_bound = (2 * forward_absorption_instructions
                      - basemul_instruction_saving
                      + inverse_arithmetic_instructions)

print(json.dumps({
    "gate": "gt864_friso2_full_polymul_cost_ledger",
    "status": "reject_cf0_composition",
    "relative_to": "2*M5R-D_FR0_Forward + staged_FRISO2-equivalent_BaseMul + FR0_Inverse",
    "two_forward_instruction_delta": 2 * forward_absorption_instructions,
    "direct_basemul_instruction_delta": -basemul_instruction_saving,
    "inverse_row_mulmods": inverse_row_mulmods,
    "inverse_arithmetic_instruction_delta": inverse_arithmetic_instructions,
    "whole_product_instruction_delta_lower_bound": static_lower_bound,
    "lower_bound_excludes_inverse_public_constant_loads": True,
    "two_forward_cycle_delta_measured": 2 * forward_absorption_cycles,
    "direct_basemul_cycle_delta_measured": -basemul_cycle_saving,
    "cycle_deficit_before_inverse_delta": pre_inverse_cycle_deficit,
    "full_path_pi5_run_authorized_by_evidence": False,
    "reason": "the two measured Forward penalties already exceed the measured BaseMul saving before adding the direct-Inverse correction",
    "production_linked": False,
}, indent=2, sort_keys=True))
