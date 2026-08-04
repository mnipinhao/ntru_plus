# NTRU+768 AVX2 vertical GT16 experiment

Round 4B tests the remaining GT16 architecture that is not covered by the
horizontal single-transform-per-YMM stop result.  One YMM lane is one of 16
independent transforms; one YMM vector is one NTT16 coefficient position.

The fixed V1 ABI is:

```text
batch  = k3                         (3 batches)
vector = k16 position              (16 vectors)
lane   = 4*branch + degree         (16 transforms)
```

`make check` regenerates no files.  It checks that the committed 1,884-entry
execution trace, physical-register allocation, instruction accounting, and
consumer-layout decision are current.  `make generate` intentionally updates
the generated artifacts.

The producer-only floor passes: 1,884 instructions is 7.02% below the frozen
2,026.260-instruction GT32 native forward.  The usable-forward gate fails.  A
vertical producer indexes `k16` by vector, whereas the frozen quartic BM indexes
`k16` by SIMD lane.  The optimistic three-batch 16x16 transpose costs 288 more
instructions, raising the boundary to 2,172 before control, address-generation,
or missing range work.

No assembly or production source is added.  The result is a pre-kernel
architecture stop, not a correctness rejection of GT(3,16).
