# M5U-B1 hypothesis

Observation: M5U-B priced two deleted widening Montgomery reductions as ten
ordinary instructions per tile.  M5R-D already showed that instruction count
alone is not an A76 cycle model.

Primary bottleneck: arithmetic dependency/reduction latency.

Hypothesis: under one fixed FR-ISO2 ABI, directly forming each complete cubic
coefficient in signed int32 lanes and reducing once will beat the staged
schedule that reduces both wrap cross-terms before multiplying by `z0*R`.

Exact change: remove two five-instruction widening Montgomery reductions per
tile.  Keep `z0=9/3`, buffers, layout, scales, bounds, wrappers, compiler flags,
host, and measurement method identical.

Expected static effect: about 360 fewer dynamic arithmetic instructions over
36 tiles.  Expected performance effect: fewer cycles from both instruction
removal and a shorter quotient/reduction dependency chain.  Expected register
effect: wide cross-terms live longer, but no spill should appear.  Range impact:
the full direct accumulators must fit signed int32 before narrowing.

Falsifier: after correctness/range/code-shape gates, direct-wide does not
consistently beat staged in three paired Cortex-A76 PMU repetitions.
