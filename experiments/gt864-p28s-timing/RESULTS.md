# P28-S — fixed-allocation Cortex-A76 timing

## Decision

P28-S is **rejected for production**.  Scheduling is effective and recovers
about 60 cycles from P28's complete Inverse regression, but P28-S still loses
to the committed P13-C/P8 production consumer in both complete Inverse and
Decaps.  Production is unchanged.

## Slothy scope

- Main and tail retain P28's fixed physical allocation and are each scheduled
  as two bounded regions with the split heuristic.
- Route is scheduled as 108 independent output windows.  Instructions never
  cross an output-store boundary.
- Renaming and spilling are disabled.
- Slothy wall times were 91.742 seconds for main, 58.732 seconds for tail, and
  73.758 seconds for route.
- Executable multisets are exact: main 841, tail 542, route 1,304 instructions
  including terminal control instructions.
- Object footprints remain 3,364 B main text, 2,168 B tail text, 5,216 B route
  text, and 3,456 B masks.  None of the three kernel objects has an
  `sp`-relative access.

This is a timing-only experiment: arithmetic, constants, ranges, coefficient
loads/stores, dense scratch, route masks and public ABI are unchanged.

## Correctness and security gates

- Exact C/assembly oracle: 1,001/1,001 cases.
- KEM: 64 round trips plus tampered-ciphertext rejection for production, P28
  and P28-S.
- KAT: all three SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Malformed-ciphertext transcript: all three SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
- 4,096 inverse-to-ternary cases pass exact output, in-place aliasing, AAPCS
  preservation and complete public scratch wipe.
- Instruction multiset, memory access sequence and fixed public control flow
  are unchanged, so P28's constant-time contract is preserved.

## Raspberry Pi 5 PMU

Environment: CPU 3, Linux Raspberry Pi 5, `ondemand`, `get_throttled=0x0`.
Six alternating processes were used.  Complete-path comparisons have 366
paired Inverse samples and 186 paired samples per KEM operation.

### Scheduling effect: P28 to P28-S

| Operation | P28 median | P28-S median | paired cycle delta | instruction delta | wins |
|---|---:|---:|---:|---:|---:|
| Isolated replacement | 3,117.360 | 3,046.344 | about -70.7 across runs | 0 | 540/540 vs own baseline |
| Complete Inverse-to-ternary | 5,029.422 | 4,969.266 | **-60.313** | 0 | 366/366 |
| Decaps | 40,226.325 | 40,175.850 | **-49.250** | 0 | 186/186 |

The complete Inverse IPC rises from approximately `7082.125/5029.422 = 1.408`
to `7082.125/4969.266 = 1.425`.  Scheduling therefore has a real, stable
effect without changing retired work.

### Promotion comparison: production to P28-S

| Operation | Production median | P28-S median | paired cycle delta | instruction delta | wins |
|---|---:|---:|---:|---:|---:|
| Complete Inverse-to-ternary | 4,893.992 | 4,974.938 | **+83.875** | -1,261 | 0/366 |
| Decaps | 40,075.475 | 40,166.550 | **+96.250** | -1,261 | 0/186 |
| Keygen control | 43,088.375 | 43,122.250 | +29.625 | 0 | 26/186 |
| Encaps control | 45,031.175 | 45,013.900 | -20.700 | 0 | 137/186 |

Production complete-Inverse IPC is approximately
`8343.125/4893.992 = 1.705`.  P28-S retires 1,261 fewer instructions, but its
TBL2/mask-load routing and dependency shape still sustain much lower IPC.
Keygen and Encaps execute none of the changed code; their small deltas are
controls/noise and are not optimization claims.

## Interpretation and next gate

P28-S recovers roughly 41% of the historical 147.266-cycle P28 regression.  A
timing-only successor cannot close the remaining gap: the unchanged standalone
route still contains 216 TBL operations, 216 public-mask loads, 5,216 bytes of
route text and 3,456 bytes of masks.

The P28 family should remain archived evidence.  Reopen it only for a new DAG
that removes most of the standalone route—preferably by producing natural
ternary Q records directly from paired terminal values.  Do not spend another
round scheduling the same instruction multiset.
