# Consumer-axis lower bound

The vertical forward naturally ends as:

```text
vectors = k16
lanes   = branch x degree
```

The frozen zero-spill quartic BM uses:

```text
vectors = branch x k3 x degree
lanes   = k16
```

Therefore `k16` must move from the vector index into the SIMD lane.  B1
(`branch-major`) and B2 (`degree-major`) only reorder the other lane bits and
cannot remove this axis exchange.

An optimistic AVX2 16x16 int16 transpose per `k3` is charged as 16 word
unpacks, 16 dword unpacks, 16 qword unpacks, 16 cross-128 permutations, 16
loads, and 16 stores: 96 instructions.  Three `k3` batches cost 288
instructions one way.  A `2*forward + BM + inverse` island needs two forward
bridges and one reverse bridge, or 864 instructions, unless a different BM is
implemented.

The alternative B1 lane-internal quartic BM handles only four quartics per
vector, versus 16 in the frozen SoA kernel.  It has a fourfold SIMD arithmetic
replication lower bound before degree-crossing shuffles, so it is rejected as a
way to avoid the transpose.

Adding only the one-way 288-instruction bridge raises the 1,884 producer floor
to 2,172.  This exceeds both the frozen 2,026.260 forward and the 1,924.947
five-percent gate.  The producer had just 40.947 instructions of headroom, so
there is no authorization to write an AVX2 kernel or claim a paired inverse
chain win.
