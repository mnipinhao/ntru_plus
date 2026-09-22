# P92 — NTRU+864's decapsulation, kernel by kernel

P91 left 864's decapsulation as the outlier: 2% ahead of Official on the
contestable part where 768 manages 31%.  This takes it apart by direct timing.

Not by sampling.  P91 established that the profiler disagrees with itself by 5%
on a 2,000 ns bucket, which is 100 ns -- the size of the thing being looked for.
Both implementations are linked into one binary, the official kernels renamed,
and each is timed under the gated harness.

## The decomposition

Both sequences are structurally identical: three unpacks, a scaled multiply, the
inverse, a forward transform, a subtraction, a multiply, a pack, hash_g,
sotp_decode, hash_h, cbd1, a second forward transform, a second pack, verify.

| kernel | GT | Official | ratio | calls | GT total | Official total |
|---|---:|---:|---:|---:|---:|---:|
| frombytes | 81.6 | 78.4 | 1.04 | 3 | 245 | 235 |
| basemul_rinv / basemul_scale | 139.4 | 125.0 | 1.12 | 1 | 139 | 125 |
| **invntt (+ crepmod3)** | **404.1** | **317.4** | **1.27** | 1 | **404** | **317** |
| ntt | 243.1 | 259.6 | **0.94** | 2 | 486 | 519 |
| sub | 24.8 | 24.2 | 1.02 | 1 | 25 | 24 |
| basemul | 128.8 | 151.3 | **0.85** | 1 | 129 | 151 |
| tobytes_small | 69.7 | 78.2 | **0.89** | 1 | 70 | 78 |
| **tobytes (full)** | **97.1** | **78.2** | **1.24** | 1 | **97** | **78** |
| sotp_decode | 45.7 | 46.2 | 0.99 | 1 | 46 | 46 |
| cbd1 | 43.1 | 40.2 | 1.07 | 1 | 43 | 40 |
| verify | 21.5 | 21.5 | 1.00 | 1 | 22 | 21 |
| **sum** | | | | | **1705** | **1637** |

It reconciles with P91's top-level figures.  P91 measured the non-permutation
remainder at 1,880 ns for GT and 1,927 for Official.  The kernels account for
1,705 and 1,637, leaving 175 and 290 of sponge wrapper, zeroization and glue --
and that 115 ns gap is the sponge saving the profile has been reporting all
along.

## Three findings

**GT's kernels are 69 ns slower than Official's.**  Decapsulation comes out
47 ns ahead only because the sponge wrapper and the clears are about 115 ns
cheaper.  The arithmetic, taken on its own, loses.

**The inverse transform is the only large item, +87 ns.**  Everything else is
inside +/-20 ns, and three of them are GT wins: the forward transform by 33 ns
over two calls, `basemul` by 22, `tobytes_small` by 8.

**The gap was previously overstated at +143 ns.**  That compared GT's
`poly_invntt_ternary`, which performs the mod-3 reduction, against Official's
`poly_invntt_scale`, which does not.  Adding `poly_crepmod3` to the official
side -- which its `kem.c` calls immediately afterwards -- gives 317.4, and the
gap is **+87**.  Same class of error as P84's component table, where decaps was
compared through the wrong function pair.

## What that does to the plan

P89 found 43 ns of the inverse mechanically addressable -- 6 to 10 in the tail,
36 in the main kernel against a risk of serialising stores Slothy interleaved.
Against the corrected +87 that is **half the gap**, not a third, and it would
take the kernel sum from +69 to +26, near parity.

It does not move the operation much.  The permutation is 53% of 864's
decapsulation and identical on both sides, so closing the whole 69 ns would take
the margin from -1.1% to about -2.8%.  The ceiling is -47% and the constraint is
the permutation, not the arithmetic.
