# D1-P3B2 hypothesis

Observation: P3B1 proves that SIMD route9 reduces the coordinate bridge from
1760/1796 to 392/417 Cortex-A76 cycles. Its exact Official outputs are then
written, reloaded and shuffled solely to satisfy the stock byte API.

Primary bottleneck: layout/permutation materialization.

Hypothesis: composing the authoritative FR0/Official map with stock
`poly_shuffle2` and `poly_shuffle` exposes direct output-oriented networks that
never create `Official[864]`.

Exact proposed change: no production code. Derive both composed maps, their
inverse, Q-vector graph, packing-block selectors and two concrete instruction
families. Compare static instructions, memory width/count, lookup depth,
register footprint and independent chains—not instruction count alone.

Expected effect: remove 108 Q stores plus 108 Q reloads and expose freedom to
place pointwise normalization around routing. Expected risk: direct output Qs
may require narrow lane loads or redundant full-vector loads.

Falsifier: either map is not a bijection/inverse, tagged/random replay fails,
or no exact direct candidate avoids the full coefficient intermediate.
