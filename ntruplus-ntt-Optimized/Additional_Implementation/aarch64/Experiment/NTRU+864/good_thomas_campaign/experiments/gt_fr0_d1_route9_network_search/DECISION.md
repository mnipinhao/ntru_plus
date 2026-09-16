# Decision

- Authorize benchmark-only R9-A transpose/repair and R9-B three-bank TBL.
- Keep them as separate symbols and compare each with current scalar and
  factorized scalar at the coordinate-only boundary.
- Generate R9-C if a concrete exact network is non-dominated on instructions,
  TBL count, critical shuffle/TBL depth, live-vector footprint, or memory
  operations. A name without such a concrete Pareto point is not a candidate.
- Do not claim a free 8-by-8 transpose: exact Official lane ordering requires
  output repair.
- Use one reusable route9 body rather than twelve unrolled copies, then inspect
  call/address overhead, spills and text size.
- No Slothy until a concrete emitted object passes tagged correctness and Pi 5
  timing. Direct ToBytes/FromBytes remain the following attribution level.
