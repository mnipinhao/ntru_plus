#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated" /
                   "gt9x16-prod3-natural-q-t0-beta-schedule.json").read_text())
constants = (ROOT / "generated" /
             "gt9x16-prod3-natural-q-t0-beta-constants.inc").read_text()

assert data["schema"] == "gt9x16-prod3-natural-q-t0-beta-schedule/v1"
assert data["frozen_contract"] == {
    "qorder": "C1-natural-Q", "top_split_changed": False,
    "paper_R2_changed": False, "D_stage_order": ["D8", "D4", "D2", "D1"],
    "radix2_chain_positions_changed": False, "transform_scale": 4,
    "montgomery_r_exponent": 0, "range_repair_added": False,
}

schedule = data["exact_schedule"]
assert len(schedule["branches"]) == 2
for branch in schedule["branches"]:
    alpha = branch["pass_A_alpha_schedule"]
    assert len(alpha) == 9
    assert sum(row["chains_per_qblock"] * row["qblocks"] for row in alpha) == 32
    assert [row["physical_row"] for row in alpha if row["action"] == "raw-load"] == [0]
    radix = branch["pass_B_branch_specific_radix2"]
    assert len(radix) == 9
    assert all([stage["stage"] for stage in row["stages"]] ==
               ["distance8", "distance4", "distance2", "distance1"]
               for row in radix)
    assert all(not stage["chain_positions_changed"] and
               not stage["packing_geometry_changed"]
               for row in radix for stage in row["stages"])

proof = data["montgomery_representation_proof"]
assert proof["exact_cases"] == (16 + 270) * 65536
assert proof["same_scale"] == 4
assert proof["same_r_exponent"] == 0

chains = data["montgomery_chain_ledger_per_forward"]
assert chains["current"]["total"] == 296
assert chains["candidate"]["total"] == 288
assert chains["delta"]["total"] == -8
assert chains["encap_two_forward_delta"] == -16

operands = data["constant_memory_operand_ledger_per_forward"]
assert operands["current"] == {"T0": 144, "NTT16": 288,
                               "other_unchanged": 234, "total": 666}
assert operands["candidate"] == {"alpha_normalization": 128,
                                 "combined_NTT16": 288,
                                 "other_unchanged": 234, "total": 650}
assert operands["delta"]["total"] == -16
assert operands["new_explicit_constant_loads"] == 0
assert operands["new_table_selection_instructions"] == 0

footprint = data["constant_table_footprint"]
assert footprint["current"]["total_vectors"] == 270
assert footprint["candidate"]["total_vectors"] == 284
assert footprint["delta_bytes"] == 448

machine = data["predicted_linked_machine_ledger_per_forward"]
assert machine["current"]["instructions"] == 2819
assert machine["candidate"]["instructions"] == 2787
assert machine["delta"] == {
    "instructions": -32, "vpmullw": -8, "vpmulhw": -16,
    "vpsubw": -8, "barrett": 0, "data_loads": 0,
    "data_stores": 0, "routing": 0, "spill": 0}
assert machine["text_byte_delta"] is None

ranges = data["range_and_pressure_gate"]
assert ranges["interval_nodes_checked"] > 200
assert ranges["candidate_global_i16"] == [-21333, 21333]
assert ranges["all_preoperations_signed_i16"] is True
assert ranges["new_reductions"] == 0
assert ranges["new_register_temporaries"] == 0
assert ranges["peak_live_ymm_upper_bound"] == 16

decision = data["decision"]
assert decision["schedule_gate_passed"] is True
assert decision["new_movement_debt"] is False
assert decision["constant_operand_penalty"] is False
assert decision["asm_authorized"] is True
assert decision["benchmark_authorized"] is False
assert decision["native_kem_authorized"] is False

assert constants.startswith(
    "/* Generated T0-BETA-TO-RADIX2 schedule constants; no ASM. */\n"
    ".section .rodata\n")
assert constants.count(".p2align 5") == 284
labels = re.findall(r"^(\.Lprod3_t0b_[^:]+):$", constants, re.MULTILINE)
assert len(labels) == 284 and len(set(labels)) == 284
print("T0 beta exact schedule: chain, constant-memory, range, and alignment gates passed")
