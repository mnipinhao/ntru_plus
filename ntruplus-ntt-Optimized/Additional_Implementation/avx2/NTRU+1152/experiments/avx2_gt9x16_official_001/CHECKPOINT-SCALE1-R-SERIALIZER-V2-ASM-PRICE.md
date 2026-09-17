# Scale-1 r serializer V2 ASM and boundary pricing

## Outcome

The corrected namespaced Serializer V2 is byte-exact and wins the isolated
materialized wire-state serializer boundary.

```text
SUPERCOP-derived serious StQ2, CPU 1, performance governor, turbo disabled
control    732.5162 cycles
V2         685.8032 cycles
delta      -46.7130 cycles  (-6.38%)
direction  9/9 fresh processes favor V2
```

This is not a Native SUPERCOP KEM result. The timed boundary is exactly:

```text
same resident materialized wire-monotone scale-1 r state
    -> serializer only
same exact 1728 wire bytes
```

Forward, `hash_g`, SOTP, and the Native caller are outside timing.

## Correctness gates

- 1000 random CBD1 inputs plus zero, all-one, all-minus-one, alternating,
  and endpoint impulses pass complete Forward-to-Official byte differential.
- Existing wire serializer, V2, and Official `poly_ntt` + `poly_tobytes` agree.
- Input immutability and output canaries pass.
- ASan/UBSan and generator stale checks pass.

## Linked machine delta

| item | control | V2 | delta |
|---|---:|---:|---:|
| dynamic instructions | 1387 | 1254 | -133 |
| `.text` bytes | 8525 | 7074 | -1451 |
| `.rodata` bytes | 2368 | 32 | -2336 |
| data loads | 72 | 72 | 0 |
| normalized vectors | 72 | 72 | 0 |
| output stores | 54 | 54 | 0 |
| stack-relative accesses | 0 | 0 | 0 |
| calls | 0 | 0 | 0 |

The `-133`, rather than abstract `-144`, is accounted for by two hoisted
constant loads, eight unrolled pointer increments, one `vzeroupper`, and
return accounting. The candidate is straight-line, 32-byte aligned, and
spill-free.

## Serious launch deltas

```text
-48.9167 -44.8333 -49.1250 -45.6458 -46.6042
-47.0000 -45.7500 -47.0625 -45.0417 cycles
```

## Decision

Serializer V2 is the selected materialized-wire serializer baseline. The
next gate is caller-boundary integration/pricing: first serializer plus hash
input staging, then hash/SOTP if the credit survives. Native KEM promotion is
not authorized by this isolated result alone.
