# D1 → stride-8 → asymmetric-r MA2 search

## Question

Can the scale-1 `r` forward leave D1 in the eight-vector stride-8 geometry
consumed by the selected serializer, while `m`, streamed `h`, and the MA2
constants retain the frozen wire-monotone coefficient-plane ABI?

This checkpoint freezes D1 arithmetic, scale, wire ownership, MA2 arithmetic,
and output bytes.  Only physical output orientation and `r` ingress are open.

## Concrete layout

For one coefficient plane in two adjacent 64-coefficient tiles, write the
current MA2 vectors as

```text
L = [l0,l1,...,l15]
H = [h0,h1,...,h15].
```

The serializer-native pair is

```text
E = [l0,l2,...,l14 | h0,h2,...,h14]
O = [l1,l3,...,l15 | h1,h3,...,h15].
```

Repeating this for the four terminal coefficient planes produces the eight
stride-8 vectors consumed directly by the Official-like 128-coefficient pack
network.

An exact asymmetric MA2 recovery exists for each plane:

```text
lo = vpunpcklwd(E,O)
hi = vpunpckhwd(E,O)
L  = vperm2i128(lo,hi,0x20)
H  = vperm2i128(lo,hi,0x31)
```

Thus one packet costs 16 routes to restore the two four-plane MA2 tiles; nine
packets cost 144 routes.  The symbolic replay is exact for all 1152 owners.

## Exhaustive D1 result

The search covers all 4096 three-level unpack networks, all 24 qword
permutations per output, output renaming, and every lane-wise D1 sign/output
swap.  It also permits the actual serializer order of one arbitrary
within-128 `vpshufb` followed by `vpermq`.

No one-shuffle-family witness exists for any of the 18 tiles.  This is a
scoped negative result: it does not prove that a larger two-route terminal
network cannot form the layout, but it proves that D1 sign/orientation freedom
alone does not absorb the serializer presentation.

## Caller-weighted movement ledger

Current selected path:

```text
D1 terminal orientation       48 routes
serializer input formation   216 routes
asymmetric r MA2 ingress        0 routes
                              ----------
                               264 routes
```

Stride-8 path, granting the impossible best case of a zero-cost compact D1:

```text
two-tile stride-8 formation    72 routes
serializer input formation      0 routes
asymmetric r MA2 ingress      144 routes
                              ----------
                               216 routes
```

Therefore the absolute optimistic ceiling is only `-48` routes.  The known
mechanical construction retains the current D1 orientation, performs eight
local routes per tile, then performs pair formation and MA2 recovery:

```text
compact D1 construction      192 routes
two-tile formation            72 routes
asymmetric r MA2 ingress     144 routes
                              ----------
                               408 routes  (+144 versus current)
```

The current D1 schedule reaches 16/16 YMM.  Unless a new pair-resident
schedule is proved, combining adjacent tiles also needs four reloads per
packet, or 36 extra vector loads per forward.

## Boundary result and decision

This ABI change deletes no complete state pass:

```text
forward state stores                         72 → 72
serializer + MA2 full-state consumer loads 144 → 144
```

It moves work from the serializer into the producer and then pays to undo the
layout at asymmetric MA2 ingress.  It does not satisfy the current objective
of deleting a representation boundary or complete data pass.

No ASM or benchmark is authorized for this form.  Reopen only as a joint
pair-resident D1/MA2 wavefront that proves executable liveness and actually
removes a state pass, or as a shared ABI in which all MA2 operands/constants
use the same lane geometry.  Do not implement an `r`-only stride-8 ABI from
this map.

Machine-readable evidence is in
`generated/d1-stride8-ma2-asymmetric-search.json` and is reproduced by
`tools/generate_d1_stride8_ma2_asymmetric_search.py`.
