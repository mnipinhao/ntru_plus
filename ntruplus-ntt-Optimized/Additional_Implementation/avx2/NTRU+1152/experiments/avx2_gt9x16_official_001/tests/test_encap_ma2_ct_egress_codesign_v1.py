#!/usr/bin/env python3
"""Evidence gates for exact machine-liveness and H4 terminal ownership."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
live = json.loads((ROOT / "generated/h3-machine-def-use-liveness.json").read_text())
h4 = json.loads((ROOT / "generated/encap-ma2-ct-egress-codesign-v1.json").read_text())

assert live["peak_live_ymm"] == 16
assert live["terminal_store_count"] == 72
assert live["minimum_terminal_free_ymm"] == 3
assert live["terminal_stores_with_zero_free_ymm"] == 0
assert live["gates"]["machine_def_use_not_symbolic_annotation"]

assert len(h4["terminal_order"]) == 72
assert sum(len(x["coefficient_ownership"]) for x in h4["terminal_order"]) == 1152
assert len(h4["serializer_pair_intervals"]) == 576
assert h4["h4a_terminal_normalization"]["hooks_feasible_without_reschedule"] == 72
assert h4["h4a_terminal_normalization"]["hooks_blocked_by_zero_machine_slack"] == []
assert h4["h4b_full_byte_egress"]["all_true_12bit_pairs_cross_ma2_vectors"]
assert h4["h4b_full_byte_egress"]["maximum_pending_pairs"] == 16
assert h4["h4b_full_byte_egress"]["minimum_full_ymm_at_max_frontier"] == 1
assert h4["h4b_full_byte_egress"]["one_or_two_pack_accumulator_assumption_supported"]
assert h4["gates"]["no_h4_asm_generated"]
print("H4 MAP: 72 live hooks, min 3 free YMM, one-YMM pending-pair frontier")
