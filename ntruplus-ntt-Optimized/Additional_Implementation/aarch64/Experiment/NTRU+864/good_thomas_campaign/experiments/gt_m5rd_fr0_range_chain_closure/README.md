# G0 — M5R-D FR-0 range-chain closure

This default-off hard gate removes the archived `8874/9342` evidence split.
It does not change the transform, assembly DAG, memory boundary, or cycle
count.  It reconstructs one current source closure:

```text
Algorithm-10 NTT16 max 9342
  -> actual M5R-D level-1 and level-2 one-product NTT9
  -> M5C FR-0 BaseMul/BaseMulAdd
  -> M5E-r1 Algorithm-10 inverse
```

The previous M5C proof replayed the old M5A schedule from a symmetric `8874`
producer bound and obtained a `24438` operand bound.  That proof was safe for
its historical source but was not a proof of the later M5R-D assembly.  G0
starts from the constant-specific M5G Algorithm-10 NTT16 model (`9342`) and
executes the exact one-product B3 order used by M5R-D for all two tops, sixteen
columns, and nine output rows.

`prove_range_chain.py` carries all 288 leaf intervals through their exact FR-0
zeta values, the M5C widening Montgomery schedule, and the M5E lazy inverse
schedule.  `make check` additionally reruns the M5R-D source audit, M5C/M5D/M5E
component checks, the exhaustive M5E fixed-product proof, an M5E boundary test
at the new input bound, and an actual linked `2F + BaseMul/BaseMulAdd + I`
schoolbook differential.

This gate is a prerequisite/evidence repair, not a performance experiment.
Production and SUPERCOP remain unchanged.

## Run

```sh
make check
```

The authoritative generated report is `build/range-chain.json`.
