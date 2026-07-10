# U01v3 F01 A1: Stage345 Block0 Preserve Block1 Live-ins

Status: generated experiment-only prototype, not a passing candidate. Production default is unchanged.

A1 computes Stage12 block0 and block1 once per row, removes the Q0..Q15 Stage12 stores, runs a renamed Stage345 block0 that avoids block1 handoff registers, then runs Stage345 block1 from those live-ins.

Block1 preserved registers: `q6`, `q9`, `q10`, `q20`, `q23`, `q24`, `q30`, `q31`.

Stage345 block0 allocator peak non-reserved live values: 15 of 23 available non-reserved registers.

Reserved registers written by renamed Stage345 block0: none.

Validation:

```text
local assemble: pass, clang --target=aarch64-linux-gnu
Pi5 correctness: fail vs u01v3_block01_production_oracle
Pi5 observed mismatches: 74568
Pi5 ABI mask: 0x0
PMU: not run because correctness fails
```

No block1 spill/reload or raw q reload is introduced by this artifact. The copied Stage345 scalar wrap chain still has its existing scalar stack temporaries from the source block.
