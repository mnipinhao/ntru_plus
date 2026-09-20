# P68 — SUPERCOP after the lane-basis inverse

supercop-20260831, Pi 5 Cortex-A76, GCC 14.2.0 `-march=native -mtune=native`,
goal `constbranchindex`, run date 20260920.

**GT 90,586 against the official's 111,367: −18.66%**, from P40's −18.39%.

## Selection cycles, one run

The pre-P68 leaf was left in the tree as `aarch64-gt1152.bak-pre-p68`, so
SUPERCOP measured **both versions in the same run, same host, same compiler
set** — the A/B is internal to the run rather than across dates.

| implementation | cycles | P40 | P33 | P29 |
|---|---:|---:|---:|---:|
| **`aarch64-gt1152`** (P68) | **90,586** | 90,942 | 92,079 | 109,446 |
| `aarch64-gt1152.bak-pre-p68` | 90,874 | 90,942 | — | — |
| `aarch64` (official) | 111,367 | 111,441 | 111,403 | 111,401 |
| `opt` | 193,348 | 193,544 | 193,359 | 193,469 |
| `ref` | 297,675 | 297,636 | 297,704 | 297,624 |

```
P68    vs official   -20,781 cycles   -18.66%
pre-P68 vs official  -20,493 cycles   -18.40%     (P40 recorded -18.39%)
P68    vs pre-P68    -   288 cycles   - 0.32%     same run
```

The control is good in both directions: the pre-P68 leaf reproduces P40's
−18.39% to within 0.01pp, and the official moved 74 cycles in 111,441, 0.07%.

SUPERCOP's `try` verdict is `ok` for all five implementations, against
checksum `2275d10293...a317cb91` — the same one P33 and P40 recorded, so the
KEM byte contract is unchanged.

## Stabilized quartiles, `aarch64-gt1152`, 3 runs x 32 samples

| operation | q1 | median | q3 | P40 q1 |
|---|---:|---:|---:|---:|
| keypair | 48,624 | 57,583 | 66,844 | 48,610 |
| encaps | 46,584 | 46,620 | 48,240 | 46,549 |
| decaps | **44,005** | 44,029 | 44,052 | 44,440 |
| **q1 sum** | **139,213** | | | 139,599 |

keypair and encaps sit within 35 cycles of P40, which is the run-to-run floor
for this host; decaps carries the change. keypair's spread is the rejection
loop, not measurement noise — encaps and decaps are inside 0.1% of their
medians.

Per-operation rows are emitted only for the selected implementation, so these
are P68's; the pre-P68 comparison above is the selection-cycles A/B.

## Against the direct measurement

A separate `perf_event` harness on the same host (median of 65 x 60, core 2)
put decaps at 44,038 before and 43,867 after, −171 cycles. SUPERCOP's
selection-cycles A/B says −288 across the whole KEM. The two are consistent in
sign and order; they are not the same statistic, and the selection-cycles
figure is the one of record.

## Leaf staging

`refresh_leaf.py` expands the four changed assembly files with `gcc -E -P` on
the target rather than pattern-matching them, because `inverse_ntt.S` uses a
live `C(name)` macro that P40's `to_leaf_asm` cannot handle; on Linux `C(name)`
is `name`, already the leaf's convention. `rebase.s` and
`invntt9_lane_tables.h` are new, and `api_glue.c` changes to pass the repacked
table.

The conversion was validated before the run: the KAT built against the leaf's
own `.s` files hashes to `2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3`,
the value recorded in `gt1152-p10-kem/pi-results.json`.
