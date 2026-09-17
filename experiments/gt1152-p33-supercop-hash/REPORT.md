# P33 — SUPERCOP after the hash campaign

Branch `neon-1152`, parent `26939b81`.  supercop-20260831, Pi 5 core 3,
GCC 14.2.0 `-march=native -mtune=native`, goal `constbranchindex`.

P29 measured -1.75%, before P30 (`frombytes`), P31 (D7 withdrawn) and P32 (the
fused hash).

**GT 92,079 against the official's 111,403: -17.35%.**

## 1. Selection cycles, all four implementations, one run

| implementation | cycles | P29 | P20 | G9 |
|---|---:|---:|---:|---:|
| **`aarch64-gt1152`** | **92,079** | 109,446 | 112,107 | 142,741 |
| `aarch64` (official) | 111,403 | 111,401 | 111,351 | 111,341 |
| `opt` | 193,359 | 193,469 | 193,424 | 193,389 |
| `ref` | 297,704 | 297,624 | 297,517 | 297,607 |

```
GT vs official   -19,324 cycles   -17.35%
```

The official has moved by 62 cycles in 111,341 across all four runs, 0.06%.  The
campaign reads

```
G9  (Milestone 1)  +28.2%
P20                 +0.68%
P29                 -1.75%
P33                -17.35%
```

All sixteen `try` records carry SUPERCOP's own `ntruplus1152` checksum
`2275d102…3ad8`, so the KEM byte contract is validated for every implementation.

## 2. Per operation

GT wins selection, so the all-implementations run's detailed records are GT's; a
third round with the official isolated gives both sides from the same session.

| operation | stat | official | GT | delta | % |
|---|---|---:|---:|---:|---:|
| keypair | **q1** | 57,240 | **50,301** | -6,940 | **-12.12%** |
| keypair | median | 62,847 | 52,439 | -10,408 | -16.56% |
| keypair | q3 | 73,833 | 65,018 | -8,815 | -11.94% |
| **enc** | q1 | 58,992 | **46,964** | -12,028 | **-20.39%** |
| **enc** | median | 59,021 | **46,984** | -12,037 | -20.39% |
| **enc** | q3 | 60,294 | **48,513** | -11,781 | -19.54% |
| **dec** | q1 | 52,469 | **45,243** | -7,226 | **-13.77%** |
| **dec** | median | 52,482 | **45,258** | -7,223 | -13.76% |
| **dec** | q3 | 52,496 | **45,271** | -7,225 | -13.76% |

For the first time **every keypair quartile is negative too**.  Keypair is still
read at q1 for P20's reason — keygen retries on a non-invertible sample, so the
median and q3 move with a run's retry count — but the hash saving is now large
enough to dominate that spread.

## 3. Agreement with the component profiler

| operation | profiler | SUPERCOP |
|---|---:|---:|
| keygen | -11.36% | -12.12% (q1) |
| encaps | -20.57% | -20.39% |
| decaps | -13.96% | -13.77% |
| **total** | **-15.25%** | **-15.53%** |

Within 0.28 percentage points on the total and under 0.8 on every operation.
That total is the sum of the three q1 figures, 168,701 against 142,507, not the
selection metric, which is a single aggregate weighted differently and reads
-17.35%.

## 4. Against NTRU+864

864 after its own hash campaign, from P58's formal SUPERCOP run:

| operation | 864 | **1152** |
|---|---:|---:|
| keygen | -11.41% | **-12.12%** |
| encaps | -21.05% | **-20.39%** |
| decaps | -13.06% | **-13.77%** |

Within a percentage point on every operation, and ahead of 864 on keygen and
decapsulation.

## 5. Procedure

`refresh_leaf.py` installed the nine files that changed since P29.  One needed
handling the others did not: `keccakf1600.S` is the only source with live
preprocessor branches (`__APPLE__`), and the leaf uses lowercase `.s`, which gcc
assembles without the preprocessor — so it is expanded with
`gcc -E -P -x assembler-with-cpp` **on the target**, and the result asserted to
contain no directive, rather than pattern-matched here.

The leaf was test-compiled before any measurement: 22 objects, no errors, the
three `NTRUPLUS1152_ASM_*` selectors active in `inverse.o`, and `symmetric.o`
referencing both fused hashes that `keccakf1600.o` defines.

SUPERCOP caches by version, host and date, and all four runs to date share a
date, so each round archived `bench/pinhao/data` and removed the cached
`crypto_kem_ntruplus1152*` objects first.  Three rounds; the tree was restored
after each isolation and is intact.

Raw data kept here: `data.all-impls`, `data.gt-only`, `data.official-only`, the
three `do-part` logs, and `supercop-hash.json`.
