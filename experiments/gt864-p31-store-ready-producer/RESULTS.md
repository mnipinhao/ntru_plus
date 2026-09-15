# P31 — store-ready producer DAG

## Decision

P31 is **rejected for production**.  It proves that pair2 can emit rows 0--3
before pair1 completes and that pair1 can consume only a retained B2-high D
stream, but this dependency shape is slower than both P29 and the frozen
P13-C/P8 production inverse.  Production is unchanged.

## Exact data flow

1. The unchanged P28 paired helper produces only bank0 Q records.
2. The P31 pair2 helper computes bank2.  After each low/high result, it moves
   the normalized B2 Q into fixed `v2`, normalizes the matching bank0 Q into
   `v0`, derives B0-high in `v1`, and stores rows 0--3 with full `ST3.4h`.
   B2-high is retained as one dense D stream.
3. The P31 pair1 helper computes bank1, loads the retained B2-high D into
   `v2`, places B1-low/B1-high in `v0/v1`, and stores rows 4--7 with full
   `ST3.4h`.
4. The unchanged P29 tail emits row 8.

There is no lane `ST3`, coefficient spill, or secret-dependent address.  The
candidate removes 32 Q loads and 32 Q stores, equal to 1,536 bytes of
coefficient scratch traffic.  It still needs 32 D stores and 32 D loads for
the B2-high handoff.

## Correctness/debugging gate

The first assembled candidate exposed two register-contract bugs before
timing:

- Slothy could return pair2 B2 in `v0`, after which fixed-v0 B0 normalization
  overwrote it.  Moving the already-required B2 copy before B0 reuse fixes
  this without adding an instruction or memory boundary.
- constant setup used `w8`, but `x8` parked the high half of the `t=8` NTT16
  state.  Using the dead duplicate pointer register `w3` fixes the resulting
  t=8-only mismatches.

Final gates on Pi 5:

- 64 full KEM round trips plus tampered-ciphertext rejection: pass.
- production/P31 complete inverse exact comparison: 256/256 pass.
- each of six PMU processes independently passed 24 valid KEM, 24 tampered
  ciphertext, 256 exact inverse, and 256 in-place alias cases.

## Static and object audit

The dynamic kernel instruction sum is 4,337 for P31 versus 4,180 for P29,
or **+157 instructions** before the two-wrapper-instruction difference seen
by PMU.  The important opcode deltas are:

| Opcode | P31 minus P29 |
|---|---:|
| `ldr` | -32 |
| `str` | -32 |
| `add` | +64 |
| `orr` | +64 |
| `ins` | +32 |
| `umov` | +20 |
| `dup` | +23 |
| `movi` | +13 |

The extra moves are the cost of keeping two transforms plus four
normalization constants live while producing a fixed consecutive `v0-v2`
store triple.  Pi 5 object text sizes are 3,364 bytes (pair0), 6,000 bytes
(pair2), 4,848 bytes (pair1), and 3,136 bytes (tail).  Slothy allocated both
producer kernels and all bounded windows with spills disabled.

## Raspberry Pi 5 paired PMU

Environment: Cortex-A76 core 3, Linux `6.18.33+rpt-rpi-2712`, `ondemand`,
`get_throttled=0x0`.  Six alternating processes produced 366 paired complete
inverse samples and 186 paired samples per KEM operation.

| Comparison | Operation | Baseline cycles | P31 cycles | paired delta | instruction delta | P31 IPC |
|---|---|---:|---:|---:|---:|---:|
| P29 → P31 | complete inverse-to-ternary | 4,967.812 | 5,311.485 | **+343.508** | +159 | 1.3273 |
| P29 → P31 | Decaps | 40,163.550 | 40,525.350 | **+344.275** | +159 | 2.2879 |
| Production → P31 | complete inverse-to-ternary | 4,894.219 | 5,314.281 | **+418.617** | -1,293 | 1.3266 |
| Production → P31 | Decaps | 40,077.625 | 40,519.625 | **+439.000** | -1,293 | 2.2882 |

Keygen and Encaps are controls: this inverse path is not called there.  Their
instruction deltas are exactly zero; observed cycle medians are noise and do
not affect the decision.

P31 loses every one of the 366 paired isolated-inverse samples against both
P29 and production.  Removing scratch traffic did not compensate for its
longer, more serialized producer/store DAG.

## Updated optimization queue

1. Keep P13-C/P8 as production and P5 as the production ToBytes baseline.
2. Close P31; do not spend a Slothy timing-scheduling round on the unchanged
   arithmetic graph.  The measured object is already structurally dominated.
3. The next inverse experiment must reduce arithmetic/move work before
   routing.  A reopen candidate must remove the `v0-v2` bridge/parking tax or
   complete one store-ready triple from a smaller producer state; merely
   deleting additional scratch bytes is insufficient.
4. Keep raw-Inverse-to-ternary/independent `center864` elimination ahead of a
   new ToBytes routing search unless a static ToBytes DAG first clears the
   previously established 829-instruction/101-read threshold.
