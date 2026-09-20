# P67 — the main kernel in the (component, half) basis, generated and asserted

P66 predicted the terminal constants would have to become per-`s`, eight tables
where there is one.  That was wrong, and the correction makes this gate much
smaller than planned.

## No table change is needed

`invntt16_main_constants` and `invntt16_tail_constants` are **64/64 rows
identical**, and every row has the shape

```
[A, A, A, A, B, B, B, B]
```

so the terminal constant depends on `half` alone — not on `s`, not on the
component.  Whether the inner four lanes mean `s_local` or `branch`, the same
constant applies.  Swapping their meaning needs no table work at all.

## The fold is already right

`invntt16_asm` folds with `ext v.16B, vA.16B, vA.16B, #8` plus `add`, thirty-two
times, every one a four-halfword self-rotate.  That is the fold over `half` in
either basis — the same rotation `gt1152-p22-tail-asm` had to introduce for the
tail.  The generator asserts all thirty-two before touching anything.

## So only the output changes

The natural index is `n = component + 4*s + 36*t + 576*half`.  The present kernel
writes `n = (c + 16*g) + 4*s_local + 36*t + 576*half`; since `576 = 16*36` and
`4*s_local < 16 < 36`, `divmod(off//2, 36)` splits an offset into the group index
`t + 16*half` and `4*s_local`.  In the new basis that group is four consecutive
halfwords, so it becomes one `STR D` at `2*36*group` — the identical mapping
`generate_tail.py` uses.

`generate_main.py` performs that collapse and asserts, over the whole kernel:

- thirty-two `ext`, all four-halfword self-rotates;
- 128 `UMOV` and 128 `STRH`, each pair matched;
- for every store, `r // 4 == lane`, which independently confirms the inner lane
  really is `s_local`;
- exactly thirty-two groups, each extracted from a single register.

The `STR D` is emitted where the `UMOV` was, not where the `STRH` was, because
Slothy reuses these registers hard and several are overwritten in between —
the same trap `generate_tail.py` documents, and the one P64's hand-made probe
fell into.

## Result

`invntt16_lane.S`: **436 instructions**, from 660 (-128 `UMOV`, -128 `STRH`,
+32 `STR D`).

Dropped into the tree for timing only — the scratch is not yet repacked, so the
values are wrong — it reproduces the P64 probe exactly:

| | A76 cycles | instructions | M2 ns |
|---|---:|---:|---:|
| current | 6,012 | 10,296 | 535.8 |
| P64's hand-made probe | 5,887 | 8,488 | 436.8 |
| **generated kernel** | **5,901** | 8,504 | **436.8** |

The fourteen-cycle difference is the probe's, not the kernel's: its grouping left
two of the thirty-two groups unplaced.

## What remains

One piece: `packed_i9` must write its scratch packed as `lane = 4*half +
component` instead of by the 16-axis.  P65 built and verified the rebase that
puts `packed_i9`'s *input* in that basis (`rebase.S`, 0/1152 mismatches, 354
cycles on A76, very nearly cancelled by the 256 output-side transposes it makes
unnecessary).  What is left is `packed_i9` itself: lanes become (component,
half), one call per `t`, and its output transpose goes.

Then the chain can be assembled and checked byte-identical against production,
as P60 did for 864.
