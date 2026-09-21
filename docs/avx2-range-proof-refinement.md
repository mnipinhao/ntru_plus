# AVX2 range-proof refinement: proposal, not a new proof

Source: user-supplied Hanno Becker, *Neon NTT – (Auto)formalised*,
`2026-1223-Neon NTT – (Auto)formalised.pdf`. Relevant material includes the
scope discussion, Montgomery bounds, Section 7 Barrett–Montgomery bridge and
constant-specific bounds, and the word-operation model.

The paper formalizes modular arithmetic kernels against an abstract word
model. It does not establish our full AVX2 NTT or our linked binary. Existing
Python enumeration and interval ledgers are useful executable evidence, but
must not be described as Isabelle-checked proofs.

## What transfers

1. Separate congruence, Montgomery exponent, representative bounds and machine
   instruction correctness. Proving a residue identity does not prove i16 safety.
2. Use the actual fixed constant and rounding rule when bounding a constant
   multiplication, rather than one worst-case envelope for every twiddle.
   Section 7 shows why approximation error / the relevant twisted residue can
   yield sharper bounds. Its assumptions must be checked for the AVX2 sequence.
3. Keep mathematical theorems, generated constants and executable checks linked
   by source/constant hashes, so documentation cannot silently use old bounds.

## Proposed AVX2 proof layers

| Layer | Obligation |
| --- | --- |
| Word semantics | Model low-word multiply, signed high-word multiply, shifts, wrapping add/sub and the exact rounding instruction in use |
| Arithmetic macro | Prove modular result, exponent and bounds for the actual Montgomery / Barrett sequence |
| Constant and lane | Specialize to branch, twiddle, lane and caller domain; cache exhaustive fixed-constant certificates where useful |
| Butterfly relation | Preserve shared-input correlations rather than treating every output interval as independent |
| Caller composition | Verify h in [0,3456], actual r/m bounds, operand order, finalizer, addend and serializer preconditions |
| Linked realization | Tie macro identities to actual instruction order, constants, def-use and load/store ownership |

Do not substitute a NEON instruction theorem for an AVX2 instruction with a
similar name. Rounding, saturation and extreme signed operands require explicit
conformance checks. Intentional low-word wrap inside Montgomery is allowed;
accidental pre-operation overflow must not be hidden by a simulator cast.

The relational-butterfly and caller layers above are proposed extensions for
our workload, not results claimed by the paper.

## Apply first to the current 768 Encap path

The existing conservative Forward envelope is approximately ±15605 for small
inputs; it is not a demonstrated reachable maximum. Keep that safe result while
refining the first operations where correlations are lost:

1. Retain frontend exact reachable sets and identify where D16/D8 propagation
   first replaces them with independent intervals.
2. For those nodes, retain joint sum/difference relations, lane/branch identity
   and constant-specific multiplication images. Use local finite enumeration
   or a solver only where interval reasoning is inconclusive.
3. Recheck asymmetric h×r with the real operand order, all partial sums, lambda,
   R² finalization and +m. Do not import inverse-domain assumptions.
4. Verify serialization as a consumer contract separately from the numerical
   suffix of its function name; maintain exact wire and r-immutability tests.

Every ledger row should carry source instruction / semantic node, domain,
operand relation, integer pre-operation bounds, machine word result, residue,
scale, proof method and outcome. Outcomes must distinguish **proved safe**,
**conservative analysis inconclusive**, and **reachable counterexample**.

Only after this closure should a reduction-removal candidate be considered.
Tighter proof may permit more aggressive code; it is not evidence by itself
that any particular reduction is redundant or that cycles will improve.

Implementation of this proposal is deferred until repository organization and
checkpoint review are complete. No new ASM or benchmark is part of this cleanup.
