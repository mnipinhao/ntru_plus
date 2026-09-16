# D1-P2 profiling hypothesis

- Observation: D1-P1 is correct and D1 saves 665--1069 KEM cycles versus
  GT-old, but GT-D1 remains 3776--10396 cycles behind Official.
- Hypothesis: the deficit can be attributed to the measured Forward, Inverse,
  coordinate/reduction, serializer/deserializer and BaseInv-bridge boundaries
  using the unchanged stock KEM call counts.
- Exact change: none to the active kernels. Compile diagnostic entry points
  from the exact P1 wrapper and measure them in an isolated binary.
- Expected static effect: zero production instruction or memory change.
- Expected performance effect: none; this experiment only attributes cost.
- Register pressure: unchanged.
- Correctness/range impact: none; each component is checked against the P1
  representation and byte contracts before timing.
- Falsification: a correctness mismatch or a large unexplained KEM ledger
  residual means the decomposition is not sufficient to choose a bottleneck.
