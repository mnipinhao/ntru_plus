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

## First implementation after repository checkpoints

`tools/refine_encap_range.py` in the 768 tile4 experiment implements exact
frontend marginal sets and arbitrary-width integer-bitset sumsets through all
five NTT32 stages. Every butterfly checks that its two inputs have disjoint
original q-input support. Thus Cartesian products are justified, not an
assumption that two outputs of the same butterfly are independent. Correlations
between different k3 rows are deliberately not claimed away.

The domain is the independent ternary coefficient superset: every r/m caller
input is covered, but a marginal endpoint need not be reachable under all
additional distribution/encoding constraints of a real caller. No joint
reachability of all terminal coefficients is asserted.

| Stage | Old symmetric interval | Exact marginal maximum absolute value |
| --- | ---: | ---: |
| D16 | 9844 | 9844 |
| D8 | 11478 | 11466 |
| D4 | 12674 | 12668 |
| D2 | 14398 | 14397 |
| D1 | 15605 | 15592 |

The conservative asymmetric h×r / lambda / R² / +m composition is reused with
the refined lane bounds. Its post-add envelope improves from 17461 to 17448;
consumer bounds remain conservative, not exact product reachability.

This small improvement is evidence against expecting a large GLOBAL bound
reduction merely by replacing forward intervals with exact sets. It does not
close lane-specific reduction removal or a different arithmetic DAG.

`tests/test_range_word_semantics.c` checks the model's actual fixed constants
against AVX2 low/high-multiply/subtract on every signed-i16 input, with UBSan.
It separately checks v=9 serializer reduction/canonicalization over 65536
inputs and the extreme rounded-high-multiply operand pair. This is hardware
conformance of the arithmetic macros, not a proof of the complete linked NTT.

Run from the experiment directory:

```sh
python3 tools/check_range_word_semantics.py
```

Artifacts: `generated/tile4_encap_range_refined.json` and
`generated/tile4_encap_range_word_conformance.json`. They record source/model
hashes and the conformance compiler/flags/ELF hash. No clean source, arithmetic,
reduction placement or performance measurement is changed.

Validation completed: 323 constants × 65536 signed inputs = 21,168,128
Montgomery hardware/model cases; 65536 serializer inputs; UBSan passed.
The existing wavefront regression was also rebuilt and run without timing:
11543 Forward cases, 100 asymmetric B3 cases, alias/canary/immutability and
ASan/UBSan checks passed. Evidence is under
`results/encap-range-refinement-20260921-check/` in the experiment. This retains
the prior independent semantic-oracle checks; it does not elevate testing into
a whole-binary proof.

Still open: theorem-prover certification, automatic correspondence of every
linked NTT instruction to a ledger row, richer joint consumer reachability and
proof-driven reduction-removal experiments. Passing this model is not permission
to remove a reduction without analyzing that changed program.
