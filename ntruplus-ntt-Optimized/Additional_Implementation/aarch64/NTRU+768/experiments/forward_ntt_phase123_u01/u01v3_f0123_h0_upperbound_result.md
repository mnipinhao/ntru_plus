# U01v3 Track H H0 Block3 Load Upper Bound

Status: measured on Pi5. Production default unchanged.

H0 mechanically removes the eight Stage345 block3 q loads in each of three rows, for 24 removed loads total. It is intentionally not a correctness candidate: stale register values model a hypothetical free producer-to-consumer register handoff while keeping the rest of the G1 whole-path instruction order unchanged.

```text
symbol: u01v3_f0123_h0_block3_load_elision
removed block3 q loads: 24
arithmetic/scatter changed: no
correctness status: skipped diagnostic
static executable instructions: G1 3727, H0 3703
local AArch64 assembly: pass
Pi5 PMU: complete
```

Pi5 core 3, `NTESTS=61`, `NITERATIONS=20000`, `NWARMUP=300`; two
consecutive runs produced the same medians:

| ID | Status | Cycles | Instructions | CPI | Delta vs G1 | Text size | addr mod32/mod64 |
|---|---|---:|---:|---:|---:|---:|---:|
| P | pass | 2724 | 3836 | 0.7101 | +28 | 15272 | 0 / 32 |
| V | pass | 2727 | 3876 | 0.7036 | +31 | 15432 | 0 / 0 |
| G1 | pass | 2696 | 3744 | 0.7201 | 0 | 14904 | 0 / 0 |
| H0 | diagnostic | 2694 | 3720 | 0.7242 | -2 | 14808 | 16 / 48 |

The 24 removed loads are visible exactly as 24 fewer retired instructions,
but only as two fewer cycles. Under the Track H decision rule this is the
`0-5 cycles` low-headroom case. Block3 scratch loads are mostly outside the
whole-path critical path, so a producer-order rewrite cannot yield a large
win even with a perfect free handoff.
