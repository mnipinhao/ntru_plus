# GT9X16-PROD3-MAP: formation and axis-order search

## Decision

This checkpoint keeps Official NTRU+1152 AVX2 only as the production
performance control. It does not import Official arithmetic into the GT
producer. The current P1-H/P2-B result closes one physical realization, not
the semantic `2 x 9 x 16 x 4` decomposition.

The selected next design checkpoint is:

```text
GT9X16-PROD3-AOS-SCHED
```

It must price a producer that retains the top-split-native four-coefficient
AoS q-cell through radix-3 and radix-2 arithmetic, then forms the already
qualified scale-4 MA2 coefficient planes at the final boundary. No assembly or
benchmark is authorized by this map.

## Frozen contract

The following do not change:

- top-split arithmetic and its 2,304-byte materialized output;
- semantic owner `(branch,p,q,terminal_coefficient)`;
- paper P order `0,3,6,1,4,7,8,2,5`;
- bit-reversed physical Q order `0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15`;
- transform scale 4 and Montgomery exponent 0;
- P2-B's exact MA2 coefficient-plane destination ABI;
- MA2, `inv4`, serializer, and caller arithmetic.

The generated oracle maps all 1,152 persistent-AoS output cells to the exact
P2-B MA2 destination, factor, Official component identity, and scale. Source,
destination, and semantic-owner sets are independently bijective.

## Why current formation is the target

P1-H reads each four-vector top-split row twice: once for terminal pair 0/1 and
again for pair 2/3. Its 36 maps therefore execute per forward:

| class | count |
| --- | ---: |
| aligned top-split loads | 144 |
| early AoS-to-SoA routing | 576 |
| pre-twist Montgomery chains | 72 |
| P2-B final plane permutations | 72 |
| MA2-plane stores | 72 |

The routing headline is 648 instructions when the 576 formation routes and 72
P2-B epilogue permutations are counted together.

The terminal coefficient is a passive transform dimension: twist, radix-3,
and radix-2 constants never depend on it. It is therefore algebraically legal
to keep the four coefficients of each q cell interleaved while both GT axes
execute. This is a representation change, not a new transform.

## G1: persistent AoS

A conservative realization can load the four AoS vectors of each branch/row
once and retain all four terminal coefficients:

```text
materialized top split AoS
-> AoS pre-twist
-> paper-R2 with j interleaved
-> adjusted NTT16 with j interleaved
-> late 16x4 AoS-to-MA2 plane formation
```

Before rescheduling the arithmetic, the mechanically known bounds are:

| class | G0 current | G1 conservative upper bound | delta |
| --- | ---: | ---: | ---: |
| aligned top-split loads | 144 | 72 | -72 |
| early formation routing | 576 | 0 | -576 |
| late plane routing | 72 | <=576 | <=+504 |
| total known routing | 648 | <=576 | <=-72 |
| pre-twist chains | 72 | 72 | 0 |
| plane stores | 72 | 72 | 0 |

The `<=576` tail bound reuses the already proved 16-instruction terminal-pair
transpose twice per tile. It is deliberately not called an optimized count.
The next schedule must determine whether adjusted D2/D1 and the final 16x4
transpose share routing. Until that synthesis exists, the table is only a
feasible upper bound, not a cycle prediction.

## G3: affine GT coordinate relabels

The map enumerates all 6,912 independent affine rekeys

```text
p' = u*p+s mod 9,  gcd(u,9)=1
q' = v*q+t mod 16, gcd(v,16)=1.
```

They are valid component/constant rekeys, but all remain in one source
movement class: the top split still stores four terminal coefficients in each
64-bit q cell. An axis relabel alone therefore cannot remove the AoS-to-plane
boundary. No relabel is selected merely because its indices look simpler.

## G2: naive 16-first

The exact existing identity is

```text
Y_a[v] = R_(a+v mod 9)[v].
```

For every `a`, the sixteen q inputs visit all nine materialized h rows. None of
the four-q blocks comes from one contiguous row. Consequently a naive
16-first realization loses the current four-aligned-load geometry before doing
arithmetic. G2 is deferred unless the shear can be absorbed into top-split
stores or fused with the first arithmetic stage. This is not a rejection of
16-first under a co-designed producer.

## G4: twist and scale placement

The branch pre-twist is mechanically separable over all 288 components:

```text
g^(offset*(16h+q)) = g^(16*offset*h) * g^(offset*q).
```

This makes twist absorption a legal schedule variable, but the map does not
prove fewer than 72 Montgomery chains. A later realization must preserve the
exact factor identity, scale 4, signed-i16 range, and MA2 lambda constants.

## Next gate

`GT9X16-PROD3-AOS-SCHED` must provide:

1. an exact AoS radix-3 and adjusted radix-2 lane schedule;
2. a fused D2/D1-to-MA2 transpose synthesis and exact opcode ledger;
3. actual-register range and scale proofs;
4. a spill-free peak-YMM and overwrite schedule;
5. a bit-exact 1,152-cell oracle against P2-B.

Only after that review may an ASM checkpoint be authorized. Repository timing,
SUPERCOP-derived timing, and native KEM are all out of scope here.

Machine-readable evidence is in
`generated/gt9x16-prod3-map.json`; its regeneration test is
`tests/test_gt9x16_prod3_map.py`.
