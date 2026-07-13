# Caller-specific loose NTT contract audit

Date: 2026-07-07

Scope: benchmark-only audit for `poly_ntt_loose_for_keygen_g`.
No production code, Makefile rule, generic `poly_ntt`, Q31 path, or KEM
default was changed.

Wave 3 update: the audit now has a machine-readable range model and expanded
candidate matrix under:

```text
experiments/ntt_loose_contract/range_proof/
```

Wave 4 update: the range proof docs now preserve the wide loose-output failure
and record narrower proof-only variants.  The variants are model/docs only:
`keygen_g_baseinv_machine_limited` at `[-16383,16383]`,
`encap_m_reduced_non_centered` at `[-3456,3456]`, and
`decap_m1_poly_sub_no_wrap_limited` at `[-31039,31039]`.

The result remains: no loose NTT ASM candidate should be written yet.

## Goal

Test whether the keygen `g` caller can use a wider or less canonical forward
NTT output because `g` is not serialized directly.

Current keygen `g` path:

```c
poly_cbd1(g, buf);
poly_triple(g, g);
poly_ntt(g, g);
return KEYPAIR_BASEINV(ginv, g);
```

Later keypair arithmetic consumes `g` as:

```c
KEYPAIR_BASEMUL(&h, g, finv);
KEYPAIR_BASEMUL(&hinv, f, ginv);
```

Candidate under audit:

```c
void poly_ntt_loose_for_keygen_g(poly *out, const poly *g_small_triple);
```

The intended external layout would remain the production GT block-major
row-bitrev layout.  Only final output reductions would be relaxed or removed.

## Production NTT Contract

Production entrypoint:

```text
poly_ntt / gt_block_major_poly_ntt
```

Production source:

```text
asm/gt/ntt/poly_ntt.S
asm/gt/ntt/poly_ntt_body.inc
asm/gt/ntt/ntt768_gt_frontend.n1.opt.inc
asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S
```

Important contract from `asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S`:

```text
Phase123 feeds raw 3-point DFT outputs bounded by 3*(q-1).
The five lazy CT stages stay below signed int16 range.
The final stage345 stores reduce to canonical range, split each output Q into
low/high D halves, and scatter directly to the final poly_ntt output layout.
```

The reduction is not one clean function tail.  It is interleaved with stage345
final scatter stores.  Each final D-half store is typically preceded by:

```asm
sqdmulh v?.8h, v?.8h, v0.h[1]
srshr   v?.8h, v?.8h, #11
mls     v?.8h, v?.8h, v0.h[0]
str     d?, [address]
```

So a loose variant would need to remove or alter many local chains inside the
stage345 store schedule, not just skip a single trailing canonicalization pass.

## Consumer Contract: Keygen `g`

Although `g` is not serialized directly, it is not a byte-contract-only value.
It feeds arithmetic consumers:

1. `poly_baseinv_scaled_r(ginv, g)`
2. `poly_basemul_scaled_r_input(h, g, finv)`

The first consumer is the blocker.  In `poly_gt_baseinv_batch.c`,
`baseinv_8_prepare()` reads the NTT-domain polynomial using `vld4q_s16()` and
performs quartic inverse numerator/denominator preparation:

```c
int16x8x4_t a = vld4q_s16(src);
int16x8_t neg2a2 = vshlq_n_s16(vnegq_s16(a.val[2]), 1);
int16x8_t neg2a3 = vshlq_n_s16(vnegq_s16(a.val[3]), 1);

t0 = reduce_mul2(a.val[2], a.val[2], a.val[1], neg2a3, con);
t1 = fqmul_neon(a.val[3], a.val[3], con);
...
```

The consumer therefore assumes each input coefficient is already safe for
signed 16-bit lane negation/doubling and for the existing `reduce_mul2`,
`reduce_mul3`, and `fqmul_neon` preconditions.

`poly_baseinv_scaled_r` can tolerate the current production representative
contract.  This audit did not find a proof that it can tolerate unreduced
stage345 outputs.

## Range Proof Status

Known safe bound in production:

```text
stage345 final stores reduce to canonical range before keygen baseinv sees g
```

Known loose candidate bound:

```text
stage345 pre-final-reduction is only known to be below signed int16
```

The NTT32 comment only proves that the lazy CT stages stay within signed int16
before the final store reductions.  That is enough for NTT internal arithmetic,
but it does not prove that the unreduced values are valid inputs for the
quartic base inverse preparation.  In particular:

```text
baseinv_8_prepare performs signed 16-bit vneg/vshl by 1 before widening.
Removing final reduction can make these local preconditions fail even if the
coefficient is congruent mod q.
```

A correct loose candidate would need a machine-checkable bound for every
coefficient at every final stage345 store, plus a second proof that the
downstream baseinv denominator/numerator preparation remains equivalent and
does not overflow or change representative-sensitive behavior.

That proof is not available in the current codebase.

## Candidate Decision

No candidate ASM was generated in this pass.

Reason:

```text
No range proof for keygen_g loose NTT output into poly_baseinv_scaled_r.
Any implementation that simply calls production poly_ntt would be a wrapper.
Any implementation that removes final reductions from stage345 would be unsafe
without a new per-store range proof and downstream baseinv equivalence proof.
```

Status:

```text
poly_ntt_loose_for_keygen_g: stopped_no_range_proof
raw_ntt_exact_mismatches: not measured, no candidate
downstream_exact_mismatches: not measured, no candidate
byte_mismatches: not measured, no candidate
full_kem_mismatches: not measured, no candidate
```

Expanded Wave 3 statuses:

```text
poly_ntt_loose_for_keygen_g:
  stopped_no_range_proof
  failing bound: stage345 loose [-32767,32767] exceeds baseinv prepare
  machine-safe bound [-16383,16383]

poly_ntt_loose_for_encap_m:
  blocked_q31_range_proof
  reason: existing Q31 byte-contract proof covers production addend range only

poly_ntt_loose_for_decap_m1:
  stopped_no_range_proof
  failing bound: stage345 loose [-32767,32767] can exceed poly_sub no-wrap
  envelope for c - m2, approximately [-31039,31039]
```

See:

```text
range_proof/README.md
range_proof/consumer_bounds.md
range_proof/candidate_matrix.md
range_proof/range_model.py
```

## Makefile Snippet for Future Candidate

Do not add this until the range proof exists and
`asm/gt/experiment/poly_ntt_loose_for_keygen_g.S` is real, non-wrapper code.

```make
GT_NTT_LOOSE_KEYGEN_G_PMU_TARGET = bench_gt_ntt_loose_contract_pmu
GT_NTT_LOOSE_KEYGEN_G_PMU_SOURCES = \
	bench_gt_ntt_loose_contract_pmu.c \
	$(GT_KEM_CURRENT_WRAPPER) \
	$(SCHEME_DIR)/experiments/ntt_loose_contract/poly_ntt_loose_oracle.c \
	$(SCHEME_DIR)/asm/gt/experiment/poly_ntt_loose_for_keygen_g.S \
	$(GT_PRODUCTION_SOURCES)

.PHONY: bench_gt_ntt_loose_contract_pmu
bench_gt_ntt_loose_contract_pmu: $(GT_NTT_LOOSE_KEYGEN_G_PMU_TARGET)
	$(SUDO) ./$(GT_NTT_LOOSE_KEYGEN_G_PMU_TARGET)

$(GT_NTT_LOOSE_KEYGEN_G_PMU_TARGET): $(GT_NTT_LOOSE_KEYGEN_G_PMU_SOURCES) bench.c
	$(CC) $(CPPFLAGS) $(CFLAGS) $(GT_PRODUCTION_FLAGS) \
		-DGT_EXPERIMENT_USE_NTT_LOOSE_KEYGEN_G \
		-I. -I$(SCHEME_DIR) \
		-o $@ bench.c $(GT_NTT_LOOSE_KEYGEN_G_PMU_SOURCES) $(LDFLAGS)
```

## Validation

Commands run:

```sh
git diff --check
```

No PMU command was run because no correctness-valid candidate was built.

## Next Action

Do not continue with keygen_g loose NTT until one of these exists:

1. A per-store stage345 range proof for unreduced outputs.
2. A downstream baseinv proof showing `baseinv_8_prepare()` is equivalent and
   safe for that wider range.
3. A tagged differential oracle that can isolate the first representative drift
   in `poly_baseinv_scaled_r`.

If the project still wants loose NTT variants, `encap_m` may be a better next
audit target than `keygen_g` because its consumer is basemul/add rather than
base inversion, but it still needs the Q31 addend range proof before any ASM
work.  The next safe implementation candidate is therefore none; the next
proof-only candidate is a per-store stage345 bound paired with the matching
downstream semantic proof.
