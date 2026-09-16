# P3B40 — KEM caller-specific range closure

## Outcome

**Range-model gate passes for either additional stage1/node0 deletion OR
additional stage2/node0 deletion on top of P3B37, across all current KEM
call-sites. They do not both pass as one common Forward implementation.**

No assembly, production selector, remote upload, Slothy or timing change.
This establishes eligibility for a separately named KEM-only experiment,
not correctness of an unimplemented assembly candidate. Generic 2F multiplication
must retain its previous contract; P3B39 counterexamples remain valid.

Scope: explore/review. q=3457, NTRU+864, existing FR0 leaf representation,
R0 Forward/D1/Inverse, signed int16 storage and signed int32 accumulators.
Arithmetic and routing semantics are inherited from the frozen P3B37 source;
only prospective reduction masks are modeled. Secret ranges are bounded,
not inferred from random observations or successful KEM samples.

## Producer closure

| Producer | Used input domain | Evidence |
|---|---|---|
| Keygen f | independent [-3,4] superset | actual 3*CBD1, only coefficient zero +1 |
| Keygen g | {-3,0,3} | 3*CBD1 |
| Encaps r / Decaps r1 | {-1,0,1} | CBD1 |
| Encaps m | {-1,0,1} | SOTP encoder has same two-bit difference extraction after XOR |
| Decaps m2 input | {-1,0,1} | inverse centered normalization then crepmod3 |
| decoded h,c,f,hinv | [0,4095] | actual cluster-transpose FromBytes masks 4095 |

CBD1/SOTP byte-pair arithmetic is exhaustively enumerated over 256² byte
pairs and both bit interleavings. XOR does not change the possible byte
domain. The code's +0x55 prevents cross-two-bit borrows; extracted pairs
minus one are exactly {-1,0,1}. Routing only rearranges those values.

Centered normalization and crepmod3 are checked for all signed-halfword
inputs to normalization. The centered result is in [-1728,1728]; modeled
SQDMULH, SRSHR and MLS return {-1,0,1}, congruent modulo 3.
FromBytes includes malformed/noncanonical byte strings, not just values
below q. Active byte_api.c routes to cluster_transpose_frombytes.c; the
older input_once implementation is not mistaken for the current entrypoint.

## BaseInv output bound

The existing adapter centers Forward output before official BaseInv.
BaseInv_1's stored numerator/denominator vectors are conservatively treated
as arbitrary signed int16. Starting from that domain, the proof follows:

1. 36-entry Montgomery prefix product;
2. the exact fqinv addition chain;
3. the final fixed multiplication (-1571,-14891);
4. backward batch inversion;
5. final numerator × inverted denominator Montgomery multiplication.

Every widening product and internal q*quotient addition is checked as
signed int32. Final output enclosure is **[-3457,3457]**. The failure
branch zeroes the output and satisfies the same enclosure.

This is a new range enclosure, not a new proof of BaseInv algebra or
BaseInv_1 internals. Those kernels are unchanged and receive the same
centered representation as before. The wrapper's official-to-FR0 step
only permutes values. Deterministic scalar batch tests complement, but
do not replace, the interval proof.

## Forward proof

Exact sparse top sets and NTT16 marginal sets are propagated, with disjoint
input-support assertions at each butterfly. Each NTT9 input twist is evaluated
over its actual marginal set, not every integer in the convex hull.
One-product oriented NTT9 then uses the existing affine-with-reset analysis.
Every sum, difference and fixed-product input/output must fit int16.

For f, the independent [-3,4] domain is a sound superset, not a claim that
all coefficients can receive the coefficient-zero offset. Failure of this
overapproximation is marked not_proven, not automatically a KEM counterexample.

| Extra bypass on P3B37 | f max abs intermediate | g max | small-input max | All KEM callers |
|---|---:|---:|---:|---|
| none | 26731 | 25487 | 22892 | pass |
| stage1/node0 | 28765 | 26930 | 24799 | pass |
| stage2/node0 | 32681 | 31358 | 25256 | pass |
| stage1 + stage2 | not proven | not proven | 27172 | Keygen not closed |
| stage3/node0 | not proven | not proven | 31996 | Keygen and Decap not closed |
| stage1 + stage3 | not proven | not proven | not proven | no |
| stage2 + stage3 | not proven | not proven | not proven | no |
| all three | not proven | not proven | not proven | no |

Full leaf intervals and first failing intermediate are stored in proof.json.
These are bounds, not runtime observed maxima.

## M5C / D1 by caller

Both early Montgomery reductions are retained. Their internal widening
additions are checked, as are the three final accumulators and the
BaseMulAdd addend. The actual 288 zeta table entries are checked to lie
within [-1728,1728]. All calculations use asymmetric operands:

| Caller | Operand pairing | Stage1-deletion D1 input enclosure |
|---|---|---|
| Keygen h | F(g) × BaseInv(f) | [-279291030,279291030] |
| Keygen hinv | F(f) × BaseInv(g) | [-298321815,298321815] |
| Encaps c | decoded h × F(r) + F(m) | [-304680514,304619084] |
| Decaps m1 | decoded c × decoded f | [-3872448,50307075] |
| Decaps r2 | (decoded c − F(m2)) × decoded hinv | [-304594290,354962790] |

Each of the 288 leaves is checked separately. No assumption that both
operands share the Forward magnitude is made. No output normalization is
inserted to make these bounds pass.

D1's existing full-signed-int32 Barrett theorem is rerun:
**output [-3023,3023], R0**. It includes legitimate low-half wrapping in the
MLS reduction implementation; it does not excuse accumulator overflow
before that reduction.

## Decap subtraction and M5E

For each leaf, subtraction is separately bounded as:

    [0,4095] - [F_low,F_high] = [-F_high,4095-F_low]

The instruction is plain signed-halfword SUB, so every interval must fit
int16 before BaseMul. Stage1 and stage2 candidates pass. The stage3 candidate
fails this gate with an enclosure [-30943,35070]; it is not rescued by the
fact that its small-input Forward alone passes.

Both Decap BaseMul outputs enter the unchanged M5E inverse at [-3023,3023].
The existing inverse bound is rerun:

| Inverse stage | Max absolute bound |
|---|---:|
| first B3 sum | 9069 |
| first B3 weighted output | 9911 |
| second B3 lazy output | 16799 |
| NTT16 maximum | 17220 |
| final top recombination | 6888 |
| centered API output | 1728 |
| following crepmod3 | 1 |

The fixed-constant inverse theorem (universal output bound 3444) and existing
inverse algebra/layout proofs are reused. This is a caller-range composition,
not a new independent verification of every existing inverse instruction.
Keygen/Encaps output serialization uses the existing full-int16 normalization
contract instead of requiring an inverse stage.

## Recommended next gate

Implement **stage1/node0 bypass as an isolated KEM-only candidate** first.
It has 4002 units of positive int16 magnitude headroom under the common
Forward bound, versus only 86 for stage2. This is a proof-margin reason,
not a prediction that stage1 will have better cycles.

Retain P3B37 for generic 2F polynomial multiplication. Do not weaken its
test silently or claim these caller-specific results cover arbitrary
Forward-output × Forward-output operands.

A later public caller-specific split could investigate stage1+stage2 for
small producers only, while Keygen retains a single deletion. It requires
explicit source selection and correctness/benchmark evidence and is not
implemented here.

Before promotion: exact lowering/range linkage, assembly correctness,
full KEM valid/malformed-input checks, byte equivalence and paired Pi timing.
This report contains no cycle claim.

## Reproduction and evidence

    python3 prove.py
    python3 test_proof.py

- prove.py: producer enumeration, BaseInv interval chain, 8 prospective
  Forward masks, per-leaf caller accumulators, D1 and M5E composition.
- test_proof.py: scalar batch inversion bound tests, generic-overflow negative
  control, asymmetric corner tests.
- build/proof.json: all 288 leaf bounds per passing Forward, call-site ranges,
  subtraction ranges, failure reasons, D1 theorem, M5E bounds and source hashes.

All generated evidence is gitignored. No production source was modified.
