# P141: NTRU+768's M2 deficits in the codec and poly_basemul_add_encap, priced

P139 left GT behind Official on M2 in `tobytes_keygen_cq` (+50 ns a key
generation), `tobytes_encap_loose` (+48), `tobytes_encap` (+26) and
`poly_basemul_add_encap` (+27 ns an encapsulation); on the A76 all but the
first loose tobytes are GT wins.

## Instruction mix per call (`mix768.c`, `mix.py`, callgrind on the Pi)

The entry points share bodies (the loose serializer falls into the reduced
one's core), so each call's mix is a whole-program run calling it once minus
a run calling nothing.  M2 SIMD floor = SIMD ops / 4 per cycle at 3.5 GHz.

| call | SIMD | notable | M2 floor | M2 measured (P139) |
|---|---:|---|---:|---:|
| GT `tobytes_keygen_cq` | 936 | 96 tbl, 96 uzp, 216 trn | 66.9 ns | 69.2 ns |
| Official `poly_tobytes` | 720 | 216 trn, 192 mls | 51.4 ns | 52.4 ns |
| GT `tobytes_encap` | 1,080 | 504 trn | 77.1 ns | 77.9 ns |
| GT `tobytes_encap_loose` | 1,368 | | 97.7 ns | 99.6 ns |
| GT `poly_basemul_add_encap` | 1,944 | **72 `ld4`, 24 `st4`** | 138.9 ns | **194-197 ns** |
| Official `poly_basemul_add` | 2,136 | 97 `ld1` | 152.6 ns | 168 ns |

The three serializers sit on their SIMD floor: their excess over Official is
the Good-Thomas permutation (tbl/uzp/trn), and on M2 nothing else is left to
take (P104's reachable part -- duplicate loads and moves -- is free on M2).

`poly_basemul_add_encap` is 56 ns above its floor.  Structured loads cost
SIMD work (`ubench_ld4.c`): on M2 an `ld4 {4 x .8h}` beside four SIMD adds
takes 3 cycles where `ld1 {4 regs}` takes 1 (about 8 SIMD slots an ld4); on
the A76 5.1 cycles against 2.0, and 6.1 against 2.1 beside the adds.
1,944 SIMD + 72 ld4 x 8 + 24 st4 x 8 slots = ~2,712 / 4 = 678 cycles = 194 ns:
the whole gap.

## What removing it would take

The `ld4` deinterleaves h, r and m from the block-major layout (four
coefficients of a base element adjacent) into coefficient-major vectors.
The layout's producers: `poly_frombytes_encap` for h (P135's tbl decoder --
any layout is free), and `poly_ntt_encap_small_lazy` for r and m, whose
`.2D` zips are part of its butterflies, not an output interleave; its
consumers besides the basemul are `tobytes_encap_loose` (r) and, through the
basemul's `st4`, `tobytes_encap`.

| step | M2 | A76 | cost |
|---|---:|---:|---|
| h in coefficient-major from the decoder, 24 of the 72 `ld4` -> `ld1` | ~-14 ns | ~-100 cycles | small: decoder tables and the basemul's h loads |
| r, m too (NTT output layout) | ~-27 ns more | ~-190 more | the Slothy-scheduled NTT tail and the loose serializer's gathers |
| the `st4` and `tobytes_encap`'s gathers | ~-7 to -14 ns | ? | regenerate the gather frontends |

Upper bound about -55 ns (-1.4%) M2 encapsulation and -300 cycles (-1.0%)
A76, most of it behind a change to the forward NTT's output layout; the first
step alone is about -0.35% on both.
