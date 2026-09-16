# A1-S results

The fixed T1 bank-major ABI and exact 552-instruction one-bank DAG were run in
the dedicated local Slothy environment. The 47-instruction tail subregion is
OPTIMAL at 60 modeled stalls (approximately 72 N1-proxy cycles). Functional RA
for the unified one-bank region is OPTIMAL in 35.93 seconds. Subsequent
split-window scheduling finishes with `split_heuristic_full:OK!`.

Post-audit proves 552 instructions, 90 each of `mul`, `sqrdmulh`, and `mls`,
one tail `ldp`, 69 `ldr`, no symbolic registers, no stack/spill, and no change
to the instruction multiset or coefficient-memory boundary. Apple clang also
assembles the integrated source as AArch64 ELF.

On Raspberry Pi 5 Cortex-A76 core 3, 64 one-bank, 64 six-bank, and 64 complete
Forward cases pass. Complete Forward is checked against Official through the
frozen FR0 map. PMU results combine three repetitions and both variant orders,
61 samples per order:

| Boundary | T1 cycles | T1+Slothy cycles | delta | instructions both | IPC T1 -> candidate |
| --- | ---: | ---: | ---: | ---: | ---: |
| one bank | 579.551 | 581.440 | +1.889 | 593.002 | 1.0232 -> 1.0199 |
| six banks | 3470.273 | 3491.145 | +20.872 | 3479.002 | 1.0025 -> 0.9965 |
| complete Forward | 4165.040 | 4208.347 | +43.306 | 4432.002 | 1.0641 -> 1.0531 |

The candidate misses the required 20-cycle improvement by 63.306 cycles and
is rejected. Identical instruction counts plus lower IPC show a scheduling
regression, not hidden arithmetic or memory work. The extra amplification at
the full boundary is an observed integration/code-layout effect; this gate
does not claim a unique microarchitectural cause.

Raw samples, environment, source hashes, and remote build/correctness logs are
under `pi5-results/` and are gitignored. Reproducible solver inputs, outputs and
logs are retained in this experiment.
