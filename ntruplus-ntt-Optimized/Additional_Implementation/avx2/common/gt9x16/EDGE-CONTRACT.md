# GT representation-edge contract

This research schema is architecture-neutral even though its first generated
instance lives in the NTRU+1152 AVX2 experiment. AVX2 and NEON prototypes may
use different instructions and costs, but they must describe the same
mathematical edge.

An edge maps a producer representation to a consumer representation:

```text
R_producer -- E=(Pi,B,g,s) --> R_consumer
```

Each representation uses `R=(P,Q,B,g,s,O)`. Each edge records:

- a complete component permutation `Pi`;
- a terminal basis map `B` or a closed, explicitly generated basis family;
- a component-frequency gauge relation `g`;
- integer transform and Montgomery scale relation `s`;
- whether each part can be absorbed into forward/inverse twiddles, BaseMul
  weights/finalizers, BaseInv adjugate/denominator work, normalization, or
  load/store addresses;
- remaining runtime operations and range obligations.

Unknown instruction counts and cycles are null. `not-applicable` is distinct
from zero. A zero is permitted only for an identity proved by construction or
the definition of a benchmark control.

No edge may introduce a standalone full-array representation conversion.
Prototype code must first try adjacent arithmetic constants, basis operations,
and load/store addressing. Cycle selection occurs on an actual producer-tail
plus consumer-head boundary; complete-path selection occurs later.

The first concrete `gt-representation-edge/v1` artifact is generated as
`NTRU+1152/experiments/avx2_gt9x16_official_001/generated/g1-edge-oracles.json`.
