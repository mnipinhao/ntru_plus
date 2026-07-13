# Decap Verify V3 Register-Resident Direct Pack Audit

Status: blocked for the current final-store-hook architecture.  No V3 ASM was
implemented from this audit.

## Target Contract

The desired helper remains:

```text
gt_decap_verify_basemul_tobytes_direct_candidate(out, c_minus_m2, hinv)
==
poly_tobytes(poly_basemul(c_minus_m2, hinv))
```

The helper is decap-only and byte-output-only.  It must not replace
`poly_basemul`, must not reuse Q31, and must not expose a public poly API.

## Why V2 Was Not Enough

The V2 candidate used the production basemul body and replaced the final store
with:

```text
loop A output -> stack
loop B output -> stack
stack ld1 shape -> production poly_tobytes vector pack
```

Pi5 result:

```text
decap_verify_basemul_plus_tobytes_r2      = 3245 cycles
decap_verify_contract_direct_candidate    = 3330 cycles
full_decap_current                        = 33307 cycles
full_decap_contract_direct_candidate      = 33418 cycles
```

Decision:

```text
correctness-pass PMU-regression
do not continue conservative scratch conversion
```

## Current Hook Boundary

The reusable include:

```text
asm/gt/basemul/poly_basemul_body.inc
```

exposes only this hook:

```text
GT_BASEMUL_FINAL_STORE(out0, out1, out2, out3)
```

At that point one basemul loop has four vectors:

```text
out0.8h, out1.8h, out2.8h, out3.8h
```

This is exactly one 32-coefficient GT block-major `st4` output.  Production
`poly_tobytes`, however, packs 64 coefficients per loop, so a byte-equivalent
direct pack needs two consecutive basemul loops.

## Register Lifetime Blocker

Static scan of `Lgt_basemul_loop` in `poly_basemul_body.inc`:

```text
vector_regs_used = v0..v31
missing_free_vector_regs = none
```

The final correction block also touches all vector registers.  Therefore the
first 32-coefficient half cannot be kept in Neon registers while the second
basemul loop runs when reusing the current production body.  Any hook-only
implementation must either:

```text
1. store the first half to scratch, then reload it later, or
2. write the first half as non-contiguous byte chunks.
```

Option 1 is the V2 route and already regressed.  Option 2 requires eight
6-byte stores into 12-byte-strided positions per 64-coefficient chunk; that is
not a good Neon store pattern and is likely to become scalar or narrow-lane
store dominated.

## Why One-Loop Direct Pack Is Awkward

For each 64-coefficient `poly_tobytes` chunk, the support kernel packs the low
and high 32-coefficient halves together.  The byte order is lane grouped:

```text
0, 8, 16, 24, 32, 40, 48, 56,
1, 9, 17, 25, 33, 41, 49, 57,
...
```

The low 32-coefficient basemul loop contributes only the first half of each
12-byte lane group; the following basemul loop contributes the second half.
That is why V2 batched two basemul loops before calling the vector pack network.

Packing only one basemul loop at a time would need strided byte output:

```text
low half writes offsets 0..5, 12..17, 24..29, ...
high half writes offsets 6..11, 18..23, 30..35, ...
```

NEON has no efficient contiguous-vector store for this pattern.

## Viable V3 Shape

A real V3 requires a new two-loop DAG, not just a final-store hook:

```text
basemul loop A product/reduction
  -> reduce/normalize/partially pack low half
  -> keep packed low-half intermediates live

basemul loop B product/reduction with reserved registers
  -> reduce/normalize/pack high half
  -> combine low/high packed intermediates
  -> st1 96 bytes
```

To make this possible, the basemul body would need a new register allocation
that reserves at least the low-half packed intermediates across loop B.  That is
not compatible with the current Slothy-scheduled body, which already uses every
Neon register.

## Required Next Design If Reopened

Before writing V3 ASM, produce:

```text
1. a two-loop basemul+pack symbolic DAG
2. a register allocation plan with explicit reserved vectors
3. a lane map from GT st4 output vectors to exact POLYBYTES offsets
4. a range proof that normalization input is still centered [-1728,1728]
5. a benchmark-only harness against decap_verify_basemul_plus_tobytes_r2
```

Promotion bar remains:

```text
candidate < decap_verify_basemul_plus_tobytes_r2 - 100 cycles
full_decap_contract_direct_candidate <= full_decap_current - 50 cycles
```

## Decision

```text
current hook-only V3 route: blocked
current scratch-conversion route: stopped
next possible route: new two-loop register-allocation DAG only
```

No production behavior changes are made by this audit.
