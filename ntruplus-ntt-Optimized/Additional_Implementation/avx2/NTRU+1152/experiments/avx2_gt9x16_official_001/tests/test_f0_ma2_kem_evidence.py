#!/usr/bin/env python3
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
run=root/"results/f0-ma2-kem-intel155h-20260825-002"
kat=json.loads((run/"kat.json").read_text()); assert kat["vectors"]==100
assert kat["request_byte_exact"] and kat["response_byte_exact"]
official=json.loads((run/"native-official-serious/stq-summary.json").read_text())["operations"]
candidate=json.loads((run/"native-candidate-serious/stq-summary.json").read_text())["operations"]
assert official["enc_cycles"]["observations"]==candidate["enc_cycles"]["observations"]==864
assert candidate["enc_cycles"]["stq2"] > official["enc_cycles"]["stq2"]
paired=json.loads((run/"fixed-elf-paired-summary.json").read_text())
assert paired["enc_direction_consistent"] and not paired["promotion_gate"]
assert len(paired["settings"])==4
for setting in paired["settings"].values():
    assert setting["enc_cycles"]["bootstrap_95_ci_cycles"][0] > 0
print("F0-MA2 KEM evidence: KAT pass; native and four fixed-ELF settings reject current caller")
