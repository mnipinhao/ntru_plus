# D1-P3B21 evidence

Status: **correct, but rejected against P3B6.**

The exact `2^15` class DP certifies a 26-vector pair-completion frontier.
Local testing passes 256 arbitrary signed-int16 inputs and guarded edges; Pi 5
passes 128 differential cases.  Target GCC nevertheless emits 69 non-ABI
vector stack accesses in `pair_wait_top`, so the released two logical values
do not become a spill-free physical allocation.

Paired Cortex-A76 PMU (core 3, three repetitions):

| variant | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| P3B6 | 1502.432 | 2769.050 | 6.010 |
| P3B21 peak-26 | 1509.182 | 2892.050 | 6.010 |
| candidate - P3B6 | +6.750 | +123 | 0 |

All repetitions lose.  Lowering the abstract frontier from 28 to 26 is not
enough because normalization and `pack16` temporaries overlap completed pairs.
