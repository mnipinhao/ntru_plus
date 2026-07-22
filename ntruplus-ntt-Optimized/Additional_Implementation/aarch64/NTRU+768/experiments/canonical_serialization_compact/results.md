# Compact shared-core canonical pack result

## Shape and Slothy

Each of the twelve chunks performs 16 fixed-offset `ldr d` operations and eight
lane-combine `mov` operations, then calls one shared normalize/transpose/pack
core.

- Shared core: 84 instructions.
- Slothy result: optimal, 47 expected cycles, self-check passed.
- Spills: 0.
- Full function: twelve gather groups, twelve `bl`/`ret` boundaries, one shared
  core.

## Correctness and ABI

Pi 5 full 1152-byte differential:

```text
canonical_full_compact_mismatches=0
canonical_full_compact_guard_mismatches=0
canonical_full_compact_abi_mask=0x0
```

## Full-pack PMU

Pi 5 Cortex-A76, core 3, `NTESTS=61`, `NITERATIONS=20000`:

| Variant | Cycles p50 | Instructions p50 | Text bytes | Delta vs P1 |
|---|---:|---:|---:|---:|
| P1 expanded | 629 | 1327 | 5264 | baseline |
| compact shared core | 625 | 1353 | 1632 | -4 cycles |

The paired win rate was 61/61, with p10/p50/p90 deltas of `-5/-4/-4`
cycles. The kernel text is 3632 bytes smaller, a 69.0% reduction. The hot-loop
L1I event was zero for both variants because both functions remained resident.

## Unique-backend keygen and L1I

The replacement binaries link only one keygen pack backend; they do not contain
both P1 and compact implementations.

| Round | Production P1 | Compact |
|---|---:|---:|
| P/X/C | 38300 | 38238 |
| C/X/P | 38276 | 38255 |
| X/P/C | 38290 | 38250 |

Median of round medians: 38290 versus 38250, or -40 cycles.

| Metric | Production P1 | Compact | Delta |
|---|---:|---:|---:|
| total binary text | 189617 | 186001 | -3616 bytes |
| L1I misses, first run | 79255 | 70118 | -11.5% |
| L1I misses, reverse-order confirmation | 79168 | 70469 | -11.0% |

The external L1I event covers the complete benchmark process containing 31 by
2000 full keygen calls. It is a relative frontend diagnostic, not a per-call
kernel counter.

## Decision

The compact backend is the selected serious serialization experiment candidate:
it is slightly faster than P1 in direct full-pack and full-keygen measurements,
reduces kernel text by 69%, and reduces full-keygen L1I misses by about 11%.
The absolute keygen gain remains small at about 40 cycles, so production default
is not changed in this round.
