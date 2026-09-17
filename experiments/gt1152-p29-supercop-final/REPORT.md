# P29 — SUPERCOP after the assembly and scheduling work

Branch `neon-1152`, parent `d337411f`.  supercop-20260831, Pi 5 core 3,
GCC 14.2.0 `-march=native -mtune=native`, goal `constbranchindex`.

P20 measured +0.68% under SUPERCOP.  Since then: P22 (`invntt16_tail` to
assembly), P23 (`sotp_decode` in two-bit fields), P24 (D7 without a Barrett),
P26 (batch inversion split into three chains), P27 (the first SLOTHY run), and
the two scheduled `baseinv` loops.

**GT is now faster than the official under SUPERCOP's own measurement.**

## 1. Selection cycles, all four implementations, one run

| implementation | cycles | P20 | G9 |
|---|---:|---:|---:|
| **`aarch64-gt1152`** | **109,446** | 112,107 | 142,741 |
| `aarch64` (official) | 111,401 | 111,351 | 111,341 |
| `opt` | 193,469 | 193,424 | 193,389 |
| `ref` | 297,624 | 297,517 | 297,607 |

```
GT vs official   -1,955 cycles   -1.75%
```

The official has moved by 60 cycles in 111,341 across all three runs, 0.05%, so
the measurement is stable and the whole change is GT's.

```
G9   (Milestone 1)  +28.2%
P20                  +0.68%
P29                  -1.75%
```

## 2. Per operation

GT won selection this time, so the detailed records in the all-implementations
run are GT's, not the official's.  A third round was run with the official
isolated so both sides come from the same session.

| operation | stat | official | GT | delta | % |
|---|---|---:|---:|---:|---:|
| keypair | **q1** | 57,262 | **55,472** | -1,790 | **-3.13%** |
| keypair | median | 66,107 | 63,535 | -2,573 | -3.89% |
| keypair | q3 | 72,839 | 76,999 | +4,161 | +5.71% |
| **enc** | q1 | 59,016 | **57,915** | -1,101 | **-1.87%** |
| **enc** | median | 59,042 | **57,942** | -1,100 | -1.86% |
| **enc** | q3 | 60,380 | **59,497** | -883 | -1.46% |
| **dec** | q1 | 52,485 | **51,565** | -920 | **-1.75%** |
| **dec** | median | 52,499 | **51,579** | -920 | -1.75% |
| **dec** | q3 | 52,519 | **51,594** | -926 | -1.76% |

enc and dec are flat across all three quartiles.  **Keypair must still be read
at q1**, for the reason P20 established: NTRU+ key generation retries when the
sampled polynomial is not invertible, so the sample is bimodal and the median
and q3 move with a particular run's retry count.

## 3. Agreement with the component profiler

| operation | profiler | SUPERCOP |
|---|---:|---:|
| keygen | -3.09% | -3.13% (q1) |
| encaps | -1.98% | -1.87% |
| decaps | -1.67% | -1.75% |
| **total** | **-2.29%** | **-2.26%** |

Within 0.11 percentage points on every operation, and 0.03 on the total.  The
total here is the sum of the three q1 figures — 168,763 against 164,952 — not
the selection metric, which is a single aggregate measurement weighted
differently and reads -1.75%.

Two independent measurement paths agree: the profiler uses `dlopen`ed shared
objects with a fixed RNG and 41 paired samples per point, SUPERCOP its own
build, its own randomness discipline and stabilized quartiles.

## 4. What was refreshed, and the two things SUPERCOP's build does differently

`refresh_leaf.py` installs the package into the leaf.  Since P20 the package
changed `inverse.c`, `inverse16_tables.h` and `support.c`, dropped
`inverse16_tail.c` and `tail_map.h`, and gained four assembly kernels.  Two
things the package's own build does that SUPERCOP's does not, and that the
refresh has to supply:

- SUPERCOP compiles every source in the directory with its own flags, so the
  `NTRUPLUS1152_ASM_*` selectors that choose the scheduled kernels over the C
  are **prepended to the leaf's `inverse.c`** rather than passed on the command
  line.  Verified after the copy: `inverse.o` carries `basemul_rinv_kernel`,
  `baseinv_num_kernel` and `baseinv_finish_kernel` as undefined symbols, which
  is only true when the selectors are active.
- The leaf uses lowercase `.s`, which gcc assembles without the preprocessor, so
  the `#ifdef __APPLE__` aliasing becomes the leaf's existing convention of a
  second `.global` and a second label.

The leaf was test-compiled before any measurement: 20 objects, no errors, all
four kernel symbols defined.

## 5. Procedure

SUPERCOP caches by version, host and date, and all three runs share a date, so
each was preceded by archiving `bench/pinhao/data` and removing the cached
`crypto_kem_ntruplus1152*` objects.  Three rounds: all four implementations for
the selection A/B, GT isolated, official isolated.  The tree was restored after
each isolation and is intact.

Raw data kept here: `data.all-impls`, `data.gt-only`, `data.official-only`, the
three `do-part` logs, and `supercop-final.json`.
