# P104 — item 2 measured: 768's hand-written codec is the last one, and it shows

Item 2 said **+109 ns on encapsulation and +69 on key generation** from the
sampling profiler.  Direct timing against SUPERCOP's `ntruplus768/aarch64`,
M2 Pro, cycles per call:

| kernel | GT | Official | x | calls kg/en/de |
|---|---:|---:|---:|---|
| `frombytes_decap` | 130 | 130 | **1.00** | 0/0/1 |
| `tobytes_decap` | 186 | 186 | **1.00** | 0/0/2 |
| **`frombytes_encap`** | **233** | 130 | **1.79** | 0/1/0 |
| **`tobytes_encap_loose`** | **352** | 186 | **1.89** | 0/1/0 |
| **`tobytes_keygen_cq`** | **245** | 186 | **1.32** | 3/0/0 |
| `tobytes_encap` | 276 | 186 | 1.49 | unused |
| `ntt_encap_small_lazy` | 543 | 650 | **0.84** | 0/2/0 |
| `ntt_decap` | 639 | 650 | 0.98 | 0/0/2 |
| `cbd1` | 129 | 121 | 1.07 | 1/1/1 |

## The +109 was a fusion accounting error

`tobytes_encap_loose` is 1.89x because it absorbs the reduction that
`poly_ntt_encap_small_lazy` skips.  Counting the serializer alone gives +270
cycles on encapsulation; counting both sides of the trade:

| encapsulation | cycles |
|---|---:|
| `tobytes_encap_loose` loses | +166 |
| `ntt_encap_small_lazy` wins, x2 | **-214** |
| `frombytes_encap` loses | +103 |
| `cbd1` | +8 |
| **net** | **+63 (+18.1 ns)** |

**The lazy-NTT / loose-serializer fusion is a net win of 48 cycles.**  The
roadmap's +109 priced only the half that got dearer.

| operation | GT | Official | difference |
|---|---:|---:|---:|
| key generation | 864 | 679 | **+185 (+52.8 ns)** |
| encapsulation | 1,801 | 1,738 | **+63 (+18.1 ns)** |
| decapsulation | 1,909 | 1,924 | **-15 (-4.3 ns)** |

So item 2 is **+53 on key generation and +18 on encapsulation**, not +69 and
+109, and key generation is now the larger half.

## Why decapsulation is exactly 1.00 and the others are not

`pack.S`, 2,232 instructions, broken down by symbol:

| symbol | instructions | stores | transpose-class |
|---|---:|---:|---:|
| `poly_frombytes_decap` | 11 + a 58-instruction loop | | 19 |
| `poly_tobytes_decap` | 10 + a 72-instruction loop | | 18 |
| **`poly_frombytes_encap`** | **1,107** | **196** | **505** |
| `poly_tobytes_keygen_cq` | 545 | 7 | 210 |
| `poly_tobytes_encap` | 427 | 7 | 42 |

The decapsulation pair are small loops shaped like Official's, which is why they
time identically.  The encapsulation and key-generation entries are fully
unrolled and carry the Good-Thomas permutation: `frombytes_encap` alone is 505
transpose-class instructions and 196 stores for 768 coefficients, where 96
16-byte store µops would carry the data.

## Against the C codecs that replaced the other two sets' assembly

| | cycles per coefficient, M2 |
|---|---:|
| 1152 `frombytes` (**C intrinsics**, P86) | **0.216** |
| 768 `frombytes_encap` (**hand-written asm**) | 0.303 |
| 1152 `tobytes_small` (**C**) | **0.199** |
| 768 `tobytes_keygen_cq` (**asm**) | 0.319 |

**768's hand-written assembly is 40-60% worse per coefficient than the C
intrinsics that replaced 864's and 1152's**, and it carries the same permutation.
P87 deleted 564 KB of assembly at 864 and P88 another 244 KB; 768's 73 KB
`pack.S` is what is left of that argument.

Porting the codec would, at 1152's rate, take `frombytes_encap` 233 -> 166 and
`tobytes_keygen_cq` 245 -> 153: **-67 cycles on encapsulation and -276 on key
generation**, which would put key generation past parity with Official.

## 768's permutation, derived, and what a C codec would have to do

Encoding coefficient `i` as the value `i` with Official's serializer and reading
it back with both readers gives the permutation directly (`perm768b.c`).  Two
facts fall out:

- **`poly_frombytes_decap` returns natural order.**  768's decapsulation path
  uses Official's layout, which is why those two kernels time at exactly 1.00.
- `poly_frombytes_encap`'s permutation is completely regular: **every 4-lane
  half of every output vector is one element position taken from four
  consecutive 12-byte blocks**, and all 24x8 (quad, element) pairs are used
  exactly once.

Four consecutive blocks are **48 contiguous bytes**, which is the structural
advantage 1152 does not have -- its eight wires are scattered, so it must load
eight vectors and do a full 8x8 `transpose8`.  Here `LD3` de-interleaves the 48
bytes on the load unit: `val[j]` lane `2b` is `h_j` of block `b` and lane `2b+1`
is `h_{j+3}`, so six `UZP` and two `unfold4` produce all eight rows.  About 25
instructions per 32 coefficients against the shipped assembly's 1,107 for 768.

**What blocks it is the pairing.**  The two halves of an output vector come from
different quads -- `0/96` share one -- and the pairing graph has **two connected
components of twelve quads each**.  One component is 96 four-lane rows, 24
q-registers, so a single pass cannot hold a component and emit whole vectors.
The choices are 192 narrow `STR D` (against the 96 sixteen-byte µops the data
needs) or a second pass over a scratch buffer, and P97 measured what a separate
movement pass costs.

Estimated at 192 narrow stores: about 888 instructions against 1,107, with the
store count unchanged, so roughly **-33 cycles** on `frombytes_encap` -- not the
-67 that 1152's rate suggested.  The store budget, not the instruction count, is
again what decides.

`poly_tobytes_keygen_cq` is the larger half of item 2 (+177 cycles across its
three key-generation calls, 545 instructions, 210 transpose-class) and has not
been analysed.  `poly_tobytes_encap` (427 instructions) is **dead code**: the
encapsulation path calls `encap_basemul_add_tobytes` instead.

## `poly_tobytes_keygen_cq`, the larger half, opened

PMU retired instructions, `-O3 -fomit-frame-pointer` as its Makefile has it,
20,000 iterations, empty-mode baseline subtracted:

| per call | instructions |
|---|---:|
| GT `poly_tobytes_keygen_cq` | **1,220** |
| Official `poly_tobytes` | 808 |
| GT `poly_tobytes_decap` | **809** |

`tobytes_decap` matching Official to one instruction confirms what the timing
said: 768's decapsulation serializers are Official's shape.

The 1,220 splits cleanly:

| | instructions |
|---|---:|
| the permutation wrapper in `pack.S` | 545 |
| the shared pack core, x12 | 675 |
| Official's fold and store | 808 |

**GT's fold-and-store core is better than Official's** -- 675 against 808, 56
instructions per 64 coefficients against 67, which is P86/P87's fold work
arriving here.  The whole +412 is the permutation wrapper.

| wrapper | count | reachable? |
|---|---:|---|
| data loads | **192** | **96 vectors, each loaded twice** |
| index loads | 24 | already optimal |
| `TBL` (two-source) | 96 | the permutation itself |
| `UZP1`/`UZP2` | 96 | the permutation itself |
| `MOV` | 48 | probably |

The index reuse is already there: all 96 `TBL` read `v13`, reloaded once per
four, so 24 loads rather than 96.  The permutation was derived empirically
(`cq768.c`): each natural output vector gathers from **four CQ vectors at stride
four**, 80 of 96 taking two lanes from each, and the 96 `TBL` need only **24
distinct index vectors**.  Two-source `TBL` is also the right choice -- P97
measured three-source `TBL` at +21% on A76.

What is left is the duplicate data loads.  `TBL` pairs are `(g, g+4)`, so vector
`g`'s other use is the pair `(g-4, g)`, which lands in a **different pack-core
call**; sharing it means holding vectors across calls, and each call already
loads sixteen.

At the measured 0.143 cycles per instruction here, removing the 96 duplicate
loads and the 48 `MOV` is about **21 cycles a call, 18 ns across key
generation's three**, against the item's +51.  **The remaining 33 ns is the 96
`TBL` and 96 `UZP` -- the permutation itself**, and that is the same answer
1152's unpack and 864's inverse gave.
