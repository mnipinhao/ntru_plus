"""Generate NTRU+1152's invntt16_tail_asm from NTRU+864's.

D6 established that this kernel cannot be carried over by remapping immediates:
it is called once and covers every component, so its output count grows with the
component count, 96 to 128.  D6 also established why that is the *whole* change:
the tail's vector arithmetic is eight-lane and entirely element-wise, so the
lanes 864 leaves as padding already hold correct results.

Reading the 864 kernel confirms it and makes the change exact.  Every one of its
589 instructions is element-wise except two kinds:

  1. the fold over `top`.  864 packs the tail scratch as lane = 3*top + branch,
     six lanes used of eight, and folds with

         ext vD.16B, vA.16B, vA.16B, #6      ; rotate three halfwords
         add vD.8H,  vA.8H,  vD.8H           ; vD[i] = vA[i] + vA[i+3]

     1152 packs lane = 4*top + branch, all eight lanes used, so the rotation
     becomes four halfwords: #6 -> #8.  There are exactly 32 such `ext`, all
     self-rotates, each paired with its `add`; this script asserts all of that.

  2. the output extraction.  864 writes out[27k + branch] for branch < 3, three
     halfwords, six bytes -- never a clean store width, so it spends three
     `umov` and three `strh` per output, 96 of each.  1152 writes
     out[36k + branch] for branch < 4: four halfwords, eight bytes, exactly one
     `str d` of the folded vector's low half.  96 umov + 96 strh become 32
     stores.  That is the same degree-4 alignment dividend the codec collected
     in P18.

Nothing else is touched.  The scratch is 16 vectors of eight lanes either way,
so the `[x1, #16t]` loads are unchanged, and the stage and terminal tables are
leaf-degree independent, so `x3`/`x4` are unchanged.

Slothy's cycle annotations are removed: they describe the 864 solve, and this
kernel is no longer that instruction sequence.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/inverse16_tail.S"

STRIDE_864, STRIDE_1152 = 27, 36     # int16 between consecutive outputs
DEG_864, DEG_1152 = 3, 4

raw = SRC.read_text().splitlines()
body = [l.split("//")[0].rstrip() for l in raw]

# ---- pass 1: the fold rotation -------------------------------------------
EXT = re.compile(r"^(\s*ext\s+v(\d+)\.16B,\s*v(\d+)\.16B,\s*v(\d+)\.16B,\s*#)6\s*$", re.I)
ADD = lambda d, a: re.compile(rf"^\s*add\s+v{d}\.8H,\s*v{a}\.8H,\s*v{d}\.8H\s*$", re.I)

folds = 0
for i, l in enumerate(body):
    m = EXT.match(l)
    if not m:
        assert not re.match(r"\s*ext\s", l, re.I), f"unexpected ext: {l}"
        continue
    d, a, b = m.group(2), m.group(3), m.group(4)
    assert a == b, f"ext is not a self-rotate: {l}"
    assert any(ADD(d, a).match(body[j]) for j in range(i + 1, min(i + 8, len(body)))), \
        f"ext #6 with no matching add fold: {l}"
    body[i] = m.group(1) + "8"
    folds += 1
assert folds == 32, f"expected 32 folds, found {folds}"

# ---- pass 2: the output extraction ----------------------------------------
UMOV = re.compile(r"^\s*umov\s+w(\d+),\s*v(\d+)\.h\[(\d+)\]\s*$")
STRH = re.compile(r"^\s*strh\s+w(\d+),\s*\[x0(?:,\s*#(\d+))?\]\s*$")

held = {}            # gpr -> (vreg, lane, index of its umov in `body`)
store_at = {}        # body index of an output's first umov -> (vreg, k)
umovs = strhs = 0
for i, l in enumerate(body):
    m = UMOV.match(l)
    if m:
        held[m.group(1)] = (int(m.group(2)), int(m.group(3)), i)
        umovs += 1
        continue
    m = STRH.match(l)
    if m:
        gpr, off = m.group(1), int(m.group(2) or 0)
        vreg, lane, at = held.pop(gpr)
        k, branch = divmod(off // 2, STRIDE_864)
        assert branch < DEG_864 and branch == lane, f"lane/branch mismatch at {l}"
        strhs += 1
        # The store must sit where the umov did, not where the strh did: Slothy
        # reuses these vector registers aggressively and several of them are
        # overwritten between an output's umov and its strh.  The umov is a
        # point where the value is provably still live.
        if k not in {kk for _, kk in store_at.values()}:
            store_at[at] = (vreg, k)
            continue
        assert store_at[min(j for j, (_, kk) in store_at.items() if kk == k)][0] == vreg, \
            f"output {k} extracted from more than one register"

out = []
for i, l in enumerate(body):
    if i in store_at:
        vreg, k = store_at[i]
        out.append(f"        str d{vreg}, [x0, #{2 * STRIDE_1152 * k}]")
        continue
    if UMOV.match(l) or STRH.match(l):
        continue
    out.append(l)

emitted = {k for _, k in store_at.values()}
assert umovs == 96 and strhs == 96, (umovs, strhs)
assert emitted == set(range(32)), sorted(emitted)
assert not held, held

# ---- header ---------------------------------------------------------------
head = f"""#ifdef __APPLE__
#define invntt16_tail_asm _invntt16_tail_asm
#endif
.text
.global invntt16_tail_asm
invntt16_tail_asm:
// NTRU+1152 invntt16 tail.  Generated by gt1152-p22-tail-asm/generate_tail.py
// from NTRU+864's inverse16_tail.S; do not edit.  Two changes only: the fold
// over `top` rotates four halfwords instead of three, because 1152 packs the
// tail scratch as lane = 4*top + branch rather than 3*top + branch; and each
// output's three umov/strh pairs become one `str d`, because four branches are
// eight contiguous bytes where three were six.  Every other instruction is
// element-wise and carries unchanged.
//
// live-in: x0 output, x1 packed scratch, x3 stage table, x4 composite terminal
// live-out: 32 eight-byte stores at x0 + 72k, k = 0..31
// Slothy annotations removed: they describe the 864 solve, not this sequence.
"""
text = [l for l in out if not re.match(r"^\s*(#ifdef|#define|#endif|\.text|\.global|invntt16_tail_asm:)", l)]
text = [l for l in text if l.strip() and not l.strip().startswith("invntt16_tail_asm_slothy")]

dst = HERE / "inverse16_tail.S"
dst.write_text(head + "\n".join(text) + "\n")
n = sum(1 for l in text if re.match(r"\s+[a-z]", l))
print(f"wrote {dst.name}: {n} instructions "
      f"(864 had 589; -192 umov/strh, +32 str d)")

# ---- the terminal table -----------------------------------------------------
#
# Reading the kernel settles which tables need repacking and which do not.  The
# x3 table (invntt16_constants) is loaded six times and every one of its 35 uses
# is lane-indexed, so it is a constant pool and carries unchanged.  The x4 table
# (invntt16_tail_constants) is loaded 64 times, once per row, and every use is a
# full-vector multiply -- its lanes line up with the data lanes, so it is packed
# for 864's lane = 3*top + branch:
#
#     [A, A, A, B, B, B, 0, 0]        three lanes of top 0, three of top 1
#
# 1152's lane = 4*top + branch needs
#
#     [A, A, A, A, B, B, B, B]
#
# This asserts the 864 shape row by row before rewriting it.
import json

TABLES = HERE.parents[1] / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/inverse16_tables.h"
src = TABLES.read_text()
blk = src.split("invntt16_tail_constants[64][8] = {", 1)[1]
rows = [[int(x) for x in r.replace("\n", " ").split(",") if x.strip()]
        for r in re.findall(r"\{([^}]*)\}", blk)[:64]]
assert len(rows) == 64 and all(len(r) == 8 for r in rows)

new = []
for i, r in enumerate(rows):
    a, b = r[0], r[3]
    assert r == [a, a, a, b, b, b, 0, 0], f"row {i} is not [A,A,A,B,B,B,0,0]: {r}"
    new.append([a] * 4 + [b] * 4)

# Emit the whole header: invntt16_main_constants unchanged (invntt16_asm packs
# its lanes by the 16-axis, not by (top, branch), so it needs no repacking), and
# invntt16_tail_constants repacked.
head_main = src.split("static const int16_t invntt16_tail_constants")[0]
head_main = head_main.replace(
    "#ifndef", "/* NTRU+1152 inverse16 tables.  Generated by\n"
    " * gt1152-p22-tail-asm/generate_tail.py from NTRU+864's inverse16_tables.h;\n"
    " * do not edit.  invntt16_main_constants is unchanged -- invntt16_asm packs its\n"
    " * lanes by the 16-axis, not by (top, branch).  Each invntt16_tail_constants row\n"
    " * is repacked from [A,A,A,B,B,B,0,0] to [A,A,A,A,B,B,B,B], because the tail\n"
    " * multiplies them full-vector against a scratch whose lane is 3*top+branch at\n"
    " * 864 and 4*top+branch at 1152.  No value changes. */\n#ifndef", 1)
hdr = [head_main.rstrip("\n"), "static const int16_t invntt16_tail_constants[64][8] = {"]
for r in new:
    hdr.append("    {" + ",".join(f"{v:6d}" for v in r) + "},")
hdr += ["};", "", "#endif", ""]
(HERE / "inverse16_tables.h").write_text("\n".join(hdr))
print("wrote inverse16_tables.h: 64 tail rows repacked 3+3+2 -> 4+4, main unchanged")
