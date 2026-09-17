# P3-A: NTRU+1152 native-component consumer feasibility

## Outcome

The common `T_d = Q16 x I_d` abstraction is exact for `d=4`, but none of the
currently executable 16-bit direct-AoS BaseMul families is authorized for
assembly. This is a high-risk representation gate, not a performance result.

The important accounting correction is that the selected pipeline pays only
one standalone representation boundary:

```text
persistent-AoS Forward
  -> 16-route AoS-to-coefficient-plane network per (branch,p) tile
  -> coefficient-plane BaseMul / MA2
  -> inverse-native coefficient-plane input
```

There is no executed `P^-1` after BaseMul. A plane-to-AoS network can be built
in 12 routes, and the generator proves it exactly, but those 12 instructions
are not baseline debt and cannot be credited to P3.

Therefore the real available budget is:

```text
16 routes/tile x 18 tiles = 288 routes/forward
```

not `P + P^-1`.

## Exact `T4` ownership

For fixed `(branch,p)`, the native macro-tile is:

```text
V0 = q0..q3,   each q owns [j0 j1 j2 j3]
V1 = q4..q7,   each q owns [j0 j1 j2 j3]
V2 = q8..q11,  each q owns [j0 j1 j2 j3]
V3 = q12..q15, each q owns [j0 j1 j2 j3]
```

The generated ownership table covers all 1,152 `(branch,p,q,j)` cells. The
existing hierarchical network is also replayed as a lane oracle. Its
standalone part is four each of `vpunpckwd`, `vpunpckdq`, `vpunpckqdq`, and
`vpermq`: 16 routes per tile.

## Candidate arbitration

| family | routing / tile | Montgomery chains / tile | result |
|---|---:|---:|---|
| full transpose wrapper | 16 | 19 | reject: recreates `P` |
| four-q coefficient broadcast | 44 | 76 | reject |
| packed four-product rotation | at least 16 | at least 20 | stop before ASM |
| `vpmaddwd` / signed-32 arithmetic | not yet exact | not yet exact | separate research only |

The coefficient-broadcast schedule uses four q-local packets. Each packet
needs eight input broadcasts and at least three output-pack routes. More
importantly, it executes the 19-chain quartic schedule four times, inflating
the arithmetic to 76 vector Montgomery chains.

The more credible packed-four-product family uses the four coefficient lanes
for four different runtime products. Four product rotations per packet cover
the 16 base products with 16 vector chains over the whole tile, but:

- the three non-identity `B` rotations already cost 12 `vpshufb` per tile;
- q-local wrapped terms need at least four weighted-wrap chains rather than
  the coefficient-plane schedule's three;
- every four-q packet needs cross-lane output aggregation.

Even the deliberately optimistic lower bound is 16 routes and 20 chains. It
only ties the complete available routing credit while adding arithmetic,
before pricing the AoS inverse first stage. It therefore does not justify ASM.

## Inverse handoff

`T4` is a valid semantic inverse input: inverse q-butterflies act independently
for each terminal coefficient and can be scheduled over q-local 64-bit groups.
That proves layout feasibility, not performance credit. The current
coefficient-plane inverse already needs no standalone adapter, so a future
AoS inverse must be compared stage-for-stage against it.

## Decision and reopen condition

No namespaced ASM and no benchmark are authorized. P2 wavefront work remains
closed.

P3 may reopen only with an exact non-q-local bilinear schedule that:

1. includes input formation, output aggregation, and inverse first-stage work;
2. beats 16 routes per tile rather than a fictional `P + P^-1` budget;
3. adds no uncompensated multiplication/reduction chains; and
4. proves peak YMM, range, scale, and Montgomery-domain contracts.

Machine-readable evidence:

```text
generated/p3-native-component-consumer.json
```

