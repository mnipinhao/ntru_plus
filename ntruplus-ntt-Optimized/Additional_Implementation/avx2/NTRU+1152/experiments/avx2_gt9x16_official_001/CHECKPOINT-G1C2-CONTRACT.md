# Checkpoint G1C2 contract: BMScale live tail to inverse head

This checkpoint inspects the actual Official BMScale result lifetime before
authorizing linked assembly. It changes no arithmetic and reports no cycles.
The GT version must preserve Official's product/add/reduction schedule while
rekeying only the lane-wise `X^4-factor(branch,p,q)` constants for 18 GT row
blocks.

## Actual result cutpoints

Within each BMScale block, Official reaches these results at different times:

| Cutpoint | Live result registers | State still required by c3 |
| --- | --- | --- |
| early | `c0=ymm5`, `c1=ymm6`, `c2=ymm7` | `a0..a1=ymm1..2`, `b0..b1=ymm3..4` |
| late | `c3=ymm1` | c3 chain complete |

After the early stores, `ymm7` is immediately reloaded with `b2`; 26
instructions separate the c2 and c3 stores. Official BMScale touches all 16
YMM registers. Consequently c2 and c3 are not simultaneously live in the
faithful schedule.

## C2-P: materialized persistent pair

The explicit reversible AVX2 packing schedule costs six routing instructions
per terminal pair, not the earlier provisional four:

```text
2 x vperm2i128
2 x vpshufb
vpunpcklqdq + vpunpckhqdq
```

That is 12 instructions per row and 216 per transform. c0/c1 can be packed at
the early cutpoint. c2/c3 additionally require one temporary c2 store and load
per row unless arithmetic is rescheduled or a linked register allocation proves
that c2 can survive. C2-P remains a diagnostic; it is not authorized as a
zero-seam implementation.

## C2-L: direct live inverse consumption

C2-L consumes each BMScale result at the cutpoint where it is born. c0, c1,
and c2 are processed sequentially before their registers are reused; c3 is
processed after its final add chain. One canonical result vector is transformed
with:

```text
adjacent-word swap
sum and difference
Montgomery multiply by alternating [z^-1,-z^-1]
blend even sums with odd twisted differences
```

The odd multiplier is negative because the swapped odd lane holds `D-S`.
This is seven instructions per terminal coefficient, 28 per row, followed by
four post-distance1 stores. There are no BMScale-edge input loads and no
materialized BMScale→inverse seam. The estimated peak is 13 YMM registers,
but only the linked-object audit may certify that number.

Generated constants cover all 18 `(branch,row)` BMScale factor vectors and all
nine row-specific inverse distance-1 vectors. The contract test performs
1,440,432 lane checks.

## Decision

C2-L is selected for the next linked ASM prototype. C2-P is retained only as a
materialized diagnostic. Before timing, the linked function must pass BMScale
and inverse-distance1 differentials, both range cutpoints, and an audit proving
no call, frame, vector spill, or materialized edge load/store. Cycles remain
null.

