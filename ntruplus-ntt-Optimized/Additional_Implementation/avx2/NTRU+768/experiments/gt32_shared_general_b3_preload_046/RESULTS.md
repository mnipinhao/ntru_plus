# GT32-SHARED-GENERAL-B3-PRELOAD-046 Results

All deltas are shared-preload minus GT Clean; negative is faster.

## Gates

- Same shared symbol, no clone and no new production symbol.
- `.text`, `.rodata`, and selected symbol addresses are identical.
- Corrected SUPERcop base-plus-deviation parser self-test passes.
- A and G both pass the canonical 100-vector byte-exact KAT.
- CPU affinity is fixed to core 1; blocks use paired AB/BA ordering.

## First 256-block run

| Operation | Paired median | Favorable | Bootstrap 95% CI |
|---|---:|---:|---:|
| Keypair | +12.5833 | 105/256 | [+3.75, +17.5] |
| Encap | **-27.8333** | 144/256 | **[-47.0833, -1.5208]** |
| Decap | **-19.0625** | 149/256 | **[-24.6667, -7.2083]** |

## Independent repeat, 256 blocks

| Operation | Paired median | Favorable | Bootstrap 95% CI |
|---|---:|---:|---:|
| Keypair | +5.2083 | 121/256 | [-4.375, +15.4583] |
| Encap | **-21.3125** | 144/256 | **[-36.8333, -0.1250]** |
| Decap | -4.3333 | 140/256 | [-11.75, +2.1667] |

## Pooled 512-block diagnostic

| Operation | Paired median | Favorable | Bootstrap 95% CI |
|---|---:|---:|---:|
| Keypair | **+8.75** | 226/512 | **[+2.6042, +15.1667]** |
| Encap | **-24.3333** | 288/512 | **[-35.7083, -7.0625]** |
| Decap | **-9.125** | 289/512 | **[-18.9792, -3.0417]** |

## Interpretation

Replacing the shared body avoids the catastrophic 045 relocation effect and is
clearly favorable to Encap.  Decap remains directionally favorable, but its
independent repeat does not keep the confidence interval below zero.  Keypair
does not call shared General-B3, yet the pooled measurement reports a small
positive shift.  That violates the predeclared neutral-control requirement and
shows that an identical-address image can still have small whole-process
delivery interactions.

The result therefore does not justify production promotion.  Keep GT Clean
unchanged.  `045` remains the stronger causal evidence for a Decap-private
mechanism; `046` shows that global replacement avoids the clone disaster but
delivers only a small, not operation-stable whole-image gain.
