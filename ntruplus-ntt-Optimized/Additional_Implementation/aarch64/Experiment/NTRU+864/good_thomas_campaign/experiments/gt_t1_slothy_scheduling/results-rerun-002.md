# A1-S-002: T1 schedule-only rerun

This rerun follows the `slothy-symbolic-asm-authoring` state machine in
`existing_region_replacement` mode.  It closes a gap in A1-S-001: the earlier
Pi 5 candidate combined Slothy register allocation and scheduling, while this
primary candidate preserves T1's original physical register allocation and
changes instruction order only.

## Contract and Slothy gates

- Exact baseline: 553 instructions including `ret`, 552 schedulable.
- Candidate: the same 552-instruction DAG and mnemonic multiset.
- Arithmetic: 90 each of `mul`, `sqrdmulh`, and `mls`.
- Memory: one tail `ldp`, 69 `ldr`, no coefficient store in the region.
- No stack access, spill, new memory boundary, or output-register ABI change.
- Local Slothy 0.2.0, checkout
  `f8462d0deb9973565b525f7e63636630fa679bd7f`.
- Schedule-only and RA+schedule both finish with
  `split_heuristic_full:OK!`; RA-only is `OPTIMAL` and self-checks.

Slothy 0.2.0 lacks the zero-offset alias parser for `ldp qA, qB, [x1]`.
Only the optimizer input copy is normalized to the encoding-equivalent
`ldp qA, qB, [x1, #0]`; the production baseline remains untouched.  The
generic skill log parser reports a false timeout because it matches Slothy's
benign `Setting timeout` configuration line.  The strict post-audit instead
requires successful full-window/self-check markers and rejects tracebacks or
parse failures.

## Raspberry Pi 5 result

All 64 one-bank, 64 six-bank, and 64 complete Forward checks pass. Complete
Forward is also checked against Official through the frozen FR0 map. Results
combine three repetitions, two opposite variant orders, and 61 samples per
order on Cortex-A76 core 3; all thermal checks report `throttled=0x0`.

| Boundary | T1 p50 | schedule-only p50 | delta | retired instructions | IPC T1 -> candidate |
| --- | ---: | ---: | ---: | ---: | ---: |
| one bank | 579.546 | 573.315 | -6.231 | 593.002 / 593.002 | 1.0232 -> 1.0343 |
| six banks | 3470.136 | 3456.479 | -13.656 | 3479.002 / 3479.002 | 1.0026 -> 1.0065 |
| complete Forward | 4165.445 | 4156.983 | -8.462 | 4432.002 / 4432.002 | 1.0640 -> 1.0662 |

Complete-Forward deltas in the three independent repetitions are -8.754,
-7.800, and -8.666 cycles. Thus the small gain is repeatable and comes from
instruction order rather than fewer retired instructions.

## Decision

Reject for promotion and retain current T1. The candidate improves complete
Forward by 8.462 cycles (0.203%), but the predeclared scheduling-only hard gate
requires at least 20 cycles. This rerun nevertheless isolates the A1-S-001
regression: preserving the original physical allocation turns `+43.306`
cycles for RA+schedule into `-8.462` cycles for schedule-only. Slothy's new
allocation, not scheduling in general, was the damaging part of A1-S-001.

Solver inputs, generated assembly, and logs are under `rerun-002/`. Pi 5 raw
samples, build/correctness logs, environment records, hashes, and summary are
under `pi5-results-rerun-002/` (gitignored).
