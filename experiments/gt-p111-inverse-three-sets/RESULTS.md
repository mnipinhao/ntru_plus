# P111 — the inverse across all three sets, and they are three different answers

The complete inverse-to-ternary as `kem.c` calls it, every call in place:
768 `poly_invntt_decap_scale` then `poly_crepmod3`, 864 and 1152
`poly_invntt_ternary` which folds the reduction in, Official
`poly_invntt_scale` then `poly_crepmod3`.  Each side fed its own forward
transform's output.

| set | M2 GT | M2 Official | x | A76 GT | A76 Official | x |
|---|---:|---:|---:|---:|---:|---:|
| **768** | 256.2 | 255.9 | **1.001** | 1,651.0 | 1,651.9 | **0.999** |
| **864** | 350.1 | 298.3 | **1.174** | 1,922.6 | 1,907.0 | **1.008** |
| **1152** | 419.8 | 405.3 | **1.036** | 2,286.2 | 2,596.0 | **0.881** |

Per coefficient, ns:

| set | M2 GT | M2 Off | A76 GT | A76 Off |
|---|---:|---:|---:|---:|
| 768 | 0.334 | 0.333 | 2.150 | 2.151 |
| 864 | 0.405 | 0.345 | 2.225 | 2.207 |
| 1152 | 0.364 | 0.352 | 1.985 | 2.253 |

## Three answers to the same problem

**768 has no Good-Thomas inverse at all.**  `poly_invntt_decap_scale` is
Official's kernel to within one instruction, and it times at **1.001 on M2 and
0.999 on A76** -- the same code.  768's decapsulation path runs in Official's
layout throughout: `poly_frombytes_decap` and `poly_tobytes_decap` measured at
exactly 1.00 as well (P104).  **768 abandoned the decomposition where it does not
pay, and has the best decapsulation of the three.**

**1152's is the best Good-Thomas inverse.**  0.881 on A76 -- it beats Official by
**310 ns** -- and 1.036 on M2.  Per coefficient it is the fastest of the three
GT inverses on A76 (1.984 against 864's 2.225).  It has the P67/P68 lane basis,
which its four base-ring components make possible: 1152 = 9 x 16 x 2 x **4**, so
the components fill the four inner lanes exactly.

**864's is the worst.**  1.174 on M2, 1.008 on A76.  864 = 9 x 16 x 2 x **3**,
and P89 established that three components cannot fill four lanes, so the lane
basis does not port.  Everything this session did to it -- P29's paired main,
the `ST3.8H` route, the packed tail normalisation -- narrowed it from **1.355 to
1.174 on M2** while taking A76 from 0.977 to 1.008, but the structural
disadvantage is the component count.

## What that suggests

864's GT inverse is **51.8 ns slower than Official's on M2 and 15.5 slower on
A76**.  Doing what 768 does -- running decapsulation in Official's layout and
using its inverse -- would gain on **both** machines: decapsulation to about
-8.0% on M2 (from -6.8%) and -16.2% on A76 (from -16.1%).

It is not a drop-in.  768 buys it by keeping its whole decapsulation path in
Official's layout, with `poly_frombytes_decap`, `poly_tobytes_decap` and
`poly_ntt_decap` arranged to match; 864's forward transform produces the GT
layout.  But the precedent exists in this repository, it is measured, and it is
the only remaining item on 864's inverse that pays on both machines.
