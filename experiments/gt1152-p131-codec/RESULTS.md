# P131 — NTRU+1152 codec, checked with P130's method

Callgrind (`cg.sh`, per call, GT vs Official):

| | GT | Official | reading |
|---|---|---|---|
| `tobytes` full | 1,156 SIMD, **288 stores** (8 B + 4 B per 12-byte block) | 1,080 SIMD, ~108 16-byte stores | P130's store scheme applies |
| `tobytes_small` | 865 SIMD, 288 stores | -- | same |
| `frombytes` | 830 SIMD, 306 scalar, one 16-byte load per block already | 758 SIMD | the load fix is already in (P86); the rest is P103's structural transpose, and the roadmap records a full unroll at +70% on M2 -- left alone |
| first product | 2,916 SIMD | 2,628 | P126's transpose, by design |

## tobytes

`gen_store_order.py` (P130's generator, generalised to the block size): a block
takes one 16-byte store when its four extra bytes land in a neighbouring block
written later.

| variant | single-store blocks | M2 decaps | A76 decaps |
|---|---:|---:|---:|
| HEAD (all split) | 0 | 4,976.8 ns | 43,519 |
| forward + backward (`vext` + store ending at the block) | 112 | **+8 ns** | -218 |
| same order, backward demoted to split (`--demote-backward`) | 66 | **+-0** | **-171** |
| forward-maximal order (`--forward-only`) | 99 | **+9 ns** | -210 |
| the new order with every block split (order alone) | 0 | +-0 | -- |

So on M2 both the backward stores and the forward-maximal order cost about
9 ns, while the order change alone is free.  Shipped: `--demote-backward`, the
only variant that does not regress M2 (rule 1).

| | M2 keygen / encaps / decaps | A76 keygen / encaps / decaps |
|---|---|---|
| HEAD | 6,181 / 6,230 / 4,976.8 ns | 54,906 / 46,765 / 43,519 cyc |
| P131 | 6,181 / 6,234 / 4,976.6 ns | 54,665 / 46,605 / 43,348 cyc |
| | +-0 | **-0.44% / -0.34% / -0.39%** |

M2 means over eight interleaved rounds, A76 over three.  KAT, M2 + Linux
`make check` (incl. 13,824 canonical-decode cases), TIMECOP (`-O`..`-Os`) pass.
The generator regenerates NTRU+864's P130 tables byte for byte.
