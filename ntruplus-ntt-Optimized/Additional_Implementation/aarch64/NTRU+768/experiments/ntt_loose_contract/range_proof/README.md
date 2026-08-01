# Loose NTT Range Proof Audit

Date: 2026-07-07

Scope: range proof/model only for caller-specific Forward NTT variants.

No ASM was written.  No Makefile target was added.  Production default, generic
`poly_ntt`, Q31, `poly_baseinv_scaled_r`, and polyinv semantics are unchanged.

## Files

```text
experiments/ntt_loose_contract/range_proof/README.md
experiments/ntt_loose_contract/range_proof/range_model.py
experiments/ntt_loose_contract/range_proof/consumer_bounds.md
experiments/ntt_loose_contract/range_proof/candidate_matrix.md
experiments/ntt_loose_contract/range_proof/p1c_per_store_proof.py
experiments/ntt_loose_contract/range_proof/p1c_per_store_bounds.json
experiments/ntt_loose_contract/range_proof/P1C-PER-STORE-PROOF.md
```

## Question

Can caller-specific Forward NTT variants return a wider or less canonical
output to save final reductions?

Initial candidates:

```text
poly_ntt_loose_for_keygen_g
poly_ntt_loose_for_encap_m
poly_ntt_loose_for_decap_m1
```

Avoided in this audit:

```text
keygen_f   // serialized into sk
encap_r    // serialized for hash_g
decap_r1   // serialized for verify
```

## Wave 4 Preservation Note

Wave 4 keeps the Wave 3 wide-output failure as a stopped proof state.  This is
not an ASM TODO and not a permission to write a wrapper.

Current wide variant:

```text
stage345_pre_final_barrett output: [-32767,32767]
removed reductions: all stage345 final output reduction chains
expected theoretical saving: 96 chains ~= 288 vector instructions per endpoint call
implementation safe: no
```

The three caller-specific failures are:

```text
keygen_g: loose [-32767,32767] exceeds baseinv prepare [-16383,16383].
decap_m1: loose [-32767,32767] exceeds poly_sub no-wrap about [-31039,31039].
encap_m: loose addend remains blocked by the Q31 addend range proof.
```

Proof-only narrower variants recorded in `range_model.py` and
`candidate_matrix.md`:

| proof-only variant | producer bound | consumer bound | machine safe? | implementation safe? | expected instruction / cycle saving |
|---|---:|---:|---|---|---|
| `keygen_g_baseinv_machine_limited` | `[-16383,16383]` | baseinv prepare `[-16383,16383]` | yes | no | 3 vector instructions per proven removed chain; upper bound 288 instructions if all 96 endpoint chains meet this bound. Current cycle saving is 0 because no proof exists. |
| `encap_m_reduced_non_centered` | `[-3456,3456]` | Q31 addend machine `[-32767,32767]`; semantic proof currently `[-1728,1728]` | yes | no | unknown/likely 0 because no separate centering tail exists in the current schedule. |
| `decap_m1_poly_sub_no_wrap_limited` | `[-31039,31039]` | poly_sub no-wrap about `[-31039,31039]` | yes | no | 3 vector instructions per proven removed chain; upper bound 288 instructions if all 96 endpoint chains meet this bound. Current cycle saving is 0 because no proof exists. |

Rows that are machine-safe but not implementation-safe still require both a
per-store producer bound and the downstream semantic proof before any ASM work.

## Producer Bounds

Source evidence is the production NTT32 header in
`asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S`.

| stage / variant | conservative bound | evidence | status |
|---|---:|---|---|
| Phase123 output into NTT32 | `[-10368,10368]` | source comment: raw 3-point DFT bounded by `3*(q-1)` | internal only |
| after NTT32 stage12 | unknown tighter bound, below signed int16 later | stage12 is an internal memory boundary | not a public output |
| after NTT32 stage345 before final output reduction | below signed int16, modeled as `[-32767,32767]` | source comment: five lazy CT stages stay below signed int16 | not safe for consumers by itself |
| production final store | modeled as `[-1728,1728]` | final stage345 stores reduce before scatter | safe production contract |
| hypothetical reduced non-centered output | `[-3456,3456]` | generic reduced residue envelope | no clear separable implementation in current schedule |

The production stage345 final reduction is interleaved with scatter stores.
Dynamic per full `poly_ntt` call:

```text
3 rows * 4 blocks * 8 final output vector reduction chains = 96 chains
each chain ~= sqdmulh + srshr + mls
theoretical instruction removal if all removed ~= 288 vector instructions
```

This is attractive only if the consumer range proof succeeds.  It does not.

The flattened production source contains both mutually-exclusive endpoint
suffixes, so a source-wide count sees 192 chains.  A call executes exactly one
96-chain suffix; 192 is not a per-call count.

## Consumer Findings

Detailed bounds are in `consumer_bounds.md`.

### keygen_g

Path:

```c
poly_ntt(&g, &g);
poly_baseinv_scaled_r(&ginv, &g);
poly_basemul_scaled_r_input(&h, g, &finv);
```

`baseinv_8_prepare()` immediately performs signed 16-bit negation and doubling:

```c
vshlq_n_s16(vnegq_s16(a.val[2]), 1)
vshlq_n_s16(vnegq_s16(a.val[3]), 1)
```

Machine safety requires roughly:

```text
|a| <= 16383
```

The loose stage345 pre-reduction envelope is only known to be below signed
int16:

```text
[-32767,32767]
```

Therefore keygen_g loose NTT fails the current machine-bound proof.

### encap_m

Path:

```c
poly_ntt(&m, &m);
poly_basemul_add / Q31 encap byte-contract
```

The production default uses Q31 direct32 for the encap-only byte-contract path.
The existing Q31 proof covers the production addend range, not a wider loose
NTT addend.  This is blocked until the Q31 reducer proof is extended.

### decap_m1

Path:

```c
poly_ntt(&m2, &m1);
poly_sub(&c_minus_m2, &c, &m2);
poly_basemul(&r2, &c_minus_m2, &hinv);
```

`poly_sub` is a plain 16-bit vector subtract.  If `c` is in the production
centered envelope, avoiding `c - m2` int16 wrap requires approximately:

```text
m2 in [-31039,31039]
```

The loose stage345 pre-reduction envelope `[-32767,32767]` exceeds that bound,
so decap_m1 loose NTT fails before verify basemul proof is considered.

## Model

Run:

```sh
python3 ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/ntt_loose_contract/range_proof/range_model.py
```

The script prints a conservative candidate/consumer matrix.  It marks a row
safe only if both:

1. producer bound is inside the consumer machine bound, and
2. producer bound is inside the current semantic proof bound.

Rows marked `needs_proof` are machine-safe but exceed the current semantic
proof.  Rows marked `no` violate a machine or no-wrap bound.

## Decision

```text
poly_ntt_loose_for_keygen_g: stopped_no_range_proof
poly_ntt_loose_for_encap_m: blocked_q31_range_proof
poly_ntt_loose_for_decap_m1: stopped_no_range_proof
```

No ASM candidate should be written from this proof state.

## Validation

Commands:

```sh
python3 ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/ntt_loose_contract/range_proof/range_model.py
make -C ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/ntt_loose_contract/range_proof check
git diff --check
```
