# P40 — SUPERCOP after the portable sponge

Branch `neon-1152`, parent `2e40a6d9`.  supercop-20260831, Pi 5 core 3,
GCC 14.2.0 `-march=native -mtune=native`, goal `constbranchindex`.

P33 measured -17.35%, before the hash work was undone and redone the other
way: the hand-written fused sponges were removed in favour of a portable
`shake256_prefixed` over the assembly permutation, which is how mldsa-native
and mlkem-native are arranged.

**GT 90,942 against the official's 111,441: -18.39%.**

## 1. Selection cycles, all four implementations, one run

| implementation | cycles | P33 | P29 | P20 | G9 |
|---|---:|---:|---:|---:|---:|
| **`aarch64-gt1152`** | **90,942** | 92,079 | 109,446 | 112,107 | 142,741 |
| `aarch64` (official) | 111,441 | 111,403 | 111,401 | 111,351 | 111,341 |
| `opt` | 193,544 | 193,359 | 193,469 | 193,424 | 193,389 |
| `ref` | 297,636 | 297,704 | 297,624 | 297,517 | 297,607 |

```
GT vs official   -20,499 cycles   -18.39%
GT vs P33        - 1,137 cycles   - 1.23%
```

The official moved 38 cycles in 111,403, 0.03%, which is the run-to-run
control.  The GT delta agrees with the direct `perf_event` measurement of the
same change on the same host: 140,914 -> 139,263 for the q1 sum, -1.2%.

SUPERCOP accepted the byte contract: the `try` verdict is `ok` against
checksum `2275d10293...a317cb91`, the same one P33 recorded, so the KEM output
is unchanged.

## 2. Stabilized quartiles, `aarch64-gt1152`, 3 runs x 32 samples

| operation | q1 | median | q3 |
|---|---:|---:|---:|
| keypair | 48,610 | 55,837 | 65,145 |
| encaps | 46,549 | 46,575 | 48,143 |
| decaps | 44,440 | 44,459 | 44,481 |
| **q1 sum** | **139,599** | | |

keypair's spread is the rejection loop, not noise in the measurement: encaps
and decaps sit inside 0.1% of their medians.

## 3. Where this sits against P35

P35 measured `hash_h` at 5,458 cycles and found the cause: `fips202.c` never
called the assembly permutation, so the generic sponge ran the portable C body
at 1,365 cycles a permutation against 927 for the assembly one.  It estimated a
fused `hash_h` at 3,653 and that "a 25-line asm-permutation sponge captures
76.3% of it".

That sponge is what shipped, as `shake256_prefixed`, and the routing bug P35
named is fixed:

| NTRU+1152 `hash_h` | cycles |
|---|---:|
| generic, as P35 measured it | 5,458 |
| prefixed sponge, portable C permutation | 4,994 |
| **prefixed sponge, assembly permutation** | **3,929** |
| P35's estimate for a fused kernel | 3,653 |

The portable route captures 84.7% of what fusion would have given, against
P35's own 76.3% estimate.  A fused kernel would still be 276 cycles ahead on
this one call; that is the price of not carrying twelve of them.

## 4. What moved since P33

The change is not one optimization but a reversal plus three repairs, and the
net is a gain:

  * the fused fixed-size sponges are gone, which costs about 4% of hash_f and
    hash_g on this core -- measured directly at 9,200 -> 9,575 and
    10,123 -> 10,560 cycles;
  * `fips202.c`'s byte-at-a-time `load64`/`store64` became single unaligned
    accesses, which is worth more than the fused kernels recovered;
  * `hash_h` stopped building `0x02 || msg` and stopped routing the shared
    secret through the generic sponge's malloc'd state;
  * and the AArch64 permutation selection stopped falling through to the
    portable C body, which alone took hash_h from 3,791 to 2,991 cycles.

The last item is why this is a gain rather than the 0.85% loss NTRU+768 took
from the same removal: NTRU+768 already routed to the assembly permutation, so
it had no compensating repair available.

## 5. What this run does not measure

The v8.4-A SHA3 backend added in `2e40a6d9` (P39).  This host's Cortex-A76 ships
without FEAT_SHA3, so `keccakf1600_v84a.S` compiles to nothing here and the
leaf omits it entirely -- see the note in `refresh_leaf.py`.  On an Apple M2
Pro the same backend takes the KEM from 29,083ns to 18,083ns, -37.8%, but that
is a different machine and a different measurement harness; it is not
comparable to these cycles and is not claimed here.

## 6. Reproduce

```sh
python3 refresh_leaf.py /path/to/experiments/gt1152-p10-kem
ssh pi@... 'cd ~/supercop-20260831 && taskset -c 3 ./do-part crypto_kem ntruplus1152'
scp pi@...:~/supercop-20260831/bench/pinhao/data data.p40
python3 extract.py data.p40
```

`data.p33` is P33's database, kept for the side-by-side above.
