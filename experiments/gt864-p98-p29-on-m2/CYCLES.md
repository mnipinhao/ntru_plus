# This round in cycles, both machines, one harness

The clock witness is 500,000 dependent `ADD`s, one cycle each, so its own
duration is the cycle length: `freq = 500000 / witness_ns`.  It read **3.506
GHz** on M2 Pro (P-core ceiling is 3.504) and **2.400 GHz** on the Pi 5's
Cortex-A76.  `bench_all.c` measures every variant of this round in one process,
round-robin, min of 301 batches after a time-driven warm-up.

## Raw

| | instr | stores | M2 cyc | M2 IPC | A76 cyc | A76 IPC |
|---|---:|---:|---:|---:|---:|---:|
| `invntt16` x6, current | 3,960 | 768 | **698** | 5.67 | **2,027** | 1.95 |
| `invntt16` x6, `ST1 {v.h}[lane]` | 3,390 | 768 | 684 | 4.96 | 2,481 | 1.37 |
| `invntt16` x6, 32 `STR D` | 2,634 | 192 | 441 | 5.97 | 1,888 | 1.39 |
| `invntt16` x6, 16 `STR Q` (invalid) | 2,328 | 96 | 394 | 5.91 | 1,844 | 1.26 |
| `packed_i9` x12, current | 2,232 | 288 | **449** | 4.97 | **1,690** | 1.32 |
| `packed_i9` x12, P95 scatter | 2,916 | 864 | 756 | 3.86 | 2,501 | 1.17 |
| repack pass | 397 | 384 | 117 | 3.39 | 259 | 1.53 |
| repack pass, Slothy-scheduled | 397 | 384 | 151 | 2.63 | 280 | 1.42 |
| main+tail+ternary, production | ~5,362 | ~972 | **963** | 5.57 | **2,772** | 1.93 |
| main+tail+ternary, P29 | 4,320 | 224 | **828** | 5.22 | **3,072** | 1.41 |

`16 STR Q` is listed for reference only: every group's final register carries its
four outputs in both halves, so a whole-vector store writes half redundant data.

## Unit costs, derived

| | M2 Pro | Cortex-A76 |
|---|---:|---:|
| one instruction, store count held fixed | **0.025 cyc** | (not measurable: the substitute form costs more) |
| one store removed from `invntt16` | **0.446 cyc** | **0.241 cyc** |
| one store added to `packed_i9` | **0.533 cyc** | **1.408 cyc** |

On M2 a store costs about the same wherever it sits (1.2x).  On A76 it costs
**5.9x more to add than removing one saves** -- the removed ones were hiding in
the multiply-port shadow and the added ones are not.  That single ratio is why
every store-relocation in this family fails on A76 and works on M2.

## Nets

| design | M2 cyc | A76 cyc |
|---|---:|---:|
| P95 lane repacking (`invntt16` -257, `packed_i9` +307/+811) | **+50** | **+672** |
| free layout + repack pass (-257 / -139, +117 / +259) | **-140** | **+120** |
| **P29** (whole changed region) | **-135** | **+300** |

Against the operations: M2 decapsulation is 14,560 cycles and A76's 34,431, so
P29 is **-0.93% on M2 decapsulation and +0.87% on A76**.
