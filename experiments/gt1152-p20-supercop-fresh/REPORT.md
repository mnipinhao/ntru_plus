# P20 — Fresh SUPERCOP measurement

Branch `neon-1152`, parent `eab636ab`.  supercop-20260831, Pi 5 core 3,
GCC 14.2.0 `-march=native -mtune=native`, goal `constbranchindex`.

The G9 record (`gt1152-p10-kem/supercop-results.json`, +28.2%) predates P12,
P13, P18 and P19 and was badly stale.  This replaces it.

## 1. What was re-run and how

Only three files changed in the package since the G9 commit `fdb1a87e` —
`pack.c`, `support.c` and the new `codec_pairs.h` — confirmed with
`git diff --name-only fdb1a87e HEAD`.  The assembly is untouched, so the
SUPERCOP leaf's `.s` files needed no reconversion; the three files were copied
into `crypto_kem/ntruplus1152/aarch64-gt1152` and test-compiled first (17
objects, no errors).

SUPERCOP caches by version/host/date and G9 ran on this same date, so the
existing `bench/pinhao/data` was archived and the cached
`crypto_kem_ntruplus1152*` objects in `work/{constbranchindex,timingleaks}/best*`
and `work/compile` removed before each run.  Two runs:

1. **all four implementations present** — the A/B at selection level, and
   detailed per-operation records for whichever SUPERCOP selects.
2. **GT isolated** (`aarch64`, `opt`, `ref` moved out of the tree, restored
   afterwards) — because SUPERCOP only produces detailed records for the
   *selected* implementation, and the official wins selection.

## 2. Selection cycles, all four implementations, one run

| implementation | best flags | cycles | G9 |
|---|---|---:|---:|
| `aarch64` (official) | -O3 | **111,351** | 111,341 |
| **`aarch64-gt1152`** | -O3 | **112,107** | 142,741 |
| `opt` | -O3 | 193,424 | 193,389 |
| `ref` | -O3 | 297,517 | 297,607 |

```
GT vs official   +756 cycles   +0.68%      (G9: +31,400, +28.2%)
```

The official moved by 10 cycles in 111,341 between the two runs, 0.009% — the
measurement is stable, and the whole change is GT's.

GT's selection figure in the isolated run was **112,074**, 0.03% from the
112,107 measured with all four present.

All sixteen `try` records carry one checksum,
`2275d102…3ad8/16659d2c…cb91`, so SUPERCOP validated the KEM byte contract for
every implementation including GT.

## 3. Per operation, stabilized quartiles

SUPERCOP's own `stq.h` definition, 96 samples per operation per side.

| operation | stat | official | GT | delta | % |
|---|---|---:|---:|---:|---:|
| keypair | q1 | 57,199 | 57,866 | +667 | **+1.17%** |
| keypair | median | 64,809 | 60,512 | -4,298 | -6.63% |
| keypair | q3 | 73,665 | 73,204 | -461 | -0.63% |
| **enc** | q1 | 58,975 | **57,929** | -1,046 | **-1.77%** |
| **enc** | median | 59,004 | **57,959** | -1,045 | **-1.77%** |
| **enc** | q3 | 60,377 | **59,304** | -1,073 | -1.78% |
| dec | q1 | 52,549 | 54,276 | +1,727 | **+3.29%** |
| dec | median | 52,573 | 54,300 | +1,727 | +3.29% |
| dec | q3 | 52,594 | 54,320 | +1,726 | +3.28% |

**Encapsulation is 1.77% faster than the official.**  Decapsulation is 3.29%
slower.  Both are flat across all three quartiles, so those figures are solid.

**Keypair must be read at q1, not the median.**  NTRU+ key generation retries
when the sampled polynomial is not invertible, so the sample is bimodal.  Bucketing
each sample by its ratio to the run's minimum:

```
official   1.0x:46  1.2x:27  1.3x:7  1.5x:8  1.6x:1  1.7x:2  1.8x:3  1.9x:1  2.4x:1
GT         1.0x:52  1.1x:5   1.2x:23 1.3x:1  1.5x:13 1.8x:1  1.9x:1
```

46 of 96 official samples and 52 of 96 GT samples land at the no-retry cost, so
the median sits at a different point of the retry distribution in each run and
moves with it.  q1 compares the no-retry mode and is the comparable statistic;
q3 is dominated by the tail in both.

## 4. Agreement with the component profiler

Two independent measurement paths, different harnesses, different statistics:

| operation | P19 profiler | SUPERCOP |
|---|---:|---:|
| keygen | +1.08% | +1.17% (q1) |
| encaps | -1.97% | -1.77% |
| decaps | +3.11% | +3.29% |
| total | +0.65% | +0.68% |

They agree to within 0.2 percentage points on every operation.  That is a real
cross-check: the profiler uses `dlopen`ed shared objects with a fixed RNG and
41 paired samples per point, SUPERCOP uses its own build, its own randomness
discipline and stabilized quartiles.

## 5. Campaign position

```
G9  (Milestone 1)   GT 142,741   official 111,341   +28.2%
P20 (now)           GT 112,107   official 111,351    +0.68%
```

The 28.2% closed to 0.68% with no change to any assembly: P12 and P13
(NEON codec and sampling), P18 (permutation in registers) and P19
(instruction-count cuts) are all C.  What remains, from P19's attribution:
baseinv +2,406, hash +985, inverse +1,134, against forward -2,618 and
serialize -1,034.

For scale, NTRU+864 stood at -3.95% before its hash campaign and reached
-11%/-21%/-13% after it.  NTRU+1152's hash is still the generic sponge.

## Reproduce

```sh
# refresh the leaf, archive bench data, clear cached objects, then
cd /home/pi/supercop-20260831 && ./do-part crypto_kem ntruplus1152
python3 extract.py data-all-impls.txt
python3 extract.py data-gt-only.txt
```

Raw data kept here: `data-all-impls.txt`, `data-gt-only.txt`, the two
`do-part` logs, and `supercop-fresh-results.json`.
