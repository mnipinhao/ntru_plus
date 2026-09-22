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
