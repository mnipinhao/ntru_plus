# P23 results — global ToBytes routing DAG

## Outcome

P23 passes the exact-map, range/ABI, no-scratch, constructive no-spill,
bounded Slothy, native executable, Pi 5 same-boundary and full-KEM gates.  It
is a promotion candidate; production remains the P18 implementation until a
separate P24 integration gate.

## Corrected baseline

The old P6-D3 reopen condition (remove about 829 instructions and 101 reads)
was already surpassed by promoted P18.  P23 therefore compares only against
current P18 production:

| Mode | P18 complete instructions | P23 | Delta |
|---|---:|---:|---:|
| Full | 2348 | 2154 | -194 |
| Small | 2128 | 1934 | -194 |

P23 preserves the exact P18 coordinate map, whose SHA-256 is
`087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270`.

## DAG and registers

Across P18's fifteen source-neighborhood classes, structural interning finds
54 unique coefficient sources, 24 rotations and 200 transpose nodes per top.
Thus the exact lower bound is 278 source-load plus routing instructions.  The
26-register capped schedule executes all 224 non-load routing nodes exactly
once and reloads only seven evicted sources, for 61 loads and 285 total route
instructions per top.  Compared with P18's measured 64 loads plus 318 routing
instructions, two tops save 194 instructions and six Q loads.

`v0-v25` are the constructive routing cache.  Full reserves `v26-v31` for the
pack index, q, reciprocal 9, normalization temporary and two packing
temporaries.  Every completed vector is normalized and packed before its
route slot is reused.  There is no coefficient scratch and no vector stack
access.  The exact trace contains 339 records per top and peaks at 26 route
values.

## Correctness

- Python exact lane/byte oracle: 516 full-range cases.
- Apple arm64 executable: 513 Full, 513 Small and two guard-page edge cases,
  both before and after Slothy scheduling.
- Pi 5: both package KEM tests, exact boundary canaries, KAT and malformed
  transcript pass.
- KAT SHA-256 remains
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Malformed transcript SHA-256 remains
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.

## Slothy result and the scheduling lesson

The canonical checkout is `/Users/chenpinhao/slothy`, run by
`/Users/chenpinhao/slothy_and_ra/.venv/bin/python` with the Cortex-A76 model,
renaming disabled and spills disabled.  The route allocation is constructive;
Slothy schedules the fixed allocation.

One-output windows were a useful rejected control.  Despite -194 instructions
and -6 reads, they regressed Full/Small by 53.813/10.648 cycles and all three
KEM operations.  They forced each normalization/pack/store chain to finish
before exposing the next consumer and destroyed cross-output instruction-level
parallelism.

The accepted candidate groups three output consumers per Slothy window.  All
18 windows per mode are solved with their instruction multisets preserved.
This is small enough for reliable bounded solving while allowing routing,
normalization and packing from adjacent outputs to overlap.  The current
Slothy parser still rejects `STUR D/W`; scheduling therefore uses the same
P18 same-width/same-address `STR` model surrogate and restores real `STUR`
before assembly and executable verification.

## Pi 5 same-boundary PMU

252-ish paired full-KEM observations and the exact component harness ran on
Cortex-A76 CPU 3 under the `ondemand` governor.  The machine remained
unthrottled.

| Mode | P18 cycles | P23 cycles | Paired delta | Instructions | Reads |
|---|---:|---:|---:|---:|---:|
| Full | 1409.828 | 1393.453 | -16.375 | -194 | -6 |
| Small | 1031.719 | 985.133 | -46.586 | -194 | -6 |

The target P23 objects contain 1108/1000 instructions versus P18's 1204/1096
and have zero Q-register stack accesses.

## Frozen full-KEM integration

| Operation | P18 cycles | P23 cycles | Paired delta | Instruction delta | Observations |
|---|---:|---:|---:|---:|---:|
| Keygen | 43256.500 | 43131.875 | -131.375 | -582 | 252 |
| Encaps | 45081.950 | 45003.100 | -81.125 | -388 | 252 |
| Decaps | 40132.250 | 40067.550 | -64.500 | -388 | 252 |

The exact instruction deltas again expose call counts: Keygen executes three
ToBytes calls, while Encaps and Decaps execute two.  The cycle savings are
smaller than the instruction savings because ToBytes remains dominated by
shuffle and packing throughput, but every required boundary wins.

## Decision and maintained queue

P23 is retained as the new ToBytes promotion candidate.  P24 is next:

1. copy the exact three-output scheduled Full/Small artifacts into production;
2. rebuild only from the committed production tree;
3. repeat manifest, linked-symbol, exact-byte, input-immutability/canary,
   AAPCS/SIMD wipe, KAT, malformed/rejection and paired boundary/full-KEM gates;
4. only after P24, refresh the selected-Official profiler if a new bottleneck
   decision is needed.
