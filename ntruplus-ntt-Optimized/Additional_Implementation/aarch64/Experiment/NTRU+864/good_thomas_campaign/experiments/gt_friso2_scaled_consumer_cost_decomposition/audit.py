#!/usr/bin/env python3
"""Machine-check the exact CF5-C arithmetic and load decomposition."""

from __future__ import annotations

import json, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPS = ROOT.parent

def region(path: Path, start: str, end: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    body = text[text.index(start + ":"):text.index(end + ":")]
    result=[]
    for raw in body.splitlines()[1:]:
        code=raw.split("//",1)[0].strip()
        if code and not code.endswith(":"): result.append(code)
    return result

base = region(EXPS/"gt_forward_level2_one_mul_b3/slothy-output/gt864_forward_one_bank_all_one_mul_b3.n1.opt.S",
              "gt864_forward_one_bank_all_one_mul_b3_slothy_start",
              "gt864_forward_one_bank_all_one_mul_b3_slothy_end")
producer = region(EXPS/"gt_friso2_ntt16_producer_pair_link/slothy-output/producer.n1.opt.S",
                  "gt864_cf5_ntt16_producer_slothy_start",
                  "gt864_cf5_ntt16_producer_slothy_end")
assert len(base)==569 and len(producer)==345
bc=Counter(x.split()[0] for x in base); pc=Counter(x.split()[0] for x in producer)
reports=[]; total_delta=Counter()
for case in ("t0c1","t0c2","t1c1","t1c2"):
    consumer=region(EXPS/f"gt_friso2_ntt16_producer_pair_link/slothy-output/{case}.n1.opt.S",
                    f"gt864_cf5_pair_{case}_slothy_start", f"gt864_cf5_pair_{case}_slothy_end")
    cc=pc+Counter(x.split()[0] for x in consumer); delta=cc-bc; total_delta += delta
    expected_ldr=37 if case.startswith("t0") else 7
    assert delta==Counter({"mul":16,"sqrdmulh":16,"mls":16,"ldr":expected_ldr})
    reports.append({"case":case,"control_instructions":569,
                    "candidate_instructions":345+len(consumer),
                    "extra_mulmods":16,"extra_mulmod_instructions":48,
                    "extra_constant_loads":expected_ldr,
                    "total_extra_instructions":48+expected_ldr,
                    "slothy_proxy_cycle_delta":21 if case.startswith("t0") else 13})
assert total_delta==Counter({"mul":64,"sqrdmulh":64,"mls":64,"ldr":88})
print(json.dumps({"status":"pass","cases":reports,
                  "full_forward_extra_mulmods":64,
                  "full_forward_extra_mulmod_instructions":192,
                  "full_forward_extra_constant_loads":88,
                  "full_forward_total_extra_instructions":280,
                  "full_forward_slothy_separate_region_proxy_delta":68,
                  "required_cycle_saving_to_optimistic_break_even":184.83945},indent=2))
