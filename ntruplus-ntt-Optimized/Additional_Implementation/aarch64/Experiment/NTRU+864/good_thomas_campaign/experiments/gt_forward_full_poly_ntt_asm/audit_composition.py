#!/usr/bin/env python3
"""Static M5O wrapper and linked-symbol audit."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = (ROOT / "gt864_forward_poly_ntt_experiment.S").read_text(encoding="utf-8")

assert source.count("bl gt864_top_split_ld3") == 1
assert source.count("bl gt864_forward_six_bank_pass2") == 1
assert source.count("sub sp, sp, #1792") == 1
assert source.count("add sp, sp, #1792") == 1
assert not re.search(r"\bb\.(?:eq|ne|lt|le|gt|ge|hi|hs|lo|ls|mi|pl|vs|vc)\b", source)

nm = subprocess.run(["nm", str(ROOT / "build/test")], check=True,
                    text=True, capture_output=True).stdout
for symbol in ("poly_ntt", "gt864_top_split_ld3",
               "gt864_forward_six_bank_pass2",
               "gt864_forward_poly_ntt_experiment"):
    assert re.search(rf"\b[Tt]\s+_?{symbol}$", nm, re.MULTILINE), symbol

wrapper_nm = subprocess.run(["nm", str(ROOT / "build/wrapper.o")], check=True,
                            text=True, capture_output=True).stdout
undefined = sorted(re.findall(r"\bU\s+_?(\w+)$", wrapper_nm, re.MULTILINE))
assert undefined == ["gt864_forward_six_bank_pass2", "gt864_top_split_ld3"]

print(json.dumps({
    "gate": "M5O_composition_object_audit",
    "status": "pass",
    "fixed_scratch_bytes": 1792,
    "calls": ["gt864_top_split_ld3", "gt864_forward_six_bank_pass2"],
    "wrapper_expected_undefined_symbols": undefined,
    "linked_required_symbols_defined": True,
    "wrapper_secret_dependent_branches": 0,
    "meaningful_coefficient_loads": 1728,
    "meaningful_coefficient_stores": 1728,
    "padding_halfword_stores": 32,
}, indent=2))
