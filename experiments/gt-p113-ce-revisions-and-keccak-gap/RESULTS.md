# P113 — upstream's CE revision is not faster, but ours is faster than upstream's

Two questions.  Does upstream's current `CE/f1600.S` differ from the March copy
the P108 baseline was built on?  And how does either compare with GT's own
`keccakf1600_v84a.S`?

## Upstream did change the file, but not its speed

Between the March import and the 2026-08-14 push upstream rewrote
`Additional_Implementation/aarch64/NTRU+768/CE/f1600.S`:

* added the MIT header crediting Becker, Hwang, Kannwischer, Yang and Yang --
  it is an adaptation of neon-ntt's `common/feat.S`
* converted Apple-style mnemonics (`eor3.16b v25, v0, v5, v10`) to standard
  ARM syntax, and added `.arch armv8.2-a+sha3`
* **added the AAPCS64 `d8-d15` save/restore** -- the violation recorded in this
  campaign's notes is fixed upstream as of that push
* `ld1r {v25.2d}, [x1], #8` became `ldr d25, [x1], #8`

Its own comment claims "adjusted state load/store, round scheduling, and
AArch64 ABI preservation".  The scheduling claim does not show up in timing.

## Three permutations, M2 Pro, same signature `(state, rc)`, outputs verified equal

| permutation | ns | x ours |
|---|---:|---:|
| **GT `keccakf1600_v84a.S`** | **147.33** | 1.000 |
| upstream `CE/f1600.S`, 2026-08 | 158.05 | 1.073 |
| upstream `CE/f1600.S`, March + our AAPCS64 patch | 158.30 | 1.074 |

**The two upstream revisions are the same speed** -- 0.16% apart, inside the
noise.  So P108's `off*_ce` binaries do not need rebuilding: the copy they used
times identically to what upstream ships today.  That question is closed.

## The question it opens instead

GT's permutation is **7.3% faster than upstream's**, 10.72 ns per call.  Both
use FEAT_SHA3; the difference is the kernel, and GT's is the mlkem-native
hybrid.  So the "Official + CE" table still credits GT with a Keccak advantage
-- smaller than the SUPERCOP table's, but not zero.

Estimated, by permutation count x 10.72 ns (**not measured**):

| set | | keygen | encap | decap |
|---|---|---:|---:|---:|
| 768 | permutations | 13 | 21 | 12 |
| | Official + CE | 4,159 | 4,751 | 3,702 |
| | + GT's Keccak (est.) | 4,020 | 4,526 | 3,573 |
| | **GT** | **3,795** | **4,081** | **3,138** |
| | **margin now** | **-8.8%** | **-14.1%** | **-15.2%** |
| | **margin if equal** | **-5.6%** | **-9.8%** | **-12.2%** |
| 864 | permutations | 14 | 24 | 14 |
| | Official + CE | 4,545 | 5,254 | 4,146 |
| | + GT's Keccak (est.) | 4,395 | 4,997 | 3,996 |
| | **GT** | **4,147** | **4,682** | **3,866** |
| | **margin now** | **-8.8%** | **-10.9%** | **-6.8%** |
| | **margin if equal** | **-5.6%** | **-6.3%** | **-3.3%** |
| 1152 | permutations | 21.4 | 32 | 19 |
| | Official + CE | 7,115 | 6,952 | 5,487 |
| | + GT's Keccak (est.) | 6,886 | 6,609 | 5,283 |
| | **GT** | **6,519** | **6,130** | **4,986** |
| | **margin now** | **-8.4%** | **-11.8%** | **-9.1%** |
| | **margin if equal** | **-5.3%** | **-7.2%** | **-5.6%** |

Holding the permutation equal would take M2 from -8.8/-14.1/-15.2 to roughly
-5.6/-9.8/-12.2 on 768, -8.8/-10.9/-6.8 to -5.6/-6.3/-3.2 on 864, and
-8.4/-11.8/-9.1 to -5.3/-7.2/-5.6 on 1152.  Still a win everywhere, about
40% smaller.

This is the strictest baseline of the three and it has never been built.  It is
one link: Official's `CE/fips202.c` sponge with GT's `keccakf1600_v84a.S`
substituted for `f1600`, both being `(state, rc)`.