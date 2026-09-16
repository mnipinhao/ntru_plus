# D1-P3B8 results

Status: **reject as a performance candidate.**

The candidate matches P3B6 byte-for-byte on 256 complete inputs, including
index tags, signed extrema, and random values.

Apple clang emits 1305 instructions/top versus 1358 for the control.  The
top-local integer `add` count falls from 54 to one while the 55 total `ldr`
instructions and the vector arithmetic/routing shape remain unchanged.  Both
cores have zero stack references.  Thus the candidate realizes 53 of the
expected 54 static removals without changing the memory boundary.

## Pi 5 result

GCC 14.2 emits 1325 instructions/top for the candidate versus 1378 for P3B6.
The integer `add` count falls from 160 to 107, with identical counts for the
56 loads, 501 vector moves, 54 table lookups and ABI save/restore.  Both
objects have no coefficient spills; their only stack references save and
restore `d8-d15`.

| variant | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| P3B6 | **1502.443** | 2769.050 | 6.010 |
| direct address | 1505.185 | **2663.050** | 6.010 |
| candidate - control | +2.742 | -106.000 | 0 |

All three paired repetitions reproduce the result and the Pi remains
unthrottled.  The deleted address instructions were therefore not on the
Cortex-A76 critical path; they overlapped the vector routing and packing work.
The candidate is cleaner and smaller but provides no cycle benefit, so it is
not promoted or linked into full KEM.  P3B6 remains the ToBytes champion.
