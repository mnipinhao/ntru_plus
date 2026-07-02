# Decap Verify Direct Byte Finalizer Design

Status: design audit only.  No optimized ASM has been implemented.

## Production Basemul Output Contract

Production decap verify currently calls plain `poly_basemul`:

```text
poly_basemul(&r2, &c_minus_m2, &hinv)
poly_tobytes(buf1, &r2)
```

The linked symbol is:

```text
symbol: poly_basemul
wrapper: asm/gt/poly_basemul.s
body: asm/gt/base_gt_opt_body.inc
```

`poly_basemul.s` owns the public `poly_basemul` symbol and
includes the shared `base_gt_opt_body.inc` basemul body.  The body include does
not export a public ABI by itself.

### Input And Output Layout

The input and output layout is GT block-major row-bitrev:

```text
coeff[branch * 384 + 4 * physical_j + lane]
```

Each loop handles eight physical quartic blocks:

```text
ld4 a0..a3 for physical_j..physical_j+7
ld4 b0..b3 for physical_j..physical_j+7
st4 out0..out3 for physical_j..physical_j+7
```

One loop stores:

```text
4 coefficients * 8 lanes * 2 bytes = 64 bytes = 32 coefficients
```

There are 24 loops, so the full output is `24 * 64 = 1536` bytes.

### Final Reduction Before Store

For the non-rminus1 plain `poly_basemul` path, `base_gt_opt_body.inc` finishes each
loop with two reduction stages before the final `st4`.

First, it applies the final Montgomery/factor correction to four output
vectors.  In the current scheduled source this is the block beginning after the
last `uzp2` group:

```text
mul       out?, raw?,  v0.h[3]
sqrdmulh  q?,   raw?,  v0.h[4]
mls       out?, q?,    v0.h[0]
```

Then it applies the centered Barrett-style representative reduction:

```text
sqdmulh  t?,   out?, v0.h[1]
srshr    t?,   t?,   #11
mls      out?, t?,   v0.h[0]
```

The final store is:

```text
st4 {v23.8H, v24.8H, v25.8H, v26.8H}, [x0], #64
```

The constants are loaded from `Lgt_base_consts`:

```text
v0.h[0] = 0x0d81 = q = 3457
v0.h[1] = 0x4bd4
v0.h[2] = 0xcd7f
v0.h[3] = 0xff6d
v0.h[4] = 0xfa8f
```

This audit does not rename the non-q constants beyond their current ASM role;
any optimized direct finalizer must preserve the existing arithmetic sequence
unless a separate range proof is written.

### Representative Range

The current PMU/range harness observed, over valid, invalid, and synthetic
cases:

```text
c_minus_m2_min=-4095,c_minus_m2_max=5823
hinv_min=-4095,hinv_max=4095
r2_pre_tobytes_min=-1728,r2_pre_tobytes_max=1728
```

This supports the intended contract that stored `r2` coefficients are already
centered representatives in:

```text
[-1728, 1728]
```

It is empirical coverage, not a formal product-bound proof.  A release
candidate still needs a proof that the final reduction always returns this
representative range for all decap verify inputs.

## Production Tobytes Contract

The linked `poly_tobytes` symbol is:

```text
symbol: poly_tobytes
source: asm/gt/support/poly_support_n1.S
```

This is the production support kernel, not the older `asm/stock/pack.s` path.

### Input Assumption

`poly_tobytes` expects int16 coefficients.  It does not require canonical
`[0,q)` input.  It normalizes each lane as:

```text
t = x + ((x >> 15) & q)
```

For the observed centered range, this maps:

```text
x >= 0: t = x
x <  0: t = x + 3457
```

Since `x in [-1728, 1728]`, the packed value is always in:

```text
[0, 3456] < 4096
```

### Byte Packing

After normalization, two 12-bit coefficients are packed as:

```text
out[3*i + 0] = t0 & 0xff
out[3*i + 1] = (t0 >> 8) | (t1 << 4)
out[3*i + 2] = t1 >> 4
```

The production support kernel reads 64 coefficients per loop and writes 96
bytes per loop.

### Lane And Memory Order

The support kernel does not serialize memory as simple adjacent coefficient
pairs.  Within each 64-coefficient chunk, the public serialization order is:

```text
0, 8, 16, 24, 32, 40, 48, 56,
1, 9, 17, 25, 33, 41, 49, 57,
2, 10, 18, 26, 34, 42, 50, 58,
3, 11, 19, 27, 35, 43, 51, 59,
4, 12, 20, 28, 36, 44, 52, 60,
5, 13, 21, 29, 37, 45, 53, 61,
6, 14, 22, 30, 38, 46, 54, 62,
7, 15, 23, 31, 39, 47, 55, 63
```

This order matches the production Slothy `poly_tobytes` transpose network and
was confirmed by the byte-correct C candidate.

## Direct Finalizer Candidate

The next viable optimized helper is:

```text
gt_decap_verify_basemul_tobytes_direct_candidate(out, c_minus_m2, hinv)
```

It should conceptually keep the plain `poly_basemul` arithmetic through the
existing final reduction, but replace:

```text
st4 reduced poly output
later poly_tobytes load/normalize/transpose/store
```

with:

```text
final reduction in registers
normalize centered lanes with q
pack directly to POLYBYTES output
```

### Reusable Part

The pointwise quartic product arithmetic and both final reductions can be
reused first.  That keeps the candidate conservative:

```text
current product DAG
current Montgomery/factor correction
current centered Barrett reduction
new byte-packing store path
```

Do not start by replacing the final reduction formula.  That would require a
new product-bound proof and is a separate candidate.

### Replacement Boundary

The natural cut point is immediately before:

```text
st4 {v23.8H, v24.8H, v25.8H, v26.8H}, [x0], #64
```

At that point, the four vectors are centered representatives for eight quartic
blocks.  A direct-byte version should consume these vectors instead of storing
them as a `poly`.

### Two-Loop Packing Requirement

One `poly_basemul` loop produces 32 coefficients.  One production `poly_tobytes`
loop consumes 64 coefficients.  Therefore a clean direct-byte finalizer should
batch two consecutive basemul loops:

```text
basemul loop A -> 32 reduced coefficients
basemul loop B -> 32 reduced coefficients
pack A+B into 96 output bytes
```

This avoids writing 64-byte poly chunks and reloading 128-byte tobytes chunks.
It also avoids awkward non-contiguous stores where loop A writes only half of
each 12-byte group and loop B fills the other half later.

### Potential Saving

The current measured windows are:

```text
decap_verify_basemul_plus_tobytes_r2 = 3288 cycles
decap_tobytes_r2                      = 421 cycles
decap_verify_contract_ref             = 3244 cycles
```

The optimistic local ceiling is roughly the standalone `poly_tobytes` cost:

```text
~400-425 cycles/call
```

The direct finalizer will need its own normalization, byte pack, and byte
stores, so expected practical saving is lower:

```text
~150-350 cycles/call
```

Projected full decap impact at `decap_total ~= 33362 cycles`:

```text
150 cycles ~= 0.45%
350 cycles ~= 1.05%
425 cycles ~= 1.27%
```

This is a small local candidate, not a major full-KEM target.

## Risks And Required Proofs

Required before ASM:

```text
1. Formalize final reduced lane range, not only empirical range capture.
2. Prove centered normalization is sufficient for every decap verify input.
3. Preserve production support-kernel byte order exactly.
4. Show two-loop packing does not create secret-dependent stores or branches.
5. Estimate register pressure for holding two output blocks plus pack temps.
6. Keep generic poly_basemul unchanged.
7. Keep Q31 out of this path.
```

Main implementation risks:

```text
register pressure from two basemul output blocks
mistaken public-byte order
accidentally producing simple adjacent-pair packing instead of support order
trying to reuse Q31 range proof where the arithmetic contract is different
claiming full-decap impact from local PMU only
```

## Recommendation

Proceed only with a benchmark-only prototype if the next pass can keep the
existing final reduction and directly pack two basemul loops at a time.  A
one-loop direct-byte prototype is likely to either use awkward non-contiguous
stores or reintroduce a layout buffer, which would erase most of the benefit.

## Prototype Result - 2026-07-01

The first benchmark-only ASM prototype is:

```text
asm/bench_only/gt_decap_verify_basemul_tobytes_direct_candidate.S
symbol: gt_decap_verify_basemul_tobytes_direct_candidate
gate: GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_DIRECT
```

It compiles the current `base_gt_opt_body.inc` plain basemul body with a default-off
final-store hook:

```text
loop A: final reduced 32 coeffs -> stack-staged st4
loop B: final reduced 32 coeffs + staged loop A -> direct 96-byte output
```

Correctness passed:

```text
verify_basemul_tobytes_mismatches=0
decap_verify_contract_total_mismatches=0,valid_cases=256,invalid_cases=1280
```

PMU on Pi5:

| window | cycles p50 | cycles IQR | instr p50 |
| --- | ---: | ---: | ---: |
| `decap_verify_basemul_plus_tobytes_r2` | 3288 | 0 | 3290 |
| `decap_verify_contract_direct_candidate` | 4355 | 1 | 5947 |
| `full_decap_current` | 33352 | 11 | 75217 |
| `full_decap_contract_direct_candidate` | 34487 | 15 | 77875 |

Decision:

```text
status: rejected_pmu_regression
local delta: +1067 cycles
full decap delta: +1135 cycles
```

This result says the byte contract and final-store hook are viable for
correctness, but scalar byte packing is not performance-viable.  A future
attempt would need vector byte packing close to the production `poly_tobytes`
network, or the route should remain stopped.
