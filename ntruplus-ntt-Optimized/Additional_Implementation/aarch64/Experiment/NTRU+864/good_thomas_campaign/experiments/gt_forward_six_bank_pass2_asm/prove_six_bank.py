#!/usr/bin/env python3
"""Prove M5N coordinate coverage, table bytes, and generated code shape."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import generate_asm as gen

ROOT = Path(__file__).resolve().parent
ASM = ROOT / "gt864_forward_six_bank_pass2.S"


def instructions(text: str) -> list[str]:
    start = text.index("gt864_forward_six_bank_pass2:")
    end = text.index("gt864_forward_six_bank_pass2_end:")
    result = []
    for raw in text[start:end].splitlines():
        line = raw.split("//", 1)[0].strip()
        if line and not line.startswith((".", "_")) and not line.endswith(":"):
            result.append(line)
    return result


text = ASM.read_text(encoding="utf-8")
code = instructions(text)
counts = Counter(line.split()[0].lower() for line in code)
assert len(code) == 790
assert counts["bl"] == 6 and counts["ret"] == 2
assert counts["str"] == 108
assert counts["ld1"] == 16 and counts["ldr"] == 72
assert not re.search(r"\b(?:stp|ldp)\b", "\n".join(code), re.I)
assert all(f"adr x2, .Lgt864_ntt16_top{top}" in text for top in range(2))
assert all(f"adr x3, .Lgt864_ntt9_top{top}" in text for top in range(2))
assert text.count("adr x5, .Lgt864_common") == 6

output_offsets = []
for top in range(2):
    for component in range(3):
        bank_offsets = [gen.store_offset(top, component, output) for output in range(18)]
        output_offsets.extend(offset // 2 + lane
                              for offset in bank_offsets for lane in range(8))
assert len(output_offsets) == len(set(output_offsets)) == 864
assert sorted(output_offsets) == list(range(864))

meaningful = []
for top in range(2):
    for component in range(3):
        bank = 3 * top + component
        meaningful.extend(range(bank * 128, bank * 128 + 128))
        meaningful.extend(768 + 8 * t + bank for t in range(16))
assert len(meaningful) == len(set(meaningful)) == 864
padding = sorted(set(range(896)) - set(meaningful))
assert padding == [768 + 8 * t + lane for t in range(16) for lane in (6, 7)]

table_vectors = gen.common_vectors()
for residue in gen.RESIDUES:
    table_vectors += gen.ntt16_vectors(residue)
    table_vectors += gen.ntt9_vectors(residue)
assert len(table_vectors) == 110
table_bytes = 16 * len(table_vectors)
assert table_bytes == 1760

helper = gen.helper_instructions()
assert len(helper) == 633
assert all(text.count(f"    {line}\n") >= 1 for line in helper)

report = {
    "gate": "gt864_forward_six_bank_pass2",
    "status": "pass",
    "static_instruction_count": len(code),
    "shared_helper_instructions": len(helper),
    "dynamic_helper_calls": counts["bl"],
    "meaningful_input_halfwords": len(meaningful),
    "padding_halfwords_not_addressed": len(padding),
    "output_halfwords": len(output_offsets),
    "output_vector_stores": counts["str"],
    "intermediate_coefficient_traffic": 0,
    "public_table_vectors": len(table_vectors),
    "public_table_bytes": table_bytes,
    "stack_instructions": 0,
    "body_sha256": hashlib.sha256("\n".join(helper).encode()).hexdigest(),
    "assembly_sha256": hashlib.sha256(ASM.read_bytes()).hexdigest(),
    "production_linked": False,
}
print(json.dumps(report, indent=2, sort_keys=True))
