# GT9X16-PROD3-NATURAL-Q-T0-ABSORPTION-MAP

## Frozen boundary

This checkpoint keeps the selected PROD3 Encap architecture unchanged:

- C1-natural-Q remains the permanent internal Q-order;
- top-split, paper-R2, and radix-2 butterfly arithmetic are frozen;
- the transform output remains scale 4 and Montgomery exponent 0;
- no route, reduction, ASM, benchmark, or native KEM work is added.

The only question is whether the 72 standalone T0 Montgomery chains per
forward can be represented by frequency reindexing or absorbed into chains
that already exist in NTT9 and NTT16.

## Exact gauge factorization

For branch offset `o` and component `(h,q)`, the T0 factor is

```text
g^(o(16h+q)) = alpha_h beta_q
alpha_h = g^(16oh)
beta_q  = g^(oq)
```

The generator checks this identity for all 288 branch/row/Q cells. Pure
frequency reindexing is impossible on both the 9-axis and 16-axis for both
branch offsets, so neither factor can be removed merely by renaming outputs.

`beta_q` is nevertheless a common gauge across the nine rows consumed by
NTT9. It passes through the unchanged paper-R2 transform and can be absorbed
into each already-existing radix-2 twiddle:

```text
w(d) -> w(d) * beta_(q+d) / beta_q
      = w(d) * g^(o d)
```

This changes only branch-specific constant values. It adds no Montgomery
chain, routing instruction, reduction, or terminal repair; `beta_0 = 1`.

## Why alpha cannot disappear

The frozen paper-R2 radix-3 DAG cannot carry the nine `alpha_h` gauges with
only its existing kappa chains. An exhaustive profile proof finds:

- two standalone normalizations for each of the three first-layer R3 groups;
- two more for the untwisted second-layer group;
- the four existing second-layer rho/rho-inverse chains absorb the remaining
  ratios.

The exact lower bound is therefore eight standalone normalizations per
branch/Q-block. There are two branches and four Q-blocks, so the attainable
minimum is 64 standalone chains per forward. Multiplying only `alpha_h`
attains this bound; the `h=0` rows are raw loads.

## Chain ledger

| class per forward | current | candidate | delta |
| --- | ---: | ---: | ---: |
| standalone T0 / normalization | 72 | 64 | -8 |
| existing NTT9 | 80 | 80 | 0 |
| existing NTT16 | 144 | 144 | 0 |
| repair or final multiply | 0 | 0 | 0 |
| **total** | **296** | **288** | **-8** |

Encapsulation executes two forwards, so the static caller saving is 16
Montgomery chains. This is the exact frozen-DAG result, not an estimate based
on twiddle counts.

## Correctness and range

The generator proves all 288 linear basis inputs and 41,472 output cells equal
modulo q after beta absorption. Raw signed representatives may differ, but the
Natural-Q lane owner, scale 4, Montgomery exponent 0, and canonical transform
are unchanged.

Closed signed-interval propagation, with exhaustive top-split seed values,
gives a candidate final envelope of `[-21333, 21333]`, compared with the
current `[-20751, 20753]`. Every actual pre-operation remains within signed
i16 and no new reduction is required.

## Decision

The candidate `T0-BETA-TO-RADIX2` reaches the minimum scheduling threshold:
eight chains saved per forward with no routing or reduction debt. The next
authorized checkpoint is an exact schedule and branch-specific constant-table
artifact only. ASM, timing, native KEM, Q-order reopening, and production
promotion remain unauthorized.

## Evidence

- `generated/gt9x16-prod3-natural-q-t0-absorption-map.json`
- `tools/generate_gt9x16_prod3_t0_absorption_map.py`
- `tests/test_gt9x16_prod3_t0_absorption_map.py`
