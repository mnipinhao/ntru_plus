#!/usr/bin/env python3
"""Keep the positive radix-3 Barrett-Shoup pair live in the two unused Q regs."""

from pathlib import Path
import hashlib
import json
import re

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
SOURCE = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/gt864_native_inverse9.S"
OUTPUT = P / "build/gt864_native_inverse9_b1.S"
OUTPUT.parent.mkdir(exist_ok=True)

text = SOURCE.read_text()
assert not re.search(r"\bv(?:0|5)\b", text, re.I), "v0/v5 are no longer free"

constant_register = {722: "v0", 6844: "v5"}
gpr_constant: dict[str, int] = {}
active: dict[str, str] = {}
removed_mov = {value: 0 for value in constant_register}
removed_dup = {value: 0 for value in constant_register}
replaced_uses = {value: 0 for value in constant_register}
out = []

write_first = {"ldr", "ld1", "mov", "dup", "add", "sub", "mul", "sqrdmulh",
               "orr", "trn1", "trn2", "ext", "mls", "and", "sshr", "cmgt"}

for raw in text.splitlines():
    stripped = raw.split("//", 1)[0].strip()
    mov = re.match(r"mov\s+(w\d+),\s*#(\d+)$", stripped, re.I)
    if mov:
        reg, value = mov.group(1).lower(), int(mov.group(2))
        gpr_constant[reg] = value
        if value in constant_register:
            removed_mov[value] += 1
            continue

    dup = re.match(r"dup\s+(v\d+)\.8h,\s*(w\d+)$", stripped, re.I)
    if dup and gpr_constant.get(dup.group(2).lower()) in constant_register:
        value = gpr_constant[dup.group(2).lower()]
        active[dup.group(1).lower()] = constant_register[value]
        removed_dup[value] += 1
        continue

    rewritten = raw
    for old, new in list(active.items()):
        # Rewrite sources, never the destination.  A destructive operation
        # such as `sqrdmulh v31.8h, v2.8h, v31.8h` both consumes the old
        # constant and overwrites its register; killing the interval before
        # replacing that final source silently leaves an uninitialised use.
        comma = rewritten.find(",")
        prefix = rewritten[:comma + 1] if comma >= 0 else rewritten
        sources = rewritten[comma + 1:] if comma >= 0 else ""
        count = len(re.findall(rf"\b{old}(?=\.)", sources, re.I))
        if count:
            sources = re.sub(rf"\b{old}(?=\.)", new, sources, flags=re.I)
            rewritten = prefix + sources
            value = next(v for v, reg in constant_register.items() if reg == new)
            replaced_uses[value] += count
    out.append(rewritten)

    instruction = re.match(r"([a-z0-9.]+)\s+([^,\s]+)", stripped, re.I)
    if instruction and instruction.group(1).lower() in write_first:
        # AArch64 names the same physical SIMD register as Vn/Qn/Dn/Sn/Hn/Bn.
        # In particular, an `ldr q14, ...` must terminate an older V14
        # constant live interval.  Treating only the V spelling as a write
        # silently rewrites later table operands and breaks the transform.
        first = re.match(r"[vqdshb](\d+)", instruction.group(2), re.I)
        if first:
            active.pop("v" + first.group(1), None)
    if stripped == "packed_i9_slothy_start:":
        out.extend([
            "        // P7-B1: v0/v5 were unused; retain one Barrett-Shoup pair.",
            "        mov w8, #722",
            "        dup v0.8H, w8",
            "        mov w8, #6844",
            "        dup v5.8H, w8",
        ])

assert removed_mov == {722: 6, 6844: 6}, removed_mov
assert removed_dup == {722: 6, 6844: 6}, removed_dup
assert all(value >= 6 for value in replaced_uses.values()), replaced_uses
generated = "\n".join(out) + "\n"
OUTPUT.write_text(generated)

def instruction_count(source: str) -> int:
    total = 0
    for raw in source.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line and not line.endswith(":") and not line.startswith((".", "#", "/*", "*")):
            total += 1
    return total

before = instruction_count(text)
after = instruction_count(generated)
assert before - after == 20, (before, after)
report = {
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "candidate_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
    "persistent_constants": {str(k): v for k, v in constant_register.items()},
    "removed_mov": removed_mov,
    "removed_dup": removed_dup,
    "replaced_uses": replaced_uses,
    "instructions_before_including_ret": before,
    "instructions_after_including_ret": after,
    "saving_per_call": before - after,
    "saving_per_complete_inverse": 12 * (before - after),
    "new_spills": 0,
    "coefficient_memory_boundary_change": 0,
}
(P / "p7b1-generation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
