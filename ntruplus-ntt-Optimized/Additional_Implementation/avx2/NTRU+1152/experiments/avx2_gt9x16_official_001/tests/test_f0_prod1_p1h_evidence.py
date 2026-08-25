#!/usr/bin/env python3
"""Check the frozen P1-H structural and instruction-attribution evidence."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
audit = json.loads((ROOT / "generated/f0-prod1-p1h-audit.json").read_text())
schedule = json.loads((ROOT / "generated/f0-prod1-schedule.json").read_text())

assert audit["checkpoint"] == "F0-PROD1-ASM-P1-H"
wrapper = audit["wrapper"]
helper = audit["helper"]
assert wrapper["stack_reservation_bytes"] <= 2432
assert wrapper["dynamic_calls_per_forward"] == {"p1h_pair_helper": 4,
                                                  "top_split": 1}
assert wrapper["vzeroupper_static"] == 0
assert helper["calls"] == helper["stack_frame_bytes"] == 0
assert helper["vector_stack_accesses"] == helper["vzeroupper_static"] == 0
assert helper["official_representation_calls"] == []
assert helper["entry_mod32"] == 0
assert helper["text_alignment_bytes"] >= 32
assert helper["rodata_alignment_bytes"] >= 32
assert helper["regions"]["formation_pair0"]["opcodes"] == \
       helper["regions"]["formation_pair1"]["opcodes"]

attribution = audit["dynamic_instruction_attribution_per_forward"]
assert attribution["formation"]["maps"] == 36
assert attribution["formation"]["aligned_split_loads"] == 144
assert attribution["formation"]["routing_total"] == 576
assert attribution["formation"]["twist_montgomery_chains"] == 72
assert attribution["r2_first"] == {"radix3_bodies": 24,
                                    "reductions": 72,
                                    "transient_f0_stores": 72}
assert attribution["boundary"]["internal_helper_calls"] == 0
assert attribution["boundary"]["internal_vzeroupper"] == 0
assert audit["removed_staging"] == {"coefficient_bytes": 0,
                                     "pair_input_bytes": 0,
                                     "pair_output_bytes": 0,
                                     "scalar_gt_adapter_calls": 0}
assert audit["retained"]["top_split_materialization_bytes"] == 2304
assert schedule["decision"]["authorized_next"] == "F0-PROD1-ASM P1-H"
assert audit["decision"]["structural_gate"] == "passed"
assert audit["decision"]["producer_benchmark_authorized"]
assert not audit["decision"]["kem_benchmark_authorized"]
print("F0-PROD1 P1-H evidence: shape, 576-route attribution, ABI/alignment gates passed")
