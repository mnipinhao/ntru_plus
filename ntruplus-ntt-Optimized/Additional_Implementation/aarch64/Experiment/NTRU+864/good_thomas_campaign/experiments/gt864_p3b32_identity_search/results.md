# P3B32 — NTT16 identity-reduction elimination search

## Decision

PASS for a bounded mathematical candidate, not assembly promotion. Under the
P3B28 small-input contract `[-3,4]`, jointly bypassing 12 all-one vector
multiplications per bank closes the Forward → M5C/D1 → M5E range chain.
Assembly, production, memory layout, scheduling and benchmark results are unchanged.

## Exact candidate

Indices below refer to the scalar DIT model after the input bit-reversal placement;
they are not physical register numbers. `node` is the start index of a butterfly
group, and only its `j=0` multiplication is bypassed.

| Region | Deleted multiplication groups per bank |
|---|---:|
| Main stage 0, length 2: nodes 0,2,4,6,8,10,12,14 | 8 |
| Main stage 1, length 4: nodes 8,12 | 2 |
| Main stage 2, length 8: node 8 | 1 |
| Tail stage 0, length 2: eight scalar butterflies packed together | 1 |
| Total | 12 |

Each main group operates on eight independent `s=0..7` lanes. The tail group
operates on eight pairs in the `s=8` transform. Apply the same policy to both
tops and all three components: six banks, hence 72 vector mulmods per Forward.
The arithmetic opportunity is 216 `mul/sqrdmulh/mls` instructions. This is not
yet a net linked-object instruction saving: lowering may need copies, and
constant loads shared with retained products cannot automatically be removed.

Keep the input `t=0` twist reduction, main length-4 nodes 0/4, length-8 node 0,
and length-16 node 0. Mixed-identity vectors are outside this experiment.

## Proof and bounds

The script asserts the eliminated constants are exactly `(b,bhat)=(1,9)`.
Bypassing them preserves residues modulo 3457, R0 scale, logical roots and
physical coordinate ordering, but not necessarily signed representatives.
Every retained fixed multiplication exhausts its integer interval; additions
and subtractions propagate independent enclosing intervals. Main and tail
are modeled separately so a main-only deletion cannot silently affect the tail.
All Forward arithmetic nodes are checked against signed int16 limits.

| Bound | No deletion, small-input model | Joint candidate |
|---|---:|---:|
| NTT16 output absolute bound | 9299 | 9667 |
| Maximum Forward intermediate absolute bound | 25536 | 25536 |
| M5C maximum absolute int32 accumulator | 1956261888 | 1956261888 |
| M5C output / add-output absolute bound | 2147 / 2204 | 2147 / 2204 |
| D1 output absolute bound | 2911 | 2911 |
| M5E maximum halfword absolute bound | 17220 | 17220 |

The 9299 baseline is a fresh tighter calculation from the two raw-top intervals
`[-2891,2170]` and `[-2172,2896]`; it does not replace the older general-input
9342 theorem. Candidate D1 accumulator domain is
`[-1955061696,1956287408]`, contained in P3B28's
`[-1961116731,1961346849]`. This run rechecks that latter domain's exact
quotient-transition residual bound and int32 quotient-product safety.
M5E reuses the P3B28-established universal fixed-product bound 3444 and
recomputes the downstream interval chain; it does not rerun the inverse-table
exhaustion. Producer and inverse-table premises remain those of P3B28.

## Search limitations

Search consists of 17 single-group tests, two opposite-order greedy joint
searches, and the all-deleted candidate. It is not an exhaustive subset search
or a minimum-reduction proof. Twelve groups pass jointly, not just individually.
Five singles remain unproved by this conservative chain. In particular,
length-4 node 4 exceeds the reused D1 theorem domain; that is not an overflow
counterexample. Removing all 17 fails the interval gate at NTT9 level-1 A sum
with `[-34421,33650]`; correlation could make this enclosure loose.

## Reproduce and next gate

Run `python3 prove.py` in this directory. `build/proof.json` contains per-candidate
outcomes, all 288 leaf bounds, the exact D1 theorem and source SHA-256 identities.

Next: lower only the 12 accepted groups into a default-off P3B29-derived
assembly candidate. Audit operand aliases and actual instruction deltas,
verify modular Forward/serialized equality and complete polynomial
multiplication, then compare same-boundary complete Forward on Pi 5.
Do not compare raw signed Forward buffers byte-for-byte: representatives may
legitimately differ. Slothy comes after this new DAG's correctness/object gate.
