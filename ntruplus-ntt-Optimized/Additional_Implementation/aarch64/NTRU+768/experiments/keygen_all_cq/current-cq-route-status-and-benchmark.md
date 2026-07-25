# NTRU+768 AArch64 CQ Route: Current Status and Benchmark

Date: 2026-07-23

Status: selected serious experiment candidate, default-off. GT production still
uses the mixed BPQ/CQ keygen backend.

## 1. Scope

The current CQ route is a keygen-specific internal-layout experiment. It does
not change the NTRU+ wire format, encapsulation arithmetic, decapsulation
`rminus1` contract, or canonical public API bytes.

The selected candidate is:

```text
all-CQ keygen backend
+ shared generic/direct-CQ forward NTT core
```

Build flags:

```text
GT_EXPERIMENT_USE_KEYGEN_ALL_CQ
GT_EXPERIMENT_USE_KEYGEN_DIRECT_CQ_ENDPOINT
GT_EXPERIMENT_USE_KEYGEN_SHARED_NTT_CORE
```

Benchmark variant:

```text
gt_keygen_all_cq_shared_core_direct_cq
```

## 2. The Three Internal Layouts

### 2.1 Generic GT block-major

The generic production `poly_ntt` keeps the layout consumed by GT's generic
basemul/inverse path. It is used by encapsulation and decapsulation.

This is not the same memory image as KPQC's NTT-domain layout, but both
represent the same polynomial modulo the transform contract. Canonical
pack/unpack functions are responsible for the protocol byte order.

### 2.2 BPQ: block/pair/quartic

BPQ stores two complete quartics in one Q register:

```text
Q0 = [P0.c0 P0.c1 P0.c2 P0.c3 | P1.c0 P1.c1 P1.c2 P1.c3]
Q1 = [P2.c0 P2.c1 P2.c2 P2.c3 | P3.c0 P3.c1 P3.c2 P3.c3]
Q2 = [P4.c0 P4.c1 P4.c2 P4.c3 | P5.c0 P5.c1 P5.c2 P5.c3]
Q3 = [P6.c0 P6.c1 P6.c2 P6.c3 | P7.c0 P7.c1 P7.c2 P7.c3]
```

This is close to the natural pairwise result produced by the completed NTT32
Stage345 arithmetic. GT production converts generic block-major output to BPQ
for keygen.

### 2.3 CQ: coefficient-major quartics

CQ stores the same coefficient from eight quartics in one Q register:

```text
C0 = [P0.c0 P2.c0 P4.c0 P6.c0 P1.c0 P3.c0 P5.c0 P7.c0]
C1 = [P0.c1 P2.c1 P4.c1 P6.c1 P1.c1 P3.c1 P5.c1 P7.c1]
C2 = [P0.c2 P2.c2 P4.c2 P6.c2 P1.c2 P3.c2 P5.c2 P7.c2]
C3 = [P0.c3 P2.c3 P4.c3 P6.c3 P1.c3 P3.c3 P5.c3 P7.c3]
```

The lane order is:

```text
P0, P2, P4, P6, P1, P3, P5, P7
```

The `gt_keygen_bpq_lambda8` table follows this order. CQ allows one Neon
instruction to evaluate the same quartic-coefficient operation for eight
independent products.

## 3. Data Flow by Implementation

### 3.1 KPQC final

```text
sample F/G
  -> triple / add one
  -> KPQC NTT layout
  -> KPQC baseinv
  -> KPQC basemul
  -> KPQC pack
```

KPQC keeps one internal NTT-domain convention across its generic primitives.

### 3.2 Current GT production: mixed BPQ/CQ

For each sampled polynomial:

```text
coefficient input
  -> triple / add one
  -> generic GT block-major poly_ntt
  -> block-major-to-BPQ adapter
  -> BPQ
```

For inversion and multiplication:

```text
BPQ operand to invert
  -> BPQ baseinv prepare
  -> CQ numerator and denominators
  -> hierarchical K=8 batch inversion
  -> fqinv15
  -> CQ baseinv finish
  -> scaled-R CQ inverse

other BPQ operand x scaled-R CQ inverse
  -> mixed BPQ x CQ basemul
  -> CQ result
```

Key serialization:

```text
public h:       CQ -> canonical bytes
secret f:       BPQ -> canonical p1 bytes
secret hinv:    CQ -> canonical bytes
```

### 3.3 Selected all-CQ candidate

For each sampled polynomial:

```text
coefficient input
  -> triple / add one
  -> shared forward NTT Phase123
  -> completed Stage345 arithmetic
  -> in-register BPQ-to-CQ transpose
  -> fixed-offset CQ stores
  -> CQ
```

The direct-CQ NTT epilogue covers all 24 CQ groups. It uses 192 `trn`
instructions and nine parking moves, with no stack spill, raw-Q reload, or
Stage12 recomputation.

The pointwise path is:

```text
CQ operand to invert
  -> CQ baseinv prepare
  -> shared hierarchical K=8/fqinv15/finish
  -> scaled-R CQ inverse

CQ operand x scaled-R CQ inverse
  -> CQ x CQ quartic basemul
  -> CQ result
```

All three key polynomials use the CQ canonical pack.

## 4. Shared NTT Core

The first direct-CQ implementation duplicated the complete generic NTT. The
current candidate shares the common part:

```text
poly_ntt generic entry
                \
                 -> common prologue and Phase123
                /       -> generic Stage12/Stage345 suffix
direct-CQ entry         -> direct-CQ Stage12/Stage345 suffix
                         -> common epilogue and one table image
```

The endpoint selector is public and fixed by the called symbol. It is stored at
`[sp,#8]`; `[sp,#0]` remains the existing Slothy spill slot.

The shared entry overhead is:

```text
generic entry:  +6 retired instructions
CQ entry:       +4 retired instructions
```

No arithmetic, modular reduction, twiddle, or endpoint layout semantics are
changed.

## 5. KEM Call Graph Impact

### Keygen

Changed by the CQ candidate:

```text
sample NTT f
sample NTT g
baseinv f
baseinv g
basemul h
basemul hinv
pack h
pack f
pack hinv
```

### Encapsulation

No CQ pointwise path is used. It continues to use:

```text
generic GT poly_ntt(r)
generic GT poly_ntt(m)
canonical unpack h
production direct-Q31 basemul-add/pack
```

The only candidate difference is that generic `poly_ntt` enters the shared
core through the public generic selector.

### Decapsulation

No CQ pointwise path is used. It continues to use:

```text
rminus1 basemul -> poly_invntt_from_rminus1
generic GT poly_ntt(m1)
canonical verify pointwise backend
generic GT poly_ntt(r1)
```

The CQ candidate does not change the `rminus1` factor or inverse contract.
Only the two generic forward NTT calls use the shared generic entry.

## 6. Source Ownership

### Current GT production

```text
asm/gt/ntt/poly_ntt.n1.opt.S
asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S
gt/keygen_bpq_cq.c
asm/gt/keygen_bpq_cq/baseinv_prepare.S
asm/gt/keygen_bpq_cq/baseinv_tree.S
asm/gt/keygen_bpq_cq/baseinv_finish.S
asm/gt/keygen_bpq_cq/basemul.S
asm/gt/keygen_bpq_cq/pack_cq.S
asm/gt/keygen_bpq_cq/pack_bpq_p1.S
asm/gt/baseinv/poly_baseinv_fqinv15.S
```

### Selected CQ experiment

```text
experiments/keygen_all_cq/keygen_all_cq.c
experiments/keygen_all_cq/keygen_all_cq.h
asm/gt/experiment/forward_ntt/poly_ntt_shared_core_direct_cq.S
experiments/keygen_all_cq/generate_shared_core_direct_cq.py
experiments/keygen_all_cq/shared_core_direct_cq_contract.json
```

It reuses production:

```text
baseinv_tree.S
baseinv_finish.S
poly_baseinv_fqinv15.S
pack_cq.S
poly_ntt_tables.inc
```

The CQ prepare and CQ x CQ basemul are currently C with explicit Neon
intrinsics. They are not yet standalone scheduled assembly kernels.

### Integration, tests, and benchmark

```text
kem.c
make/experiments/keygen-all-cq.mk
gt_test/test_direct_cq_endpoint.c
gt_test/test_shared_core_direct_cq.c
gt_test/shared_core_ntt_abi_sentinel.S
aarch64-bench/Makefile.production
aarch64-bench/bench.c
aarch64-bench/bench_kem_runtime.c
aarch64-bench/scripts/run_gt_kpqc_component_profile.py
```

## 7. Correctness Status

Verified on Raspberry Pi 5:

```text
direct-CQ differential:       1000 cases, 0 mismatches
shared generic differential:  1000 cases, 0 mismatches
shared CQ differential:       1000 cases, 0 mismatches
generic in-place:             pass
CQ in-place:                  pass
generic ABI sentinel:         0x0
CQ ABI sentinel:              0x0
full KEM test:                count 0
```

The three deterministic benchmark variants produced the same combined
PK/SK/CT/shared-secret checksum:

```text
485833929768143945
```

This confirms the benchmark fixtures reached the same serialized outputs. It
does not replace a separately archived canonical `.rsp` KAT artifact.

## 8. Benchmark Policy

Platform:

```text
Raspberry Pi 5
Cortex-A76
Linux 6.18
GCC 14.2.0
core 3 pinned
portable NO_CE SHAKE
31 samples x 2000 calls
100 warmup calls
Linux perf cycles and instructions in separate runs
uniform -ffunction-sections -fdata-sections --gc-sections
```

Full KEM totals are decisive. Component rows use deterministic, contract-valid
fixtures and are for attribution.

Raw output and the exhaustive component table:

```text
aarch64-bench/results/cq_route_uniform_gc_2026-07-23/
```

## 9. Full-KEM Results

| Operation | KPQC p10/p50/p90 | GT production p10/p50/p90 | CQ p10/p50/p90 |
|---|---:|---:|---:|
| keygen | 39929/39937/39944 | 37745/37753/37758 | 36764/36767/36768 |
| encapsulation | 39063/39067/39073 | 37586/37590/37595 | 37601/37604/37608 |
| decapsulation | 35178/35182/35187 | 32848/32850/32852 | 32952/32955/32957 |

| Operation | GT vs KPQC | CQ vs KPQC | CQ vs GT production |
|---|---:|---:|---:|
| keygen | -2184 (-5.47%) | -3170 (-7.94%) | -986 (-2.61%) |
| encapsulation | -1477 (-3.78%) | -1463 (-3.74%) | +14 (+0.04%) |
| decapsulation | -2332 (-6.63%) | -2227 (-6.33%) | +105 (+0.32%) |

Retired instructions:

| Operation | KPQC | GT production | CQ |
|---|---:|---:|---:|
| keygen | 80801 | 86069 | 81573 |
| encapsulation | 103976 | 106173 | 106185 |
| decapsulation | 72677 | 76429 | 76441 |

The exact `+12` instructions in encapsulation and decapsulation are two
generic shared-core entries times six instructions. Their cycle differences
are small replacement-binary/code-placement effects, not CQ arithmetic.

## 10. Keygen Component Results

Cycles per call:

| Component | Count | KPQC | GT production | CQ | CQ vs GT |
|---|---:|---:|---:|---:|---:|
| sample NTT f | 1 | 3642 | 3299 | 2846 | -453 (-13.73%) |
| sample NTT g | 1 | 3639 | 3304 | 2858 | -446 (-13.50%) |
| baseinv actual | 2 | 4056 | 4039 | 3946 | -93 (-2.30%) |
| basemul actual | 2 | 2641 | 1670 | 1762 | +92 (+5.51%) |
| baseinv + basemul contract | 2 | 6694 | 5710 | 5708 | -2 (-0.04%) |
| pack public h | 1 | 458 | 566 | 568 | +2 |
| pack secret f | 1 | 458 | 619 | 568 | -51 |
| pack secret hinv | 1 | 458 | 566 | 568 | +2 |

Interpretation:

1. The two NTT/layout boundaries save about `453 + 446 = 899` cycles.
2. CQ baseinv is faster in isolation, but CQ x CQ basemul is slower than the
   production BPQ x CQ assembly.
3. The valid combined baseinv/basemul contract is effectively tied:
   `5708` versus `5710` cycles.
4. All-CQ packing mainly removes the special BPQ p1 cost for secret `f`,
   saving about 51 cycles.
5. The measured full-keygen improvement is 986 cycles. Most of it is therefore
   explained by direct-CQ NTT output and removal of the block-major/BPQ/CQ
   boundary.

The candidate pointwise pair retires 6073 instructions versus 6625 for GT
production, but its cycle count is flat because the instruction mix and
pipeline pressure differ.

## 11. Generic and Non-Keygen Diagnostics

These are generic public kernels, not the specialized keygen CQ kernels:

| Kernel | KPQC | GT production | CQ binary |
|---|---:|---:|---:|
| generic forward NTT | 3620 | 2860 | 2872 |
| generic inverse NTT | 3965 | 4079 | 4071 |
| generic basemul | 2669 | 2851 | 2858 |
| generic basemul_add | 2637 | 2951 | 2929 |
| generic baseinv | 4056 | 4983 | 4983 |
| canonical tobytes | 458 | 612 | 612 |
| canonical frombytes | 326 | 487 | 487 |

The CQ binary's generic kernels are the GT production kernels. Small cycle
differences come from the shared entry and function/code placement.

Selected actual KEM-path checks:

| Component | KPQC | GT production | CQ |
|---|---:|---:|---:|
| enc NTT r | 3458 | 2594 | 2596 |
| enc NTT m | 3441 | 2588 | 2596 |
| enc basemul-add actual | 2569 | 2287 | 2285 |
| dec first basemul actual | 2641 | 2020 | 2019 |
| dec first inverse actual | 3952 | 3555 | 3558 |
| dec verify product-to-bytes | 3425 | 3282 | 3282 |
| dec NTT m1 | 3441 | 2588 | 2596 |
| dec NTT r1 | 3458 | 2594 | 2596 |

This confirms the CQ candidate does not replace the specialized encap/decap
backends.

## 12. Code Size

Uniform section-GC full-keygen binaries:

| Variant | `.text` bytes | Delta vs GT |
|---|---:|---:|
| KPQC final | 23178 | -66656 |
| GT production | 89834 | 0 |
| shared-core all-CQ | 92794 | +2960 |

The earlier separate generic/direct-CQ implementation used 101257 bytes. The
shared core removes 8432 bytes from that shape. The remaining CQ cost over GT
production is 2960 bytes.

## 13. Current Decision

What is established:

- Direct-CQ output is correct and removes the keygen layout adapters.
- Shared-core code generation makes the code-size cost manageable.
- Full keygen improves by 986 cycles versus GT production and 3170 cycles
  versus KPQC in the uniform-GC run.
- The gain is concentrated in the two sample NTT/layout boundaries.
- Encapsulation and decapsulation algorithms remain GT production.

Why it is still default-off:

- CQ prepare and CQ x CQ basemul are Neon C, not finalized scheduled assembly.
- The baseinv/basemul pair is not faster than the existing mixed BPQ/CQ pair.
- The candidate adds 2960 bytes over GT production.
- Replacement-binary encap/decap results move by up to about 0.32% because the
  shared body changes code placement. A promotion decision should use a
  same-binary paired audit or deliberately accept that whole-binary result.
- Production function names and source closure have not yet been simplified
  from experiment naming.

The current engineering conclusion is:

```text
Keep shared-core direct-CQ as the best all-CQ experiment.
Do not replace GT production yet.
The proven value is the NTT-to-CQ boundary, not an across-the-board CQ win.
```
