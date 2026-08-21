# Checkpoint E: NTT-domain representation closure contract

Checkpoint E intentionally stops before provisional D-B assembly. Its gate is
to make every value's mathematical identity, physical placement, scale, range,
factor, and next consumer explicit across forward, BaseMul/BaseInv, and
inverse.

## Official lifecycle audit

The audit reads the pinned source and linked assembly objects. It rejects a
source drift if the terminal stores, BaseMul R² pass, BaseInv denominator
side-output, inverse load block, or observed scaled-BaseMul→inverse caller edge
disappears.

| Official leaf | Instructions | Vector loads | Vector stores | YMM set |
| --- | ---: | ---: | ---: | ---: |
| `poly_ntt` | 362 | 33 | 20 | 16 |
| `poly_basemul` | 290 | 40 | 12 | 16 |
| `poly_basemul_scale` | 249 | 34 | 8 | 16 |
| `poly_baseinv_1` | 251 | 14 | 10 | 16 |
| `poly_invntt_scale` | 417 | 36 | 20 | 16 |

All are call/frame/stack-reference/`vzeroupper` free. Vector load/store counts
are static instructions, not dynamic totals.

The audit found two contracts that the prior layout document did not model:

1. regular BaseMul returns resident `R^0`, while scaled BaseMul returns
   inverse-feed `R^-1`;
2. BaseInv has an 18-YMM denominator side layout spanning its assembly phase,
   batch inversion, and final application phase.

## Pipeline component map

The normalized map contains 288 `(branch,row,lane)` terminal factors and 1,152
`(b,p,q,j)` physical cells. It records:

- trit/bit-reversed physical-to-mathematical maps;
- `X^4-factor`, normal factor, Montgomery factor, and qinv constant;
- value-contract IDs for forward, resident arithmetic, BaseInv, regular
  BaseMul, and scaled inverse feed;
- Official, terminal-major, terminal-stream, persistent-pair, and hybrid
  physical positions.

The generator proves each dense layout is a bijection over 1,152 cells and
cross-checks every Official position against the component oracle.

## Candidate cost matrix

| Candidate | Forward ABI | Arithmetic input | Arithmetic output | Estimated BM routing | Estimated BI routing |
| --- | --- | --- | --- | ---: | ---: |
| A | terminal-major | terminal-major | terminal-major | 0 | 0 |
| B | persistent pair | persistent pair | persistent pair | 432 | 288 |
| C | terminal-major | terminal-major | persistent pair | 144 | 144 |

These are full-transform counts for the current explicit AVX2 pack/unpack
schedule. They exclude arithmetic and are not cycle measurements. Candidate A
may pay more inverse arithmetic; candidates B/C depend on an unimplemented
paired adjusted inverse. No candidate is selected yet.

## Next implementation gate

Implement provisional Official-style R3R3 NTT9-first forward and adjusted
NTT16 with the required final range reduction. Emit A and B directly; C uses
A at the forward boundary. Each physical output is checked through this
contract rather than canonicalized. Forward-only timing remains diagnostic.

After that, BaseMul/BaseInv consume the candidate layouts with routing inside
their loads/stores, followed immediately by scale-correct adjusted inverse
NTT16 and inverse R3R3. Selection is based on `2F+BM_scale+I` and `F+BI+I`,
never on the static matrix or forward alone.
