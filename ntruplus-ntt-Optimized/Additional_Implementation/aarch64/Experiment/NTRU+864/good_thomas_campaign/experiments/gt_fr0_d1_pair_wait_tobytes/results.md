# D1-P3B15 evidence

Status: **correct but rejected against P3B6.**

Local correctness passes 256 arbitrary signed-int16 cases plus both guarded
input/output edges.  Pi 5 passes 128 differential cases.  The target GCC
object has a 1460-instruction `pair_wait_top`, a 256-byte frame and 75 vector
stack accesses.  Eight are the four `d8-d15` ABI save/restore pairs; the other
67 are compiler spill/reload accesses.  Thus using all architectural registers
did not remain a register-only implementation.

Paired Cortex-A76 PMU, core 3, 400 calls/sample, 41 samples per order, both
orders and three repetitions:

| variant | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| P3B6 | 1502.432 | 2769.050 | 6.010 |
| P3B15 pair-wait | 1507.465 | 2882.050 | 6.010 |
| candidate - P3B6 | +5.033 | +113 | 0 |

All three repetitions lose: +5.015, +8.504 and +6.200 cycles using their
individual medians.  The small cycle regression means the architecture is not
catastrophic, but it neither removes instructions nor satisfies no-spill.
