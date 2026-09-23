# P127 — 864 inverse: priced before redesign

Item 3 of the 864/1152 plan was "864's packed_i9 scatter stores and the tail
pieces, ~450 A76 cycles over the multiply floor".  P126 showed that floor model
is wrong on the A76 (permutes share V0 even when multiplies saturate it), so
every candidate here is priced by direct knockout, not by instruction counts.
GT tree at 56c896d8; Official from SUPERCOP 20260831 (symbols renamed o_*).

## Where the M2 gap is: decapsulation arithmetic, component by component (`comp.c`)

| per decaps | M2, GT - Official | A76, GT - Official |
|---|---:|---:|
| inverse -> ternary | +52 ns | +40 |
| first product | +13 | +12 |
| forward NTT (x2) | -29 | -947 |
| basemul | -21 | -262 |
| frombytes (x3) | +10 | -71 |
| tobytes (small + full) | ~+10 | ~+100 |
| **total** | **~+60 ns** | **-1,105 cycles** |

GT's 864 decapsulation arithmetic is *slower* than Official's on M2; its
decaps lead there is all hashing.  Running decaps in Official's layout (768's
approach) is ruled out: it would give up the forward NTT and basemul leads
(~-1,200 A76 cycles) to gain ~50, and a hybrid would decode `c` twice (~80 ns).

## Inverse per callee (skip-the-call knockouts)

| callee | M2 | A76 |
|---|---:|---:|
| packed_i9 x12 | 120 ns | 1,670 |
| invntt16_paired x3 (incl. p28_main) | 135 ns | 1,980 |
| tail_direct | 33 ns | 417 |
| route (mod 3 + st3 interleave, 96 vectors) | 52 ns | 500 |

On M2 invntt16_paired + p28_main sit exactly on their SIMD-op bound
(1,884 ops / 4 per cycle = 135 ns) and packed_i9 is close to it.

## Upper bounds of the redesign candidates

| knockout (timing only, output wrong) | M2 | A76 |
|---|---:|---:|
| packed_i9: 192 lane stores -> plain stores (same count) | -4 ns | -69 |
| packed_i9: lane stores deleted (one store per vector) | **-10 ns** | **-237** |
| p28_main: 192 ext -> mov, 114 lane inserts deleted | **-12 ns** | 0 |

A real redesign has to pay for the permutes that build full vectors, so the
achievable gain is a fraction of these: together at most ~-22 ns M2 (-0.57%
of decaps) and ~-237 A76 cycles (-0.55%), realistically about half.

## Verdict

The 864 inverse redesign does not pay for its cost: the whole store and
data-movement layer it would attack is worth at most ~0.5% of decaps on
either machine, before the replacement permutes.  The remaining M2 gap to
Official's inverse is the arithmetic structure itself (three components, the
route/tail stages), not a removable overhead.
