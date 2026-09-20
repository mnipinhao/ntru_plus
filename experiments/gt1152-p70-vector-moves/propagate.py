#!/usr/bin/env python3
"""P70: copy-propagate the 32 pure vector moves out of invntt16_asm.

Every one has the shape `orr vD.16B, vS.16B, vS.16B` -- a vector move, the
residue of an in-place butterfly that is no longer in place.  Slothy preserves
the instruction multiset by design, so no amount of scheduling removes them.

For a move vD <- vS at i, walk forward:
  * a read of vD is rewritten to vS, and is safe as long as vS has not been
    DEFINED by an earlier instruction -- a definition at the same index happens
    after the read, so it does not block that read;
  * a definition of vS ends the interval after that instruction;
  * a definition of vD ends the interval, and the move is dead if nothing read
    vD first;
  * an accumulate into vD (`mls`/`mla`) blocks: rewriting the destination would
    redirect the write to vS.

The def/use model is the one P60 had to correct four times: an instruction that
READS its destination is not a pure define -- `mls` accumulates, `str` reads
its operand and defines nothing.
"""
import re, sys
from pathlib import Path

SRC = Path(sys.argv[1]); DST = Path(sys.argv[2])
SYM = sys.argv[3] if len(sys.argv) > 3 else "invntt16_asm"
LIMIT = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9

text = SRC.read_text()
head, rest = text.split(f"{SYM}_slothy_start:", 1)
body, tail = rest.split(f"{SYM}_slothy_end:", 1)
lines = body.splitlines()

INSN = re.compile(r'^(\s+)([a-z][a-z0-9.]*)\s+(.*?)(\s*//.*)?$')
# The kernel spells the same architectural register v27 / q27 / d27 depending
# on the instruction, so operands are parsed positionally rather than by a
# `v\d+` scan -- that scan is what made the first version of this pass miss
# every `ldr q` as a definition, and it produced wrong code that the
# differential test caught on its first trial.
def vregs(args):
    out = []
    for part in args.split(','):
        p = part.strip().lstrip('[').rstrip(']')
        m = re.match(r'^([vqd])(\d+)\b', p)
        out.append(f"v{m.group(2)}" if m else None)
    return out
ACC  = ("mls", "mla")

def parse(l):
    m = INSN.match(re.sub(r'\s+$', '', l))
    return (m.group(2), m.group(3)) if m and m.group(3) else None

def defuse(op, args):
    slots = vregs(args)
    regs  = [r for r in slots if r]
    if not regs:      return set(), set()
    if slots[0] is None: return set(), set(regs)     # destination is not a vector
    if op == "str":   return set(), set(regs)        # reads only
    if op in ACC:     return {regs[0]}, set(regs)    # accumulates into dest
    if op in ("ldr", "dup"): return {regs[0]}, set()
    return {regs[0]}, set(regs[1:])

parsed = [parse(l) for l in lines]
moves = []
for i, p in enumerate(parsed):
    if not p: continue
    m = re.match(r'(v\d+)\.16B,\s*(v\d+)\.16B,\s*(v\d+)\.16B$', p[1])
    if p[0] == "orr" and m and m.group(2) == m.group(3):
        moves.append((i, m.group(1), m.group(2)))

removable, dead, blocked = [], [], []
# Two independent limits, which the first two versions of this pass conflated:
#   vD's live range ends when vD is REDEFINED -- that is what decides whether
#     the move is dead;
#   vS's value survives only until vS is REDEFINED -- that is what decides
#     whether a use can be rewritten.
# Stopping the scan at the vS redefinition made a move whose reader lay beyond
# it look dead, and deleting it produced wrong code on the first trial.
for i, vD, vS in moves:
    uses, ok, src_dead_at = [], True, len(parsed)
    for j in range(i + 1, len(parsed)):
        p = parsed[j]
        if not p: continue
        op, args = p
        d, u = defuse(op, args)
        if vD in u:
            if op in ACC and vregs(args)[0] == vD:
                ok = False; break              # accumulator: cannot redirect
            uses.append(j)
        if vS in d and j < src_dead_at: src_dead_at = j
        if vD in d: break                      # vD's live range ends here
    if not ok:
        blocked.append((i, vD, vS, "accumulator"))
    elif not uses:
        dead.append((i, vD, vS))
    elif all(k <= src_dead_at for k in uses):  # a def at j happens after the read at j
        removable.append((i, vD, vS, uses))
    else:
        blocked.append((i, vD, vS, f"source reused at {src_dead_at}"))

print(f"  {len(moves)} pure vector moves")
print(f"    copy-propagated : {len(removable)}")
print(f"    dead (no reader): {len(dead)}")
print(f"    blocked         : {len(blocked)}")
for i, vD, vS, why in blocked: print(f"      line {i}: {vD} <- {vS} ({why})")

def rewrite(line, vD, vS):
    """Rewrite only the SOURCE operands.  A blanket textual substitution also
    renames the destination, which silently turned `sub v0, v0, v9` into
    `sub v21, v21, v9` -- correct-looking code that the differential test
    caught only because it reads and writes the same register."""
    m = INSN.match(re.sub(r'\s+$', '', line))
    ind, op, args, cmt = m.group(1), m.group(2), m.group(3), (m.group(4) or '')
    parts = args.split(',')
    first = 0 if op == "str" else 1        # `str` reads its first operand
    for n in range(first, len(parts)):
        parts[n] = re.sub(rf'\b([vqd]){vD[1:]}\b', rf'\g<1>{vS[1:]}', parts[n])
    return f"{ind}{op} {','.join(parts)}{cmt}"

out = list(lines)
applied = sorted(removable + [(i,d,s2,[]) for i,d,s2 in dead], key=lambda r: r[0])[:LIMIT]
removable = [r for r in applied if r[3]]
dead      = [(i,d,s2) for i,d,s2,u in applied if not u]
print(f"  applying {len(applied)} of {len(moves)} (LIMIT={LIMIT})")
for i, vD, vS, uses in removable:
    for k in uses: out[k] = rewrite(out[k], vD, vS)
    out[i] = None
for i, vD, vS in dead: out[i] = None
kept = [l for l in out if l is not None]
DST.write_text(head + f"{SYM}_slothy_start:\n" + "\n".join(kept) + "\n" +
               f"{SYM}_slothy_end:" + tail)
n_in, n_out = len([p for p in parsed if p]), len([l for l in kept if parse(l)])
print(f"  {SRC.name}: {n_in} -> {n_out} instructions ({n_out-n_in:+d})")

