# D1-P3B5 fused ToBytes hypothesis

Observation: the selected P3B4 `r9_to` materializes both `official[864]` and
`post[864]`, performs separate route, normalization and shuffle passes, then
re-runs the stock packer's sign correction.

Primary bottleneck category: memory and layout boundary.

Hypothesis: retaining the P3B1 R9-A input-major route but consuming every
completed Official-order q-vector immediately with full modulo-3457
normalization and a contiguous eight-coefficient pack can remove all
coefficient scratch without increasing FR0 loads.

Exact proposed change: introduce a distinct `gt864_fr0_fused_tobytes` symbol.
Each of the twelve route9 calls loads nine contiguous FR0 q-vectors.  Its nine
outputs are normalized, packed and stored directly at their final 12-byte
protocol offsets instead of being stored as an Official polynomial.

Expected static effect: remove two 1728-byte arrays, `norm_only`,
`stock_shuffle2`, `stock_to`, and every intermediate coefficient load/store.
Keep 108 FR0 q-loads and emit exactly 108 twelve-byte stores.

Expected performance effect: reduce the selected P3B4 ToBytes from 1849.450
Pi 5 cycles to below 1250 cycles, which is the conservative threshold needed
for the current full Encaps path to overtake Official.

Expected register-pressure effect: higher transient pressure inside one R9-A
core because route, reduction and packing overlap.  More than the ABI GPR frame
or any coefficient/vector spill falsifies the static hypothesis.

Correctness or range impact: none.  The FR0/Official permutation, R0 scale and
logical roots are unchanged.  Every signed-int16 input is reduced to [0,3456]
before the exact reference 12-bit encoding.  Addresses depend only on public,
compile-time route coordinates.

Falsifying measurement: any mismatch over all 1296 output bytes, any guarded
edge fault, any unsupported ISA feature, any coefficient/vector spill, or a
paired Pi 5 median at or above 1250 cycles.
