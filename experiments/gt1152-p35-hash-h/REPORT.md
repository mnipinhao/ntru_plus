# P35 — what `hash_h` actually costs, and what fusing it would buy

Branch `neon-1152`, parent `0a0fa550`.  Pi 5 core 3, GCC 14.2.0 `-march=native
-O3`, `taskset -c 3`.

Three times now I have stated `hash_h`'s permutation count from reasoning and
been wrong each time: P32 said **one** ("a single block, where the fusion has
nothing to amortize"), P34's correction said **five**.  This gate counts them by
instrumenting `fips202.c` instead of arguing.

**`hash_h` is four permutations.  Fusing it is worth ~1,806 cycles per call,
~3,611 across the KEM — and three quarters of that is available from a much
cheaper change than a fused kernel.**

## 1. The count, measured

`fips202_counted.c` is `fips202.c` with a counter on every
`KeccakF1600_StatePermute` call site (there are two: one in `keccak_absorb`, one
in `keccak_squeezeblocks`).

```
  hash_h  generic, 176 in + 1 prefix, 320 out : 4
```

Which the structure explains.  `keccak_absorb` permutes once per **full** block
and leaves the padded tail XORed but unpermuted; `keccak_squeezeblocks` permutes
**before** each block it emits:

| | bytes | rate-136 blocks | permutations |
|---|---|---|---:|
| absorb | 1 + 176 = 177 | 1 full + 41 tail | 1 |
| squeeze | 320 | 2 full + 48 | 3 |
| | | | **4** |

For calibration the same accounting gives 13 for `hash_f` (1,729 in = 12 full +
97 tail; 32 out needs no extra permutation) and 15 for `hash_g` (13 absorb + 2
extra squeeze), and both match what the fused kernels' stage machines actually
execute.

## 2. Measured

```
                                            cycles  per perm
  hash_h, generic sponge (as shipped)       5458.3    1364.6
    ... without the prefix memcpy           5453.8    1363.5
    the malloc/free pair alone                37.5         -
    the prefix memcpy alone                   11.5         -
  4 bare assembly permutations              3709.6     927.4
  hash_h over the asm permutation           4081.0    1020.2
  genf/geng seed expand (32 in, 288 out)    4111.1    1370.4
  hash_f fused (1729 in, 32 out)           11931.8     917.8
  hash_g fused (1729 in, 288 out)          13749.0     916.6
```

`hash_f` at 917.8 per permutation and `hash_g` at 916.6 agree to 0.13%, which is
what a correct permutation count on both looks like.

## 3. Where the 1,365 per permutation goes — and the thing I had missed

The generic path costs 1,365 per permutation against 927 for the assembly one.
I had assumed the gap was sponge bookkeeping around a shared permutation.  It is
not.  **`fips202.c` never calls `ntruplus_keccak_f1600_x1_aarch64`** — it has its
own C `KeccakF1600_StatePermute`, and that is what every `shake256()` in the KEM
runs.  P34's `audit_abi.py` had already printed this and I did not read it:

```
keccakf1600.S  ntruplus_keccak_f1600_x1_aarch64   -   False   internal
```

So the 1,806-cycle saving decomposes as

| | per call |
|---|---:|
| C permutation → assembly permutation (4 × 437) | **1,750** |
| assembly permutation → in-register fused stage (4 × 14) | 56 |
| the `malloc`/`free` pair `shake256()` performs internally | 37 |
| the 176-byte prefix `memcpy` | 12 |
| less double-counting in the estimate | −49 |
| **total** | **~1,806** |

`shake256_absorb` really does `malloc(200)` and `shake256_ctx_release` really
does `free` — every generic sponge call in this KEM heap-allocates.  It is only
37 cycles, but it is 37 cycles of allocator on a constant-time primitive's path.

**The dominant term is not the fusion.  It is that `hash_h` is still running the
C permutation.**

## 4. Two routes, both real

**(a) The cheap one.**  Keep the sponge shape; call the assembly permutation the
package already ships.  About 25 lines of C, no generator, no new kernel.
Verified byte-identical to `shake256` on the full 320-byte output:

```
  asm-sponge hash_h vs shake256: identical, 320/320 bytes
  4081.0 cycles   saving 1377.3 per call   = 76.3% of the total
```

**(b) The fused kernel**, following `hash_f`/`hash_g`: 2 absorb stages + 2
squeeze stages at the measured per-stage costs = **3,652.8**, saving 1,805.5 per
call.  It buys **428 per call beyond route (a)**.

| | per call | × 2 calls |
|---|---:|---:|
| as shipped | 5,458.3 | 10,916.6 |
| (a) asm-permutation sponge | 4,081.0 | 8,162.0 |
| (b) fused kernel | 3,652.8 | 7,305.6 |
| **saving, (a)** | 1,377.3 | **2,754.6** |
| **saving, (b)** | 1,805.5 | **3,611.0** |

Route (b) is still the right target — it is the same generator, the same five
anchored-replacement discipline, and `hash_h` is the smallest of the three sizes
— but route (a) is the honest fallback if the generator work does not land, and
it is what should ship first because it is verifiable in an afternoon.

## 5. `hash_h` is not the only site left on the C permutation

```
kem.c:55  genf_derand:  shake256(buf, NTRUPLUS_N/4, coins, 32)
kem.c:81  geng_derand:  shake256(buf, NTRUPLUS_N/4, coins, 32)
```

32 bytes in, 288 out = 0 absorb + 3 squeeze permutations, measured 4,111.1 at
1,370.4 each — the same 1,365 signature.  Two calls per keygen **attempt**, so
the count moves with the retry rate.  A fused kernel for this shape is 3 stages
and would save ≈1,380 per call; it is the natural companion to `hash_h` and
shares everything except the block counts.

Total still on the C permutation: 4 + 4 + 3 + 3 = **14 permutations per
keygen+encaps+decaps**, ≈19,000 cycles, of which ≈6,400 is recoverable.

## 6. What this changes upstream

P34's follow-up put `hash_h` fusion at "~2,100" from a five-permutation count
and a 860-per-permutation figure that came from dividing `hash_g`'s 13,765 by 16
instead of 15.  Both were wrong; the answer is **~3,611**, and it is the largest
single item left in the campaign by a wide margin.

## Reproduce

```sh
cp ../gt1152-p10-kem/fips202.c fips202_counted.c   # then add the permute counter
gcc -O3 -march=native -D_DEFAULT_SOURCE -I. bench_h.c fips202_counted.c \
    ../gt1152-p10-kem/keccakf1600.S -o bench_h
taskset -c 3 ./bench_h
```
