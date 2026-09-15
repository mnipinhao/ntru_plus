# P33 results — two-bank inverse16 terminal sharing

## Current decision

P33 is **rejected for production**.  It passes the static, no-spill and all
correctness gates, and it retires 147 fewer instructions in complete Inverse,
but the main-I16 boundary loses 132.110 cycles and complete Inverse/Decaps lose
95.297/104.150 cycles.  Production is unchanged.

## Realized data flow

For each of the three components:

1. `p33_i16_prefix` loads all sixteen Q records of half zero, executes the
   exact P13-B inverse16 prefix, and overwrites the consumed 256-byte block
   with its sixteen preterminal values.
2. `p33_i16_pair` loads all sixteen Q records of half one and executes the
   same prefix while retaining the sixteen results in registers.
3. For each `t=0..15`, the pair helper loads the four composite constants
   once, loads `A[t]`, completes/scatters A, then completes/scatters the live
   `B[t]` at the exact `+24`-byte half offset.
4. Once `B[t]` is stored its register becomes available to later columns.

The tail, natural FR0 ordering, raw-to-ternary pass, 1792-byte scratch and
complete scratch wipe are unchanged.

## Static and Slothy evidence

- Slothy code root: `/Users/chenpinhao/slothy`.
- Interpreter/dependencies: `/Users/chenpinhao/slothy_and_ra/.venv/bin/python`.
- Target model: Cortex-A76; spilling disabled.
- The prefix allocates to 17 live vector outputs (`B[0..15]` and `q`).
- A joint 69-instruction `t=0` search was stopped after it did not converge;
  the same DAG was split into A and B timing windows while the four shared
  constants and all future B states remained fixed.  All 32 windows then
  allocated and scheduled without spill.
- The generic log parser reports false `timeout`/`infeasible` signals from
  intermediate binary-search probes.  The generated physical artifacts,
  zero remaining executable symbolic operands, all 32 completed logs and
  successful assembly are the authoritative completion evidence.

| main-I16 work | Production | P33 | Delta |
|---|---:|---:|---:|
| executable instructions | `6 x 667 = 4002` | `3 x (190 + 1112) = 3906` | **-96** |
| composite Q loads | 384 | 192 | **-192** |
| added preterminal Q store/load | 0 | 48 / 48 | +96 instructions |
| reusable helper text | 2672 B | 760 B prefix + 4448 B pair | +2536 B |

The pair helper is 6484 bytes smaller than P32's 10932-byte six-bank terminal
body and has no global six-bank phase barrier.

## Local correctness

- Both allocated assembly files assemble for arm64.
- 4096/4096 complete inverse-to-ternary exact, in-place alias, AAPCS and
  scratch-wipe probes pass.
- 64 KEM round trips and tampered-ciphertext rejection cases pass.
- 100-case KAT SHA-256 is
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`,
  identical to production.
- Production and P33 malformed transcripts are byte-identical: 417216 bytes,
  SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.

## Raspberry Pi 5 paired PMU

Environment: core 3, Linux `6.18.33+rpt-rpi-2712`, `ondemand`,
`get_throttled=0x0`, 57.6 C after measurement.  Six processes produced 546
paired main-I16, 366 paired complete-Inverse and 186 paired samples per KEM
operation.

| Operation | Production cycles | P33 cycles | paired delta | instruction delta | P33 wins | IPC production → P33 |
|---|---:|---:|---:|---:|---:|---:|
| main-I16 ×6 | 2279.000 | 2411.266 | **+132.110** | -132.875 | 0/546 | 1.9604 → 1.7978 |
| Inverse-to-ternary | 4891.594 | 4983.688 | **+95.297** | -147 | 0/366 | 1.7056 → 1.6446 |
| Keygen control | 43092.750 | 43078.250 | -18.625 | 0 | 121/186 | unchanged work |
| Encaps control | 45002.725 | 44989.575 | -6.550 | 0 | 112/186 | unchanged work |
| Decaps | 40073.050 | 40184.000 | **+104.150** | -147 | 1/186 | 2.3460 → 2.3359 |

Main-I16 cycle-delta IQR is `[+129.531,+133.062]`, complete Inverse is
`[+93.156,+102.328]`, and Decaps is `[+89.687,+120.212]`.  The two required
full-path gates fail decisively.

## P33-S timing-only rescue

The first P33 allocation used separate A and B scheduling windows.  A
timing-only rescue fixed every physical register, disabled renaming and tried
to schedule each complete A+B column jointly.  `t=0..2` emitted schedules;
`t=3` did not converge inside the bounded experiment and the run was stopped.
Because the already measured candidate loses all 546 main-I16 pairs by at
least 129.531 cycles at the first quartile, unbounded solver work is not
justified.

## Conclusion

P32 and P33 now establish the same A76 economics at two batching widths:
removing repeated composite loads through a preterminal memory boundary lowers
retired instructions but lowers IPC by more, so cycles regress.  This family
should not be reopened unless a new DAG removes arithmetic or scatter/routing
work and does not materialize preterminal state.
