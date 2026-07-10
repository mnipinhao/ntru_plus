# U01v3 F01 Track E E1 Preserve Live-ins

Status: correctness failed; PMU not run.  Production default is unchanged.

E1 computes Stage12 block0 and block1 once per row, keeps both block0 and block1 handoff values live, renames Stage345 block0 away from the block1 live-in registers, then runs Stage345 block1 from the live block1 handoff registers.

Preserved block1 registers: `q6`, `q9`, `q10`, `q20`, `q23`, `q24`, `q30`, `q31`.

Stage345 block0 reserved registers written: none.

Allocator peak non-reserved live values: 15 of 23 available non-reserved registers.

Validation:

```text
local assemble: pass, clang -target aarch64-linux-gnu
Pi5 correctness: fail
Pi5 mismatches: 74572
Pi5 ABI mask: 0x0
PMU: not_run_because_correctness_failed
```
