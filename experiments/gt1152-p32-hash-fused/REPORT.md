# P32 — M2-1: the fused fixed-size SHAKE256 kernels

Branch `neon-1152`, parent `524b7085`.  Pi 5 core 3, GCC 14.2.0.

The last large item, and the one every gate since P11 has pointed at.  Hash was
49.9% of GT's cycles.

**keygen -3.12% -> -11.36%, encaps -2.18% -> -20.57%, decaps -2.75% -> -13.96%,
the KEM -2.69% -> -15.25%.**

## 1. What NTRU+864 did, and what carries

864's P53 and P55 produced `ntruplus_hash_g_fused_aarch64` and
`ntruplus_hash_f_fused_aarch64` by adapting NTRU+768's, with anchored
replacements for the size-dependent parts.  This does the same for 1152, so the
lineage is 768 -> 864 -> 1152 and the Keccak core is untouched at each step.

Both kernels hash one domain byte followed by exactly `NTRUPLUS_POLYBYTES`, with
the whole 25-word state **live in registers**.  Three things the generic sponge
pays and these do not:

- **no state array** — no store and reload of 200 bytes per permutation;
- **no copy to prepend the domain byte** — it is folded into the first absorbed
  word with `lsl #8`, plus `orr #1` for hash_g's `0x01`, so every subsequent load
  is a `ldur` at offset `7 mod 8` and the 1728-byte message is never duplicated;
- **no length arithmetic** — the block count is a compile-time constant and the
  stage machine is a counter in a stack slot.

Both `fips202.c` files are byte-identical between 864 and 1152, so none of 864's
hash advantage came from a faster permutation; it is all in the fusion.

## 2. What is size-dependent

| | 768 | 864 | **1152** |
|---|---:|---:|---:|
| input + prefix | 1153 | 1297 | **1729** |
| full absorb blocks (rate 136) | 8 | 9 | **12** |
| tail bytes | 65 | 73 | **97** |
| hash_g output | 192 | 216 | **288** |
| squeeze blocks | 1 + 56 | 1 + 80 | **2 + 16** |

`generate_keccak.py` makes exactly five anchored edits, each asserted to match
once (or twice, where both kernels share it):

1. the tail absorb — 864 takes nine whole words then one byte into lane 9; 1152
   takes twelve then one byte into lane 12;
2. the block count in both dispatches;
3. the stage the tail hands to;
4. **hash_g's squeeze dispatch** — 1152 is the first of the three to need *two*
   full squeeze blocks, so the equality test becomes a range test and
   `Lhash_g_squeeze_first` increments the stage counter instead of assigning it;
5. hash_g's final squeeze, 80 bytes becoming 16.

Everything else, including the first-block absorb with its `7 mod 8` offsets, is
size-independent and carries unchanged.

## 3. Correctness

Differential against the generic sponge, which is the oracle:

```
4000 inputs (all-zero, all-ones, 3998 random), 1728 bytes each
  hash_f, shake256(0x00 || msg) to 32 bytes    mismatches 0
  hash_g, shake256(0x01 || msg) to 288 bytes   mismatches 0
```

Package gates on the Pi, all green: KAT sha256 `2ddfc810c4...64c3`, 64 round
trips with tampered rejection, 13,824 canonical cases, 11/11 ABI sentinel masks
zero, 288/288 baseinv, zeroization clean.

`clear_calls` falls from 26 to 23 and `clear_bytes` from 37,526 to 32,338:
hash_f and hash_g no longer allocate and wipe a 1729-byte copy of the message,
because they no longer make one.  Less secret material is duplicated, not more.

`hash_h` keeps the generic sponge in this gate.  Measured 10,687 against the
official's 10,663, unchanged.

**Correction (2026-09-18).** This gate justified leaving it alone by calling its
input "176 bytes, a single block, where the fusion has nothing to amortize".
That is wrong.  `HASH_H_INBYTES` is `N/8 + SYMBYTES` = 176, so input + prefix is
177 = one rate-136 block + a 41-byte tail, which is **two** absorb permutations;
`HASH_H_OUTBYTES` is `SYMBYTES + N/4` = 320 = two full blocks + 48, which is
**three** squeeze permutations.  `hash_h` is five permutations, not one, and the
fusion has exactly as much to amortize per permutation as it does in hash_f and
hash_g.  See the P34 entry in GT1152-ROADMAP.md.

## 4. Measured

Standalone, per call:

| | generic | fused | delta | |
|---|---:|---:|---:|---:|
| `hash_f`, 32 out | 17,754 | **11,947** | **-5,807** | 1.49x |
| `hash_g`, 288 out | 20,339 | **13,765** | **-6,574** | 1.48x |

Both larger than 864's -4,103 and -4,358, as the 33% longer input predicts.

In the KEM:

| | official | GT | was |
|---|---:|---:|---:|
| `hash_f` (2 calls) | 34,466 | **24,004** | 34,532 |
| `hash_g` | 39,627 (2 calls) | **13,800** (1 call) | 19,695 |
| `hash_g_fr0` | - | **15,184** | 20,915 |
| `hash_h` (2 calls) | 10,663 | 10,687 | 10,677 |
| **total** | **84,757** | **63,675** | +998 -> **-21,082** |

| operation | official | GT | delta | was |
|---|---:|---:|---:|---:|
| keygen | 64,056 | 56,781 | **-11.36%** | -3.12% |
| **encaps** | 59,522 | **47,278** | **-20.57%** | -2.18% |
| decaps | 52,511 | 45,181 | **-13.96%** | -2.75% |
| **total** | **176,089** | **149,240** | **-15.25%** | -2.69% |

## 5. Where this lands

NTRU+864 after its own hash campaign, from P58's formal SUPERCOP run:

| operation | 864 | **1152** |
|---|---:|---:|
| keygen | -11.41% | **-11.36%** |
| encaps | -21.05% | **-20.57%** |
| decaps | -13.06% | **-13.96%** |

Within a percentage point on every operation, which is what a campaign that
followed 864's ground should produce.

Hash is now 42.7% of GT's cycles rather than 49.9%.  A fresh SUPERCOP run is
owed; P29's -1.75% predates this and P31.

## Reproduce

```sh
python3 generate_keccak.py
gcc -O3 -march=native -I. test_hash.c hash_fixed.c fips202.c keccakf1600.S -o t && ./t
gcc -O3 -march=native -D_DEFAULT_SOURCE -I. bench.c hash_fixed.c fips202.c keccakf1600.S -o b && ./b
```
