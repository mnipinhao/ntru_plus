# Round 4B: vertical/batched GT16 static gate

## Frozen inputs

- Reuse the scalar GT(3,16) factorization, scale law, branch roots, and Official
  component mapping committed by Round 4 at parent `c62ec1a`.
- Keep the frozen GT32 native champion at 2,026.260 retired instructions per
  lazy forward and 3,179.5 cycles / 17,784.325 instructions for the tracked
  complete chain.
- Do not change public APIs, production objects, canonical contracts, or the
  default Official backend.

## Static scheduler

1. Build DFT3-first V1 batches with fixed `k3`, 16 `branch x degree` lanes, and
   16 coefficient-position vectors.
2. Expand every optimistic instruction in the producer schedule.  Use a
   physical allocator with YMM0--YMM14 available and YMM15 reserved.
3. Fuse R2 packing, branch/wrap constants, and the explicit preweight into the
   same frontend.  Folding constants changes the table operand, not the count:
   canonical `s=1` still needs the column-dependent Montgomery multiply.
4. Retain one DFT3 output batch while four positions are assembled; materialize
   the other two.  Run two-stage four-vector tiles, then paired stage-3/4 tiles.
5. Compare B1 and B2 lane ordering at the consumer boundary, and compare an
   explicit 16x16 transpose with lane-internal quartic multiplication.

## Gates

```text
producer forward < 0.95 * 2026.260 = 1924.947 instructions
consumer-compatible forward < 1924.947 instructions
complete F+B+I < 0.95 * frozen complete chain
```

Assembly is authorized only after all three gates have a consumer-complete
static schedule.  A producer-only win is recorded but cannot authorize a
kernel.
