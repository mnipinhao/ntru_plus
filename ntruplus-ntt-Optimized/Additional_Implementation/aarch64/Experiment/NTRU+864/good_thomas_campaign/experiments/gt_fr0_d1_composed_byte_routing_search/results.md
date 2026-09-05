# D1-P3B2 results

Status: **PASS — exact direct byte-layout networks exist, but route9 is no
longer the composed Q-vector unit.**

The exact maps have hashes:

- FR0→post-shuffle: `087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270`
- pre-shuffle→FR0: `cf61c0ed6992cb4d4be3cf21f2a02992b40e190e8c2d293ac1c50790e13ee2d9`

They are bijective exact inverses and pass all 864 tags plus 128 random
roundtrips. Pointwise nonnegative normalization commutes with the forward
permutation, so P3B3 may schedule it before, during or after routing.

## New machine shape

At Q-vector granularity, each direction is two top-local connected graphs:

```text
2 × (54 input Q, 54 output Q, degree 8, 432 edges)
```

Every output Q receives exactly one halfword from eight distinct input Qs.
Therefore the old twelve 9×9 route9 components do not survive after composing
the packing shuffle. Holding all outputs simultaneously requires 54 vectors,
but connectivity does not prove that every load-once schedule needs that many.
The previous claimed lower bound is withdrawn; optimal frontier/register
feasibility remains unresolved. A factorized route9 implementation is not
ruled out by this graph.

Each 48-coefficient packing block contains sixteen `(component0,component1,
component2)` triples from sixteen FR0 tiles. The target triple is contiguous,
but its FR0 source addresses are separated by 8 coefficients (16 bytes), so
one `LD3 lane` cannot load it without changing the FR0 ABI.

## Static machine Pareto set

The counts below exclude address-generation and loop control and therefore are
P3B3 screening ledgers, not cycle predictions.

| Candidate | core instructions | coefficient reads | final stores | TBL | dependent depth | full intermediate |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| M0 R9-A + stock shuffle, forward | 1956 | 216 Q loads | 216 Q | 204 | 1 TBL | yes |
| M0 reverse | 1800 | 216 Q loads | 216 Q | 108 | 1 TBL | yes |
| C1 direct lane-load | **972** | 864 H lane loads / 1728 bytes | 108 Q | 0 | 8 lane loads/output | no |
| C2 direct two-TBL4 | 1512 | 864 Q loads / 13824 bytes | 108 Q | 216 | 1 TBL + ORR | no |

C1 minimizes static work, bytes read, register footprint and eliminates TBL,
but each output carries an eight-lane-load dependency chain. C2 deliberately
over-reads vectors but exposes 108 short and independent lookup/merge chains.
Neither dominates the other for Cortex-A76 execution shape, so both proceed.
