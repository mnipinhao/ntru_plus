# P40 — Inverse9-to-I16 phase ABI

P40 is **rejected**. Production remains P35.

## Exact candidate

The production inverse9 terminal constant factors exactly as

```text
k(top,column,row) = k(top,0,row) * 2863^(column*row) mod 3457.
```

`2863` has order 144. P40 deletes all nine terminal Algorithm-10 products
from each inverse9 call, absorbs the geometric column factor into a twisted
radix-2 I16 table, and composes `k(top,0,row)` into the existing P13 terminal
table. It changes only the private inverse9-to-I16 representation.

The exact machine audit checked 288 terminal-factor contexts and 336 complete
I16 basis vectors. Signed-int16 peaks are 28135/21889/19268 for main row half
0, main row half 1 and tail. Only tail column 6 low requires a terminal
`b=1` reset to stay inside P8's accepted radius 5185. There are no new
coefficient loads, stores, scratch bytes or memory passes.

The static dynamic ledger predicted 136 fewer instructions per complete
Inverse: inverse9 saves 540, six main calls add 396, tail adds 56, and the
wrapper saves 48. Pi PMU observed 137 fewer retired instructions.

## Slothy and physical gates

The first I16 DAG loaded all level constants before consuming them and exceeded
the 32-vector live frontier. Reordering each public `(b,bhat)` load immediately
before all butterflies that consume it preserves the exact DAG and instruction
count while reducing constant liveness to one pair.

Using `/Users/chenpinhao/slothy` with the configured external virtualenv:

- inverse9: 139 instructions, no-spill RA `OPTIMAL`, selfcheck `OK`;
- main I16: 723 instructions, no-spill RA `OPTIMAL`, selfcheck `OK`;
- tail I16: 645 instructions, no-spill RA `OPTIMAL`, selfcheck `OK`;
- all three fixed allocations completed bounded Cortex-A76 timing windows;
- all three scheduled sources assemble as arm64 objects.

## Pi 5 correctness

- Both packages pass `test_kem`.
- Both 100-case KAT files have SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Both malformed transcripts are byte-identical: 417216 bytes, SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
- Exhaustive 9155-value raw conversion and 1024 complete
  exact/alias/AAPCS/wipe cases pass.

## Paired Pi 5 PMU

Six balanced processes ran on Cortex-A76 core 3 with no throttling.

| Boundary | P35 baseline | P40 | Cycle delta | Instruction delta |
|---|---:|---:|---:|---:|
| Inverse-to-ternary | 4753.867 | 4975.375 | +221.508 (+4.66%) | -137 |
| Keygen | 43089.500 | 42981.000 | -108.500 noise | 0 |
| Encaps | 45005.650 | 45015.975 | +10.325 noise | 0 |
| Decaps | 39917.525 | 40137.050 | +219.525 (+0.55%) | -137 |

Inverse IPC falls from about 1.739 to 1.634. The terminal work was not removed
economically: nine products per inverse9 block became products on every I16
butterfly right branch, with deeper multiply dependencies and more varied table
loads. Fewer instructions therefore do not translate into fewer A76 cycles.

P40 is kept as a proved experimental ABI and negative cost result. It must not
be promoted or combined into production. The next optimization should return
to the remaining measured positive boundary, Full ToBytes, and must satisfy the
existing routing-DAG reopen threshold before Slothy.
