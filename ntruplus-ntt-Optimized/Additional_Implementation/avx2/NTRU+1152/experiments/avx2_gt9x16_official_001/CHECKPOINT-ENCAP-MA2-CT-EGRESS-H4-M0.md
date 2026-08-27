# ENCAP-MA2-CT-EGRESS-H4-M0

H4-M0 closes the scale-gauge search before terminal ownership and packing are
changed.  It is a generated algebra/range checkpoint only: no H4 assembly or
benchmark is authorized.

## Result

The scale-4 terminal `inv4` Montgomery chains are not mathematically
mandatory.  A scale-1 forward can be obtained by multiplying every
post-top-split `alpha_h` input gauge by `inv4`.  The 64 existing alpha chains
are rekeyed, while the two branches times four q-blocks whose `h=0` action was
a raw load acquire eight new vector Montgomery chains per forward.  The
beta-absorbed radix-2 constants do not change.

Scaling only the radix-2 twiddles was explicitly rejected: the untwiddled half
of each butterfly would not receive the common factor.  The generator proves
the valid construction over all 288 modular basis inputs and 41,472 output
cells, exhaustively verifies every new alpha Montgomery constant over all
65,536 signed-i16 inputs, and replays the complete closed interval proof.

The scale-1 forward envelope is `[-21469,21335]`, inside signed i16.

## Candidate gauges

| variant | r | m | h presentation | MA2 output | added producer chains / Encap | H4 terminal | r-hash terminal | predicted delta |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: |
| current | 4 | 4 | `hR` | 4 | 0 | 72 inv4 Mont | 72 inv4 Mont | 0 instructions |
| H4-local | 4 | 1 | `hR/4` | 1 | 8 | 72 Barrett | 72 inv4 Mont | -40 instructions |
| caller-wide | 1 | 1 | `hR` | 1 | 16 | 72 Barrett | 72 Barrett | **-80 instructions** |

The H4-local candidate rekeys the 72 existing H3 `h-R2` constants to produce
`hR/4` and makes only the `m` producer scale 1.  It is the minimum when H4 is
viewed in isolation.

The caller-wide candidate makes both `r` and `m` producers scale 1 and leaves
H3's `hR` conversion unchanged.  It is selected for H4-M1 because the same
`r` also feeds Direct H1 hashing: both the ciphertext and r-hash scale-4
finalizers can then be replaced.

## Important correction: reduction is still required

Scale absorption eliminates the `inv4` factor; it does not make the lazy raw
representatives canonical.  The proved pre-terminal envelopes are:

- H4-local: `[-30705,30571]`;
- caller-wide: `[-30697,30547]`.

One exact Barrett pass maps either envelope to `[-3107,3107]`, which is inside
`(-q,q)` and supports the existing sign-add-q canonicalization.  Therefore the
real structural replacement per 72-vector terminal is:

```text
72 x four-instruction inv4 Montgomery
    ->
72 x three-instruction Barrett
```

For caller-wide scale 1, the two producers add 16 four-instruction Montgomery
chains per Encap.  Across the ciphertext and r-hash terminals, the pre-ASM
budget is consequently:

```text
current:    2 x 72 x 4                         = 576 instructions
candidate: 16 x 4 + 2 x 72 x 3                = 496 instructions
delta:                                            -80 instructions
```

Routing and ordinary data loads/stores do not change.  The producer gauge adds
32 constant memory operands per Encap and needs at least one shared 64-byte
zeta/qinv constant pair.  Linked assembly remains the eventual source of truth
for this instruction and constant taxonomy.

## Range and contract gates

- MA2 quartic formulas, lambda placement, Natural-Q ownership, and terminal
  coefficient owners are unchanged.
- The scale-1 producer basis proof and all new Montgomery constants pass.
- All forward and MA2 preoperations fit signed i16.
- One terminal Barrett pass is sufficient; a zero-reduction terminal is
  rejected.
- No routing, temporary vector, spill, or new materialized array is introduced
  by the map.

The reproducible evidence is
`generated/encap-h4-scale-absorption-audit.json`.

## Decision

H4-M0 is complete.  H4-M1 may search terminal ownership and orientation under
the caller-wide scale-1 gauge.  H4 ASM, performance pricing, native KEM, and
promotion remain unauthorized.
