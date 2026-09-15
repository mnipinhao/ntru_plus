# P32 — split I16 producer plus batched terminal

## Decision

P32 is **rejected for production**.  It is exact, constant-time and retires
173 fewer instructions in the complete Inverse boundary, but it loses every
paired Inverse sample and every paired Decaps sample on Cortex-A76.
Production remains the P13-C/P8 inverse consumer.

## Exact data flow

The production path calls the same 667-instruction `lazy_i16` helper six times.
Every call performs one 16-point CT inverse prefix, loads 64 Q vectors from the
same composite table, computes low/high terminal forms, and scatters 128
halfwords.

P32 splits that helper at the exact preterminal state:

1. Six 190-instruction producers load all sixteen P8 Q records, run the same
   I16 prefix, then overwrite the fully consumed 256-byte block with the
   sixteen preterminal vectors.
2. One column-major consumer visits `t=0..15`.  It loads the four composite Q
   constants once, loads the six independent preterminal vectors, applies the
   exact P13-B terminal DAG to each, and uses the unchanged `UMOV+STRH`
   addresses.
3. Tail-I16 and raw-to-ternary remain unchanged.

The internal scratch remains 1,792 bytes.  Roots, R0 scale, selective resets,
the `2617 -> 21397 -> 4454` range chain, natural output order and public API do
not change.

## Static and Slothy gates

- Canonical kernel-contract and symbolic checks pass.
- Local Slothy root: `/Users/chenpinhao/slothy`; Cortex-A76 model; spilling
  disabled.
- The producer allocates without spill.  A whole-region timing solve was
  stopped after it failed to return inside the bounded run; the allocated
  producer was retained.
- Four terminal shapes (`none`, `low reset`, `high reset`, `both resets`) were
  independently timing-scheduled, then instantiated at the exact 96 public
  `(column,bank)` offsets.  `v26-v29` hold the four column constants and
  `v30-v31` hold `q` and `magic(1)`.
- Both objects assemble on macOS arm64 and Pi 5 with no symbolic-register leak
  or stack spill.

| Main-I16 work | Production | P32 | Delta |
|---|---:|---:|---:|
| executable instructions | `6 x 667 = 4002` | `6 x 190 + 2733 = 3873` | **-129** |
| composite Q loads | 384 | 64 | **-320** |
| added preterminal Q store/load | 0 | 96 / 96 | +192 instructions |
| dynamic bytes, modeled net | — | — | **-2048 bytes** |
| helper text | 2672 B reused | 760 B prefix + 10932 B terminal | **+9020 B** |

The linked wrapper also removes most of the old six-call nested-loop overhead;
PMU therefore observes exactly 173 fewer complete-Inverse instructions and one
fewer branch, rather than only the 129-instruction kernel delta.

## Correctness and security

- 64 KEM round trips and tampered-ciphertext rejection: pass.
- KAT: 100 cases; production and P32 SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Direct complete-Inverse comparison: 256/256 pass.
- Exact output, in-place alias, AAPCS preservation and complete scratch wipe:
  4,096/4,096 pass.
- Malformed transcript: both 417,216 bytes, SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
- All branches and addresses remain fixed/public.

## Raspberry Pi 5 PMU

Environment: core 3, Linux `6.18.33+rpt-rpi-2712`, `ondemand`,
`get_throttled=0x0`, 58.2 C after measurement.  Six alternating processes
produced 366 paired Inverse and 186 paired samples per KEM operation.

| Operation | Production cycles | P32 cycles | paired delta | instruction delta | P32 wins | IPC production -> P32 |
|---|---:|---:|---:|---:|---:|---:|
| Inverse-to-ternary | 4894.938 | 5004.234 | **+106.664** | -173 | 0/366 | 1.7044 -> 1.6326 |
| Decaps | 40075.550 | 40186.425 | **+111.300** | -173 | 0/186 | 2.3458 -> 2.3351 |
| Keygen control | 43092.625 | 43096.750 | +11.000 | 0 | 64/186 | unchanged work |
| Encaps control | 45004.225 | 44976.500 | -35.000 | 0 | 166/186 | unchanged work |

Inverse paired cycle-delta IQR is `[+104.821,+107.996]`; Decaps is
`[+96.525,+124.237]`.  Both hard promotion gates fail decisively.

Measured hashes: production library
`7e71af800dbcf220977d0f6344bcf92542e279edf6d64ca66de2844d2125aff0`,
P32 library `a153b23012ed2eb3579270964bafcde9c4c949f46ba1334781ce11216b5ee898`,
prefix source `f594d72a442efaebbe1e8ffb302af9cd254f6280374a38e07ad2019dbe896566`,
terminal source
`d0caf97498063121403eacb7da6130c37362b12aac4ab09d56675ec912626059`.

## Interpretation and next gate

The shared constants are real work removal, but T6 batching creates a global
phase barrier, an extra scratch round trip and a 10.9 KiB terminal body.  The
complete-Inverse IPC drop converts 173 fewer instructions into a 106.7-cycle
loss.  Another scheduling-only P32 round is not justified.

P33 should test a smaller two-bank hybrid: materialize one bank, compute the
second bank's I16 prefix, and consume both terminals while the second result is
live.  That shares constants without a six-bank synchronization point and lets
one smaller terminal body be reused three times.  It must first demonstrate a
production-like IPC model and a static win; production remains unchanged.
