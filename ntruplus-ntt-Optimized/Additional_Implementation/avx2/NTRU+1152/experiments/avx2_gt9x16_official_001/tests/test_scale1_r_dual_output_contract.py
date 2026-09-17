#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
doc = json.loads((root / "generated/scale1-r-dual-output-fanout-contract.json").read_text())
assert doc["representation"]["cells"] == 1152
assert doc["representation"]["scale"] == 1
assert doc["representation"]["montgomery_exponent"] == 0
assert doc["representation"]["mapping_bijection"]
assert doc["consumers"]["ma2"]["requires_input_unchanged"]
assert doc["consumers"]["hash_fanout"]["requires_input_unchanged"]
assert doc["alias_contract"]["ma2_may_read_r_after_hash_fanout"]
assert doc["decision"]["contract_frozen"]
print("scale-1 r dual-output/fanout contract: ok")
