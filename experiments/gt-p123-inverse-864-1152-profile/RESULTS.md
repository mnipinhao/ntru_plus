# P123 — 864/1152 inverse: where the cycles go (measurement only)

The complete inverse-to-ternary as `kem.c` calls it, against SUPERCOP 20260831's
Official `poly_invntt_scale` + `poly_crepmod3` (symbols renamed `o_*`).  GT trees
at `97ef2d6b`.  `build.sh` builds either tree from its Makefile source list.

## Totals (reproduce P111 exactly)

| set | M2 GT | M2 Off | x | A76 GT | A76 Off | x |
|---|---:|---:|---:|---:|---:|---:|
| 864 | 350.1 ns / 1,221 cyc | 298.3 / 1,041 | 1.174 | 4,614 cyc | 4,577 | 1.008 |
| 1152 | 419.8 / 1,471 | 405.3 / 1,420 | 1.036 | 5,486 | 6,231 | 0.880 |

## Machine models (measured, `ubench.c`)

A76: Q-form `mul` / `sqrdmulh` / `mls` issue once per 2 cycles (V0 only);
`add` / `trn1` twice per cycle.  **A76 floor = 2 x multiplies.**
M2: 4 SIMD ops per cycle, multiplies included.  **M2 floor = SIMD ops / 4.**

## Dynamic instruction mix (callgrind, `cg.sh`, per call)

| | instrs | SIMD ALU | mul+sqrdmulh+mls | ext | ins/lane | ld | st |
|---|---:|---:|---:|---:|---:|---:|---:|
| 864 GT | 6,446 | 4,136 | 1,999 | 224 | 198 | 842 | 460 |
| 864 Off | 4,612 | 4,034 | 2,178 | 0 | 0 | 257 | 176 |
| 1152 GT | 8,186 | 5,422 | 2,557 | 288 | 0 | 1,398 | 624 |
| 1152 Off | 6,018 | 5,378 | 2,904 | 0 | 0 | 250 | 221 |

GT does 8-12% fewer multiplies than Official and about the same SIMD ALU work;
it loses on everything around the arithmetic.

## A76 per function (perf sampling, `perf.sh`; cycles = share x total)

| 864 GT | cycles | mul floor | over |
|---|---:|---:|---:|
| packed_i9 | 1,659 | 1,368 | **+291** |
| p28_main | 1,219 | 1,224 | 0 |
| invntt16_paired | 694 | 636 | +58 |
| 14 tail_direct pieces + driver | ~500 | ~340 | **+160** |
| **total** | 4,614 | 3,998 | **+616** (Official: +221) |

| 1152 GT | cycles | mul floor | over |
|---|---:|---:|---:|
| invntt16 | 2,459 | 2,416 | 0 |
| packed_i9 | 1,790 | 1,824 | 0 |
| crepmod3 pass | 573 | 576 | 0 |
| invntt16_tail | 298 | 298 | 0 |
| p65_rebase | 284 | 0 | **+284** |
| **total** | 5,486 | 5,114 | **+372** (Official: +423) |

## Reading

- **864, both machines:** the multiply advantage (-358 A76 cycles) is eaten by
  overhead in `packed_i9` (192 single-lane `st1`, 132 scalar, 84 `umov`) and the
  14 tail pieces.  `p28_main` sits on its floor on A76; on M2 its 192 `ext` +
  114 `ins` cost ~75 cycles.  Same diagnosis as memory `inverse-864-store-bound`:
  the scatter stores are the M2 problem.
- **1152:** everything except `p65_rebase` is on the A76 floor.  The rebase is
  432 permutes + 74 scalar with no arithmetic: 284 A76 cycles and ~110 M2 cycles
  (> the whole +51 M2 deficit).  Folding it into the producer's stores (the
  768 lesson: redesign basemul + inverse together) removes it on both machines.
- **1152 crepmod3 pass:** its multiply pair is the mod-3 step and must stay; the
  centering (`cmgt`/`add`/`sub`) is needed because the last stage ends in a
  Montgomery multiply, range (-q,q).  Fusing saves only the 144 ld + 144 st and
  the loop, i.e. M2 slots, not A76 cycles.
