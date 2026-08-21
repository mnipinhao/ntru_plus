# GT32 Load-to-Compute Production 043 Results

## Scope

This gate tests one predefined deterministic SUPERcop export.  Relative symbol
placement was not swept.  The candidate differs from frozen GT Clean only in:

1. Decode keeps the `0123` mask resident.
2. General B3 preloads `qinv`.

The experiment answers exact-image performance, not placement-independent
mechanism performance.  The latter already failed the 042 Normal/Reversed gate.

## Correctness

The candidate passed the canonical deterministic 100-vector KAT byte-exact for
Keypair, Encap, Decap, ciphertext, and shared secrets.

## Fixed-image audit

All three measurement programs were freshly built with the same captured
SUPERcop compiler profile.  GT Clean and DB have identical selected symbol
addresses and identical section sizes.

| Item | Official | GT Clean | GT DB |
|---|---:|---:|---:|
| `.text` | 42,007 B | 64,343 B | 64,343 B |
| `.rodata` | 5,384 B | 21,576 B | 21,576 B |

Selected GT Clean and DB addresses are identical:

| Symbol | Address |
|---|---:|
| `ntt_frontend` | `0x38e0` |
| unpack body | `0x4c60` |
| unpack wrapper | `0x5a00` |
| lazy Q24 pack | `0x6a00` |
| high-range Q24 pack | `0x8f20` |
| general B3 | `0x9900` |
| inverse NTT | `0xb120` |
| M Forward | `0xcac0` |

ELF SHA-256:

- Official: `1b0f1a4353415dd2abfbbe05841be8fbdd3bccf88af036b957f88d476f1f8ad4`
- GT Clean: `29bf895dbe86c11d32d6e75c75b0bba10e7cb30b1901b246ea1e56a9d0306e9a`
- GT DB: `1ab77877cea8ff7ad85601aa3317930a1f86ff4352b23224c88bb4268942ba3d`

## Serious benchmark

Method:

- CPU 1, ASLR enabled.
- 256 balanced mirrored three-way blocks.
- Eight discarded warmup launches per implementation.
- 512 measured launches and 49,152 timing observations per operation and
  implementation.
- Primary comparison: paired block median with bootstrap 95% CI.
- Negative delta means GT DB is faster.

### GT DB versus GT Clean

| Operation | Aggregate StQ2 delta | Paired median delta | Favorable blocks | Bootstrap 95% CI | Decision |
|---|---:|---:|---:|---:|---|
| Keypair | +4.78 | -2.75 | 129/256 | [-16.30, +7.73] | neutral control |
| Encap | +9.16 | -12.95 | 141/256 | [-29.10, +4.17] | inconclusive; no promotion |
| Decap | -33.58 | -43.36 | 183/256 | [-50.15, -31.68] | exact-image win |

The Encap aggregate and paired estimates have opposite signs.  This is exactly
why the predeclared paired confidence interval is the promotion criterion.  Its
upper bound remains positive, so DB is not selected as the new Encap image.

### GT DB versus Official

| Operation | Official StQ2 | GT DB StQ2 | Aggregate delta | Paired median delta | Favorable blocks | Bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| Keypair | 21,688.40 | 21,338.66 | -349.73 | -306.85 | 248/256 | [-321.98, -292.81] |
| Encap | 28,443.07 | 28,533.33 | +90.26 | +173.35 | 56/256 | [+150.19, +188.49] |
| Decap | 19,468.64 | 19,238.55 | -230.09 | -207.80 | 227/256 | [-219.42, -197.00] |

Thus this fixed image clearly wins Official Keypair and Decap, but clearly loses
Official Encap.  The DB changes do not close the remaining Encap delivery gap.

## Interpretation

The natural production export does not reproduce 042 Normal's approximately
35-cycle Encap win.  In 042, control and candidate copies occupied different
slots; in this clean export, the selected bodies occupy the original production
slots.  The exact-image benchmark therefore validates the attachment's proposed
methodology while rejecting this particular Encap promotion.

The result supports three separate claims:

1. The load-to-compute mechanism is not placement-robust.
2. In the predefined production layout its Encap effect is too small to prove.
3. The same exact image gives a reproducible Decap improvement of about 43 paired
   cycles, without a measurable Keypair change.

Raw per-block data and all launch observations are preserved in
`results/formal-aslr-on-warm-256/benchmark.json` (raw launch files are ignored).
