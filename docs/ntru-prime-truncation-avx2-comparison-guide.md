# NTRU Prime truncation AVX2 reading and NTRU+768 comparison guide

This note records what is worth learning from Vincent Hwang's truncated-Rader
AVX2 polynomial multiplier for `sntrup761`, how it differs from both NTTRU and
the active NTRU+768 AVX2 lane, and which ideas are plausible NTRU+ experiments.

For a shorter concept-first Chinese explanation, start with
[`ntru-prime-truncation-avx2-essence-zh.md`](ntru-prime-truncation-avx2-essence-zh.md).

## Scope and source

- Upstream: <https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation>
- Paper: [Pushing the Limit of Vectorized Polynomial Multiplications for NTRU Prime](https://eprint.iacr.org/2023/604)
- Reviewed revision: `3eb881fb4aa83a9c424a121acefb1b8d35cf6f93`
- Reviewed lane: [`third_party/NTRU_Prime_truncation/avx2/avx2_bench/`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/)
- Active comparison lane: [`ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/`](../ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/)
- License: CC0-1.0

The checkout is ignored by the outer repository and retains its own Git
history. The paper's central contribution is more important than any isolated
instruction sequence: choose an algebraic decomposition whose subproblem
dimensions match the vector register before scheduling the assembly.

## First correction: this is not another NTRU+ NTT implementation

The implementation exports a complete `sntrup761` polynomial multiplication,
not a drop-in forward-NTT/basemul/inverse-NTT interface. Its transform ring,
modulus, output reduction, scaling, and scratch contract are different from
NTRU+768.

| Contract | NTRU Prime truncation AVX2 | Active NTRU+768 AVX2 |
| --- | --- | --- |
| Scheme polynomial size | `p = 761` | `N = 768` |
| Modulus | `q = 4591` | `q = 3457` |
| Scheme ring | `Z_q[x]/(x^761-x-1)` | `Z_q[x]/(x^768-x^384+1)` |
| Multiplication working domain | `Z_q[x]/Phi_17(x^96)`, degree 1536 | native-ring NTT ending in 192 quartic blocks |
| SIMD endpoint | 48 cyclic plus 48 negacyclic size-16 rings | 192 quartic terminal blocks |
| Lane interpretation at multiplication | one coefficient position across 16 independent rings | one coefficient position across 16 terminal blocks |
| Small multiplication | CT/Bruun decomposition plus size-8 Karatsuba | quartic basemul with ring-specific zeta |
| Public arithmetic API | whole `mulcore` and `polymul` | separate NTT, basemul, inverse NTT, and polymul |
| Final step | fold modulo `x^761-x-1` and remove accumulated scale | inverse transform for the NTRU+ ring |

Even the superficially similar count `192` means different things. The paper's
AVX2 path performs 192 size-8 polynomial multiplications after decomposing 96
size-16 cyclic/negacyclic subproblems. NTRU+ production has 192 quartic
terminal blocks. Formulas, tables, and layouts are not interchangeable.

## The whole pipeline

The call graph is easiest to understand from `_mulcore` in
[`__avx2.c`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/__avx2.c):

```text
761 coefficients, zero padded
    |
    | truncated Rader-17 x 6 calls per operand
    v
16 copies of a cyclic size-96 problem
    |
    | Good-Thomas 3 x 2 plus twist
    v
48 cyclic and 48 negacyclic size-16 problems
    |
    | fused twist + 16 x 16 transpose
    v
six groups; every YMM lane is one independent size-16 problem
    |
    | cyclic CT/Karatsuba or negacyclic Bruun/Karatsuba
    v
inverse transpose + inverse twist
    |
    | inverse Good-Thomas, inverse truncated Rader
    v
1536-coefficient scaled product
    |
    | fold x^761 = x + 1, remove scale
    v
761-coefficient sntrup761 product
```

For each input, `_mulcore` makes six calls to
`__asm_rader17_truncated`, one call to `__asm_3x2_pre`, and six calls
to `twist_transpose_pre`. It then makes three cyclic and three negacyclic
size-16 multiplication calls. The reverse path makes six transpose calls, one
`__asm_3x2_post`, and six inverse-Rader calls.

The degree-1536 working ring is deliberate. A product of two degree-at-most-760
polynomials has degree at most 1520, so it can be recovered before the final
reduction modulo `x^761-x-1`. The cyclotomic form simultaneously exposes a
truncated size-17 transform whose nontrivial part has size 16: exactly the
number of signed 16-bit values in one AVX2 YMM register.

## Recommended reading order

1. Read Sections 3 and 4 of the paper for “vectorization-friendly” and
   “permutation-friendly”; the source layout is difficult to infer from
   assembly alone.
2. Read [`params.h`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/params.h)
   and [`NTT_params.h`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/NTT_params.h)
   to establish the ring, Montgomery constants, and scaling contract.
3. Read `_mulcore` and `polymul` in
   [`__avx2.c`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/__avx2.c)
   as the authoritative dataflow.
4. Read the two intrinsic `twist_transpose_*` functions in that same file.
   They explain the lane layout consumed by the assembly kernels.
5. Read [`rader17.S`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/rader17.S)
   and [`radix_3x2.S`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/radix_3x2.S)
   for the outer transformations.
6. Read [`basemul.S`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/basemul.S)
   together with [`butterflies.inc`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/butterflies.inc)
   for the cyclic/negacyclic size-16 kernels.
7. Use [`basemul_core.inc`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/basemul_core.inc)
   as a macro reference, not as the first file to read.
8. Finish with [`__avx2_const.c`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/__avx2_const.c)
   and [`gen.c`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/gen.c)
   to connect the table layout back to the algebra.

The copies under `avx2/avx2/` are the integration sources. The `avx2_bench/`
copies are preferable for learning because the test and microbenchmark make
the operation boundaries explicit.

## 1. Truncated Rader-17: remove the component that does not belong

[`rader17.S`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/rader17.S)
implements transforms for `Phi_17`, not a padded 17-point transform with a
dummy output. Rader's discrete-log permutation turns the 16 nonzero indices
into a cyclic convolution of length 16. This is the key alignment:

```text
17-point prime structure
    -> discard the trivial cyclotomic component
    -> 16 useful components
    -> 16 packed int16 lanes
```

The source then decomposes the length-16 convolution into power-of-two
cyclic/negacyclic work and uses all 16 YMM registers. Fixed factors and their
`qinv` forms are supplied in full lane-expanded tables. Independent low/high
products are grouped before their corrections, as in NTTRU, but the larger
lesson is that truncation eliminated an awkward component before instruction
scheduling began.

The kernel manually aligns the stack and reserves 1536 bytes. It is valuable
as an arithmetic/layout reference, but its hand-written prologue has no unwind
metadata and should not be copied as a production ABI template.

## 2. Good-Thomas 3-by-2: exploit coprime structure without twiddles

[`radix_3x2.S`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/radix_3x2.S)
turns each size-96 cyclic problem into six size-16 problems by using the
coprime factors 3 and 2. The `pre` and `post` variants incorporate the twist
tables needed by the neighboring representations.

Its loop body is a compact scheduling lesson:

- six vectors are loaded in the Good-Thomas order;
- additions and subtractions for two independent branches are interleaved;
- the two omega-3 Montgomery products are issued together; and
- public pointer increments advance exactly six YMM vectors per iteration.

There is no generic transform dispatcher in the hot path. The source commits
to the one factorization and memory order required by `sntrup761`.

## 3. `twist_transpose_*`: fuse representation changes

The intrinsic functions in
[`__avx2.c`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/__avx2.c)
are the most directly transferable code to the current NTRU+ Good-Thomas
experiments.

`twist_transpose_pre` loads the even rows of a 31-by-16 view, applies each
row's Montgomery twist, and performs a complete 16-by-16 transpose with:

- `vpunpckl/hwd` for 16-bit pairs;
- `vpunpckl/hdq` for 32-bit groups;
- `vpunpckl/hqdq` for 64-bit groups; and
- `vperm2i128` for the final cross-lane exchange.

The output view is:

```text
YMM coefficient 0 = coefficient 0 from 16 independent rings
YMM coefficient 1 = coefficient 1 from 16 independent rings
...
YMM coefficient 15 = coefficient 15 from 16 independent rings
```

Thus, a vector-by-vector multiply performs the same scalar operation in 16
independent rings. `twist_transpose_post` reverses the map and applies the
inverse twist before storing. There is no separate full-array twist pass and no
separate transpose pass.

This is stronger than merely making each helper fast. It removes two material
boundaries from the full multiplication pipeline.

## 4. Cyclic and negacyclic size-16 kernels

The name `basemul.S` is easy to misread. Its main exported functions perform
complete size-16 cyclic or negacyclic polynomial convolutions on 16 instances
in parallel. They are not analogous to NTRU+'s quartic terminal basemul.

- `__asm_cyclic_FFT16` splits into cyclic/negacyclic size-8 pieces and uses
  Karatsuba subproducts.
- `__asm_negacyclic_FFT16` uses Bruun butterflies before and after the size-8
  Karatsuba work.
- `__asm_weighted_karatsuba16` is an alternate standalone kernel exposed by
  the microbenchmark.

The cyclic and negacyclic cases are separate straight-line routines. That
duplicates code, but it removes signs, twiddles, and branches from the hot
path. The reviewed Zen 5 binary's `text` section was 52,889 bytes; key kernels
are several kilobytes each. This implementation consciously trades instruction
footprint and stack scratch for fewer arithmetic subproblems.

## 5. Arithmetic macros: precomputation plus independent chains

[`basemul_core.inc`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/basemul_core.inc)
defines several variants instead of forcing every call site through one macro:

- ordinary Montgomery multiplication;
- two independent Montgomery products interleaved as `x2`;
- fixed-operand multiplication with precomputed `operand*qinv`;
- register/memory variants; and
- Barrett reducers interleaved in groups of two, three, or four.

The precomputed form removes one `vpmullw` from a fixed-factor chain. The `x2`
and `x3`/`x4` forms issue the same dependency level for several independent
vectors before consuming results. This is the same latency-hiding principle
seen in NTTRU, expressed as a small assembly macro vocabulary.

`vpmulhrsw` is used in the Barrett reducer with `Qbar = 7`. That constant and
its proven input range are specific to `q=4591`; neither can be transplanted to
NTRU+'s `q=3457`.

## 6. The final fold is part of the SIMD contract

`polymul` does not return the degree-1536 intermediate. It applies the
`x^761 = x + 1` fold and the final Montgomery scaling in a vector loop.
`ARRAY_N = 1632` gives the implementation enough padded storage for its
fixed-width loads near the logical boundary.

This is a useful reminder for NTRU+ work: output reduction and padding should
be designed together with the multiplier, but the raw-pointer API does not
express the required allocation size. Any reuse needs explicit wrapper and
guard tests; copying only the loop would risk out-of-bounds reads and the wrong
ring reduction.

## What differs from the NTTRU lesson

The two external AVX2 implementations are complementary references:

| Question | Better first reference |
| --- | --- |
| How should a conventional NTT, basemul, and inverse pipeline be hand-scheduled? | NTTRU |
| How can transform choice eliminate vector-unfriendly subproblems? | NTRU Prime truncation |
| How should twiddle/qinv pairs be pre-expanded? | both |
| How can a terminal SoA layout remove a transpose? | NTTRU |
| How can twist and a 16-by-16 instance transpose be fused? | NTRU Prime truncation |
| How should full-pipeline cost guide an isolated kernel choice? | both |

NTTRU is a compact production example of consumer-driven NTT layout. NTRU
Prime truncation is a more radical example of changing the mathematical route
so that the machine layout becomes natural.

## Transferable experiments for NTRU+768

### P0: write a lane-semantic table before writing assembly

For each GT stage, record what every YMM lane represents before and after the
stage. Require the next consumer to use the produced order directly. The
NTRU Prime transpose is readable because its 16-by-16 instance/coefficient
meaning is stable throughout the small convolutions.

### P1: fuse fixed twists with an unavoidable permutation

Audit the NTRU+ GT frontend and inverse for a permutation or transpose that is
already mandatory. If a public fixed Montgomery factor is consumed immediately
before or after it, make one differential candidate that fuses the two while
preserving the exact existing range and layout contracts.

### P2: search for quotient-direct transforms, not just faster stages

The biggest NTRU Prime win came from reducing the number of small products,
not scheduling the old transform better. For any future NTRU+ transform, count
useful terminal blocks, padded/don't-care blocks, full-array permutations, and
the exact lane occupancy before selecting the kernel family. This is an
algebra-design experiment and requires a new correctness/range proof.

### P3: specialize paired terminal shapes when it removes hot-path work

NTRU Prime keeps cyclic and negacyclic size-16 paths separate. For NTRU+, audit
whether positive/negative zeta groups or GT branches can share a schedule while
keeping sign changes explicit, or whether two specialized straight-line paths
remove enough shuffles to justify their code footprint.

### P4: keep two benchmark levels

Retain boundary microbenchmarks for Rader/GT/transpose-like regions and a full
`2*forward + basemul + inverse` NTRU+ measurement. The upstream microbenchmark
is useful for locating cost, while `polymul` determines whether eliminated
boundaries actually matter.

Do not copy the `Phi_17(x^96)` embedding, `q=4591` reducers, Rader tables,
Good-Thomas constants, Bruun formulas, final fold, or manual stack prologues.

## Remote AVX2 validation

Revision `3eb881fb4aa83a9c424a121acefb1b8d35cf6f93` was copied without its
Git metadata to a temporary directory and tested on 2026-07-22.

Environment:

- Host: `pinhao@172.25.166.141`, SSH port `51208`
- CPU: AMD Ryzen 7 9700X, 8 cores / 16 threads, AVX2 available
- OS: Linux `7.1.0-0.rc1.260501g26fd6bff2c050.13.fc45.x86_64`
- Compiler: GCC 16.1.1 20260703
- Governor: `performance`
- Boost: enabled
- Timing affinity: CPU 2; SMT sibling CPU 10 was not isolated
- Source directory: `/tmp/ntru-prime-truncation-3eb881f.JXj5d9/avx2/avx2_bench`
- Comparison flags: `-march=x86-64-v3 -mtune=znver5
  -mprefer-vector-width=256 -O3 -mavx2`

### Upstream build defect and working command

The documented `make test` fails at this revision for two source-list reasons.
The Makefile defines `COMMON_SOURCEs` but uses the undefined singular
`COMMON_SOURCE` in `SOURCEs`; the `test` and benchmark targets also omit
`ring.c`. The resulting link lacks at least `coeff_ring` and `naive_mulR`.

The upstream checkout was not patched. The correctness binary was instead
built by explicitly listing those sources:

```sh
cd avx2/avx2_bench
gcc -march=x86-64-v3 -mtune=znver5 -mprefer-vector-width=256 \
  -O3 -Wall -I../../common -mavx2 -Wl,-z,noexecstack \
  radix_3x2.S basemul.S rader17.S __avx2_const.c __avx2.c \
  ../../common/tools.c ../../common/naive_mult.c \
  ../../common/cpucycles.c ring.c -o test test.c
taskset -c 2 ./test
```

Result:

```text
mulcore finished!
polymul finished!
```

The test compares all 1536 scaled `mulcore` coefficients with a naive
convolution and all 761 `polymul` coefficients after the NTRU Prime fold. It is
only one deterministic `rand()` input pair and does not test aliasing, guard
bands, malformed inputs, or a scheme KAT. The separate upstream generator
self-check also completed with `gen finished!`. An `objdump` audit found no
ZMM or opmask registers in the comparison binary.

## Timing evidence and its boundary

The paper reports the following AVX2 cycle counts with Turbo Boost and SMT
disabled:

| Operation | Haswell | Skylake |
| --- | ---: | ---: |
| `mulcore` | 12,336 | 9,778 |
| `polymul` | 12,760 | 9,876 |

On the Ryzen 7 9700X host, the median of five pinned runs' reported medians was:

| Operation | upstream raw-TSC ticks |
| --- | ---: |
| `mulcore` | 5,852 |
| `polymul` | 6,042 |

One pinned microbenchmark run reported:

| Region | reported median TSC ticks |
| --- | ---: |
| truncated Rader forward | 1,178 |
| Good-Thomas 3-by-2 pre | 2,052 |
| fused pre-twist/transpose | 342 |
| cyclic size-16 kernel | 1,596 |
| negacyclic size-16 kernel | 2,432 |
| weighted Karatsuba-16 alternate | 3,040 |
| fused post-transpose/twist | 342 |
| Good-Thomas 3-by-2 post | 2,014 |
| truncated Rader inverse | 1,254 |

The microbenchmark labels aggregate repeated direct calls and do not correspond
one-for-one to the full `_mulcore` call counts, so the rows must not be summed
into a predicted total.

For background only, the existing validated NTRU+768 production `polymul` on
the same CPU and compiler reported a median-of-five of 1,884 serialized-TSC
ticks. This is **not a performance ranking**: the schemes, moduli, rings,
working dimensions, output contracts, and harnesses differ. In particular, the
NTRU Prime harness uses unsynchronized `rdtsc`, uninitialized benchmark input
arrays, 100,000 single-call samples, and no overhead subtraction; the NTRU+
harness uses `lfence`/`rdtscp`, rotating initialized inputs, warmups, and 1,000
calls per sample. A numeric ratio between those rows is not meaningful.

## Security and integration boundary

The reviewed assembly has fixed public loop counts and fixed-address table
accesses, but this review did not establish a complete constant-time proof,
range proof, ABI/unwind safety, or scheme-level KAT result. The upstream
polynomial test and generator self-check establish consistency for their tested
relations only.

Any NTRU+ experiment inspired by this implementation must preserve the active
ring, Montgomery domain, terminal layout, in-place behavior, coefficient
ranges, and KAT bytes. A change to the transform decomposition or reduction
identity is new algebra, not a schedule-only optimization, and needs independent
differential tests and range reasoning before performance results are useful.
