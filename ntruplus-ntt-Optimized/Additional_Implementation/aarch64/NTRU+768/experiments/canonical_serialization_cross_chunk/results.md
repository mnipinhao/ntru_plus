# Cross-chunk canonical pack result

## Slothy

- Region: two adjacent P1 chunks.
- Instructions: 216, unchanged from two independent P1 chunks.
- Spills: 0.
- Expected cycles: 113 versus `2 x 58 = 116` for independent P1 schedules.
- Slothy status: feasible, self-check passed, 1800-second run.

## Correctness and ABI

Pi 5 full 1152-byte differential:

```text
canonical_full_cross_chunk_mismatches=0
canonical_full_cross_chunk_guard_mismatches=0
canonical_full_cross_chunk_abi_mask=0x0
```

## Full-pack PMU

Pi 5 Cortex-A76, core 3, `NTESTS=61`, `NITERATIONS=20000`:

| Variant | Cycles p50 | Instructions p50 | Text bytes | Delta vs P1 |
|---|---:|---:|---:|---:|
| P1 expanded | 629 | 1327 | 5264 | baseline |
| cross-chunk | 619 | 1327 | 5264 | -10 cycles |

The paired win rate was 61/61, with p10/p50/p90 deltas of
`-11/-10/-9` cycles.

## Unique-backend keygen

Three balanced process orders produced these keygen p50 cycles:

| Round | Production P1 | Cross-chunk |
|---|---:|---:|
| P/X/C | 38300 | 38247 |
| C/X/P | 38276 | 38247 |
| X/P/C | 38290 | 38226 |

Median of round medians: 38290 versus 38247, or -43 cycles.

The unique-backend total binary text stayed at 189617 bytes. External
full-keygen `L1-icache-load-misses` measurements were about 79.2k for P1 but
525k for cross-chunk, confirmed in a second reverse-order run. This is a large
instruction-cache regression despite the cycle win.

## Decision

Cross-chunk scheduling proves that overlapping adjacent gather/arithmetic DAGs
has a real 10-cycle full-pack benefit. It is not the selected code-size/L1I
candidate: it keeps the 5264-byte expansion and causes a severe keygen L1I
regression in its current placement. Production default remains unchanged.
