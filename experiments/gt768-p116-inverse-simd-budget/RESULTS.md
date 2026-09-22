# P116 — 768's GT inverse is SIMD-bound, and two tail rewrites put it ahead of Official on both machines

> **Warning (P117):** E3 below is **not correct for every input**.  Its stage45
> overflows int16 for products with |x| > 1,846, and Official's product reaches
> 2,458.  Use E4 (`../gt768-p117-frontend-barrett-loads/`), which is proven safe
> for the full range and faster.

P115 planned E1 (stage45 + post fusion) and E2 (paired `str q` outputs), both
aimed at stores.  Before writing them, knockout probes on M2 showed they could
not pay off.  This gate finds what the kernel is actually bound by and rewrites
the part that costs.

## The planned E1/E2 would not have paid on M2

Knockouts on the reference kernel (output wrong, timing valid), M2, ns:

| removed | inverse |
|---|---:|
| nothing | 245.7 |
| all 192 post `str d` (E2's target) | 246.5 |
| 96 lo `str d` | 246.6 |
| stage45 row-buffer stores + post row loads (E1's target) | 243.3 |

At most 2.4 ns: **the 768 GT inverse is not store-bound on M2.**
(`inverse-864-store-bound` is about 864's `umov`/`strh`, a different kernel.)

## It is bound by SIMD ALU throughput

Dynamic instruction mix from the disassembly (loops weighted), M2 at 3.497 GHz:

| | cycles | SIMD ALU | SIMD/cycle | loads | stores |
|---|---:|---:|---:|---:|---:|
| Official `poly_invntt_decap_scale` | 743 | 2,768 | 3.73 | 137 | 124 |
| GT reference `poly_invntt` | 860 | 3,314 | 3.85 | 830 | 389 |

Microbenchmark, M2 P-core, eight independent `add.8h` chains plus four extras per
iteration:

| extra | cycles/iter |
|---|---:|
| none (8 adds) | 2.05 |
| 4 `mov.16b` | 2.05, **eliminated at rename** |
| 4 `ext` | 3.15 |
| 4 multiply-class | 3.04 |

Four SIMD ops per cycle, vector moves free.  GT's 144 `mov.16b` cost nothing, so
the real excess was 3,170 against 2,768: +402 ops ≈ 115 cycles ≈ 33 ns, which is
the measured +34 ns.

Where GT's extra ops sit: 288 Barrett reductions (864 ops; Official has none),
192 `ext`, 96 `ins`.  Its fqmul count is *lower* (374 against Official's ~480-576).

## E1 — one merge and one Barrett per output vector

The post branch merge spent 16 SIMD ops per output vector: two fqmul, then for
lo and hi separately `ext` + `add` + Barrett.  E1 zips the two products,
`[lo.b0 | hi.b0]` + `[lo.b1 | hi.b1]`, adds once and reduces once:
12 ops, −384 in total.  The lane values are unchanged, so the output is
bit-exact.  The hi half is stored with `st1 {v.d}[1]` through `x15`.

## E2 — crepmod3 fused into the tail

Production always runs `poly_crepmod3` straight after the inverse.  The post
Barrett's output is exactly centered in [−1728, 1728] for every |x| < 29,385
(exhaustive over all int16), so crepmod3's two centering corrections are
redundant.  Only its 2-op mod-3 step is needed, and the separate pass (4 ops + a
load and a store per vector) goes away.

Range proof (`range_proof.c`): for **every int16 input** and every constant in
the 96-vector branchfold table, |product| ≤ 3,439 and the merged sum
**|y| ≤ 6,789**, well inside 29,385.  The fused tail is correct for all inputs,
not only for sampled ones.

E2 carries E1.

## Results: inverse + crepmod3, as `kem.c` calls it

All variants are bit-exact against reference inverse + crepmod3: 2,000 real
decap products + 200 range-corner inputs, and in place.

| | M2 ns | vs Off | A76 cycles | vs Off |
|---|---:|---:|---:|---:|
| Official, in place (copy-corrected) | 254.1 | — | 3,959 | — |
| GT reference | 287.7 | +13.2% | 3,968 | +0.2% |
| **E1** + crepmod3 | 264.9 | +4.3% | **3,665** | **−7.4%** |
| **E2 fused**, in place (copy-corrected) | **237.8** | **−6.4%** | 3,701 | **−6.5%** |

M2: witness-gated best of 301 x 1000, three runs within 0.1 ns.
A76: Pi5 core 3, PMU cycles, median of 61 x 2000, three runs within 4 cycles,
`throttled=0x0`.

GT's out-of-place entries were timed without a copy.  Official and E2-in-place
were timed in place with the 1,536 B copy subtracted.

**E2 beats Official on both machines**: 16.3 ns on M2, 258 cycles on A76.  On
A76 it is 36 cycles behind E1 + separate crepmod3.  The fused tail puts two more
multiply-class ops on post's longest dependency chain, and post was not
rescheduled after either edit.  Rescheduling it (Slothy, or interleaving
stripes by hand) is the obvious next step for A76.

## Tried and dropped

**Lane load instead of `ldr d` + `ins`** in stage123 (`invntt_e2.S`): 223.3
against E1's 223.0 ns.  `ld1 {v.d}[1]` costs a SIMD µop on M2 too.

## Per-phase, E1, M2

| phase | cycles | SIMD ops | ops/cycle |
|---|---:|---:|---:|
| stage123 x3 | 157 | ~564 effective | 3.6 |
| stage45 x3 | 205 | 750 | 3.66 |
| post | 419 | 1,472 | 3.51 |

Every phase is close to four ops per cycle, so further gains have to come from
removing ops.  The remaining candidates, largest first:

- stage45's 96 row-end Barretts (288 ops), which need a range proof through
  post's DFT3;
- a post schedule for A76.

## What this means for integration

The P115 route still holds: Official's fused decode + basemul product feeds the
GT inverse after a quartic-preserving relayout, and the scratch can live in the
KEM's `buf1/buf2`.  The inverse no longer needs the E1/E2 store work to win.
What is left for integration is the QSoA-reading stage123 (P115 E3).  It must not
add more SIMD ops than the ~16 ns (M2) / ~258 cycles (A76) margin: the relayout
has to be paid in loads, not transposes.

## Files

- `invntt_e1.S`, `invntt_e2t.S`: variants of `test/reference/invntt.S`, symbols
  prefixed.
- `invntt_e2.S`: the dropped lane-load variant.
- `bench_e.c`: inverse alone vs reference and Official (M2).
- `bench_t.c`, `bench_t_a76.c`: inverse + crepmod3 on M2 and on the Pi (perf
  cycles).
- `range_proof.c`, `branchfold_table.h`: the exhaustive bound.

M2 build, from this directory:

```sh
P=../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768
cc -O3 -fomit-frame-pointer -I$P -I$P/.. bench_t.c invntt_e1.S invntt_e2t.S \
   $P/ntt.S $P/base.S $P/pack.S $P/cbd.S $P/crepmod3.S $P/add.S \
   $P/basemul_lambda.c $P/keygen_lambda.c $P/test/reference/basemul.S \
   $P/test/reference/invntt.S -Wl,-dead_strip -o bench_t
```

---

# E2b and E3 — interleaved lanes, then Official's front-end

## E2b — one `addp` for the branch merge

The inverse's global lane order is free: stage123 and stage45 multiply only by
lane-broadcast twiddles (`vN.h[i]`), and the DFT3 constants are scalars.  Only
post's branchfold constants are per lane.  E2b interleaves the branches,
`[c0.b0, c0.b1, c1.b0, c1.b1, ...]`:

- stage123 builds each vector with `zip1.8h` in place of `ins` (same cost);
- the post merge `zip1.2d + zip2.2d + add` becomes one `addp`: −2 ops per output
  vector, **−192**;
- the 384 branchfold constant vectors are lane-permuted, new[2k+b] = old[4b+k]
  (`make_e2b.py`).

`addp` sums the same lane pairs as before, so the output is bit-exact and the
range proof carries over.

| inverse + crepmod3, M2 | ns |
|---|---:|
| Official, in place (copy-corrected) | 254.1 |
| E2 | 237.8 |
| **E2b** | **221.9 (−12.7%)** |

−16 ns over E2, against −13.7 predicted from 192 fewer ops.

## E3 — the GT inverse fed by Official's fused decode + basemul

The QSoA product's elements sit in different groups and lanes from their branch
partners (P115).  An in-register transpose costs 3 ops per vector, +192 over
today's `ins`.  Instead:

- **front-end** (`frontend_e3.S`, extracted from `base.S`): its two product
  stores `st1 {v12-v15}.8h` become `st4 {v12-v15}.8h`, so each group lands as
  eight AoS elements (element (g,l) at byte 64g + 8l, coefficients contiguous).
  Nothing else changes; `decoded_ct` still comes out in QSoA for the
  verification suffix.
- **inverse** (`invntt_e3.S`, from `make_e3.py`): E2b whose stage123 takes both
  `ldr d` from the product at the offsets the P115 map gives.  The whole
  permutation lives in load immediates.

`st4` is not free.  Microbenchmark, M2, in a SIMD-saturated loop: +2.1 cycles
per `st4 {4}.8h`, against +0.5 for four `str q` (about 8 SIMD slots).  The same
+192 as the transpose, but a two-line change.

`bench_chain.c`, the full first-product chain as `kem.c` runs it:

| | M2 ns | A76 cycles |
|---|---:|---:|
| Official front-end (`st1`) | 208.5 | 2,161.8 |
| E3 front-end (`st4`) | 224.1 (+15.6) | 2,304.1 (+142) |
| Official inverse + crepmod3 (copy-corrected) | 254.0 | 3,955.3 |
| E3 inverse, fused crepmod3 (copy-corrected) | 227.0 | 3,608.7 |
| **Official chain** | **464.0** | **6,122.8** |
| **E3 chain** | **450.5 (−13.5, −2.9%)** | **5,909.1 (−214, −3.5%)** |

- Correctness: output, `decoded_ct` and the fail flag are identical to Official's
  chain over 3,000 trials, 10% of them malformed ciphertexts.
- M2: three runs within 0.1 ns.  A76: three runs within 2.3 cycles,
  `throttled=0x0`.

On M2, E3's inverse is 5 ns slower than E2b's (227.0 against 221.9) with the
same instruction count.  The loads now gather from the whole 1,536 B product.
Not investigated.

## Not yet in the numbers: the working area

The GT inverse allocates 2,144 B on its own stack and does not clear it (the
reference file lost its clear when it became test-only).  Production has to
take the 2,048 B as caller-owned scratch in `buf1/buf2`, which
`crypto_kem_dec_internal` already clears on exit (P115).  Until then the E3
numbers are **compute-only**.  Paying an in-leaf clear would cost 20.6 ns on
M2 (P115), which exceeds the 13.5 ns margin.

## Where the M2 margin went, and where more is

| step | M2 chain effect |
|---|---:|
| E3 inverse vs Official inverse | −27.0 |
| `st4` front-end | +15.6 |
| **net** | **−13.5** |

Next candidates:

- **Front-end `st4`** (+15.6 ns / +142 cycles).  Cheaper would need the product
  to leave the basemul already element-major.  The front-end is Slothy-scheduled
  for A76, so any rewrite there needs rescheduling too.
- **stage45's 96 row-end Barretts** (288 ops ≈ 20 ns on M2), if a range proof
  through post's DFT3 allows deferring them.
- **Post schedule on A76.**

## Files (E2b / E3)

- `make_e2b.py` → `invntt_e2b.S`; `bench_t2b.c` (E2b on M2).
- `make_e3.py` + `qsoa_map.txt` → `invntt_e3.S`.
- `frontend_e3.S`: Official's fused decode + basemul with `st4` product stores.
- `bench_chain.c`: full chain on M2 (witness-gated) or Linux (perf cycles),
  including the malformed-input check.
