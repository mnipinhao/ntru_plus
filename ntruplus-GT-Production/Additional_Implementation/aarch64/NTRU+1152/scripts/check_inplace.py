#!/usr/bin/env python3
"""Guard the precondition that lets the rebase buffer share the scratch.

packed_i9 call t reads nine vectors at j*256 + t*16 and writes nine at
s*256 + t*16 -- the same nine addresses.  Overlaying the two buffers is
therefore safe only while every data load retires before the first store.

That holds for the current schedule by 80 instructions, but it is a property
of the schedule, not a guarantee: a future Slothy run is free to interleave
them, and the result would be silent corruption that only shows up as wrong
coefficients.  This check fails the build instead.
"""
import re, sys
from pathlib import Path

src = Path(sys.argv[1] if len(sys.argv) > 1 else "../gt1152-p10-kem/inverse9.S")
body = src.read_text().split("packed_i9_slothy_start:", 1)[1] \
                      .split("packed_i9_slothy_end:", 1)[0]

loads, stores, i = [], [], 0
for line in body.splitlines():
    line = re.sub(r'//.*', '', line)
    m = re.match(r'\s+([a-z][a-z0-9.]*)\s+(.*)', line)
    if not m: continue
    op, args = m.group(1), m.group(2).strip()
    if op == "ldr" and "[x2" in args: loads.append(i)     # x2 = rebased input
    if op == "str" and "[x0" in args: stores.append(i)    # x0 = scratch
    i += 1

if len(loads) != 9 or len(stores) != 9:
    print(f"FAIL {src.name}: expected 9 data loads and 9 stores, "
          f"found {len(loads)} and {len(stores)}")
    sys.exit(1)
if max(loads) >= min(stores):
    print(f"FAIL {src.name}: store at {min(stores)} precedes the last data load "
          f"at {max(loads)} -- the scratch overlay in inverse_ntt.S is no longer "
          f"safe.  Either re-separate the buffers or re-schedule with the loads "
          f"constrained ahead of the stores.")
    sys.exit(1)
print(f"OK   {src.name}: all 9 data loads retire by instruction {max(loads)}, "
      f"first store at {min(stores)} (margin {min(stores)-max(loads)})")
