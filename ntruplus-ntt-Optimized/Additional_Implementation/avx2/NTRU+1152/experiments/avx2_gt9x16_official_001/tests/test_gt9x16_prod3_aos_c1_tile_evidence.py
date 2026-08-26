#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
audit = json.loads(
    (ROOT / "generated/gt9x16-prod3-aos-c1-tile-audit.json").read_text())

assert audit["checkpoint"] == "GT9X16-PROD3-AOS-ASM0"
tile = audit["linked_tile"]
assert tile["input_loads"] == 4
assert tile["output_stores"] == 4
assert tile["routing_total"] == 24
assert tile["montgomery_chains"] == 4
assert tile["calls"] == 0
assert tile["conditional_branches"] == 0
assert tile["frame_instructions"] == 0
assert tile["stack_references"] == 0
assert tile["vector_spills"] == 0
assert tile["vzeroupper"] == 0
assert tile["entry_mod32"] == 0
assert audit["register_flow"]["peak_live_ymm"] == 9
assert audit["register_flow"]["spill_free"] is True
assert audit["alignment"]["rodata_section_alignment_bytes"] >= 32
assert audit["alignment"]["caller_pointer_alignment_required"] is False
assert audit["authorization"] == {
    "benchmark": False,
    "full_branch_asm": False,
    "full_producer_asm": False,
    "native_kem": False,
    "tile_machine_feasibility": True,
}
print("GT9X16-PROD3-AOS-ASM0 evidence passed")
