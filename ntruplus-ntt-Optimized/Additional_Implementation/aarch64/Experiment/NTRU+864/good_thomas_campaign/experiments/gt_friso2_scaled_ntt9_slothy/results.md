# Results

## Hard-gate result: pass, candidate remains investigate

All four witness-specific single-block regions passed the scoped allocation
gate on the remote Slothy environment.

| Case | Real instructions | RA | RA wall time | Schedule | N1 proxy cycles | Spill / stack / store / branch |
| --- | ---: | --- | ---: | --- | ---: | --- |
| `t0c1` | 154 | OPTIMAL + self-check OK | 5.213138 s | split full OK | 38 | none |
| `t0c2` | 154 | OPTIMAL + self-check OK | 5.258137 s | split full OK | 38 | none |
| `t1c1` | 138 | OPTIMAL + self-check OK | 4.497679 s | split full OK | 34 | none |
| `t1c2` | 138 | OPTIMAL + self-check OK | 4.391432 s | split full OK | 34 | none |

Every emitted result uses `v0-v15,v25-v31`; `v16-v24` are untouched.  `v31`
is the fixed modulus.  The only memory instructions are public constant loads
through `[x3], #16`.

## Why the region is 138/154 instructions

The original attempt presented an entire roughly 600-instruction bank to the
solver.  That is not a useful Slothy optimization unit and was stopped.  The
corrected region is exactly one scaled NTT9 block, while modeling the important
integration pressure by reserving nine physical vectors for its sibling.

Top-0 requires 17 lane-varying factors (34 independent vector loads) and one
packed common live-in.  Top-1 requires nine lane-varying factors (18 loads) and
three packed common live-ins.  Each block contains 26 real Algorithm-10
mulmods.

## Static whole-Forward cost warning

Extrapolating the exact load ledger to the complete Forward gives `+280`
instructions relative to M5R-D.  The measured CF0 implementation was `+292`,
including four address-setup instructions.  Therefore CF2 is only eight static
instructions below CF0 under the required two-independent-`ldr` baseline.

This gate proves register feasibility, not speed.  The 34/38 figures are a
Neoverse-N1 Slothy schedule proxy for isolated blocks; they are not Cortex-A76
measurements and cannot be compared with Official or SUPERCOP results.

## Parser note

The generic skill log parser reports a false timeout because it treats the
configuration line `Setting timeout of 1800 seconds` as evidence that the run
timed out.  The complete logs instead contain `OPTIMAL`, self-check `OK`, and
`split_heuristic_full:OK!`.  `audit_slothy.py` checks these terminal markers and
audits the emitted instructions directly.  The parser discrepancy is recorded
rather than silently ignored.
