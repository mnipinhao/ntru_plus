# Results

Status: **the algebra proof passes; the zero-post-add candidate is rejected.**

## B3 scale connectivity

The frozen one-product oriented NTT9 contains 61 scale-labelled nodes and 42
add/sub operations.  Requiring every add/sub to be free means its output and
both inputs must carry the same scale.  Unioning those exact equalities leaves
one connected component across all 61 nodes and all nine outputs.

Therefore zero post-add scaling does not merely create six independent B3
islands: the level-1 and level-2 dataflow connects them into one complete NTT9
common-scale island.

Write a geometric basis as

`u = kappa * theta^(2*column + h*row)`.

Because `theta` has order 864, common scale across all rows requires
`h = 0 mod 864`.  Making `z/u^3` independent of row requires
`96-3h = 0 mod 864`, or `h in {32,320,608}`.  The two sets have empty
intersection.  Thus zero post-add rescaling and the two-constant `9/3` BaseMul
cannot coexist in this DAG.

## Exact hybrid basis

Dropping only the row factor gives

- alpha: `u=theta^(2*column)`, `z'=9*theta^(96*row)`;
- beta: `u=27*theta^(2*column)`, `z'=3*theta^(96*row)`.

All 288 leaves times nine degree-3 basis products pass the exact homomorphism
identity, for 2,592 checks.  The representation reduces 288 legacy weights to
18 weights: nine per top branch.

Under zero-post-add connectivity, all ten existing rho/eta products remain and
none of the nine input twists becomes identity.  The resulting Forward cost is
19 mulmods per NTT9 block, versus 18 for M5R-D.  That is eight extra mulmods per
Forward, or 48 extra Algorithm-10 instructions across the two Forwards in one
polynomial multiplication.

## BaseMul range gate

The direct-wide proof used by FR-ISO2 requires `|z'| <= 27` for component zero
and `|z'| <= 69` for component one under the accepted `B0=26306` and
`B12=5185` bounds.  The strict limit is therefore 27.

The proof exhaustively tries all 3,456 public multipliers `gamma`; changing
`u` by `gamma` rescales the nine row weights by the public cube
`gamma^-3`.  Even the best row cosets have:

| branch | best gamma | minimum possible max `|z'|` | worst c0 bound | result |
| --- | ---: | ---: | ---: | --- |
| alpha | 24 | 966 | 52,632,328,336 | int32 fail |
| beta | 84 | 766 | 41,878,638,336 | int32 fail |

Both are far above `2^31-1`.  Consequently this hybrid cannot delete either of
the two widening Montgomery reductions that supplied the measured 334.194-cycle
FR-ISO2 BaseMul benefit.

## Decision boundary

The candidate reduces the weight table from 288 to 18 classes, but adds Forward
arithmetic and preserves the expensive BaseMul reduction shape.  Constant-table
compression alone is not enough to claim a complete-operation win, especially
after CF5-C rejected load-only optimization as the primary Forward bottleneck.

No assembly, Slothy, Pi 5 timing, Inverse implementation, or Production change
is authorized.  This does not reject every B3–BaseMul co-design.  It rejects the
specific hard constraint `postadd=0` on the current NTT9 topology while retaining
the known direct-wide BaseMul bounds.
