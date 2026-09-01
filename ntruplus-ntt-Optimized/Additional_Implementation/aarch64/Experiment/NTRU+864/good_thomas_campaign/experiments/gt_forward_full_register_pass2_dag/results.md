# M5R results

M5R passes the requested feasibility and performance gate.

- Copy-free M5R-A: 620 instructions, remote Slothy RA OPTIMAL in 92.2132 s,
  no spill, selfcheck OK, and real-instruction scheduling OK.
- Pinned M5R-B: 617 instructions, remote Slothy RA OPTIMAL in 144.2395 s,
  no spill, selfcheck OK, and `split_heuristic_full:OK`.
- Integrated Pass-2: 3861 instructions versus M5O's 3960, down 99.
- Integrated full Forward: 4734 instructions versus 4825, down 91 after the
  eight-instruction public ABI cost.
- Memory: 32 meaningful coefficient loads per bank, zero coefficient stores
  inside the bank, and zero new memory boundaries.
- Correctness: 1,122 Pass-2 cases and 1,254 full Forward cases pass; the latter
  performs 1,083,456 coefficient comparisons.
- ABI: explicit seeded `d8-d15` preservation probe passes.

Pi 5 Cortex-A76 paired PMU, core 3, three repetitions, both `OBCN` and `NCBO`
orders per repetition, 61 samples per order, 20,000 calls per sample:

| variant | p50 cycles | kernel instructions | IPC |
|---|---:|---:|---:|
| Official | 4396.969375 | 4028 | 0.91768 |
| M5O baseline GT | 4695.155125 | 4825 | 1.02915 |
| M5R-B candidate GT | 4669.251475 | 4734 | 1.01537 |

M5R-B is 25.90365 cycles or 0.5517% faster than M5O.  It remains 272.2821
cycles or 6.1925% slower than Official and retains a 706-instruction gap.
Every PMU sample reports the exact static instruction count; thermal status
remained `throttled=0x0`.

The canonical log parser reports a false failure because it treats the
configuration line `Setting timeout of 14400 seconds` as a timeout event.
The raw RA logs end in `OPTIMAL` and `selfcheck:OK!`; both schedule logs end in
`split_heuristic_full:OK!`.  `audit_artifacts.py` checks these exact terminal
signals and rejects spill text.

The canonical candidate scorer returns `promote` relative to the selected M5O
replacement baseline.  That is only a within-Experiment result: the repository
promotion gate still rejects Production linkage because Official remains
faster and no full-KEM or SUPERCOP-native evidence exists for M5R.
