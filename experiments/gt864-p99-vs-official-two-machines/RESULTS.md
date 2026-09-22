# P99 — GT against Official with the hash removed, both machines, in cycles

P92 decomposed 864's decapsulation kernel by kernel on M2 and found GT's
arithmetic **losing**.  This runs the same harness on Cortex-A76 and reports
cycles, so the two machines can be put side by side.  Official is SUPERCOP's
`crypto_kem/ntruplus864/aarch64`, renamed and linked into the same binary; the
clock witness (500,000 dependent `ADD`s) supplies the frequency.

M2 Pro 3.504 GHz, Cortex-A76 2.400 GHz.  Cycles per call.

| kernel | calls | GT A76 | Off A76 | ratio | GT M2 | Off M2 | ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| frombytes | 3 | 708 | 731 | **0.97** | 286 | 275 | 1.04 |
| basemul_rinv / basemul_scale | 1 | 1,753 | 1,738 | 1.01 | 488 | 438 | 1.12 |
| **invntt (+crepmod3)** | 1 | **4,466** | **4,669** | **0.96** | **1,416** | **1,111** | **1.27** |
| ntt | 2 | 3,378 | 3,854 | **0.88** | 851 | 908 | **0.94** |
| sub | 1 | 199 | 196 | 1.02 | 87 | 85 | 1.02 |
| basemul | 1 | 2,156 | 2,418 | **0.89** | 464 | 530 | **0.87** |
| tobytes_small | 1 | 620 | 1,084 | **0.57** | 244 | 274 | **0.89** |
| tobytes (full) | 1 | 1,157 | 1,084 | 1.07 | 340 | 274 | 1.24 |
| sotp_decode | 1 | 370 | 388 | **0.95** | 160 | 162 | 0.99 |
| cbd1 | 1 | 367 | 377 | **0.97** | 151 | 141 | 1.07 |
| verify | 1 | 168 | 168 | 1.00 | 75 | 75 | 1.00 |
| **total** | | **20,135** | **22,025** | **0.914** | **5,985** | **5,729** | **1.045** |

**The sign flips.  GT's decapsulation arithmetic is 8.6% faster than Official's
on A76 and 4.5% slower on M2.**

Official has no `tobytes_small`; that row compares GT's specialised path against
Official's general one on both sides.

## Why: the two machines extract different amounts of width

Cycle ratio A76/M2 is how much more parallelism the wider machine finds in the
same kernel -- clock is already divided out.

| kernel | GT | Official |
|---|---:|---:|
| **invntt** | **3.15** | **4.20** |
| ntt | 3.97 | 4.24 |
| basemul | 4.65 | 4.56 |
| tobytes (full) | 3.40 | 3.96 |
| frombytes | 2.48 | 2.66 |
| **whole decapsulation** | **3.36** | **3.84** |

Official's inverse finds 4.20x more parallelism on M2; GT's finds 3.15x.  That
one row is most of the 14% difference in the totals, and `basemul` going the
other way (4.65 against 4.56) shows it is not a blanket property of GT.

The mechanism is the Good-Thomas trade itself.  P94 measured GT's inverse at
**2.02 multiply-class instructions per coefficient against Official's 2.27** --
12% fewer, the decomposition delivering exactly what it promises -- and **7.89
total against 4.52**, 75% more, the excess being the data movement the index
permutation costs.

Multiply throughput goes from one effective pipe on A76 to four on M2.  Store
throughput roughly doubles.  So the resource GT saves scales 4x and the resource
GT spends scales 2x: **the trade that wins on the narrow machine loses on the
wide one**, and it is not a coding defect but the arithmetic of the decomposition
meeting the microarchitecture.

## What this means for the KEM numbers

On A76 neither side has FEAT_SHA3, and GT's `keccakf1600.S` beats Official's
portable C by 1.27x.  GT's decapsulation there is 34,431 cycles against 40,701,
**-15.4%** -- of which the arithmetic contributes -1,890 and Keccak most of the
rest.

On M2 the honest baseline is Official + CryptoExtension, where the permutation
counts and costs are identical on both sides.  GT's Keccak advantage goes to
zero, the arithmetic's +4.5% is all that remains, and 864's decapsulation loses.

So the answer to "why does GT win so little, or lose, once the hash is removed"
is in three parts:

1. **Most of GT's headline win was always the Keccak backend**, not the
   transform.  Hold Keccak equal on M2 and 768's arithmetic wins by only
   0.3-3%, while 864 loses 1.3% on key generation and 2.2% on decapsulation.
2. **The transform's own win is real but small**: the forward NTT is 0.88/0.94
   and `basemul` 0.89/0.87 on the two machines.  Good-Thomas does deliver there.
3. **The inverse gives it all back on M2**, at 1.27, because that is where the
   permutation's data movement is concentrated: 768 narrow stores per call,
   against Official's component-major layout which needs none of them.

Fixing the inverse is therefore not a refinement, it is the whole gap.  P96/P97
established that the inverse is store-µop bound and that relocating the
transpose cannot help; P98 found `gt864-p29-direct-st3` already cuts stores
972 -> 224 and is worth -135 cycles on M2, held back only by an IPC collapse on
A76.
