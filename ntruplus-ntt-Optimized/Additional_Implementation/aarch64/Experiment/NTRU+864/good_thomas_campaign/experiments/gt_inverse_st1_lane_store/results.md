# A2 results

The generated ST1-lane candidate is bit-exact to M5E for 81 cases, congruent
to the independent inverse reference, and preserves eight halfword sentinels
on both sides of the output.

Raspberry Pi 5 Cortex-A76 results use core 3, three repetitions, both orders,
and 61 samples per order.  Counts in parentheses subtract the nine-instruction
noop harness.

| Boundary | variant | cycles p50 | instructions (minus noop) | IPC | branches |
| --- | --- | ---: | ---: | ---: | ---: |
| I16 only | M5E UMOV+STRH | 3885.671 | 5663 (5654) | 1.457 | 19 |
| I16 only | ST1 lane | 4363.537 | 5029 (5020) | 1.153 | 19 |
| complete inverse | M5E UMOV+STRH | 6866.058 | 9373 (9364) | 1.365 | 54 |
| complete inverse | ST1 lane | 7350.215 | 8739 (8730) | 1.189 | 54 |

ST1 lane is 477.866 cycles (12.30%) slower at I16-only and 484.157 cycles
(7.05%) slower for complete inverse.  It retires 634 fewer instructions at
both boundaries, but its much lower IPC more than cancels that saving.

Both variants still issue 864 scalar-width store instructions.  ST1 removes
the vector-to-GPR transfers but introduces address setup/post-index dependency
chains and uses the Neon lane-store path.  Thus instruction count alone is the
wrong cost model for this scatter.

Raw samples, source hashes, thermal state and build logs are retained under
`build/pi5` and intentionally gitignored.
