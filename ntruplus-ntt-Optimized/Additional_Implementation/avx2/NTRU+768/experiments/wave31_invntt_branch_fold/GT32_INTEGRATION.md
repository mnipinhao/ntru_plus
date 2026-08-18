# Wave31 relationship to the current GT32 inverse

Wave31 is preserved here as a historical, reproducible predecessor experiment.
Its measured assembly is **not** linked into the current GT32 backend and its
cycle counts are **not** attributed to the current GT32 inverse.

## Mechanism retained by GT32

Wave31 showed that, after inverse DFT3, the separate untwist, branch merge,
normalization, and branch correction can be composed into one fixed lane-wise
2x2 map:

```text
L = Mont(x0, fL0) + Mont(x1, fL1)
H = Mont(x0, fH0) + Mont(x1, fH1)
```

The current GT32 T9 tail independently uses this same class of composition.
`tools/generate_tile4.py::inverse_tail_matrix()` generates four coefficients
per physical lane and `src/tile4_inverse_tail_asm.S::MATRIX_PAIR` evaluates the
two outputs directly.  Thus GT32 already folds inverse DFT3 output handling,
untwist, top reconstruction, normalization, and final representative selection
into its generated branch-matrix tail.

## Why the Wave31 assembly is not imported into production

The executable ABIs differ:

- Wave31 consumes two old GTN-L3 branch vectors after inverse DFT3.
- Current GT32 consumes `I1 TILE4 AoS`, exponent `e=-1`, with a proved input
  bound of 12150, then performs its own checkpoint, inverse DFT3, and T9 matrix
  tail.
- Lane placement, factor tables, scale, range, and representative contracts
  therefore differ.

Wave31 measured a real improvement over its same-body algebraic control, but
the lazy and exact endpoints were still slower than its materialized Official
control.  Those measurements support the folding mechanism only; they are not
a current-GT32 performance result.

## Integration decision

```text
algebraic mechanism: subsumed by current GT32 T9 MATRIX_PAIR
old Wave31 assembly: archived, default-off, not linked
old PMU data: retained as provenance, not combined with GT32 benchmarks
new production change required: none
```

The original generator, exhaustive proof data, assembly harnesses, KEM
differentials, and PMU JSON are retained in this directory so the prototype
branch is not required to reproduce the result.
