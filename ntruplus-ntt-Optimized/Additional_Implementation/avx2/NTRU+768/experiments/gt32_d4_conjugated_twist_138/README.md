# GT32 D4 conjugated twist/transpose gate (138)

This is the generator-only follow-up selected by Experiment 137.  It does not
modify GT Clean and emits no assembly.

## Question

Experiment 076 showed that every production quartic leaf can be normalized
from

```text
Fq[x] / (x^4 - lambda[tile,Q])
```

to one fixed algebra

```text
Fq[y] / (y^4 - 2)
```

with

```text
lambda[tile,Q] = 2*s[tile,Q]^4
D(s) = diag(1,s,s^2,s^3).
```

The explicit `D(s)` bridge lost because it added 120 Montgomery chains.  Gate
138 asks the narrower NTRU-Prime-inspired question: can the diagonal replace
constants on Montgomery nodes that already exist in the complete Forward and
terminal path?

## Exact conjugation

The production NTT32 Forward is:

```text
S1       raw CT
S2--S5  CT with one Montgomery multiplication on the high arm
```

For one current butterfly

```text
CT(w)(u,v) = (u+w*v, u-w*v),
```

an arbitrary output diagonal has the exact identity

```text
diag(c,d) * CT(w) = GS(d/c) * diag(c,c*w),
```

where

```text
GS(k)(u,v) = (u+v, k*(u-v)).
```

The generator pulls every production `D(s)` backward through all five NTT32
stages, synthesizes the replacement factors, folds the resulting input
diagonal into the already-existing lane-dependent frontend twist tables, and
checks every 32-dimensional basis vector for all six tiles and all four
quartic degrees.

Result:

```text
6 tiles * 4 degrees * 32 basis vectors = 768 exact checks: PASS
```

Thus the mathematical conjugation is real.  The rejection below is an
execution-shape result, not an algebra failure.

## Why the executable topology loses

TILE4 stores all four quartic degrees in one qword.  One vector butterfly
therefore cannot use CT for `c=0` and GS for `c=1..3` without adding lane
selection/blend work.  The topology must be common across the four degrees.

At S5, adjacent leaves have different `s` values, so `c=1` forces GS.  Pulling
that exact GS gauge backward makes the next stage unequal even in the `c=0`
lane; this repeats through S4, S3, S2 and S1.  The exact common topology is
therefore:

```text
S1--S5: GS at every butterfly
```

This result does not depend on choosing the minimum-centered fourth root.
Each tile's 32 lambda values are distinct, so S5 is forced for every valid
fourth-root choice.  After S5, the degree-zero gauges are root-independent and
by themselves force GS through S4--S1.

Current S1 is raw and free of Montgomery multiplication.  Conjugated S1 needs
one lane-dependent multiplication on every difference arm:

```text
4 full-width chains/tile * 6 tiles = +24 chains/Forward.
```

S2--S5 retain the same number of multiply chains as current.  No standalone
transpose or new physical layout is needed; the blocker is the new S1
arithmetic layer.

The conservative interval trace is also unfavorable:

| stage | maximum absolute bound | int16 safe |
|---:|---:|:---:|
| S1 | 3,456 | yes |
| S2 | 6,912 | yes |
| S3 | 13,824 | yes |
| S4 | 27,648 | yes |
| S5 pre-add/output low arm | 55,296 | **no** |

The GS low arm is not reduced.  A real AVX2 lowering would therefore require
an additional centering/checkpoint mechanism before S5 unless a tighter exact
range proof replaces this conservative bound.  No such cost is credited in
the already-losing accounting below.

## Terminal side

The inverse diagonal on the normalized B3 product does have a free placement:
replace the existing per-coefficient B3 R2-finalizer constants by
`R2*s^-c`.  This keeps the number of finalizer chains and dynamic constant-load
instructions unchanged.  Q24 arithmetic and routing then remain unchanged.

This is useful negative attribution: the failure is not caused by Q24.

## Complete operation-class accounting

The unit below is one full-width vector Montgomery chain.

### Generic two-Forward multiplication path

```text
two conjugated Forward paths   +48
normalized D4 B3 credit        -36
B3-finalizer inverse diagonal    0
-----------------------------------
net                             +12 chains
```

Even before range repair and scheduling, this does not delete an operation
class.

### Actual Encap provenance

Encap does not obtain both B3 operands from Forward.  `r` is Forward-produced,
but `h` comes from the wire decoder:

```text
r Forward conjugation          +24
h decoder D(s) bridge           +36
normalized D4 B3 credit         -36
B3-finalizer inverse diagonal     0
-----------------------------------
net                              +24 chains
```

The decoder has no existing arbitrary-constant Montgomery node that can be
relabelled.  This is why a generic `2F+B3` argument would overstate the value
for Encap.

## Decision

```yaml
generator: PASS
mathematical_conjugation: PASS
current_range_proof: FAIL_AT_S5
operation_class_deletion: NONE
assembly: NOT_AUTHORIZED
benchmark: NOT_RUN
decision: CLOSED_FOR_CURRENT_EXECUTION_CLASS
```

Closed scope:

```text
current TILE4 qword packing
+ one-multiply radix-2 CT/GS NTT32
+ normalized D4 B3
+ current Q24
```

This does **not** close normalized D4 or all twist/transpose co-designs.
Reopen only with a new premise that changes the accounting:

1. a frontend/NTT factorization that absorbs `D(s)` without adding the 24 S1
   chains per Forward;
2. a decoder that emits normalized `h` by replacing an existing
   multiplication/reduction class rather than adding one; or
3. an asymmetric raw-`h`/normalized-`r` B3 tensor that retains the normalized
   B3 saving.

## Reproduce

```sh
python3 experiments/gt32_d4_conjugated_twist_138/tools/generate_gate.py
```

The complete per-tile roots, synthesized input gauges, stage topology counts,
bounds and operation accounting are in
[`generated/d4_conjugated_twist_gate.json`](generated/d4_conjugated_twist_gate.json).
