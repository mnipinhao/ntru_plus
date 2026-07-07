# Loose NTT Candidate Matrix

Date: 2026-07-07

Generated from the same assumptions encoded in `range_model.py`.

## Summary

No loose NTT candidate is safe to implement yet.

The only reduction-removal variant with obvious instruction savings is removing
the stage345 final output reduction chains:

```text
3 NTT32 rows * 4 stage345 blocks * 16 output reduction chains
= 192 chains per poly_ntt

Each chain is approximately:
  sqdmulh + srshr + mls

theoretical removed vector instructions ~= 576 per full poly_ntt
```

That variant only has the existing NTT-internal guarantee:

```text
below signed int16
```

It does not satisfy the downstream consumer contracts below.

Wave 4 preserves that failure and records only proof/model variants.  No row
below authorizes ASM.  A `needs proof` row has expected savings of 0 until both
the per-store producer bound and downstream semantic proof exist.

## Wave 4 Proof-Only Variants

| proof-only variant | candidate | producer bound | consumer bound | machine safe? | implementation safe? | expected instruction reduction | cycle estimate | blocker |
|---|---|---:|---:|---|---|---|---|---|
| `keygen_g_baseinv_machine_limited` | `poly_ntt_loose_for_keygen_g` | `[-16383,16383]` | baseinv prepare `[-16383,16383]` | yes | no | 3 vector instructions per proven removed chain; upper bound ~576 if all 192 chains meet this bound | 0 now; proportional to removed chains only after proof and measurement | baseinv semantic proof still covers only production `[-1728,1728]` representatives |
| `encap_m_reduced_non_centered` | `poly_ntt_loose_for_encap_m` | `[-3456,3456]` | Q31 machine `[-32767,32767]`; current semantic proof `[-1728,1728]` | yes | no | unknown/likely 0 because no separate centering tail exists | unknown | Q31 byte-contract proof must be rerun for wider addend |
| `decap_m1_poly_sub_no_wrap_limited` | `poly_ntt_loose_for_decap_m1` | `[-31039,31039]` | poly_sub no-wrap about `[-31039,31039]` | yes | no | 3 vector instructions per proven removed chain; upper bound ~576 if all 192 chains meet this bound | 0 now; proportional to removed chains only after proof and measurement | verify basemul semantic proof still covers only production representatives after `poly_sub` |

## Matrix

| candidate | removed reductions | output bound | consumer accepted bound | safe? | expected instruction reduction | cycle estimate | next action |
|---|---|---:|---:|---|---:|---|---|
| `poly_ntt_loose_for_keygen_g` | none / representative wording only | `[-1728,1728]` | current production | yes but no-op | 0 | 0 | no implementation value |
| `poly_ntt_loose_for_keygen_g` | hypothetical final centering only | `[-3456,3456]` | baseinv machine `[-16383,16383]`; semantic proof `[-1728,1728]` | needs proof | unknown / likely 0 because no separate centering tail exists | unknown | prove baseinv semantic equivalence before code |
| `poly_ntt_loose_for_keygen_g` | selected final chains, proof target only | `[-16383,16383]` | baseinv machine `[-16383,16383]`; semantic proof `[-1728,1728]` | no / needs proof | 3 vector instructions per proven chain; max ~576 if all chains satisfy this bound | 0 now; measure only after proof | prove per-store bounds and baseinv semantic equivalence before code |
| `poly_ntt_loose_for_keygen_g` | all stage345 final output reductions | `[-32767,32767]` conservative | baseinv machine `[-16383,16383]` | no | ~576 vector instr per `poly_ntt` | potentially large but invalid | stopped_no_range_proof; failing bound exceeds `vneg/vshl #1` safe range |
| `poly_ntt_loose_for_encap_m` | none / representative wording only | `[-1728,1728]` | current Q31 addend proof | yes but no-op | 0 | 0 | no implementation value |
| `poly_ntt_loose_for_encap_m` | hypothetical final centering only | `[-3456,3456]` | Q31 existing proof covers production range only | needs proof | unknown / likely 0 | unknown | rerun Q31 exact byte-contract proof for wider addend |
| `poly_ntt_loose_for_encap_m` | all stage345 final output reductions | `[-32767,32767]` conservative | Q31 existing proof covers production range only | no / needs proof | ~576 vector instr per `poly_ntt` | potentially large but unsafe | blocked until Q31 reducer range is extended and full encap differential passes |
| `poly_ntt_loose_for_decap_m1` | none / representative wording only | `[-1728,1728]` | current `poly_sub` + verify basemul contract | yes but no-op | 0 | 0 | no implementation value |
| `poly_ntt_loose_for_decap_m1` | hypothetical final centering only | `[-3456,3456]` | `poly_sub` machine safe; verify basemul semantic proof current only | needs proof | unknown / likely 0 | unknown | prove verify basemul accepts wider `c_minus_m2` |
| `poly_ntt_loose_for_decap_m1` | selected final chains, proof target only | `[-31039,31039]` | `poly_sub` no-wrap about `[-31039,31039]`; verify basemul semantic proof `[-1728,1728]` | no / needs proof | 3 vector instructions per proven chain; max ~576 if all chains satisfy this bound | 0 now; measure only after proof | prove per-store bounds and verify basemul range semantics before code |
| `poly_ntt_loose_for_decap_m1` | all stage345 final output reductions | `[-32767,32767]` conservative | `poly_sub` no-wrap requires about `[-31039,31039]` for m2 | no | ~576 vector instr per `poly_ntt` | potentially large but invalid | stopped_no_range_proof; failing bound can overflow `poly_sub` |

## Candidate Status

```text
poly_ntt_loose_for_keygen_g:
  status: stopped_no_range_proof
  exact failing bound: stage345 loose [-32767,32767] exceeds baseinv prepare
  machine-safe bound [-16383,16383]

poly_ntt_loose_for_encap_m:
  status: blocked_q31_range_proof
  exact failing proof: existing Q31 byte-contract reducer was proven for the
  production addend range, not loose NTT output.

poly_ntt_loose_for_decap_m1:
  status: stopped_no_range_proof
  exact failing bound: stage345 loose [-32767,32767] exceeds poly_sub no-wrap
  envelope for c - m2, approximately [-31039,31039].
```

## What Would Unblock This Track

1. Per-store symbolic bounds for each stage345 output before final reduction.
2. A proof that a selected subset of reductions can be removed while all
   remaining outputs stay within the relevant consumer bound.
3. A downstream semantic proof:
   - keygen_g: `baseinv_8_prepare()` equivalence for wider residues.
   - encap_m: Q31 byte-contract reducer exhaustive proof for the wider addend.
   - decap_m1: `poly_sub` no-wrap plus verify basemul range proof.
