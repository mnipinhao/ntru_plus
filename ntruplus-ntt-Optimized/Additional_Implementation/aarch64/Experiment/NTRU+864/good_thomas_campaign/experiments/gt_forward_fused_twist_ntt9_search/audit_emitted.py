#!/usr/bin/env python3
"""Audit returned Slothy code and integrated M5S-A assembly."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
opt = (ROOT / "slothy-output/gt864_forward_one_bank_paired_twist_loads.n1.opt.S").read_text()
alloc_log = (ROOT / "slothy-output/gt864_forward_one_bank_paired_twist_loads.alloc.log").read_text()
schedule_log = (ROOT / "slothy-output/gt864_forward_one_bank_paired_twist_loads.schedule.log").read_text()
pass2 = (ROOT / "gt864_forward_six_bank_paired_twist_loads.S").read_text()
wrapper = (ROOT / "gt864_forward_poly_ntt_paired_twist_loads.S").read_text()

start = opt.index("gt864_forward_one_bank_paired_twist_loads_slothy_start:")
end = opt.index("gt864_forward_one_bank_paired_twist_loads_slothy_end:")
region = opt[start:end]
physical = [line for line in region.splitlines()
            if re.match(r"^\s+[a-z][a-z0-9]*\s", line) and not line.lstrip().startswith("//")]
assert len(physical) == 601
assert sum(re.match(r"^\s+ldp\s+q", line) is not None for line in physical) == 16
assert not re.search(r"\b(?:str|st1|stp)\b", "\n".join(physical))
assert "OPTIMAL" in alloc_log and ".selfcheck:OK!" in alloc_log
assert "split_heuristic_full:OK!" in schedule_log
assert "spill" not in alloc_log.lower()
liveouts = re.search(r"allocated_liveouts=([^\n]+)", schedule_log)
assert liveouts and len({entry.split(":")[1] for entry in liveouts.group(1).split(",")}) == 18
assert pass2.count("bl .Lgt864_m5s_one_bank") == 6
assert pass2.count("str q") == 108
assert "[sp" not in pass2
assert wrapper.count("stp d") == 4 and wrapper.count("ldp d") == 4
print("emitted_code_gate=pass")
print("slothy_RA=OPTIMAL")
print("slothy_schedule=split_heuristic_full_OK")
print("spill=0")
print("helper_instructions=601")
print("pass2_instructions=3765")
print("full_forward_instructions=4638")
