# Scale-1 r serializer V2 packet map

## Corrected result

The boundary-preserving 8-input serializer packet is ownership-correct and
has a concrete structural credit. The first ASM hard gate exposed and fixed
an important modeling error: Official `pack.s` consumes eight stride-8
vectors and emits coefficients lane-major; it does not consume eight
contiguous 16-coefficient vectors.

For packet zero the required inputs are:

```text
ymm0 = c0,c8,...,c120
ymm1 = c1,c9,...,c121
...
ymm7 = c7,c15,...,c127
```

The physical tiles are state vectors `20..23` and `16..19`. For each
coefficient plane, `vpshufb`, `vpermq`, and two `vperm2i128` operations split
even/odd lanes and join the two tiles. Four planes cost exactly 24 routes and
form the eight inputs required by the unchanged Official pack network.

The old `4x16 -> contiguous vectors` model was an ownership-valid transpose
but the wrong consumer contract. It failed the real Forward-to-Official byte
differential and is not retained.

## Exact proof and budget

- All 18 quartets own exact 64-coefficient intervals.
- All nine packets form eight exact stride-8 Official inputs.
- Official lane-major ownership emits a sequential 128-coefficient / 192-byte block.
- The nine blocks cover bytes 0..1727 exactly once.
- Packet four safely crosses the GT branch boundary after materialization.
- Each packet costs 8 loads + 24 formation routes + 48 normalization
  instructions + 58 Official pack/store instructions = 138.
- Abstract packet-body delta is `154 -> 138`, or `-144` over nine packets.

Linked totals additionally include hoisted constants, pointer updates,
`vzeroupper`, and `ret`; linked truth is reported in the ASM/PRICE checkpoint.
