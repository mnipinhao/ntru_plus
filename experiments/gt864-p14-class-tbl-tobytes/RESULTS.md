# P14 result — class-local TBL4 routing rejected

P14 tested a genuinely new routing DAG rather than reopening P6 scratch
storage.  The exact composed map has 54 output Q vectors per top but only 15
distinct eight-source neighborhoods: ten classes produce four outputs, four
produce two, and one produces six.  A Hamilton-path dynamic program maximizes
adjacent overlap at 56 and needs only 64 source Q loads per top.

## Implementations

P14-A expressed the DAG with Neon intrinsics.  Exact bytes passed, but GCC
could not maintain the two consecutive four-register TBL banks: full/small
top functions became 1712/1560 instructions with 83/69 stack references.
It was rejected at target lowering.

P14-B fixed the source banks at `v0-v7`.  Every output uses two independent
`TBL4`, `ORR`, the unchanged P9 full or small normalization, and the unchanged
eight-coefficient pack.  Results are consumed immediately; there is no partial
output frontier or coefficient scratch.  Mac and Pi pass 513 full, 513 small,
both guarded edges, and the Pi timing harness rechecks 256 cases per mode.

| Complete path | P9 instructions | P14-B instructions | Delta |
|---|---:|---:|---:|
| full | 2809 | 2260 | -549 |
| small | 2607 | 2036 | -571 |

The top body has no stack reference.  The full+small Decaps call ledger would
remove about 1120 instructions, so the static common-DAG gate passes.

## Pi 5 paired PMU

Pi 5 Cortex-A76 core 3, GCC 14.2, `-O3 -march=armv8-a+simd`, three
repetitions, both AB/BA orders, 41 samples per order and 400 calls per sample;
throttling stayed `0x0`.

| Mode | P9 cycles | P14-B cycles | Delta | Retired-instruction delta |
|---|---:|---:|---:|---:|
| full | 1507.220 | 1706.213 | **+198.993** | -555 |
| small | 1172.662 | 1277.245 | **+104.583** | -573 |

All three repetitions lose in both modes.  P14 replaces 864 cheap lane moves
with 216 additional gather TBL operations and their public index loads per
complete call.  On A76 the lookup/load throughput costs more cycles than the
retired-instruction reduction saves.  This is a measured microarchitecture
inference; correctness and the static reduction remain valid.

## Decision

Reject P14-A and P14-B.  Production remains P9.  Slothy is not run because the
candidate already triggers its predeclared exact-boundary performance
falsifier; scheduling cannot remove the extra TBL/load throughput floor.
Full-KEM integration is intentionally skipped because both full and small
serializers regress independently.

The next bounded experiment is P15: retain P9's input-once lane-move DAG and
memory behavior, extract target-lowered completion windows, and test whether
Slothy can interleave routing with normalization/packing without adding TBL,
input loads, scratch, or spills.
