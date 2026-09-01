# M5I: complete NTT9-core Slothy hard gate

This experiment answers the pressure question left by M5H: can one complete
paper-oriented NTT9 consume nine already-twisted vectors while another
nine-vector column block remains live, without spill or an extra load/store
boundary?

The register-only region contains 102 real instructions:

- three 15-instruction correlation-safe level-1 B3s;
- four 3-instruction Algorithm-10 eta/eta-inverse products;
- three 15-instruction correlation-safe level-2 B3s.

The dataflow is deliberately consumer ordered. After A, B, and C are formed,
`G0=B3(a0,b0,c0)` consumes row 0. The two eta products for G1 are then made
and consumed immediately, followed by the two products for G2. Distinct
symbolic names preserve the exact DAG; destructive physical reuse is selected
by Slothy from the dead lifetimes.

One constant vector is enough. Its halfwords are
`rho,rho',rho2,rho2',eta,eta',eta^-1,(eta^-1)'`; the modulus occupies one
additional vector. The driver reserves `v8-v15` for the ABI and `v16-v24` for
the untouched column block, leaving exactly `v0-v7,v25-v31`.

Because 102 instructions are a medium region, the driver uses two fresh
Slothy instances. Pass 1 performs functional-only allocation with instruction
order fixed. Pass 2 extracts the nine physical live-outs from that
order-preserving artifact, declares them explicitly, then schedules the real
allocated instructions with the N1 split-window heuristic. The first draft of
pass 2 was rejected because it did not declare those physical outputs; the
retained driver and log are from the corrected run.

The corrected remote run uses Slothy 0.2.2. RA is OPTIMAL in 1.96 seconds and
selfcheck passes. Window scheduling completes with
`split_heuristic_full:OK!`. Both artifacts use all fifteen allowed vector
registers and no reserved vector, GPR, memory, branch, stack, or spill
instruction. They assemble locally as Armv8-A Neon.

The scheduled file reports 25 expected N1-proxy cycles. This is scheduler
metadata, not a Raspberry Pi 5 or full-Forward performance claim. The region
is not linked into production and has no full-path benchmark yet.
