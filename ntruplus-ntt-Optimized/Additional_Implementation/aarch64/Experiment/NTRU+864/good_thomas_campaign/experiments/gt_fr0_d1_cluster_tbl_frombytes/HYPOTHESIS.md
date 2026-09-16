# D1-P3B20 clustered-TBL FromBytes hypothesis

The exact inverse map partitions all 54 serialized input q-vectors per top
into 15 clusters whose members touch the same eight FR0 output q-vectors.
Replace per-coefficient lane moves by TBL2/TBL4 routing of whole clusters.

The fixed contract is P3B11: arbitrary 12-bit representatives, 54 input
groups loaded exactly once per top, no coefficient scratch and native FR0
output.  Exact subset DP selects an order with peak 16 persistent outputs.

The candidate must delete routing instructions, have no non-ABI vector spill,
pass guarded differential tests, and recover at least 145 cycles against
P3B11 to meet the user target.
