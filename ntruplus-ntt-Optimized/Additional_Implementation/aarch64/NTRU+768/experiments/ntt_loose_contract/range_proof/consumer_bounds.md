# Loose NTT Consumer Bounds

Date: 2026-07-07

Scope: caller-specific Forward NTT range audit for NTRU+768 GT production.
This document records downstream consumer preconditions only.  It does not
change code or define a production variant.

## Baseline Producer Contract

The production Forward NTT entrypoint is:

```text
poly_ntt / gt_block_major_poly_ntt
```

The production body is:

```text
asm/gt/poly_ntt.s
asm/gt/ntt_gt_body.inc
asm/slothy/production/my_ntt_phase123.n1.opt.s
asm/slothy/production/my_32ntt.opt.s
```

The NTT32 contract in `my_32ntt.opt.s` is the active source evidence:

```text
Phase123 feeds raw 3-point DFT outputs bounded by 3*(q-1).
The five lazy CT stages stay below signed int16 range.
The final stage345 stores reduce to canonical range, split each output Q into
low/high D halves, and scatter directly to the final poly_ntt output layout.
```

For this audit, the only production-proven consumer contract is the current
final reduced Forward NTT output.  We model it as centered q representatives:

```text
q = 3457
current reduced representative envelope = [-1728, 1728]
```

The exact code may return a bounded centered representative rather than a
canonical unsigned representative.  Existing consumers are validated against
that current production convention.

## Wave 4 Consumer-Limited Proof Targets

These are proof/model targets only.  They are not implementation contracts.

| target | producer bound | immediate consumer bound | machine safe? | implementation safe? | missing proof |
|---|---:|---:|---|---|---|
| keygen_g baseinv-limited | `[-16383,16383]` | baseinv prepare `[-16383,16383]` | yes | no | `baseinv_8_prepare()`, `reduce_mul2`, `reduce_mul3`, and `fqmul_neon` semantic equivalence for wider representatives |
| encap_m reduced-non-centered | `[-3456,3456]` | Q31 addend machine `[-32767,32767]` | yes | no | Q31 byte-contract reducer proof for wider addend |
| decap_m1 poly_sub-limited | `[-31039,31039]` | `poly_sub` no-wrap about `[-31039,31039]` | yes | no | verify basemul range proof for wider `c_minus_m2` representatives |

The current wide stage345 variant remains outside these consumer-limited
targets:

```text
keygen_g loose [-32767,32767] exceeds baseinv prepare [-16383,16383].
decap_m1 loose [-32767,32767] exceeds poly_sub no-wrap about [-31039,31039].
encap_m loose is still blocked by the Q31 addend range proof.
```

## Consumer: `poly_baseinv_scaled_r`

Primary caller candidate:

```text
poly_ntt_loose_for_keygen_g
```

Relevant path:

```c
poly_ntt(&g, &g);
poly_baseinv_scaled_r(&ginv, &g);
```

The first strict consumer block is `baseinv_8_prepare()` in
`poly_gt_baseinv_batch.c`:

```c
int16x8x4_t a = vld4q_s16(src);
int16x8_t neg2a2 = vshlq_n_s16(vnegq_s16(a.val[2]), 1);
int16x8_t neg2a3 = vshlq_n_s16(vnegq_s16(a.val[3]), 1);

t0 = reduce_mul2(a.val[2], a.val[2], a.val[1], neg2a3, con);
t1 = fqmul_neon(a.val[3], a.val[3], con);
...
```

Machine-lane bound:

```text
vneg/vshl #1 without signed 16-bit wrap requires |a.val[2/3]| <= 16383
```

That is a machine safety bound only.  The semantic proof bound remains the
current production reduced representative envelope:

```text
semantic proof bound = [-1728, 1728]
```

Reason: `reduce_mul2`, `reduce_mul3`, and `fqmul_neon` use 16-to-32-bit products
and a Montgomery-style reduction.  A wider input may be machine-safe but still
requires a separate proof that quotient approximation, representative handling,
and denominator/numerator formulas remain equivalent.

Conclusion:

```text
keygen_g loose NTT is blocked unless the producer proves every output lane is
within the baseinv machine bound and a new baseinv semantic proof is added.
The current stage345 lazy bound "below signed int16" is not sufficient.
```

## Consumer: `poly_basemul_scaled_r_input`

Relevant keygen public arithmetic path:

```c
poly_basemul_scaled_r_input(&h, g, &finv);
```

This kernel uses the shared `base_gt_opt_body.inc` path with `ld4/st4` quartic
blocks.  It widens variable products into 32-bit accumulators, so its immediate
machine bound is not the first blocker for `keygen_g`.

However, this consumer is downstream of `poly_baseinv_scaled_r(ginv, g)`, so
`keygen_g` must satisfy the baseinv consumer first.  This audit does not claim
that scaled basemul is safe for arbitrary signed-int16 NTT residues.

Conclusion:

```text
not the primary keygen_g blocker; still requires a separate base_gt product
range proof for any widened representative contract.
```

## Consumer: `poly_basemul_add` / Q31 Encap Path

Candidate:

```text
poly_ntt_loose_for_encap_m
```

Current production encap uses Q31 for the encap-only `poly_basemul_add` +
`poly_tobytes` byte-contract path.  The additive operand `m` is folded into the
Q31 direct32 finalizer as a widened `saddw/saddw2` addend.

Machine-lane bound:

```text
the addend is loaded as int16 and widened to s32
```

Semantic proof bound:

```text
current Q31 byte-contract proof covers the production addend range only
```

Conclusion:

```text
encap_m loose NTT cannot be marked safe until the Q31 reducer proof is rerun
for the wider m range.  The generic arithmetic-correct poly_basemul_add path
would need its own base_gt accumulator proof and is not the current production
default for encap.
```

## Consumer: `poly_sub` + Decap Verify Basemul

Candidate:

```text
poly_ntt_loose_for_decap_m1
```

Current decap path:

```c
poly_ntt(&m2, &m1);
poly_sub(&c, &c, &m2);
poly_basemul(&r2, &c, &hinv);
```

`poly_sub` in `asm/gt/support/poly_support_n1.S` performs plain 16-bit vector
subtractions:

```asm
sub v?.8h, v?.8h, v?.8h
```

It does not reduce modulo q and does not widen.  If `c` is bounded by the
production centered envelope, avoiding signed 16-bit wrap in `c - m2` requires:

```text
m2 lower bound >= -31039
m2 upper bound <=  31039
```

because `1728 - (-32767) = 34495`, which would wrap a signed 16-bit lane.

The stage345 lazy contract only says values stay below signed int16, which
does not prove the tighter `[-31039, 31039]` requirement and does not prove the
verify basemul accepts the resulting wider `c_minus_m2` representatives.

Conclusion:

```text
decap_m1 loose NTT is blocked by poly_sub overflow risk and missing verify
basemul range proof.
```
