#!/usr/bin/env python3
"""Audit the linked M5N object symbols and generated assembly invariants."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OBJECT = ROOT / "build/gt864_forward_six_bank_pass2.o"
ASM = ROOT / "gt864_forward_six_bank_pass2.S"

nm = subprocess.run(["nm", str(OBJECT)], check=True, text=True,
                    stdout=subprocess.PIPE).stdout
assert re.search(r"\b_?gt864_forward_six_bank_pass2$", nm, re.M)
assert " U " not in nm and not re.search(r"^\s*U\s", nm, re.M)

text = ASM.read_text(encoding="utf-8")
assert "sp" not in "\n".join(
    raw.split("//", 1)[0] for raw in text.splitlines()
)
assert text.count("bl .Lgt864_one_bank") == 6
assert len(re.findall(r"^\s*str q[0-9]+, \[x6, #[0-9]+\]$", text, re.M)) == 108
assert not re.search(r"\b(?:stp|ldp)\b", text, re.I)

print(json.dumps({
    "gate": "gt864_forward_six_bank_linked_object",
    "status": "pass",
    "defined_public_symbol": "gt864_forward_six_bank_pass2",
    "undefined_symbols": 0,
    "helper_calls": 6,
    "direct_vector_stores": 108,
    "stack_instructions": 0,
}, indent=2, sort_keys=True))
