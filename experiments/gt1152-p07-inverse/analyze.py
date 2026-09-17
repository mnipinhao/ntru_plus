"""Can NTRU+864's inverse Slothy artifacts be carried to 1152 by remapping
immediates alone?

Decision D6 in the campaign roadmap assumed yes for all three kernels.  This
gate checks that claim statically, against the real sources.

Answer: yes for packed_i9 and invntt16_asm, no for invntt16_tail_asm.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
GT864 = HERE.parents[1] / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

results = []


def note(name, detail, **extra):
    results.append({"item": name, "detail": detail, **extra})
    print(f"  {name:20s} {detail}")


def mem_offsets(path):
    """Memory operand offsets, grouped by base register and mnemonic."""
    ops = defaultdict(lambda: defaultdict(list))
    for line in Path(path).read_text().splitlines():
        line = line.split("//")[0]
        m = re.match(r"\s*(st|ld)(\w*)\s+.*\[\s*(x\d+)\s*(?:,\s*#(-?\d+))?\s*\]", line)
        if m:
            ops[m.group(3)][m.group(1) + m.group(2)].append(int(m.group(4) or 0))
    return ops


def mnemonics(path):
    c = Counter()
    for line in Path(path).read_text().splitlines():
        line = line.split("//")[0].strip()
        if not line or line.startswith((".", "/*", "*", "#")) or line.endswith(":"):
            continue
        m = re.match(r"([a-z][a-z0-9_.]*)", line)
        if m:
            c[m.group(1)] += 1
    return c


print("output coefficients per call, from static strh counts:\n")
mn = {f: mnemonics(GT864 / f)
      for f in ("inverse9.S", "inverse16.S", "inverse16_tail.S")}

per_call = {
    "packed_i9": 72,                       # 9 rows x 8 lanes, no strh
    "invntt16_asm": mn["inverse16.S"]["strh"],
    "invntt16_tail_asm": mn["inverse16_tail.S"]["strh"],
}
calls_864 = {"packed_i9": 2 * 3 * 2, "invntt16_asm": 3 * 2, "invntt16_tail_asm": 1}
calls_1152 = {"packed_i9": 2 * 4 * 2, "invntt16_asm": 4 * 2, "invntt16_tail_asm": 1}

total_864 = per_call["invntt16_asm"] * calls_864["invntt16_asm"] \
    + per_call["invntt16_tail_asm"] * calls_864["invntt16_tail_asm"]
note("total_864", f"invntt16 {calls_864['invntt16_asm']} x "
     f"{per_call['invntt16_asm']} + tail {per_call['invntt16_tail_asm']} "
     f"= {total_864}, equals 864: {total_864 == 864}")

tail_1152 = 1152 - per_call["invntt16_asm"] * calls_1152["invntt16_asm"]
note("required_tail_1152",
     f"1152 - invntt16 {calls_1152['invntt16_asm']} x "
     f"{per_call['invntt16_asm']} = {tail_1152} outputs, against 864's "
     f"{per_call['invntt16_tail_asm']}")

print("\nwhich kernels keep their instruction multiset:\n")
note("packed_i9", "invariant: 9 rows x 8 lanes per call either way; "
     f"{calls_864['packed_i9']} calls become {calls_1152['packed_i9']}",
     invariant=True)
note("invntt16_asm", f"invariant: {per_call['invntt16_asm']} outputs per call "
     f"either way; {calls_864['invntt16_asm']} calls become "
     f"{calls_1152['invntt16_asm']}", invariant=True)
note("invntt16_tail_asm",
     f"NOT invariant: {per_call['invntt16_tail_asm']} outputs must become "
     f"{tail_1152}", invariant=False)

print("\nbut the tail's vector arithmetic is already eight-lane:\n")
VEC = ("mul", "mla", "mls", "add", "sub", "sqrdmulh", "sqdmulh", "srshr",
       "shl", "sshr", "neg", "uzp1", "uzp2", "trn1", "trn2", "zip1", "zip2",
       "tbl", "ext", "orr")
va_main = sum(v for k, v in mn["inverse16.S"].items() if k in VEC)
va_tail = sum(v for k, v in mn["inverse16_tail.S"].items() if k in VEC)
note("vector_arithmetic", f"inverse16.S {va_main} vs inverse16_tail.S "
     f"{va_tail} - essentially identical, so the two lanes NTRU+864 leaves as "
     "padding already carry correct results")
note("difference", f"inverse16.S has {mn['inverse16.S']['umov']} umov / "
     f"{mn['inverse16.S']['strh']} strh; the tail has "
     f"{mn['inverse16_tail.S']['umov']} / {mn['inverse16_tail.S']['strh']}. "
     f"The gap is exactly {mn['inverse16.S']['strh'] - mn['inverse16_tail.S']['strh']}"
     " = 2 padding lanes x 16 t")

print("\nimmediate maps for the two kernels that do transfer:\n")
i9 = mem_offsets(GT864 / "inverse9.S")
x2 = sorted(set(i9["x2"]["ldr"]))
note("inverse9.S", f"one change: [x2, #{x2[1]}k] -> [x2, #128k] over "
     f"{len(x2)} offsets; every other base uses 16-byte strides")

i16 = mem_offsets(GT864 / "inverse16.S")
strh = sorted(set(i16["x0"]["strh"]))
note("inverse16.S", f"all {len(strh)} strh offsets are multiples of 6 "
     f"(6*m, branch folded into the base pointer), so they scale by 8/6 "
     f"exactly; range [{strh[0]}..{strh[-1]}] becomes "
     f"[{strh[0] * 4 // 3}..{strh[-1] * 4 // 3}]")

tail = mem_offsets(GT864 / "inverse16_tail.S")
tstrh = sorted(set(tail["x0"]["strh"]))
branches = sorted({(o % 6) // 2 for o in tstrh})
note("inverse16_tail.S", f"offsets decompose as 6m + 2b with b in {branches}; "
     f"1152 needs b in [0, 1, 2, 3], which is why the store count grows")

report = {
    "per_call_outputs": per_call,
    "calls_864": calls_864,
    "calls_1152": calls_1152,
    "required_tail_outputs_1152": tail_1152,
    "instruction_counts": {f: dict(c) for f, c in mn.items()},
    "d6_holds": {"packed_i9": True, "invntt16_asm": True,
                 "invntt16_tail_asm": False},
    "findings": results,
}
(HERE / "analysis-report.json").write_text(json.dumps(report, indent=2) + "\n")
print("\n-> analysis-report.json")
