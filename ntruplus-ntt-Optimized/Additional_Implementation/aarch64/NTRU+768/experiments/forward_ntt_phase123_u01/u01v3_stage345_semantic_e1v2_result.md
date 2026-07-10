# U01v3 Track E E1v2 Preserve Live-ins

Status: Pi5 correctness/ABI pass; PMU run completed.

E1v2 makes one allocator change relative to E1: destructive `mls` `same_as old_dest` values are colored immediately when the source color is available. This removes the late-overwrite interference that the rename validator found in old E1.

Contract:

```text
spills: 0
raw q reloads: 0
duplicate Stage12: no
max live vector values: 15
```

Pi5 validation:

```text
u01v3_stage345_semantic_e1v2_preserve_liveins_abi_mask=0x0
u01v3_stage345_semantic_e1v2_preserve_liveins_mismatches=0
```

Pi5 PMU matrix, `NTESTS=61`, `NITERATIONS=20000`:

```text
P:     2054 cycles, 2847 instructions
V:     2072 cycles, 2887 instructions
F0:    2059 cycles, 2839 instructions
F1:    2060 cycles, 2839 instructions
E2:    2059 cycles, 2839 instructions
E1v2:  2047 cycles, 2788 instructions
```

E1v2 deltas:

```text
vs P:  -7 cycles, -59 instructions
vs V:  -25 cycles, -99 instructions
vs F0: -12 cycles, -51 instructions
vs F1: -13 cycles, -51 instructions
```
