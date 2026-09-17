# P57 results

Status: passed.

Correctness and release gates on Raspberry Pi 5:

- 64 valid KEM round trips and 64 tampered-ciphertext rejections pass.
- All eleven AAPCS64 sentinels report mask `0x00000`.
- All 10,368 noncanonical boundary cases pass.
- Zeroization reports 23 calls, 24,310 bytes, and zero uncleared bytes.
- KAT response SHA-256 remains
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Deterministic export regeneration passes.
- The checked-in SUPERCOP leaf compiles independently and passes the same
  64-case KEM/tamper test.

Paired PMU deltas, P57 minus P55/P56 production:

| Boundary | Cycles median | Cycle IQR | Instructions | Branches | Pairs |
|---|---:|---:|---:|---:|---:|
| hash_f | -0.641 | [-2.508, +2.414] | 0 | 0 | 122 |
| Keygen | -20.125 | [-38.188, +2.188] | 0 | 0 | 62 |
| Encaps | -7.975 | [-17.125, +3.088] | 0 | 0 | 62 |
| Decaps | -0.225 | [-4.725, +4.975] | 0 | 0 | 62 |

The zero instruction and branch deltas establish that the renamed production
closure preserves the executable work. Cycle movement is consistent with
measurement noise; there is no performance regression.

An initial Makefile draft added `-fomit-frame-pointer` while changing to a
single compiler invocation. That changed the KEM C wrapper allocation and
caused a real Decaps regression. Both unrelated changes were removed: P57 now
uses the original compiler policy, separate objects, and the original object
link order.
