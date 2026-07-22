# Canonical pack next-wave results

Historical experiment baseline: P0 was production when this experiment ran.
After full-KEM promotion on 2026-07-18, P1 is enabled only for the three keygen
pack calls; non-keygen pack calls still use P0. P2/P3 remain default-off.

## Slothy whole-chunk results

| Variant | Normalization | Instructions/chunk | Expected cycles | Solver bound | Status |
|---|---|---:|---:|---:|---|
| P0 | post-transpose `sshr/and/add` | 112 | not rescheduled here | - | production baseline |
| P1 | pre-transpose `sshr/and/add` | 108 | 58 | 51 | feasible, self-check pass |
| P2 | pre-transpose `sshr/mls` | 100 | 59 | 58 | feasible, self-check pass |
| P3 | pre-transpose `ushr/mla` | 100 | 59 | 58 | feasible, self-check pass |

Each CP-SAT run used a 300-second internal timeout, no spilling, and fixed
integration GPR/vector contracts. `Feasible` does not mean proven optimal.
The expected-cycle counts use the repository's Neoverse-N1 model and are not
Pi5 PMU measurements.

P1 also removes four physical copy aliases per chunk through symbolic register
allocation. P2/P3 remove a further eight normalization instructions per chunk,
but the model places enough pressure on the multiply pipeline that their best
known schedules are one expected cycle slower than P1.

## Correctness and ABI

The following pass locally for baseline, P1, P2, and P3 chunk wrappers:

- every uniform input value in `[-3457, 3456]`;
- 2,000 deterministic random physical-layout polynomials;
- comparison against the first 96 bytes of production canonical pack;
- output guard bytes;
- x19-x28 and d8-d15 ABI sentinels.

The mechanically expanded 12-chunk P1/P2/P3 full-pack functions also pass the
same full-range/random checks against all 1,152 production bytes, output guards,
and ABI sentinels.

Commands:

```sh
make -B test_gt_canonical_pack_chunk_candidates
make -B test_gt_canonical_pack_full_candidates
```

## Full-pack static effect

| Variant | Body instructions | Delta vs production |
|---|---:|---:|
| production | 1,357 | 0 |
| P1 | 1,309 | -48 |
| P2 | 1,213 | -144 |
| P3 | 1,213 | -144 |

The counts include one function prologue/epilogue and all 12 chunks. They do
not predict cycles by themselves.

## Pi 5 PMU result

Raspberry Pi 5 Cortex-A76, core 3, `NTESTS=61`, `NITERATIONS=20000`:

| Scope | Variant | Cycles p50 | Instructions p50 | Paired delta | Wins |
|---|---|---:|---:|---:|---:|
| chunk | production | 70 | 142 | - | - |
| chunk | P1 | 66 | 138 | -4 | 61/61 |
| chunk | P2 | 69 | 130 | -1 | 61/61 |
| chunk | P3 | 67 | 130 | -3 | 61/61 |
| full pack | production | 643 | 1374 | - | - |
| full pack | P1 | 638 | 1326 | -5 | 61/61 |
| full pack | P2 | 656 | 1230 | +13 | 0/61 |
| full pack | P3 | 662 | 1230 | +19 | 0/61 |

P1 is the only candidate that wins the full-pack microbenchmark. P2/P3 retire
more instructions but increase CPI enough to regress cycles.

Same-binary full-KEM testing showed that P1 is context-sensitive. Restricting
P1 to the three consecutive keygen pack calls saves 75.5 cycles at the paired
median and wins 61/61 samples. Using P1 for every pack call instead regresses
encapsulation by 44.9 cycles and decapsulation by 6.9 cycles. Therefore P1 was
promoted only for keygen, not as a universal replacement for production pack.

Commands:

```sh
make bench_gt_canonical_pack_chunk_pmu
make bench_gt_canonical_pack_full_pmu
```

Raw output is under
`aarch64-bench/results/serialization_candidates_2026-07-18/`.

## Post-F2 revalidation (2026-07-20)

The current source tree was retested with the promoted decap F2 backend and the
same core-pinned `61 x 20000` PMU settings. Correctness, output guards, and ABI
sentinels remain clean. The decision is unchanged:

| Scope | Production | P1 | P2 | P3 |
|---|---:|---:|---:|---:|
| chunk cycles | 70 | 66 | 69 | 67 |
| full-pack cycles | 637 | 631 | 648 | 658 |

P1 wins all 61 full-pack pairs by a median 6 cycles. P2/P3 retire fewer
instructions but regress by 11/21 cycles. Keygen-only P1 plus the already
selected U1 unpack saves about 72 cycles in same-binary keypair PMU.

## Source-major decision

The source-major model remains model-only. For a 16-block source group, its
scalar-store lower bound is 146 stores across the full polynomial, versus 24
multi-register output stores in the canonical-major baseline, before counting
source-major shuffles. Do not emit source-major ASM unless fragment coalescing
substantially changes that bound.
