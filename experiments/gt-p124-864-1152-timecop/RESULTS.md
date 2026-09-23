# P124 — 864/1152: TIMECOP, scratch ownership, declassify

SUPERCOP 20260831 on the Pi 5, system valgrind 3.24.0 + `libc6-dbg`,
`timecop.sh` (one implementation at a time), four gcc levels.

| leaf | TIMECOP=1 | TIMECOP=256 | where it fails |
|---|---|---|---|
| 864 GT before (903b516f) | fail | | Decaps `poly_frombytes(sk)` branch; BaseInv `cbnz` (`inverse.S`) |
| 864 GT after | pass x4 | pass x4 | |
| 864 Official `aarch64` | fail | | `poly_fqinv_batch` |
| 1152 GT before | fail | | Decaps `poly_frombytes(sk)` branch; BaseInv `inverse.c:294` |
| 1152 GT after | pass x4 | pass x4 | |
| 1152 Official `aarch64` | fail | | `poly_fqinv_batch` |

SUPERCOP's functional check passes in every run (`try ... ok`, checksums
`b0cdac76...` and `2275d102...`).

## Changes
- the inverse's scratch comes from `kem.c`'s `io` union over `buf1`/`buf3`,
  cleared with them;
- both status bits are declassified as Official does (`ntruplus_declassify` in
  `secure_clear.h`, `declassify_poly_frombytes`, keygen retry);
- 864 BaseInv is branch-free (zero the running inverses after the inversion);
- 1152 BaseInv declassifies and keeps its early exit.

## Why 1152 keeps the early exit
A branch-free 1152 BaseInv cost keygen +600 cycles on A76 (+1.1%), although
BaseInv itself was +4 cycles on an invertible input.  `failrate.c`: 29.6% of f
and 27.4% of g candidates are non-invertible, 0.80 failed BaseInv calls per
keygen, and each failure now ran the full inversion (~710 cycles).  864's
candidates never failed in 4,000 tries, so it is branch-free at no cost.

## Timing (min of 400 blocks x 100, deterministic randombytes)

| | A76 keygen / enc / dec, cycles | M2 keygen / enc / dec, ns |
|---|---|---|
| 864 before | 36,722 / 35,812 / 34,089 | 4,168 / 4,751 / 3,876 |
| 864 after | 36,723 / 35,797 / 34,092 | 4,176 / 4,750 / 3,870 |
| 1152 before | 54,692 / 46,727 / 43,509 | 6,261 / 6,219 / 4,991 |
| 1152 after | 54,686 / 46,755 / 43,476 | 6,296 / 6,219 / 4,985 |

All within run-to-run noise except 864 keygen on M2 (+0.2%).  M2 keygen for
1152 moves by +-100 ns with code layout alone (five `nop`s moved it by as much).
