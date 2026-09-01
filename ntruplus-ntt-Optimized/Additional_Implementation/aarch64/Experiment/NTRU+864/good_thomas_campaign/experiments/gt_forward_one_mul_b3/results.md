# Results

Status: **passed** as an experimental Forward candidate; Production unchanged.

## Mathematical and representation gates

- `rho^2=-1-rho (mod 3457)` machine-checked.
- 8,717 exact Algorithm-10 congruence checks over the full level-1 difference range.
- All public non-identity NTT9 twist constants re-enumerated from `theta=9`.
- Twisted input union: `[-2179,2179]` from the NTT16 producer bound `[-8874,8874]`.
- New level-1 plus unchanged eta/level-2 DAG maximum magnitude: 26306.
- No signed-int16 add/sub wrap; R0 scale and physical row ordering unchanged.
- Exact signed representatives differ from M5R-B by multiples of q.  This is
  intentional and is why the local Pass-2 oracle compares modulo q.

## Assembly gates

- Slothy RA: 593 instructions, `OPTIMAL`, self-check OK, no spill.
- Slothy schedule: split heuristic full self-check OK, no spill.
- Counts: 69 `ldr`, 16 `ld1`, and 96 each of `mul/sqrdmulh/mls`.
- The 32 NTT9 twist-table loads remain two independent `ldr`s; no `ldp` experiment leaked in.
- No `orr`, coefficient store, or stack operation in the one-bank helper.
- Full dynamic instruction count: 4590, exactly 144 below M5R-B's 4734.

## Correctness and ABI

- Pass-2: 1,122 cases, 969,408 modulo-q comparisons, zero padding dependency failures.
- Full Forward: 1,254 cases, 1,083,456 comparisons against Official Neon after the exact ABI permutation.
- Public wrapper `d8–d15` preservation probe passed.
- No new coefficient memory boundary.

## Cortex-A76 PMU

Same binary, core 3, both `OBCN` and `NCBO` orders, three repetitions, 366
samples per variant overall, `get_throttled=0x0` throughout:

| Variant | kernel instructions | cycles p50 | cycles IQR |
|---|---:|---:|---:|
| Official Neon | 4028 | 4396.925575 | 0.192525 |
| M5R-B baseline | 4734 | 4668.879375 | 5.826075 |
| M5R-C one-mul B3 | 4590 | 4454.589575 | 5.211263 |

M5R-C saves 214.2898 cycles, or **4.5897%**, versus M5R-B.  It is only
57.664 cycles, or **1.3115%**, behind Official in this Forward-only benchmark.

The hard gate was “delete at least one complete Algorithm-10 multiplication
per NTT9 block.”  M5R-C deletes three per block and converts the arithmetic
reduction into a repeatable A76 cycle reduction.
