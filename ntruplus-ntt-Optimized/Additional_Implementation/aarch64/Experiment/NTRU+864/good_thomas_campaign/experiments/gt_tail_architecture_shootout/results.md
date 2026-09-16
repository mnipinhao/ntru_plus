# A1 results

All variants pass 80 tail tests and 48 one-bank, six-bank, and complete-Forward
tests.  T0 and T1 are bit-exact; T2 is coefficientwise equal modulo 3457.
Complete Forward is also equal to the Official transform through the frozen
FR0-to-Official map.

The target was a Raspberry Pi 5 Cortex-A76, core 3.  Each row is the overall
p50 from three repetitions, both variant orders, with 61 samples per order.
Instruction counts include the common C call harness; the parenthesized count
subtracts the measured nine-instruction noop.

| Boundary | Variant | cycles | instructions (minus noop) | IPC | branches |
| --- | ---: | ---: | ---: | ---: | ---: |
| tail only | T0 | 414.013 | 436 (427) | 1.053 | 15 |
| tail only | T1 | 307.005 | 333 (324) | 1.085 | 15 |
| tail only | T2 | 319.255 | 345 (336) | 1.081 | 3 |
| one bank, routing prepared | T0 | 599.125 | 610 (601) | 1.018 | 5 |
| one bank, routing prepared | T1 | 579.672 | 593 (584) | 1.023 | 5 |
| one bank, routing prepared | T2 | 533.564 | 548 (539) | 1.027 | 5 |
| six banks, routing prepared | T0 | 3561.345 | 3581 (3572) | 1.006 | 15 |
| six banks, routing prepared | T1 | 3471.471 | 3479 (3470) | 1.002 | 15 |
| six banks, routing prepared | T2 | 3196.828 | 3209 (3200) | 1.004 | 15 |
| complete Forward | T0 | 4231.714 | 4454 (4445) | 1.053 | 35 |
| complete Forward | T1 | 4165.076 | 4432 (4423) | 1.064 | 37 |
| complete Forward | T2 | 4206.830 | 4422 (4413) | 1.051 | 37 |

T1 improves complete Forward by 66.638 cycles (1.57%) over T0.  T2 improves
it by only 24.884 cycles (0.59%), and is 41.754 cycles slower than T1.  The
isolated T2 pass-2 result excludes its column-to-bank transpose, so it is not a
complete-Forward claim.

Static coefficient-memory counts at the tail boundary are 96 halfword lane
loads for T0, 12 vector loads for T1, and 16 vector loads for T2.  All variants
perform 12 vector output stores.  T0/T1 execute 36 Algorithm-10 products; T2
executes 48.  The Pi raw load/store event IDs returned zero for every variant
and the noop, so those PMU fields are invalid and are deliberately not used.
The architectural counts above come from generated assembly.

Raw samples, source hashes, environment and build logs are retained below
`build/pi5-tail` and `build/pi5-full` and intentionally gitignored.
