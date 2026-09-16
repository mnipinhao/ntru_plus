# ToBytes producer range audit

Scope: localized/review. No production, arithmetic, or ToBytes assembly edits.
Ring q=3457, N=864; FR0 input is signed int16 in R0. Output bytes require
canonical [0,q-1], not merely a congruent representative.

## Verdict

The common (-q,q) hypothesis fails for K1 Forward's declared small-input domains.
Four of seven static KEM call sites pass; three require Barrett or a new proof
and redesign. Source identity is recorded in proof-results.json.

| Caller/value | Direct producer | Proven output / finding | Sign-add-only ToBytes |
|---|---|---|---|
| Keygen h → pk | D1 BaseMul(g,finv) | [-3023,3023] | pass |
| Keygen f → sk | K1 Forward(3*CBD+delta0) | concrete domain counterexample 3865 | reject common contract |
| Keygen hinv → sk | D1 BaseMul(f,ginv) | [-3023,3023] | pass |
| Encaps r → hash_g input | K1 Forward(CBD) | concrete domain counterexample -5595 | reject common contract |
| Encaps c → ct | D1 BaseMulAdd(h,r,m) | [-3023,3023] | pass |
| Decaps r2 → hash_g input | D1 BaseMul(c-m2,hinv) | [-3023,3023] | pass |
| Decaps r1 → verification bytes | K1 Forward(CBD) | same CBD domain counterexample | reject common contract |

The timed native candidate changes BaseInv and only Decaps' FIRST BaseMul and
Inverse (m1). Its SECOND BaseMul producing r2 still uses D1 R0, so this table
applies to both current production and the timed native candidate. Neither
BaseInv nor Inverse writes a buffer directly passed to ToBytes here.

## D1 proof, not a sampled maximum

Both D1 entrypoints end every output component with reduce_r0_s32:

    h = floor((621199*x + 2^30)/2^31)
    r = x - 3457*h
    out = narrow_int16(r)

Enumerating every possible h and the exact inclusive interval of x mapping to
that h covers all 2^32 signed32 inputs. r is linear within each interval, so
its extrema occur at the endpoints. The resulting exact union extrema are
[-3023,3023], strictly inside (-3457,3457). NEON MLS is modular32; even when
h*q alone overflows signed32, its low-bit subtraction decodes to the same
small r. XTN is exact for this residual. There is no C scalar signed-overflow
assumption in this argument.

Thus this output-range result does not depend on tightening upstream product
bounds, and even applies to malformed input bytes. It is NOT a replacement for
the earlier accumulator/algebraic-correctness proof: wrapping a wrong product
can still yield a small wrong residue. This audit only certifies the output
range needed by ToBytes. The old source comment [-2911,2911] is a narrower
historical accumulator-union result; we deliberately use the stronger-domain
[-3023,3023] theorem instead of transplanting that comment to new callers.

For every x in [-3456,3456], sign-add-only equals the existing five-instruction
normalization exactly; proof.py exhausts all 6913 such values.

## Forward counterexamples

forward_witness.c invokes the exact production K1 wrapper, top split, six-bank
helper and T1 layout assembly, with no scalar Forward substitution.

- CBD domain, xorshift32 seed 864, first trial: output[0]=-5595.
  Sign-add-only gives -2138, but canonical residue is 1319.
- f domain, seed 2326130036, first trial of that domain: output[0]=3865.
  Sign-add-only leaves 3865, canonical is 408.

Inputs are realizable at the CBD coefficient-domain boundary (-1,0,1), with
the f transformation 3*CBD+delta0. These are not full SHAKE/Keygen seed traces
or a proof of an accepted secret-key sample; no hash-preimage claim is made.
They falsify the declared producer-domain bound. A tighter reachable-hash-only
claim would need a separate proof; it is not a safe basis for deletion here.
The 128-trial extrema in forward-witness.jsonl are observations, not bounds.

## Safe next experiment

Use two caller-selected entries, without inspecting secret coefficient values:

- ToBytes small-R0: proven D1 producers; delete 108 SQRDMULH and 108 MLS per
  complete call, retain sign-add canonicalization and identical routing/packing.
- ToBytes lazy-R0: K1 Forward producers; retain existing normalization.

Potential static savings: Keygen 2 calls =432 vector instructions; Encaps
1 call =216; Decaps 1 call =216. No cycles predicted. Moving a reduction to
Forward solely to remove it in ToBytes is not an end-to-end saving.

For current production r9_to, the later stock packer also performs its own
sign-add normalization. A separate audited direct packer could avoid that
redundancy; this is not the same source as the new byte_pair_block candidate.

## Reproduce locally

Run `python3 proof.py` in this directory. Build forward_witness.c with clang
-O2 -arch arm64 and production gt864_forward_poly_ntt.S,
gt864_forward_six_bank.S, gt864_top_split.s, tail_variants.S, then execute it.
No Slothy, upload, benchmark, production mutation, or commit performed here.
