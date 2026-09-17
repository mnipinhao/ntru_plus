# Scale-1 fanout, tail V2, and H3 pair-unpack Native checkpoint

## Result

The scale-1 `r` fanout contract is now frozen, the current tail has been
reattributed from PK bytes, and the largest measured tail component was
attacked with a new namespaced AVX2 candidate.

The candidate is correct and materially improves the isolated tail, but it
does not beat pinned Official in Native SUPERCOP `enc_cycles`. It remains a
research baseline and is not promoted to clean production.

## Scale-1 `r` dual-output/fanout contract

The generated contract is
`generated/scale1-r-dual-output-fanout-contract.json`.

It freezes one 1152-cell wire-monotone, scale-1, Montgomery-exponent-zero
state with two consumers:

1. the exact serializer/hash-G/SOTP path; and
2. the unchanged lane-wise MA2 path.

The serializer may not mutate the retained MA2 state. A future fused producer
must be priced from coefficient input through serializer/hash-G/SOTP while
retaining the same state for MA2; serializer-only timing is insufficient.

## Current tail attribution

SUPERCOP-derived fixed-O3GC serious measurement, nine fresh processes, CPU 1,
performance governor, turbo disabled:

| boundary | Official | current wire | debt |
|---|---:|---:|---:|
| T0: PK decode/materialized ingress proxy | 430.4421 | 638.4630 | +208.0208 |
| T1: PK bytes to MA2 output | 1293.3958 | 1606.8102 | +313.4144 |
| T2: PK bytes to ciphertext | 1638.5116 | 2059.5556 | +421.0440 |

Using one estimator family, the diagnostic incremental debts are about
`+105.39` cycles for T1-T0 and `+107.63` cycles for T2-T1. T0 is explicitly a
materialized routing-equivalent proxy: the real H3 implementation streams h
directly into MA2 and has no resident h object.

This made PK decode/h-lane formation the largest actionable tail debt.

## H3 pair-unpack optimization

The exact ownership replay proved that every adjacent-p pair of h planes is
the low/high-half word interleave of the same two decoded vectors. The old
formation for two planes used ten routing instructions:

```text
2 planes × (2 vperm2i128 + 2 vpshufb + 1 vpor)
```

The candidate forms both planes together:

```text
vpunpcklwd
vpunpckhwd
vperm2i128 low-half plane
vperm2i128 high-half plane
```

Across 36 coefficient pairs this changes the linked H3 symbol by:

| mnemonic | delta |
|---|---:|
| `vperm2i128` | -72 |
| `vpshufb` | -144 |
| `vpor` | -72 |
| `vpunpcklwd` | +36 |
| `vpunpckhwd` | +36 |
| total instructions | -216 |
| `.text` | -1746 bytes |

There is no arithmetic, range, scale, r/m ABI, MA2, or ciphertext ownership
change. The linked leaf remains call-free, branch-free, frame-free, and
`vzeroupper`-free.

Correctness passed 1003 raw H3 bit-exact and full ciphertext byte-exact cases,
invalid-PK differential, ASan/UBSan, and a 100-case installed KAT.

## Tail repricing

The pair-unpack candidate measured:

| boundary | Official | pair-unpack | debt |
|---|---:|---:|---:|
| T0 proxy (unchanged code/noise control) | 429.0764 | 643.8681 | +214.7917 |
| T1: PK bytes to MA2 output | 1298.8981 | 1498.5069 | +199.6088 |
| T2: PK bytes to ciphertext | 1643.4352 | 1985.1898 | +341.7546 |

Relative to the previous serious campaign, the candidate reduces the T1 wire
path by about `108.30` cycles and the T2 wire path by about `74.37` cycles.
After accounting for the contemporaneous Official values, the measured debt
reduction is about `113.81` cycles at T1 and `79.29` cycles at T2. Roughly 34
cycles are lost again when the unchanged large egress follows the smaller H3,
so the next tail target is egress scheduling/footprint rather than further h
formation.

## Native SUPERCOP candidate

Installed without overwrite as:

```text
crypto_kem/ntruplus1152/avx2-gt9x16-wire-h3-pairunpack-exp009-sc20260831
```

Pinned SUPERCOP 20260831 Native results (nine fresh processes, 864
observations/operation, CPU 1):

| campaign | Official enc | candidate enc | delta |
|---|---:|---:|---:|
| first | 42968.7083 | 43894.5648 | +925.8565 |
| confirmation | 43021.2037 | 43893.1620 | +871.9583 |

Both Official and candidate selected GCC 15.2 `-O3`. The candidate itself was
stable across the two campaigns, but remains roughly 0.87--0.93k cycles behind
Official. Keypair and decapsulation source paths are unchanged and serve only
as noise controls.

The same-period legacy control selected `-O2`, while pair-unpack selected
`-O3`; therefore its apparent `-232.29` Native delta versus that control is not
attributed solely to the ASM change. The derived tail result supplies the
clean component attribution; Native Official remains the promotion authority.

## Decision

- Freeze pair-unpack as the new H3/H4 research realization.
- Do not promote it to clean production: Native `enc_cycles` still loses.
- Do not pursue mixed-p state while r/m remain in the frozen wire ABI; its
  saved h routes are paid back by r/m cross-half formation.
- The next measured tail debt is the exact ciphertext egress, now about
  `+142` cycles after pair-unpack. The other major caller debt remains the
  scale-1 r dual-output/hash fanout contract.

