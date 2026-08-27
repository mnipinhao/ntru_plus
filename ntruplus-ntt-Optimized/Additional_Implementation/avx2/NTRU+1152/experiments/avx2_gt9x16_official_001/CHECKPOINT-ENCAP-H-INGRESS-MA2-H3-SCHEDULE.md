# ENCAP-H-INGRESS-MA2-H3-SCHEDULE

This checkpoint closes the exact machine-schedule gate for H3.  It does not
implement assembly and does not authorize a benchmark.

## Contract

The planned leaf has the production-shaped contract:

```text
(pk bytes, r Natural-Q scale-4, m Natural-Q scale-4)
    -> c MA2 scale-4
```

Its accepted public-key set and error result remain identical to Official.
For every valid key, the output must be raw bit-exact with the implemented H1
decoder followed by preprojected-h MA2.  No equality is required for an
intermediate h array because H3 has no such array.

## Pairwise decoder wavefront

The packed decoder naturally exposes four source pairs:

```text
(d0,d4), (d1,d5), (d2,d6), (d3,d7)
```

Each pair supplies one terminal coefficient to both MA2 tiles owned by the
192-byte block.  The exact schedule therefore performs, for each pair:

```text
finish decoded pair
-> unsigned max/compare against q-1
-> vpmovmskb into edx; OR into public GPR accumulator eax
-> form tile-A h_j
-> form tile-B h_j
-> overwrite the now-dead decoded pair
```

The validation YMM is short-lived.  A mechanical backward-liveness pass over
the reordered decoder gives a peak of 12 YMM registers.  Pairwise validation
costs four max/compare/movemask/GPR-OR groups per block; this is six more
instructions than the H1 tree reduction, but it removes the long-lived vector
validation state and permits immediate ownership conversion.

The in-place allocation ends with:

```text
tile A h0..h3: ymm6, ymm11, ymm12, ymm13
tile B h0..h3: ymm7, ymm8,  ymm9,  ymm10
```

Both quartets are then converted by the same four-per-tile R2 Montgomery
operations as H1.  No h value is stored or reloaded.

## Exact 16-register MA2 allocation

Tile A is the zero-slack cut:

| State | Registers |
| --- | --- |
| tile-A h quartet | `ymm6,ymm11,ymm12,ymm13` |
| retained tile-B h quartet | `ymm7,ymm8,ymm9,ymm10` |
| tile-A r quartet | `ymm0..ymm3` |
| c / wrapped / product / Montgomery temporary | `ymm4,ymm5,ymm14,ymm15` |

This is exactly 16/16 with no spill or frame scratch.  After tile A finishes,
its h and r registers die; tile B consequently peaks at 12 registers.

The two tiles are one block wavefront at decode and formation time, but their
quartic arithmetic remains sequential.  Running both quartic accumulations
simultaneously would require extra output and wrapped-sum state.  Sequential
arithmetic preserves the frozen raw-representative DAG while still keeping the
shared decoded data entirely in registers.

## Arithmetic and movement ledgers

H3 retains the linked H1 MA2 ledger exactly:

```text
18 tiles
72  h R2 Montgomery chains
288 h*r Montgomery chains
54  lambda Montgomery chains
72  r loads
72  m loads
72  c stores
```

It also retains the 360 lane-alignment routes.  Those routes are now classified
as consumer-required work: they create the first arithmetic presentation of
each h coefficient.  The pure h-ABI formation count is zero.

Relative to H1, the structural delta is therefore:

```text
-72 h vector stores
-72 h vector reloads
  0 change in consumer-required routing
  0 pure h-ABI routes
  0 new temporary bytes
```

The range proof is unchanged because product order, wrapped accumulation, the
single lambda multiplication per wrapped sum, and output order remain the same.
This is also why the stronger raw-exact H1 output contract remains attainable.

## Terminal and future serializer contract

The ASM prototype must expose a terminal hook for every output:

```text
H3_EMIT_C(tile, coefficient, live-register)
-> aligned final store
```

The live register contains the raw H1-exact scale-4 MA2 value and has no
mandatory canonicalization or prior materialization.  Tile A cannot retain all
four outputs simultaneously because the second h quartet occupies four
registers, so the hook is coefficient-streaming rather than quartet-live.  This
still leaves a clean attachment point for a later H4 serializer or for storing
to the old h stack slot followed by one final 1728-byte copy.  H4 is not part of
this checkpoint.

## Decision

H3-full passes the schedule gates:

```text
peak YMM             16
h stores/reloads      0 / 0
pure h-ABI routes     0
spill/frame scratch   0 / 0
MA2 arithmetic        unchanged
raw H1 output         preserved by construction
```

The 128-byte H3-half and persistent H2 fallbacks remain documented but are not
selected.  The next authorized action is one namespaced H3 assembly prototype
with correctness and linked structural audit.  Performance pricing and native
KEM measurement remain unauthorized until that prototype closes.
