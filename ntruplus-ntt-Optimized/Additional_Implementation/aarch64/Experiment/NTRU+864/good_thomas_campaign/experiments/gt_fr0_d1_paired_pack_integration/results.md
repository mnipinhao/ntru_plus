# D1-P3B10 results

Status: **reject complete integration; P3B6 remains champion.**

The generated candidate preserves the exact composed byte map, peak-16 partial
frontier and arbitrary signed-int16 normalization.  It uses one reusable
432-byte scratch buffer, exactly 27 partner stores, 27 partner reloads and 27
paired `ST3` operations per top.  Local 256-case tests and both guarded buffer
edges pass; Pi 128-case correctness also passes.

## Cortex-A76 PMU

| complete ToBytes | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| P3B6 input-once | **1502.457** | 2769.050 | 6.010 |
| P3B10 paired/scratch | 1508.182 | **2648.050** | 7.010 |
| candidate - control | +5.725 | -121.000 | +1.000 |

All three paired repetitions are effectively identical and the Pi remains
unthrottled.  The candidate retires 121 fewer instructions but does not reduce
cycles.

## Target object audit

The top-local candidate has zero `TBL`, 27 static `ST3`, 27 declared scratch
stores and 27 declared scratch reloads.  Its stack references save GPRs and
`d15`; there is no compiler-created coefficient spill.  The outer function's
480-byte frame consists of the declared 432-byte scratch plus ABI/alignment
space and is reused by both tops.

P3B9's isolated 174.300-cycle pack16 benefit therefore does not survive this
FR0 completion schedule.  Partner memory round trips and their dependency/
address work consume the benefit even though static instruction count falls.
The failure is architectural, not correctness, thermal noise, or spilling.

No full-KEM binding is run.  P3B6 remains the measured ToBytes champion at
1502.457 cycles in this paired run and about 1502.44-1502.46 across its gates.
