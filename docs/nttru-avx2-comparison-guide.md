# NTTRU AVX2 reading and NTRU+768 comparison guide

This note records what is worth learning from Gregor Seiler's NTTRU AVX2
implementation, what can be compared with the active NTRU+768 AVX2 lane, and
what must not be transplanted without a new proof.

For a shorter concept-first Chinese summary, start with
[`nttru-avx2-essence-zh.md`](nttru-avx2-essence-zh.md).

## Scope and source

- NTTRU upstream: <https://github.com/gregorseiler/NTTRU.git>
- Reviewed revision: `65bb4da35944d0ee2ce8462de86e479486904625`
- NTTRU lane: [`third_party/NTTRU/avx2/`](../third_party/NTTRU/avx2/)
- Active lane: [`ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/`](../ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/)

The NTTRU `avx2/` history consists of Gregor Seiler's initial implementation
and a follow-up key-generation retry fix. The checkout is ignored by the outer
repository and retains its own Git history.

## First correction: the parameters are not identical

Both implementations use 768 coefficients and the ring shape

```text
Z_q[X] / (X^768 - X^384 + 1),
```

but they do not use the same field or the same terminal NTT algebra.

| Contract | NTTRU AVX2 | Active NTRU+768 AVX2 |
| --- | --- | --- |
| Dimension | `N = 768` | `N = 768` |
| Modulus | `q = 7681` | `q = 3457` |
| Packed coefficient width | 13 bits | 12 bits |
| Packed polynomial size | 1248 bytes | 1152 bytes |
| Forward transform layers | 8 | 7 |
| Terminal blocks | 256 cubic blocks | 192 quartic blocks |
| Pointwise layout per 16 blocks | 3 YMM coefficient vectors | 4 YMM coefficient vectors |
| Base inversion | cubic determinant and `a^(q-2)` in ASM | quartic denominator, 12-vector batch inversion, final scaling |

Consequently, the reusable material is instruction scheduling, register
allocation, table packing, shuffle placement, and constant-time aggregation.
Twiddles, Montgomery constants, reduction identities, layer counts, terminal
formulas, serialized layouts, and range bounds are not reusable as-is.

## Recommended reading order

Before the six kernels, read
[`params.h`](../third_party/NTTRU/avx2/params.h),
[`poly.h`](../third_party/NTTRU/avx2/poly.h),
[`ntru.c`](../third_party/NTTRU/avx2/ntru.c), and
[`consts.c`](../third_party/NTTRU/avx2/consts.c). They establish the API,
call graph, terminal representation, and pre-expanded constant layout.

Then use this order:

1. `ntt.s` -- learn the forward dataflow and physical layout.
2. `basemul.s` -- learn why the transform emits that layout.
3. `invntt.s` -- read the reverse shuffle and normalization strategy.
4. `reduce.s` -- separate the modulus-specific reducer from generic scheduling.
5. `baseinv.s` -- study the most aggressive register and latency schedule.
6. `pack.s` -- study serialization independently of NTT-domain layout.

## 1. `ntt.s`: the main scheduling reference

[`ntt.s`](../third_party/NTTRU/avx2/ntt.s) is the best first read.

Its eight transform levels are arranged by physical working set rather than as
eight uniform source-level loops:

- Levels 0 and 1 handle the wide-stride butterflies separately.
- Levels 2 through 7 are fused into a per-block loop, keeping independent
  coefficient streams live across several layers.
- Each fixed-factor Montgomery multiplication is expressed with paired low and
  high products: `vpmullw`, `vpmulhw`, correction `vpmulhw`, then `vpsubw`.
- Independent multiply chains are issued in groups before their dependent
  corrections. This exposes instruction-level parallelism instead of finishing
  one butterfly at a time.
- The table stores expanded `factor*qinv` and `factor` forms in the lane shape
  needed by the consumer. The hot path does not construct twiddle vectors.
- Layout changes are fused into the transform: cross-128-bit `vperm2i128`,
  64-bit `vpunpck*`, and progressively narrower shift/blend networks appear as
  butterfly distance shrinks.
- The test suite exercises `out == in`, so load/store ordering is part of the
  in-place contract.

The strongest NTRU+ comparison is not the stage count. It is the decision to
group independent Montgomery chains and to make the last transform stores
match the pointwise consumer. The active Good-Thomas experiment already uses
the same principles in its prepacked tables and SoA handoff; NTTRU is a compact
production example of the complete approach.

Do not copy its twiddle offsets, eight-level schedule, or final permutation.
NTRU+ stops at quartic blocks after seven production layers.

## 2. `basemul.s`: consumer-driven layout

[`basemul.s`](../third_party/NTTRU/avx2/basemul.s) consumes 256 cubic terminal
blocks. Sixteen blocks occupy three YMM vectors holding their three
coefficients. One loop handles a positive-zeta group and a negative-zeta group,
so each iteration advances by 32 blocks.

Points worth studying:

- Inputs are already in coefficient-SoA form; there is no standalone transpose.
- Low-half Montgomery premultipliers are prepared once and reused across
  several products.
- Independent coefficient products are accumulated before the zeta-dependent
  wrap terms, reducing live-range churn.
- Positive and negative zeta cases share almost the same schedule, making the
  sign difference explicit and auditable.
- The table pointer advances with the terminal-block loop, so address
  generation remains simple and public.

The active NTRU+ production kernel instead consumes quartic blocks and four YMM
coefficient vectors. Its algebra therefore differs, but the NTTRU scheduling
question remains useful: can premultipliers and zeta products be reused across
more independent quartic terms, and can producer stores exactly match the
consumer loads?

## 3. `invntt.s`: reverse layout plus sparse checkpoints

[`invntt.s`](../third_party/NTTRU/avx2/invntt.s) reverses both the arithmetic
and the physical permutations of `ntt.s`.

- Levels 0 through 4 operate on six loaded YMM vectors and perform the
  narrow-distance shuffles in registers before a store.
- Levels 5 and 6 use a shared variable-distance loop.
- Level 7 combines the widest butterfly with the final scaling operations.
- `reduce2` checkpoints appear only where the lazy range requires them, rather
  than after every butterfly.
- The shuffle sequence is the reverse structural map of the forward kernel,
  which makes the forward/inverse pair more useful than either file alone.

The active NTRU+ inverse is already organized in the analogous broad groups
`6..3`, `2`, `1`, and `0`. NTTRU is useful for auditing whether loads,
reductions, shuffles, and stores are ordered to hide multiply latency. Its
normalization constants and reduction locations remain tied to `q=7681` and
its cubic output layout.

## 4. `reduce.s`: elegant, but modulus-specific

[`reduce.s`](../third_party/NTTRU/avx2/reduce.s) is the easiest file to
understand and the most dangerous one to copy blindly.

For `q = 7681 = 8192 - 511`, it splits a signed 16-bit value around bit 13 and
uses

```text
x = low13 + 8192*high
  = low13 + 511*high  (mod 7681).
```

The assembly realizes `511*high` as `-high + (high << 9)`. It processes six
YMM vectors, or 96 coefficients, per iteration. `poly_freeze` follows the fold
with branch-free sign masks and conditional additions/subtractions of `q`.

This exact identity does not apply to `q=3457`. What is reusable is the method:
search for a modulus-specific fold that maps well to packed 16-bit operations,
prove its full input and output ranges, and unroll enough independent vectors
to cover shift/add latency. Any NTRU+ reducer inspired by this file needs a new
congruence proof and exhaustive range test.

## 5. `baseinv.s`: the most interesting latency schedule

[`baseinv.s`](../third_party/NTTRU/avx2/baseinv.s) is the densest and most
instructive file.

For each pair of positive/negative-zeta cubic groups it:

1. computes the cubic adjugate coefficients and determinant;
2. keeps two determinant vectors live together;
3. evaluates a fixed Fermat inversion chain ending at `a^7679 = a^(q-2)`;
4. scales all three adjugate coefficients by the inverse determinant; and
5. folds zero-determinant lane masks into one scalar return value without a
   secret-dependent branch.

The exponentiation chain interleaves the two determinant vectors at every
squaring/multiplication level. This is the clearest example in the repository
of using independent SIMD work to cover multiply latency.

The active NTRU+ path has a different and generally better global strategy for
its contract: ASM produces quartic adjugates and 12 vectors of denominators,
C performs one 12-vector batch inversion, then scales the adjugates. A direct
port of NTTRU's repeated `q-2` exponentiation would discard that advantage.
Useful candidates to borrow are narrower:

- interleave independent chains inside the one field inversion;
- keep denominator/adjugate values in their eventual consumer order;
- aggregate zero tests with vector masks and one public return value; and
- inspect whether the final adjugate scaling can be scheduled or fused more
  tightly around the batch-inversion boundary.

The source also manually realigns the stack and lacks unwind annotations. This
is a historical implementation detail, not a pattern to reproduce unchanged.

## 6. `pack.s`: direct bitstream formation

[`pack.s`](../third_party/NTTRU/avx2/pack.s) contains three exported routines:

- `poly_pack_uniform`: 256 13-bit coefficients become 416 bytes per loop;
- `poly_unpack_uniform`: the inverse 416-byte-to-256-coefficient mapping; and
- `poly_pack_short`: 128 short coefficients become 32 bytes after adding one
  and combining eight 2-bit streams.

Uniform packing uses only vector shifts, additions, and unaligned stores. It
does not first scatter coefficients to scalar temporaries. The unpacker loads
the 13 packed vectors and reconstructs 16 coefficient vectors with shifts and
the 13-bit mask. This is a useful model for deriving a straight-line pack
network from a fixed bit width.

NTRU+ uses 12-bit coefficients, so the shift schedule and byte counts differ.
The transferable idea is to derive pack and unpack together, keep their chunk
boundaries symmetric, and test exact byte compatibility. Note that NTTRU's
header declares `poly_unpack_short`, but this revision does not implement or
call that symbol.

## Cross-file lessons to try in NTRU+768

Prioritize these experiments:

1. Compare the production `ntt.s`/`invntt.s` dependency order with NTTRU's
   grouped low-products, high-products, corrections, and updates. Measure a
   schedule-only candidate with identical NTRU+ arithmetic and layout.
2. Audit whether each NTRU+ twiddle table is already stored in the exact lane
   shape consumed by the kernel. Remove only runtime broadcasts or shuffles
   that can be safely moved to generated public tables.
3. Treat forward NTT, terminal basemul, and inverse NTT as one layout pipeline.
   Reject a faster isolated transform if it adds a full-polynomial transpose.
4. Compare NTTRU's two-stream inversion-chain interleaving with the single
   inversion inside NTRU+'s 12-vector batch inversion, without replacing the
   batch strategy.
5. For serialization, generate a 12-bit NTRU+ shift network and verify exact
   round trips and KAT bytes before benchmarking.

Do not begin with `reduce.s`: its short sequence is attractive precisely
because `7681 = 2^13 - 511`, a property NTRU+'s `3457` does not share.

## Remote AVX2 validation

The untouched NTTRU revision was copied to a temporary directory and tested on
2026-07-21.

Environment:

- Host: `pinhao@172.25.166.141`, SSH port `51208`
- CPU: AMD Ryzen 7 9700X, 8 cores / 16 threads, AVX2 available
- OS: Linux `7.1.0-0.rc1.260501g26fd6bff2c050.13.fc45.x86_64`
- Compiler: GCC 16.1.1 20260703
- OpenSSL: 4.0.1
- Governor: `performance`
- Timing affinity: CPU 2
- Source directory: `/tmp/nttru-avx2-65bb4da.EtND2q/avx2`
- Build flags: upstream `-Wall -march=native -mtune=native -O3
  -fomit-frame-pointer`, linked with `-lcrypto -ldl`

Commands:

```sh
make clean
make all

taskset -c 2 test/test_poly
taskset -c 2 test/test_ntru
taskset -c 2 test/test_kem
```

All three binaries were run once unpinned and five times pinned. There was no
`Failure` or `Messages don't match` output in any run.

Correctness coverage from the upstream harness:

| Binary | Cases per run | Checked relation |
| --- | ---: | --- |
| `test/test_poly` | 512 | NTT multiplication vs naive ring multiplication; nonconstant coefficients after multiply-by-inverse |
| `test/test_ntru` | 512 | key generation, encryption, decryption, message equality |
| `test/test_kem` | 1024 | KEM key generation, encapsulation, decapsulation, shared-key equality |

Median of the five pinned runs' reported medians:

| Harness measurement | TSC ticks |
| --- | ---: |
| Forward NTT | 417 |
| NTRU key generation | 2735 |
| NTRU encryption | 1291 |
| NTRU decryption | 835 |
| KEM key generation | 3115 |
| KEM encapsulation | 3190 |
| KEM decapsulation | 3913 |

These are upstream-harness TSC ticks, not hardware-cycle counts. The default
build uses unsynchronized `rdtsc`, subtracts the minimum measured timer
overhead, and does not isolate the SMT sibling. Treat the values as a local
orientation baseline, not as an apples-to-apples performance comparison with
NTRU+: the schemes, moduli, serialization, randomness/hash paths, and test
harnesses differ.

The upstream correctness harness also has two important limitations. A
mismatch prints a message but still exits with status zero, which is why the
run was judged by both exit status and failure-text inspection. In addition,
the base-inversion check tests coefficients `1..767` of `a * a^-1` but neither
checks coefficient zero against one nor checks `poly_baseinv`'s return value.
The result above is therefore upstream-test compatibility, not a complete
independent differential validation.

GCC 16 emitted warnings in the legacy AES helper for `_bswap` macro
redefinitions, an unknown `#pragma unroll`, and array-parameter declaration
differences. The AVX2 assembly compiled successfully, and the warnings did not
affect the recorded correctness runs.

## Porting and security boundary

Passing these tests establishes consistency with NTTRU's own tested relations;
it does not establish NTRU+ compatibility, constant-time behavior, complete
range safety, or production security. Any borrowed schedule must preserve the
active NTRU+ ABI, terminal layout, Montgomery domain, reduction checkpoints,
in-place behavior, and KAT bytes. Arithmetic or representation changes require
new differential tests and range proofs before timing results are meaningful.
