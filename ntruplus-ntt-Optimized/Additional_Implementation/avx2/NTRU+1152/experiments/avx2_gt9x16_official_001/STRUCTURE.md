# Official-vs-GT assembly-structure audit

This is a structure checkpoint, not a speed result. The reproducible report is
`generated/gt9x16-pipeline-structure-audit.json`; it audits the pinned Official
assembly objects and the exact linked GT correctness benchmark ELF under GCC
15.2 `-O3 -mavx2`.

## Main result

| Function | Static calls | Stack allocation | `vzeroupper` | Vector stack references |
| --- | ---: | ---: | ---: | ---: |
| Official `poly_ntt` | 0 | 0 | 0 | 0 |
| Official `poly_basemul` | 0 | 0 | 0 | 0 |
| Official `poly_baseinv_1` | 0 | 0 | 0 | 0 |
| Official `poly_invntt_scale` | 0 | 0 | 0 | 0 |
| GT full-forward orchestrator | 9 | 5,600-byte `rsp` subtraction | 3 | 10 |
| GT shear + distance-8 helper | 0 | 0 | 1 | 0 |
| GT NTT16 distances 4/2/1 helper | 0 | 0 | 1 | 0 |
| GT two-radix3 NTT9 helper | 0 | 576 bytes | 1 | 29 |

The linked wrapper has nine static call sites. Expanding its fixed loops gives
97 hot helper invocations per transform: one top split, eight adapters, eight
shear/distance-8 calls, 72 row-level NTT16 calls, and eight NTT9 calls. From
the observed call sites and helper exits, approximately 98 `vzeroupper`
instructions execute per transform. This is reference structure tax, not a
request to delete isolated instructions by hand.

The compiler did vectorize the scalar-looking NTT9 source: its body contains
553 vector instructions and no loop back edge. Its problem is instead a
3,000-byte generated schedule with a 576-byte frame and 29 vector stack
references. Likewise, the adapter is partly vectorized but retains scalar
index arithmetic and two vector stack references.

The fixed C layout materializes 72 YMM rows at each of the shear→NTT16 and
NTT16→NTT9 boundaries, then ends with 1,152 position-addressed scalar stores
into Official layout. Those conversions stay inside full-real timing until a
native-layout producer/consumer actually removes them.

## Checkpoint E lifecycle extension

`generated/ntt-domain-lifecycle-audit.json` extends this structural snapshot
to the actual cross-kernel value contract. It records the regular BaseMul R²
post-pass, the distinct R^-1 scaled-BaseMul→inverse edge, BaseInv's 18-YMM
denominator side state, and the exact forward/inverse terminal block loads and
stores. `LAYOUT.md` uses that evidence; the earlier Checkpoint-C layout choice
is no longer treated as a complete-pipeline selection.

Official forward contains 279 vector instructions, 61 vector-memory
instructions, no call, no frame, and no vector stack reference across the
whole transform. Official BaseMul and inverse have the same leaf/no-frame/no-
`vzeroupper` shape. Their stage stores are deliberate pipeline layout, whereas
the GT correctness path materializes arrays at every helper boundary.

## Rule for Checkpoint C

The optimized NTT16 prototype should be one leaf-ish block spanning the
27-blend shear, distance-8, and distances 4/2/1. It must not call row helpers
or restore a canonical C array between stages. Do not add `vzeroupper` inside
the block. An outer AVX-to-legacy-SSE boundary may be considered only after it
is demonstrated and separately benchmarked.
