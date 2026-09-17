# P26 — `baseinv`: three independent chains

Branch `neon-1152`, parent `1319b2fd`.  Pi 5 core 3, GCC 14.2.0.

P25 measured `baseinv`'s batch inversion at 1,928 cycles of strictly serial
work: a 35-step `fqmul` prefix chain, `fqinv`'s addition chain, then 35 recover
steps each carrying `inv = fqmul(inv, di)`.  One vector in flight, multiply pipe
idle.

**1,928 -> 1,191.  `poly_baseinv` went from +2,397 to +850, keygen from +1.09%
to -1.65%, and the KEM from -0.53% to -1.55%.  All three operations now beat the
official.**

## 1. The split is the same algorithm, one level up

Split the 36 groups into K chains of 36/K.  Each chain builds its own prefix
product; the K chain products are then batch-inverted **by the identical
routine**, and each chain recovers independently.

Correct by associativity alone, and the Montgomery bookkeeping is unchanged:

```
chain c product  P_c = (prod of its 36/K values) * R^-(M-1)
cpre[K-1]        = P_0...P_(K-1) * R^-(K-1)
                 = (prod of all 36) * R^-(K(M-1) + K-1)
                 = (prod of all 36) * R^-(KM-1)
```

which is **exactly** what the single chain fed to `fqinv`, so `fqinv` sees the
same value in the same representation.  The inner inversion then yields
`ip[c] = P_c^-1 * R^-m`, which is precisely the initial carry each chain's
recover loop needs.  **No range and no representation changes, so no bound is
re-derived.**

The non-invertibility test moves from `prefix[35]` to `cpre[K-1]`, which is the
same product.  It stays exact: a residue of 0 has only one representative in
(-q, q), so `vminvq_u16(...) == 0` detects it whatever the multiplication order.

Serial depth is `2(36/K - 1) + 2(K - 1)` against 70.

## 2. Measured, and why the outputs differ

| K | chain length | serial depth | cycles |
|---|---:|---:|---:|
| 1 (baseline) | 36 | 70 | ~6,550 |
| 2 | 18 | 36 | 5,904 |
| **3** | 12 | 26 | **5,793** |
| 4 | 9 | 22 | 5,792 |
| 6 | 6 | 20 | 5,813 |

K = 3 and K = 4 are tied within run-to-run noise; K = 3 was taken, matching
NTRU+864's documented 12x3 decomposition.

**The differential needed correcting, not the code.**  A byte comparison against
the serial version reports mismatches on 1.5-2.7% of trials, rising with K.  They
are all **congruences**: `montgomery_reduce`'s output lies in (-q, q), which is
not a unique representative — 100 and -3357 are both in range and both
congruent — so a different multiplication order legitimately lands on a
different one.  Checked properly:

```
4000 trials (1,909 invertible, 2,091 non-invertible, one leaf forced singular)
  real mismatches                                    0
  congruent, different representative      59/85/94/106  for K = 2/3/4/6
```

Downstream this is immaterial: the consumer reduces mod q, and both
representatives satisfy the same |x| < q contract.  The KAT confirms it byte for
byte.

## 3. Phases, before and after

| phase | before | after |
|---|---:|---:|
| numerator loop, 36 groups | 3,783 | 3,711 |
| **prefix + inversion + recover** | **1,928** | **1,191** |
| finish loop, 36 groups | 1,087 | 1,095 |

Only the serial phase moves, by 737 cycles, as designed.

## 4. What is left is scheduling

| phase | V0 floor | measured | utilisation |
|---|---:|---:|---:|
| numerator | 2,952 | 3,711 | 79% |
| finish | 864 | 1,095 | 79% |

Unrolling does not reach it.  At 2, 3 and 4 groups per iteration, and with
`-funroll-loops`, the result lands between 5,751 and 5,783 against 5,793 — 20 to
40 cycles, run-to-run noise.  The remaining ~990 cycles are a genuine scheduling
problem, the same class as `basemul_rinv`'s 503, and belong to M2-2.

## 5. Correctness

Package gates on the Pi, all green, including the 288/288 non-invertibility
sweep which exercises the new chain structure's failure branch:

```
KAT sha256  2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3
test_kem            64 round trips + tampered rejection
test_canonical      cases=13824 failures=0
test_abi            11/11 sentinel masks 0x00000
test_baseinv_fail   288/288 reject, clear, alias-clear
test_zeroization    clear_calls=26 clear_bytes=37526 nonzero_after=0
```

## 6. Where the campaign stands

| operation | official | GT | delta | was |
|---|---:|---:|---:|---:|
| **keygen** | 64,074 | **63,020** | **-1.65%** | +1.09% |
| **encaps** | 59,533 | **58,316** | **-2.05%** | -2.03% |
| **decaps** | 52,492 | **52,039** | **-0.86%** | -0.80% |
| **total** | **176,100** | **173,374** | **-1.55%** | -0.53% |

`poly_baseinv` is 5,722 per call against the official's 5,297, +850 over two
calls, down from +2,397.

**Every operation now beats the official, with the hash still the generic
sponge.**  For scale, NTRU+864 stood at -3.95% before its hash campaign and
reached -11%/-21%/-13% after it.

Remaining: hash +902 (M2-1), `baseinv` ~990 and `basemul_rinv` ~503 of
scheduling (M2-2), `frombytes` +659 structural, `inverse` level with ~1,200 of
absolute headroom.

## Reproduce

```sh
python3 patch.py K inverse.c out.c
gcc -O3 -march=native -D_DEFAULT_SOURCE -I. check.c out.c ref.c -o c && ./c
```
