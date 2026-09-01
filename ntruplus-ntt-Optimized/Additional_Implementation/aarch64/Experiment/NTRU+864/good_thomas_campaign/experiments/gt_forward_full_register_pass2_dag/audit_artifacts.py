#!/usr/bin/env python3
"""Machine-check M5R-B instruction, register, memory, and wrapper ABI gates."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASM = ROOT / "gt864_forward_six_bank_full_register.S"
WRAPPER = ROOT / "gt864_forward_poly_ntt_full_register.S"
OPT = ROOT / "slothy-output/gt864_forward_one_bank_full_register_pinned.n1.opt.S"
RA_LOG = ROOT / "slothy-output/gt864_forward_one_bank_full_register_pinned.ra.log"
SCHED_LOG = ROOT / "slothy-output/gt864_forward_one_bank_full_register_pinned.schedule.log"


def instructions(text: str, start: str, end: str) -> list[str]:
    body = text[text.index(start + ":") + len(start) + 1:text.index(end + ":")]
    result = []
    for raw in body.splitlines():
        code = raw.split("//", 1)[0].strip()
        if code and not code.startswith(".") and not code.endswith(":"):
            result.append(code)
    return result


def main() -> None:
    asm = ASM.read_text(encoding="utf-8")
    wrapper = WRAPPER.read_text(encoding="utf-8")
    opt = OPT.read_text(encoding="utf-8")
    helper = instructions(asm, ".Lgt864_m5r_one_bank",
                          "gt864_forward_six_bank_pass2_full_register_end")[:-1]
    optimized = instructions(opt,
        "gt864_forward_one_bank_full_register_pinned_slothy_start",
        "gt864_forward_one_bank_full_register_pinned_slothy_end")
    assert helper == optimized
    assert len(helper) == 617
    assert not any(line.startswith(("str", "st1", "stp")) for line in helper)
    assert not any("[sp" in line or line.startswith("sub sp") for line in helper)
    assert not any(line.startswith("orr ") for line in helper)
    assert sum(line.startswith("ld1 ") for line in helper) == 16
    assert sum(line.startswith("ldr ") for line in helper) == 69
    assert not any("[x5" in line for line in helper)
    helper_text = "\n".join(helper)
    assert all(re.search(rf"\bv{reg}\b", helper_text) for reg in range(8, 16))

    assert asm.count("bl .Lgt864_m5r_one_bank") == 6
    assert len(re.findall(r"^\s*str q\d+, \[x6, #\d+\]$", asm, re.M)) == 108
    assert asm.count("adr x5, .Lgt864_m5r_common") == 1
    assert asm.count("ldp q14, q15, [x5], #32") == 1
    assert asm.count("ldr q13, [x5]") == 1
    assert len(re.findall(r"^\s*adr x[23], \.Lgt864_m5r_ntt(?:16|9)_top[01]$", asm, re.M)) == 12

    assert wrapper.count("stp d") == 4 and wrapper.count("ldp d") == 4
    for reg in range(8, 16):
        assert re.search(rf"\bd{reg}\b", wrapper)
    assert "[sp, #-96]!" in wrapper and "[sp], #96" in wrapper

    ra = RA_LOG.read_text(encoding="utf-8")
    schedule = SCHED_LOG.read_text(encoding="utf-8")
    assert "Instructions in body: 617" in ra
    assert "OPTIMAL" in ra and ".selfcheck:OK!" in ra
    assert "split.split_heuristic_full:OK!" in schedule
    assert "allocated_liveouts=" in schedule
    assert "spill" not in (ra + schedule).lower()

    pass2 = 4 + 3 + 6 * 6 + 108 + 6 * 617 + 6 + 2
    full = 24 + 849 + pass2
    result = {
        "one_bank_instructions": len(helper),
        "copies_removed_per_bank": 13,
        "hoisted_constant_loads_per_bank": 3,
        "meaningful_coefficient_loads_per_bank": 32,
        "coefficient_stores_inside_bank": 0,
        "new_memory_boundaries": 0,
        "pass2_dynamic_instructions": pass2,
        "baseline_pass2_dynamic_instructions": 3960,
        "pass2_reduction": 3960 - pass2,
        "full_dynamic_instructions": full,
        "baseline_full_dynamic_instructions": 4825,
        "full_reduction_after_abi_cost": 4825 - full,
        "official_dynamic_instructions": 4028,
        "remaining_instruction_gap": full - 4028,
        "d8_d15_save_restore_instructions": 8,
    }
    assert pass2 == 3861 and full == 4734
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
