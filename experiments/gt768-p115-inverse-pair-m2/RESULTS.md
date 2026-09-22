# P115 — 768's retired GT inverse on M2, and why only the inverse needs redesigning

The question: 768's GT inverse (`test/reference/invntt.S`) was replaced on
2026-07-31 by Official's `poly_invntt_decap_scale` (Wave 21/23, A76 only).  The
decision was taken on the whole decode + basemul + inverse contract.  To bring the
GT inverse back, which of those three must change?

## The chain on M2, split into parts

`bench_pair.c`, M2 Pro, witness-gated (P-core at full clock), best of 301 rounds
x 1000 calls, three runs identical to 0.1 ns.  Both chains agree bit-for-bit after
`poly_crepmod3`.

| | Official (production) | GT (retired) | GT − Off |
|---|---:|---:|---:|
| decode ct + f | ~75 | 133.3 | **+58** |
| first basemul | ~133 | 173.4 | **+40** |
| (decode + basemul, as run) | 208.4 fused | 306.7 | +98 |
| inverse | 212.4 | 245.8 | **+34** |
| scratch clear, 2,144 B | — | 20.6 | **+21** |
| **chain** | **422.3** | **574.0** | **+152 (+36%)** |

Official's decode and basemul rows are taken from `poly_frombytes_decap` x2 (74.8)
and the fused total. Its inverse row is the in-place call minus a 1,536 B copy
(19.0).

Two thirds of the gap is decode and basemul, not the inverse.

## Decode and basemul do not have to change

`check_perm.c`:

1. Official's scaled first product `poly_frombytes_basemul_decap_scale` is
   **identical mod q** to GT's `poly_basemul` product, slot for slot: both
   retain one R^-1.
2. Relaid out to block-major, it goes into GT `poly_invntt` and comes out
   **bit-identical to the Official chain**, 0 mismatches over 64 random `f`.
3. The relayout preserves quartics: **all 192** GT 4-coefficient blocks are one
   element's c0..c3 at QSoA stride 8 (the same lane of four consecutive vectors).

Pointwise multiplication commutes with the layout permutation, so the permutation
only has to be applied once, to the product.  Official's fused decode + basemul
(208 ns, which already writes the QSoA `c` that the verification suffix needs)
can stay as it is.  The GT inverse only needs a stage123 that reads QSoA.

Caveat: 64 random inputs do not reach the range extremes.  Official's product
range has to be proved inside the GT inverse's lazy-reduction bounds before
promotion.

## The clear can cost nothing

`crypto_kem_dec_internal` already runs `secure_clear` over its whole scratch
struct on exit.  When the inverse runs, `buf1` + `buf2` (2,304 B, contiguous)
are dead, and that is more than the inverse's 2,048 B of secret working space
(512 B stripe + 1,536 B row buffers).  With caller-owned scratch (P80's pattern),
the 21 ns clear goes away.

## What remains: the inverse itself, +34 ns

Static count per call:

| | GT inverse | Official inverse |
|---|---|---|
| passes over 1,536 B | 3 (stage123 → stripe, stage45 → rows, post → out) | 2 |
| store instructions | 96 `str q` + 96 `str q` + **192 `str d`** = 384 | ~192 |
| bytes stored | 4,608 | 3,072 |
| input loads | 192 `ldr d` + 96 `ins` (branch halves from `x1`, `x1+768`) | `ldr q` / `ld1` |
| constant loads | 384 `ldr q` (6 KB branchfold table) in post | per-layer zetas |

Wave 10 (A76) put post/branchfold at 2,764 of about 4,760 instructions.

Levers, each checkable in isolation:

1. **Fuse stage45 into post.**  Run stage45 for the three rows stripe by stripe
   (3 x 4 vectors live) and feed DFT3 + branchfold directly.  The row buffers
   disappear: −96 `str q`, −96 `ldr q`, −1,536 B of scratch.  Paused on A76
   (row-buffer/post fusion); never tried on M2.
2. **Pair the output stores.**  One 3-stripe group writes 24 contiguous bytes per
   output pointer, so two groups make 48 B: 192 `str d` → 96 `str q`, plus one
   permute per vector (M2 has four vector pipes).
3. **QSoA-reading stage123.**  96 `ldr q` + in-register transposes, replacing
   192 `ldr d` + 96 `ins`.  Integration needs this anyway.  The branch-0/branch-1
   partners sit in different QSoA groups and different lanes (e.g. GT block 0 →
   QSoA 5, block 96 → 743), so the transpose needs one extra pairing step.
4. **Caller-owned scratch** (above).

After 1 + 2 the store count reaches 192, Official's level.  Whether that gets
under 212 ns is the experiment; this note does not claim it.

## Plan, cheapest first

> **Superseded by P116** (`../gt768-p116-inverse-simd-budget/`): knockouts showed the
> inverse is SIMD-bound on M2, not store-bound, so E1/E2 below were replaced by two
> tail rewrites that beat Official on both machines.

| step | change | gate |
|---|---|---|
| E1 | stage45 + post fusion, block-major input kept | inverse alone < 246 on M2; A76 not worse than current GT |
| E2 | paired `str q` output | inverse alone, both machines |
| E3 | QSoA stage123 input (range proof for Official's product) | inverse alone < 212.4 on M2 |
| E4 | kem.c: Official fused front-end → GT QSoA inverse, scratch in `buf1/buf2` | KAT, zeroization, ABI; full decap M2 and A76 vs production |

Stop at E3 if the inverse does not beat 212.4 ns: the front-end and the clear are
already neutral, so nothing else can make up the difference.

## Files

- `bench_pair.c`: the timing split.
- `check_perm.c`: the relayout derivation and the bit-exact check.

Build from the NTRU+768 production directory:

```sh
cc -O3 -fomit-frame-pointer -I. ../../../../experiments/gt768-p115-inverse-pair-m2/bench_pair.c \
   ntt.S base.S pack.S cbd.S crepmod3.S add.S basemul_lambda.c keygen_lambda.c \
   test/reference/basemul.S test/reference/invntt.S -Wl,-dead_strip -o bench_pair
```
