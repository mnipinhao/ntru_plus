# U01v3 Track E E2 Parking Bridge

Status: Pi5 correctness and ABI pass. PMU intentionally not run in this round.

E2 is deliberately conservative. It keeps the one-pass Stage12 block0/block1 producer, but parks all block1 live-ins to the wrapper frame before running unchanged Stage345 block0. It then restores those values and runs Stage345 block1 through the live-handoff contract.

This is not a performance candidate. It is a correctness proof point that separates Stage12/block1 handoff correctness from the failed E1 Stage345 block0 SSA allocator.

Parking plan:

```text
q spills:    24  (8 block1 vectors * 3 rows)
q restores:  24
raw q reloads: 0
duplicate Stage12: no
Slothy: no
```

Validation:

```text
local assemble: pass, clang -target aarch64-linux-gnu
Pi5 correctness: pass
Pi5 mismatches: 0
Pi5 ABI mask: 0x0
PMU: not run by rule
```

E1 allocator summary retained for comparison:

```text
reserved_written: []
max_nonreserved_live_values: 15
```
