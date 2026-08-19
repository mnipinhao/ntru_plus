# GT32 producer-native merge-basis gate 026

> **Superseded semantic accounting:** executable gate 027 found that Gate B
> propagated the absolute merge weight, not the exact candidate/current
> representative ratio.  Consequently the claimed `45 chains + 48 blends`
> graph is not mathematically equivalent to the control.  Gate A remains
> valid; Gate B's chain, range, and terminal-permutation conclusions must not
> be used as correctness or performance evidence.  See
> `../gt32_unweighted_merge_asm_027/`.

This gate jointly examines producer scaling, QBM output basis, and the
conjugated inverse.  GT Clean and production symbols are unchanged.

## Gate A: independent producer transforms cannot delete merge mixing

One component-wise product of independently transformed producer coordinates
is an outer-product bilinear form and has matrix rank at most one.  Both
desired merge outputs have rank two:

```text
p + m:       [[1, 0], [0, 1]]       determinant 1
w(p - m):    [[w, 0], [0, -w]]      determinant -w^2 != 0
```

Therefore two diagonal component products cannot directly become the two
merged outputs without output mixing.  Arbitrary independent producer linear
bases do not make both merge add/sub operations disappear; non-diagonal bases
introduce the cross terms that the target omits.

## Gate B: unweighted merge basis

The useful remaining candidate is

```text
u = p + m
d = alpha * (p - m), alpha in {+1,-1} lane-wise
```

The sign is free: the existing plus/minus shuffle masks can exchange sources
for selected lanes before `vpsubw`.  The merge Montgomery multiplication is
removed, and the residual diagonal scale is conjugated through the complete
inverse.

### Montgomery-chain propagation

Removing 48 merge chains initially looks attractive.  Exact conjugation shows
that the residual scale makes previously identity inverse butterflies
non-identity:

| Inverse stage | Current chains | Candidate chains | New identity chains |
|---|---:|---:|---:|
| size 2 | 0 | 24 | 24 |
| length 4 | 12 | 24 | 12 |
| length 8 | 18 | 24 | 6 |
| length 16 | 21 | 24 | 3 |

Existing non-identity chains only relabel their constants and none disappear.
Thus 45 of the 48 removed merge chains reappear in the inverse.  The actual
arithmetic credit is only three Montgomery chains, or 12 instructions.

The unweighted `p +/- m` interval is `[-4185,4185]`.  Exhausting each modified
Montgomery constant over the complete stage interval gives the conservative
trace `5934 ->center_twice 1728 -> 3467 ->center_once 1790 -> 3545`; the DFT3
raw bound is 10,635.  Everything remains signed-int16 safe.  The first new
high-arm chain occurs before the already-existing `center_twice`, so no new
full checkpoint is required.  Range is therefore not the blocker.

### DFT3 terminal obstruction

Lane-wise free signs can normalize every residual k3 scale into a DFT3
character.  Algebraically this is an output permutation, not an additional
multiplication.  Physically, however, the permutation is heterogeneous inside
each YMM:

```text
8 sum lanes:         output order (0,1,2)
8 difference lanes:  output order (2,0,1)
```

Postweight constant relabeling cannot move values between the three YMM
outputs.  The current branch-merge/coefficient stores contain both lane
classes in each 64-bit group, so whole-register destination relabeling also
cannot absorb it.  Reconstructing the three expected vectors needs at least
one lane blend per output for each of 16 positions: 48 blends.

```text
Montgomery credit:  -12 instructions
DFT3 route floor:   +48 instructions
-------------------------------------
static lower bound: +36 instructions
```

This is before any larger constant-table/load cost.  No assembly is emitted.

## Gate C: producer provenance

Gate C is intentionally not run.  Gate B did not produce a negative-cost
consumer basis, so moving weights into Forward, Decode/Q24, or BaseInv would
only relocate work rather than delete an operation class.

## Decision

The unweighted merge basis is stopped under the current inverse coefficient-
output contract.  Together with 024 and 025, this closes the current QBM-to-
`merge2` architecture sufficiently for AVX2.

Reopen if a downstream consumer natively accepts the mixed lane-wise k3
order, or if a prepared/wider-ISA representation changes the final output
contract.  Do not reopen merely to move producer preweights.

## Reproduction

```sh
make check
```
