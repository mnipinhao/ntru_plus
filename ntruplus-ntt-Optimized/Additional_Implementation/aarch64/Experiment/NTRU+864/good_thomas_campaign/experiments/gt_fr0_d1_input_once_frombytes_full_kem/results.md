# D1-P3B12 evidence

Status: **full-caller gate passed; accept P3B11 as the experimental
production-shaped FromBytes champion.**

Official, frozen P3B4 and P3B4 plus P3B11 are linked into one binary.  Both GT
variants use identical M5R-D Forward, D1 BaseMul/BaseMulAdd, M5E Inverse and R9
ToBytes objects.  Their only difference is C1 versus input-once FromBytes.

Eight deterministic Keypair/Encaps/Decaps cases are byte-identical.  Valid
decapsulation succeeds; tampered ciphertexts fail with identical returned
bytes.  Relocation audit confirms the baseline and candidate FromBytes symbols.

## Paired Cortex-A76 PMU

The Pi 5 used core 3, both `ODB` and `BDO` orders, 41 samples/order, and three
complete repetitions.  Every thermal check reported `throttled=0x0`.

| API | Official | P3B4 baseline | P3B11 FromBytes | candidate - baseline | candidate - Official |
| --- | ---: | ---: | ---: | ---: | ---: |
| Keypair | 46877.750 | 55882.250 | 55895.750 | +13.500 | +9018.000 (+19.24%) |
| Encaps | 47031.350 | 48202.625 | **47960.563** | **-242.063 (-0.50%)** | +929.212 (+1.98%) |
| Decaps | 43444.050 | 47653.975 | **46836.925** | **-817.050 (-1.71%)** | +3392.875 (+7.81%) |

The exact retired-count deltas close the FromBytes call ledger:

| API | FromBytes calls | instructions | branches |
| --- | ---: | ---: | ---: |
| Keypair | 0 | 0 | 0 |
| Encaps | 1 | -1458 | -24 |
| Decaps | 3 | -4374 | -72 |

All three repetitions favor P3B11 in Encaps by 226.438/246.575/242.688
cycles and in Decaps by 806.650/823.775/813.675 cycles.  Keypair has identical
retired counts and its small mixed-sign cycle differences are caller noise, as
required by the zero-call control.

The Decaps cycle saving is larger than three isolated medians because caller
cache/dependency context differs; the exact instruction and branch closure
proves that no unrelated code path changed.

## Decision and next gate

P3B11 replaces C1 as the experimental full-caller FromBytes champion.  This is
not a Production or SUPERCOP promotion.  The next byte-boundary experiment is
ToBytes structured routing: it must change the P3B6 completion structure so
adjacent output groups are naturally live together, rather than adding scratch
or deleting more isolated encodings from the same schedule.
