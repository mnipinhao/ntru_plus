# A2 — inverse ST1-lane store shootout

This default-off experiment changes only the M5E inverse-finish scatter:

```
UMOV lane -> GPR; STRH
        versus
ST1 {v.h}[lane]
```

Arithmetic, register values, output addresses and output bytes are unchanged.
The candidate is generated mechanically from the retained M5E assembly.
Correctness is bit-exact to M5E over 81 edge/impulse/random cases at the G0
input bound 2205, with an independent intrinsic modulo-q oracle and surrounding
sentinels.

Pi 5 measurement rejects the candidate: I16-only grows from 3885.671 to
4363.537 cycles and complete inverse grows from 6866.058 to 7350.215 cycles,
despite retiring about 634 fewer instructions.  This identifies lane-store
throughput/address dependency, not the GPR round trip, as the dominant issue.
No Slothy or Production change was made.
