# U01v3 Track E E3 F012

Status: Pi5 correctness/ABI pass; PMU matrix completed.

E3 extends E1v2 from F01 to F012. It uses a new block2 handoff register set and allocates Stage345 block0/block1 with future live-ins reserved.

Static contract:

```text
spills: 0
raw q reloads: 0
duplicate Stage12: no
same_as_interference_count: 0
interference_count: 0
block2 inserted moves: 7
```

Pi5 correctness:

```text
u01v3_stage345_semantic_e3_f012_abi_mask=0x0
u01v3_stage345_semantic_e3_f012_mismatches=0
```

Localization checks:

```text
u01v3_stage12_compact_block012_scratch_debug: pass
u01v3_stage345_semantic_e3_b0_live_debug: pass
u01v3_stage345_semantic_e3_b01_live_debug: pass
```

The first generated block2 handoff used q14/q16 as sources, but Stage345
block2 clobbered them before their replacement load sites. The fixed E3 mapping
checks each block2 source against pre-load clobbers:

```text
Q16: q7
Q17: q11
Q18: q12
Q19: q13
Q20: q15
Q21: q16
Q22: q21
Q23: q19
```

Pi5 PMU matrix, `NTESTS=61`, `NITERATIONS=20000`, core pinned with
`taskset -c 3`:

```text
P:     2395 cycles, 3338 instructions, CPI 0.7175
V:     2400 cycles, 3378 instructions, CPI 0.7105
F0:    2381 cycles, 3330 instructions, CPI 0.7150
F1:    2385 cycles, 3330 instructions, CPI 0.7162
F2:    2382 cycles, 3327 instructions, CPI 0.7160
E1v2:  2374 cycles, 3279 instructions, CPI 0.7240
E3:    2362 cycles, 3246 instructions, CPI 0.7277
```

E3 deltas:

```text
vs P:     -33 cycles, -92 instructions
vs V:     -38 cycles, -132 instructions
vs E1v2:  -12 cycles, -33 instructions
vs F0:    -19 cycles, -84 instructions
vs F1:    -23 cycles, -84 instructions
vs F2:    -20 cycles, -81 instructions
```
