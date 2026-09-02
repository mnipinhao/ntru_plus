# Results

Status: **passed as an experimental candidate; Production unchanged.**

## Hard gates

- Arithmetic: three additional Algorithm-10 mulmods removed per NTT9 block;
  six removed per block relative to M5R-B.
- Proof: 26,149 Algorithm-10 congruence checks and 47,803,396 field identity
  checks; widest difference `±13074`, maximum new-node magnitude 26306.
- Slothy: 569 instructions, 143 expected cycles, `OPTIMAL`, self-check OK,
  split scheduling OK, no spill.
- Memory: 32 independent twist `ldr`s per bank retained; no new coefficient
  load/store boundary.
- Correctness: Pass-2 1,122 cases / 969,408 comparisons; full Forward 1,254
  cases / 1,083,456 comparisons; padding dependency zero.
- ABI: public wrapper preserves `d8-d15`.

## Instruction ledger

| Item | M5R-C | M5R-D | Delta |
|---|---:|---:|---:|
| one-bank instructions | 593 | 569 | -24 |
| Algorithm-10 mulmods per bank | 96 | 90 | -6 |
| mulmods per NTT9 block | 48 | 45 | -3 |
| full Forward dynamic instructions | 4590 | 4446 | -144 |

## Cortex-A76 PMU

Pi 5 core 3, same binary, `OBCN` and `NCBO`, three repetitions, 366 samples
per variant, and `get_throttled=0x0` throughout:

| Variant | Kernel instructions | Cycles p50 | Cycles IQR | IPC |
|---|---:|---:|---:|---:|
| Official Neon | 4028 | 4396.91215 | 0.178775 | 0.917690 |
| M5R-C | 4590 | 4457.45735 | 4.8936875 | 1.031306 |
| M5R-D | 4446 | 4229.9409 | 0.9943 | 1.052734 |

M5R-D improves M5R-C by **227.51645 cycles (5.1047%)** and Official by
**166.97125 cycles (3.7974%)**.  It still executes 418 more instructions than
Official, but its higher IPC turns the arithmetic simplification into a real
A76 cycle win.

The generic Slothy log parser flags the word `timeout` in Slothy's benign
configuration message.  That is a parser false positive: the complete returned
RA log explicitly reports `OPTIMAL` and self-check OK, and the scheduling log
reports `split.split_heuristic_full:OK!`.
