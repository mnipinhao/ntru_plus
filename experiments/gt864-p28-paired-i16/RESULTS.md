# P28 — paired I16, dense tail, and routed ternary consumer

## Decision

P28 is **rejected for production**.  It passes every correctness and constant-
time gate and wins the isolated replacement boundary, but loses both complete
Inverse-to-ternary and Decaps on the Raspberry Pi 5.

Production remains the P13-C/P8 inverse consumer.

## What changed

P28 applies the P27 bank pairing to the complete consumer boundary:

- three calls to a paired main-I16 kernel replace six one-bank calls;
- six completed vector values are parked in `x5`–`x16`, so neither main nor
  tail kernel spills to the stack;
- the tail writes 96 useful lanes densely into 12 Q records;
- a final fixed route normalizes the dense records modulo 3 and emits the 108
  natural-order Q records expected by the KEM.

The local Slothy tree lacks a modeled TBL4 instruction.  The exact four-vector
route is therefore lowered to two TBL2 operations plus ORR.  This makes the
route 1,303 instructions and requires 3,456 bytes of public masks.

## Static accounting

| Region | Body instructions | Loads | Stores | Object text/data |
|---|---:|---:|---:|---:|
| paired main, one call | 840 | 108 | 32 | 3,364 B text |
| dense tail | 541 | 86 | 12 | 2,168 B text |
| normalize + route | 1,303 | 216 coefficient/mask | 108 | 5,216 B text |
| masks | — | — | — | 3,456 B read-only data |
| full P28 replacement | 4,364 | — | — | 10,748 B active text + masks |

The main and tail allocated objects contain no `sp`-relative access.  The route
also has no stack access.  The public wrapper retains the existing 1,792-byte
scratch and its complete wipe.

## Correctness and security gates

- Exact C/assembly oracle: 1,001/1,001 cases.
- KEM test: 64 round trips plus tampered-ciphertext rejection, both packages.
- KAT: 100 cases; both SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Complete malformed-ciphertext transcript: 417,216 bytes; both SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
- 4,096 inverse cases: exact output, in-place aliasing, AAPCS preservation and
  scratch wipe all pass.
- All addresses and branches remain public; no secret-dependent lookup or
  control flow was added.

## Pi 5 measurements

Environment: Raspberry Pi 5, Linux 6.18.33, GCC 14.2.0, CPU 3, `ondemand`,
`get_throttled=0x0`.  Six alternating processes were used.  SUPERCOP reference
root remains `/home/pi/supercop-20260831`.

### Isolated replacement boundary

| Metric | Baseline | P28 | Delta |
|---|---:|---:|---:|
| cycles | 3,219.750 | 3,112.469 | **-107.281 (-3.33%)** |
| instructions | 5,640.219 | 4,429.219 | **-1,211** |
| branches | 49.344 | 13.344 | **-36** |

### Complete path

| Operation | Baseline cycles | P28 cycles | paired median delta | instruction delta | branch delta |
|---|---:|---:|---:|---:|---:|
| Inverse-to-ternary | 4,894.656 | 5,040.828 | **+147.266** | -1,261 | -42 |
| Keygen | 43,095.750 | 43,121.125 | +21.125 | 0 | 0 |
| Encaps | 45,003.225 | 45,034.125 | +8.525 | 0 | 0 |
| Decaps | 40,082.550 | 40,230.350 | **+146.000** | -1,261 | -42 |

Inverse loses all 366 paired samples, with cycle-delta IQR
`[+135.715,+150.351]`.  Decaps loses all 186 paired samples, with IQR
`[+129.887,+166.175]`.  Keygen and Encaps execute no changed instructions;
their small cycle deltas are noise/control measurements.

## Interpretation

The arithmetic pairing is real: P28 retires 1,261 fewer instructions and wins
when only the replacement boundary is hot.  It does not survive the complete
consumer context.  The current route is the structural problem: it executes
216 TBL instructions, performs 216 public-mask Q loads, and adds a 5,216-byte
unrolled code body plus 3,456 bytes of masks.  That footprint and dependency
shape cost more cycles after the preceding inverse9 stage than the removed
arithmetic saves.

The important conclusion is not that pairing is impossible.  It is that the
P27 coordinate ABI cannot be materialized through this standalone TBL2 route.
Any successor must fuse terminal production with final routing, or find a much
smaller permutation network, before returning to Slothy or Pi timing.

## Updated work queue

1. Keep P13-C/P8 as production; do not promote P28.
2. Preserve P28 as evidence that paired arithmetic can win in isolation.
3. Do not reopen this layout with scheduling-only changes.
4. Reopen only if a static route eliminates most of the 1,303 route
   instructions and 216 mask loads, preferably by producing natural Q records
   directly from each paired terminal.
5. Continue the broader roadmap at the next uncompleted inverse/ToBytes gate;
   P28 adds no production change to Keygen, Encaps or Decaps.
