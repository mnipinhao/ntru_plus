# NTRU+768 AVX2 benchmark harness

This directory benchmarks the existing production AVX2 pipeline and the GT SoA
forward, pointwise, inverse, and full-polynomial prototypes on an x86-64 host.
Correctness is a mandatory gate and setup work stays outside measured regions.

## Operations

| Name | Implementation | Included work |
| --- | --- | --- |
| `ntt` | production AVX2 | one forward NTT |
| `gt-ntt` | GT intrinsic prototype | one forward GT NTT |
| `gt-ntt-asm-soa` | GT hybrid ASM prototype | intrinsic frontend/stage 1+2, hand-scheduled stage 3+4+5, and fused 16-block SoA store |
| `gt-frontend` | GT AVX2 intrinsic region | CRT-indexed loads, top split, branch twist, and DFT3 into frontend scratch |
| `gt-frontend-asm` | GT hand-scheduled ASM region | the same exact frontend boundary using generated input-offset and packed twist/qinv tables, with no stack traffic |
| `gt-stage12` | GT AVX2 intrinsic region | prepared frontend scratch through NTT32 stage 1+2 |
| `gt-stage12-asm` | GT hand-scheduled ASM region | the same exact stage2 boundary with interleaved Montgomery chains and no stack traffic |
| `gt-stage12-identity-asm` | GT identity-reducer Stage12 candidate | the same prepared frontend scratch through stage 1+2, replacing only factor-`R` Montgomery identities with the signed reducer |
| `gt-frontend-stage12-asm` | GT fused forward producer | one ASM entry and one 1536-byte semantic frontend scratch; no internal calls or compiler spill slots |
| `gt-frontend-stage12-identity-asm` | GT lazy-reducer producer | canonical frontend plus signed identity reduction at the factor-`R` stage1+2 sites |
| `gt-frontend-stage12-{u2,u4}-asm`, `gt-frontend-stage12-{u2,u4}-identity-asm` | GT pipelined producer candidates | preload the next CRT-indexed pair during the current DFT3 tail, with two- or four-pair loop bodies |
| `gt-ntt-fixed-high-first-native-centered-pipelined-asm` | GT fixed-displacement native candidate | fully unrolled 16-pair high-first frontend with generated public CRT load displacements |
| `gt-ntt-wide-high-first-native-centered-pipelined-asm` | GT Q/Q+3 wide-load candidate | one 32-byte load plus `vpermq` handles each non-wrapped public CRT row; fixed stores retain the native forward contract |
| `gt-ntt-wide-fused-delayed-native-centered-pipelined-asm` | GT wide/fused/delayed candidate | consumes duplicated Q/Q+3 loads in fused split/twist chains and delays 24 centered reductions to the Stage3→4 boundary |
| `gt-ntt-wide-fused-delayed-row2q2-native-{centered,lazy}-pipelined-asm` | GT adjacent-Q Stage1/2 candidates | processes two singleton-row Q objects in each YMM; lazy omits only the final Stage5 center |
| `gt-ntt-wide-fused-partial-n0-native-centered-pipelined-asm` | GT partial cross-pair experiment | moves only the next pair's `n3=0` fused split/twist chain into the current DFT3/store tail; retained as a default-off negative control |
| `gt-frontend-stage12-direct-asm`, `gt-frontend-stage12-half-asm` | GT handoff candidates | stripe-first stage2 producers with zero or 768-byte frontend semantic handoff; both retain canonical 1536-byte stage2 output |
| `gt-stage345-{serial,interleaved,remapped,resident,queued-store}-asm` | GT isolated Stage345 schedules | consume a prepared canonical stage2 scratch and compare butterfly/Barrett/transpose/SoA-store schedules without producer work |
| `gt-stage345-{centered,centered-queued}-asm` | GT centered-checkpoint schedules | centered variants of the remapped and queued-store schedules, using the three-instruction signed representative checkpoint |
| `gt-stage345-native-centered-asm` | GT native-layout Stage345 | centered arithmetic plus lane-local transpose, direct branch/coefficient stores, and no cross-half `vperm2i128` packing |
| `gt-ntt-frontend-asm-soa` | GT forward ASM prototype | fused frontend/stage1+2 followed by the existing hand-scheduled stage3+4+5/SoA store |
| `gt-ntt-{direct,direct-interleaved,direct-queued-store,half,remapped,half-remapped,resident,queued-store}-asm-soa` | GT full-forward candidates | compose the listed producer and Stage345 schedules; `direct-queued-store` combines both experiment families |
| `gt-ntt-{centered,centered-queued,identity,identity-centered,identity-centered-queued}-asm-soa` | GT reducer-only forward compositions | isolate centered final reduction, identity stage reduction, and their queued-store composition |
| `gt-ntt-{u2,u4}-identity-centered-queued-asm-soa` | GT selected-idea SoA compositions | pipelined producer, identity stage reducer, centered final reducer, and queued existing-SoA stores |
| `gt-ntt-{identity,u2-identity,u4-identity}-native-centered-asm` | GT native full-forward candidates | emit the new 12-batch native NTT-domain layout; no basemul or inverse is included |
| `gt-ntt-{u2,u4}-identity-native-centered-fused-asm` | GT single-entry native forwards | inline the selected producer and native Stage345 in one two-argument ASM symbol with two disjoint 1536-byte stack regions and no internal call |
| `basemul` | production AVX2 | one pointwise/base multiplication on prepared NTT inputs |
| `gt-basemul-soa` | GT AVX2 intrinsic prototype | 192 quartic products as 12 batches of 16 blocks; prepared SoA inputs and lambda-table generation are excluded |
| `gt-basemul-native-asymmetric` | GT direct native consumer | the same 192 quartics on prepared centered-by-lazy native inputs with native-order lambda tables |
| `gt-basemul-{soa,native-asymmetric}-rminus1[-c0lazy]-asm` | GT R^-1 pointwise candidates | remove the R² finalizers; the safe variant checkpoints all coefficients and c0-lazy checkpoints only c1..c3 |
| `gt-native-forward2-basemul-{centered,asymmetric}-boundary` | separate-symbol native boundary | two full forwards plus direct native basemul; retained to expose the two-code-image I-cache regression |
| `gt-native-forward2-basemul-runtime-{centered,asymmetric}-boundary` | shared-code native boundary | two calls to one runtime-center forward symbol plus direct native basemul; this is the current adoption gate |
| `invntt` | production AVX2 | one inverse NTT on a prepared valid NTT input |
| `gt-invntt32` | GT AVX2 intrinsic region | direct-SoA inverse NTT32 through the packed Barrett scratch boundary |
| `gt-invntt32-asm` | GT hand-scheduled ASM region | the same inverse NTT32 scratch boundary, using all 16 YMM registers and no stack |
| `gt-invdft3` | GT AVX2 intrinsic region | prepared inverse-NTT32 scratch through inverse DFT3 and three packed Barrett checkpoints |
| `gt-invdft3-asm` | GT hand-scheduled ASM region | the same in-place DFT3 boundary, with three interleaved Barrett chains and no stack |
| `gt-invpost` | GT AVX2 intrinsic region | prepared inverse-DFT3 scratch through untwist, branch merge, normalization, 4×8 transpose, and final stores |
| `gt-invpost-asm` | GT hand-scheduled ASM region | the same postprocess boundary with four interleaved coefficient chains and no stack |
| `gt-invntt-soa` | GT AVX2 intrinsic prototype | direct SoA inverse NTT32, inverse DFT3, untwist, normalization, branch merge, and canonical stores |
| `gt-invntt-soa-hybrid` | GT partial ASM inverse | hand-scheduled inverse NTT32 followed by intrinsic inverse DFT3 and postprocess |
| `gt-invntt-soa-dft3-hybrid` | GT two-region ASM inverse | hand-scheduled inverse NTT32 and DFT3 followed by intrinsic postprocess |
| `gt-invntt-soa-postprocess-hybrid` | GT three-region ASM inverse | three separately callable hand-scheduled regions with C-owned row scratch |
| `gt-invntt-soa-fused-asm` | GT fused ASM inverse | one ASM entry, one 1536-byte scratch, no internal calls, and one terminal `vzeroupper` |
| `polymul` | production AVX2 | two NTTs, basemul, and inverse NTT |
| `gt-polymul-soa` | GT hybrid/intrinsic prototype | two hybrid ASM SoA NTTs, SoA basemul, and direct SoA inverse |
| `gt-polymul-soa-hybrid` | GT partial ASM inverse pipeline | the same GT path with the hand-scheduled inverse NTT32 region |
| `gt-polymul-soa-dft3-hybrid` | GT two-region ASM inverse pipeline | the same GT path with hand-scheduled inverse NTT32 and DFT3 regions |
| `gt-polymul-soa-postprocess-hybrid` | GT three-region ASM inverse pipeline | the same GT path with all three inverse regions hand-scheduled |
| `gt-polymul-soa-{basemul-asm,rminus1-asm,rminus1-c0lazy-asm}-postprocess-hybrid` | GT pointwise-domain comparison | paired full paths using normal, safe R^-1, or c0-lazy R^-1 basemul with matching inverse normalization |
| `gt-polymul-soa-fused-asm` | GT fused inverse pipeline | the same GT path using the single-entry inverse ASM |
| `gt-polymul-frontend-fused-asm` | GT forward+inverse ASM pipeline | hand-scheduled frontend/stage1+2 and stage3+4+5, SoA basemul, and fused inverse ASM |
| `gt-polymul-{identity,u2-identity,u4-identity}-centered-queued-fused-asm` | GT reducer/pipeline compositions | two matching SoA forwards, SoA basemul, and fused inverse ASM |
| `gt-polymul-{direct,direct-interleaved,direct-queued-store,half,remapped,half-remapped,resident,queued-store}-fused-asm` | GT full-polymul candidates | two matching candidate forwards, SoA basemul, and fused inverse ASM |

The canonical GT ASM prototype uses the candidate SoA mapping
`batch=4*k3+Q/8, lane=8*branch+Q%8`.  Its packed int16 Barrett checkpoint emits
a bounded `[0,q]` representative rather than the intrinsic path's centered
representative; validation therefore compares modulo `q` after applying the
mapping oracle.

Centered candidates emit `[-3080,3079]`.  Native output uses different batch
lanes and is validated by a test-only conversion to SoA: serial-arithmetic
candidates compare byte-exactly, while fused-arithmetic candidates compare
modulo `q`.  That conversion is never included in a timed operation.  Native
basemul now uses a generated lane-permuted lambda table and preserves native
layout; native inverse first-load mapping remains future work.

The two-entry and single-entry U2/U4 native timing targets all write the same
32-byte-aligned output arena.  This keeps output address/cache-color effects
out of paired sub-1% comparisons; validation outputs remain separate so each
candidate is still checked independently.  The single-entry prototype test
also places 32-byte guard bands before and after its 768-word output.

The GT prototype now has matching intrinsic pointwise and inverse kernels, so
the harness measures the complete GT polynomial multiplication.  The isolated
Stage345, SoA basemul, and inverse-region operations use prepared inputs and
exclude their producers.  `--validate` covers u2/u4 exact boundaries, reducer
representative ranges, native mapping, and the matching full-polymul
compositions.  The prototype test also covers independently filled
`±5*(q-1)` stage2 scratch and public-wrapper in-place calls.  NTRU+768 has no
scheme-level matrix-vector multiplication; `basemul_add` and KEM components are
the relevant future caller benchmarks.

## Build and validate

The default build is AVX2-only and tuned for the benchmark host without enabling
AVX-512:

```sh
make build
make asm-audit
make validate
make kpqc-audit
```

`BENCH_LDFLAGS` may be used for benchmark-linker controls.  The recorded
single-entry run used an ELF `EXEC` binary, so symbol addresses and code layout
were inspected in the same linked form that was measured.

Default target flags:

```text
-march=x86-64-v3 -mtune=znver5 -mprefer-vector-width=256
```

`make validate` runs the production AVX2 scheme test, the GT prototype's
boundary/differential tests, and the benchmark harness's round-trip,
schoolbook-polymul, and GT-reference checks.

`make kpqc-audit` verifies that the production arithmetic sources linked here
(`ntt.s`, `invntt.s`, `basemul.s`, `consts.c`, and `poly.c`) are byte-identical
to `ntruplus-KpqC-Final/Additional_Implementation/avx2/NTRU+768`.  Therefore
the production NTT/basemul/inverse/polymul rows are also the KPQC Final AVX2
baseline when compiler and target flags are held fixed.

## Reproducible benchmark run

```sh
CORE=2 PERF_PREFIX= ./run_bench.sh
```

If hardware counters require privilege:

```sh
CORE=2 PERF_PREFIX=sudo ./run_bench.sh
```

The runner records:

- CPU model and topology;
- pinned core and its SMT sibling list;
- governor and boost state;
- compiler, build flags, kernel, and perf version;
- `perf stat` hardware cycles, repeated five times by default.

The default performance result is only `cycles`; this is the common metric used
for prototype comparisons.  Extra counter groups remain opt-in through
`PERF_CORE_EVENTS` and `PERF_CACHE_EVENTS`, and run in separate passes to avoid
unnecessary multiplexing.

`perf stat` wraps the whole benchmark process, so the count also includes fixed
input preparation, warmups, checksum, and reporting.  Reported cycles/call are
therefore amortized whole-process values.  Same-binary candidates share almost
all of that setup; for sub-1% comparisons, rebuild with a larger
`BENCH_PERF_ITERATIONS` (the final Stage345 checks use 1,000,000), repeat both
sequential operation orders, and describe the result as a same-harness signal.

The older serialized-TSC sampler remains available as a diagnostic with
`RUN_TSC=1`, but it is disabled by default and is not used for performance
conclusions.

Defaults are 100 warmups, 1000 calls per sample, 101 samples, 64 rotating input
sets, and 100000 calls for each perf loop.  Override them at build time, for
example:

```sh
make clean
make build CFLAGS='-O3' TARGET_FLAGS='-march=x86-64-v3 -mtune=znver5 -mprefer-vector-width=256 -DBENCH_NTESTS=31'
```

The runner pins the process but cannot guarantee the SMT sibling is idle.  For
release numbers, disable SMT or reserve both sibling CPUs.  It also records
Turbo/boost state; use `STRICT_ENV=1` to reject an active boost setting instead
of merely warning.

Results are written under `results/<UTC timestamp>/` and are ignored by git.

For same-binary, explicitly ordered subsets, override `OPERATIONS`, for example:

```sh
OPERATIONS='gt-stage345-serial-asm gt-stage345-queued-store-asm gt-ntt-frontend-asm-soa gt-ntt-queued-store-asm-soa' \
PERF_REPETITIONS=10 CORE=2 ./run_bench.sh
```
