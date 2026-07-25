# GT Production NTT Consumer, Code Size, and Neon Audit

Updated: 2026-07-23

This document answers three separate questions:

1. Which functions consume each NTT-domain representation?
2. Why does GT production need specialized kernels instead of one universal
   `ntt.s`, `invntt.s`, and `base.s` path?
3. Which code-size and AArch64 Neon optimizations are still worth testing?

The selected GT production configuration remains the mixed BPQ/CQ keygen
backend. The all-CQ route is a default-off experiment.

## 1. The Representation Contracts

The same 1,536-byte `poly` storage can hold several incompatible internal
representations. Equal object size does not make the layouts interchangeable.

### 1.1 Coefficient domain

```text
poly.coeffs[n] = coefficient n
```

This is used by sampling, `poly_triple`, inverse output, `poly_crepmod3`, and
the message encoding/decoding support.

### 1.2 Generic GT block-major NTT domain

This is the public GT `poly_ntt` output and the main encap/decap NTT-domain
contract. Conceptually:

```text
index = branch * 384 + 4 * physical_j + lane
```

The Good-Thomas row and NTT32 ordering are embedded in `physical_j`. It is not
the same memory image as KPQC's NTT-domain array.

### 1.3 BPQ: block/pair/quartic

One Q register contains two complete quartics:

```text
Q0 = [P0.c0 P0.c1 P0.c2 P0.c3 | P1.c0 P1.c1 P1.c2 P1.c3]
Q1 = [P2.c0 P2.c1 P2.c2 P2.c3 | P3.c0 P3.c1 P3.c2 P3.c3]
Q2 = [P4.c0 P4.c1 P4.c2 P4.c3 | P5.c0 P5.c1 P5.c2 P5.c3]
Q3 = [P6.c0 P6.c1 P6.c2 P6.c3 | P7.c0 P7.c1 P7.c2 P7.c3]
```

BPQ is close to the complete NTT32 Stage345 result. GT production uses it for
the keygen secret polynomials before base inversion and mixed basemul.

### 1.4 CQ: coefficient-major quartics

Four Q registers hold the same coefficient from eight quartics:

```text
C0 = [P0.c0 P2.c0 P4.c0 P6.c0 P1.c0 P3.c0 P5.c0 P7.c0]
C1 = [P0.c1 P2.c1 P4.c1 P6.c1 P1.c1 P3.c1 P5.c1 P7.c1]
C2 = [P0.c2 P2.c2 P4.c2 P6.c2 P1.c2 P3.c2 P5.c2 P7.c2]
C3 = [P0.c3 P2.c3 P4.c3 P6.c3 P1.c3 P3.c3 P5.c3 P7.c3]
```

CQ makes one Neon lane-wise multiply represent the same coefficient operation
for eight quartic products. It is used by keygen baseinv finish, public-product
basemul, and keygen pack.

### 1.5 QSoA verification layout

Decapsulation verification has a private QSoA layout:

```text
canonical hinv bytes
  -> small internal poly_frombytes
  -> QSoA hinv

GT block-major c-minus-m2
  -> gather in verify_pointwise
  -> QSoA product
  -> small internal poly_tobytes
  -> canonical verification bytes
```

This is a private byte-to-byte backend, not a generic `poly_basemul` output.

### 1.6 Scale/factor variants

Layout and Montgomery scale are independent contract dimensions:

```text
normal block-major product
  -> generic poly_invntt

block-major product with one extra R^-1
  -> poly_invntt_from_rminus1

scaled-R CQ inverse
  -> keygen BPQ x CQ or CQ x CQ basemul
```

Mixing the normal and `rminus1` pair in either direction is incorrect.

## 2. Selected Full-KEM Consumer Map

### 2.1 Keygen: selected mixed BPQ/CQ production

For both `f = 3F+1` and `g = 3G`:

```text
coefficient-domain sample
  -> poly_triple / add one
  -> poly_ntt
  -> generic GT block-major
  -> gt_keygen_blockmajor_to_bpq
  -> BPQ
```

The BPQ values then have three consumer roles:

| Value | Consumer | Input contract | Output contract |
|---|---|---|---|
| `f` or `g` | `gt_keygen_baseinv_bpq_to_cq_scaled_r` | BPQ | scaled-R CQ inverse |
| other secret operand | `gt_keygen_basemul_bpq_cq_to_cq_scaled_r` | BPQ x scaled-R CQ | CQ public product |
| secret `f` | `gt_keygen_tobytes_bpq_p1` | BPQ | canonical secret-key bytes |

CQ outputs are consumed by:

| Value | Consumer | Result |
|---|---|---|
| `finv` / `ginv` | mixed BPQ x CQ basemul | CQ `h` or `hinv` |
| `h` | `gt_keygen_tobytes_cq` | public-key bytes |
| `hinv` | `gt_keygen_tobytes_cq` | secret-key bytes |

The baseinv and basemul rows are one factor contract. Their isolated cycle
counts are not meaningful as generic drop-in comparisons.

### 2.2 Keygen: default-off all-CQ experiment

```text
coefficient-domain sample
  -> poly_triple / add one
  -> gt_experiment_poly_ntt_to_cq
  -> CQ
  -> CQ baseinv or CQ x CQ basemul
  -> CQ pack
```

The direct-CQ NTT performs the final BPQ-to-CQ transpose while Stage345 output
registers are live. It removes the block-major-to-BPQ and BPQ-to-CQ memory
boundaries.

Only keygen changes. Encap and decap still enter the generic block-major
`poly_ntt` symbol in the same dual-endpoint object.

### 2.3 Encapsulation

```text
r coefficient-domain
  -> poly_ntt
  -> block-major r
  -> poly_tobytes_gt_canonical
  -> hash_g input bytes

m coefficient-domain
  -> poly_ntt
  -> block-major m

public-key bytes
  -> poly_frombytes_gt_canonical
  -> block-major h

block-major h, r, m
  -> poly_basemul_add_encap_direct32_q31_tobytes_contract
  -> byte-equivalent Q31 representative
  -> poly_tobytes_gt_canonical
  -> ciphertext bytes
```

The Q31 result is not a generic centered polynomial representative. Its only
valid consumer is the immediate canonical pack.

### 2.4 Decapsulation first product

```text
ciphertext bytes -> canonical unpack -> block-major c
secret f bytes   -> canonical unpack -> block-major f

c x f
  -> poly_basemul_rminus1
  -> block-major product with extra R^-1
  -> poly_invntt_from_rminus1
  -> normal coefficient-domain m1
  -> poly_crepmod3
```

`poly_invntt_from_rminus1` is specialized because its final constants absorb
the correction deliberately omitted by `poly_basemul_rminus1`.

### 2.5 Decapsulation verification product

```text
m1 coefficient-domain
  -> poly_ntt
  -> block-major m2

block-major c - block-major m2
  -> poly_sub
  -> block-major c_minus_m2

canonical hinv bytes + block-major c_minus_m2
  -> gt_decap_verify_to_bytes
  -> QSoA verify_pointwise
  -> canonical verification bytes
```

The selected KEM does not call generic `poly_basemul` and canonical pack for
this product. The F2 backend owns the whole private product-to-bytes boundary.

### 2.6 Decapsulation re-encryption check

```text
r1 coefficient-domain
  -> poly_ntt
  -> block-major r1
  -> poly_tobytes_gt_canonical
  -> hash/byte comparison
```

### 2.7 Consumer source ownership

| Contract or symbol | Source owner | Selected KEM |
|---|---|---|
| KEM call graph and backend selection | `kem.c` | yes |
| generic block-major `poly_ntt` | `asm/gt/ntt/poly_ntt.n1.opt.S` | yes |
| NTT constants and tables | `asm/gt/ntt/poly_ntt.n1.opt.S` | yes |
| block-major to BPQ adapter | `gt/keygen_bpq_cq.c` | mixed GT only |
| BPQ baseinv prepare | `asm/gt/keygen_bpq_cq/baseinv_prepare.S` | mixed GT only |
| hierarchical K=8 tree | `asm/gt/keygen_bpq_cq/baseinv_tree.S` | yes |
| CQ baseinv finish | `asm/gt/keygen_bpq_cq/baseinv_finish.S` | yes |
| fqinv15 | `asm/gt/baseinv/poly_baseinv_fqinv15.S` | yes |
| mixed BPQ x CQ basemul | `asm/gt/keygen_bpq_cq/basemul.S` | mixed GT only |
| CQ/BPQ keygen pack | `asm/gt/keygen_bpq_cq/pack_cq.S`, `pack_bpq_p1.S` | mixed GT only |
| direct-CQ dual-endpoint NTT | `asm/gt/experiment/forward_ntt/poly_ntt_shared_core_direct_cq.S` | all-CQ experiment only |
| CQ prepare and CQ x CQ basemul | `experiments/keygen_all_cq/keygen_all_cq.c` | all-CQ experiment only |
| canonical GT pack/unpack | `asm/gt/support/poly_canonical_pack.S`, `poly_canonical_unpack_u1.S` | yes |
| encapsulation Q31 product | `asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.n1.opt.S` | yes |
| decapsulation rminus1 product | `asm/gt/basemul/poly_basemul_rminus1.S` | yes |
| paired rminus1 inverse | `asm/gt/invntt/poly_invntt_rminus1.S` | yes |
| generic inverse | `asm/gt/invntt/poly_invntt.S` | profiler/generic API only |
| decapsulation verify wrapper | `gt/decap_verify.c` | yes |
| decapsulation verify QSoA core | `asm/gt/decap/verify_pointwise.S` | yes |
| closure manifest | `gt_production_sources.mk` | source of truth |
| feature selection | `gt_production_variants.mk` | source of truth |

## 3. Generic API and Profiler Consumers

Component builds intentionally link additional standalone primitives:

```text
poly_ntt
  -> poly_basemul / poly_basemul_add / poly_baseinv
  -> poly_invntt
  -> canonical pack/unpack diagnostics
```

These are useful for differential tests and algorithm-level profiling, but
they are not the selected full-KEM path:

```text
inverse_ntt_generic != dec_first_invntt_actual
baseinv_generic     != keygen_baseinv_actual
basemul             != keygen or decap specialized product
```

Deleting those source files does not reduce the linker-GC KEM-only binary,
because they are already absent from that closure.

## 4. Why Specialized Kernels Are Valid

The protocol fixes public-key, secret-key, ciphertext, and shared-secret bytes.
It does not require all internal NTT arrays to equal KPQC's memory image.

Specialization is valid when all of these are true:

1. Producer and consumer agree on layout, ordering, and Montgomery factor.
2. A private representation does not leak through a generic `poly_*` API.
3. Canonical pack/unpack emits and accepts the required wire bytes.
4. Cross-implementation KAT and KPQC/GT encap-decap tests pass.

The practical design should therefore be:

```text
one mathematical arithmetic source of truth
  + explicit private layout/factor contracts
  + small caller-specific load/store/finalizer variants
```

It should not be one universal machine-code kernel for every caller. A
universal kernel would reintroduce layout conversions and final-factor work
that the specialized KEM paths currently avoid.

## 5. Linked Code-Size Result

Raspberry Pi 5, GCC 14.2, portable `NO_CE`, uniform section GC:

| Full-KEM closure | `.text` bytes | Delta vs GT |
|---|---:|---:|
| KPQC final | 23,098 | -66,656 |
| GT production | 89,754 | baseline |
| all-CQ shared NTT | 92,714 | +2,960 |

The detailed linker maps are in:

```text
aarch64-bench/results/ntt_consumer_code_size_2026-07-23/
```

### 5.1 Largest GT regions

| Region | Approximate address span |
|---|---:|
| forward NTT code + tables | 18,040 bytes |
| rminus1 inverse NTT | 16,352 bytes |
| decap verify F2 | 11,984 bytes |
| generic canonical pack + unpack | 9,856 bytes |
| keygen CQ + BPQ packs | 10,432 bytes |

These five families explain most of the gap to KPQC. GT is faster partly
because these kernels are aggressively unrolled and caller-specialized.

### 5.2 All-CQ size accounting

The shared generic/direct-CQ NTT is 9,640 bytes larger than the generic-only
NTT. The all-CQ keygen simultaneously removes about 6,704 bytes of BPQ adapter,
prepare, mixed basemul, and BPQ pack code. The observed net increase is only
2,960 bytes.

Therefore the all-CQ code-size question is specifically:

```text
Can the generic and direct-CQ Stage345 suffixes share more arithmetic code
without losing the approximately 986-cycle keygen gain?
```

It is not correct to describe all-CQ as adding a second full NTT.

## 6. Recommended Code-Size Architecture

### Priority 0: define two supported build products

```text
gt-kem-fast:
  only crypto_kem_* and selected private backends
  section GC
  hidden internal symbols

gt-poly-generic:
  standalone poly_ntt/poly_invntt/baseinv/basemul APIs
  component and differential tests
```

Research candidates remain in experiment targets. This is the cleanest way to
keep generic APIs without forcing every generic kernel into deployed KEM code.

### Priority 1: preserve object-level garbage collection

- Keep C functions in function/data sections.
- Give independent assembly entry families their own `.text.<symbol>` section.
- Keep tables in dedicated read-only sections so unused kernels do not retain
  unrelated tables.
- Run the production symbol-closure audit for every promoted backend.

Aliases at the same address do not duplicate machine code. Removing names such
as `_poly_ntt` does not materially reduce size.

### Priority 2: add an explicit size/speed Pareto build

The fastest production backend need not also be the smallest. The following
are meaningful size-optimized candidates:

1. **Compact decap verify.** F2 is about 11,984 bytes; the historical compact
   F1 shape was about 2,880 bytes and only about 108 cycles slower than F2 in
   the recorded full-decap comparison. Revalidate it as a `SIZE_OPT` backend,
   not as the fastest default.
2. **Looped inverse row kernel.** The rminus1 inverse is about 16.3 KB. Emit one
   internal-ABI row body and call it for three fixed rows. This trades fixed
   branches/calls for a potentially large text reduction.
3. **Compact canonical pack/unpack.** The selected fast pack/unpack occupy
   about 9.9 KB. Existing broad cross-chunk schedules did not win speed, but a
   looped implementation can still be valid for a size-first build.

Every size candidate must report both `.text` and full-KEM cycles. It should
not silently replace the fast default.

### Priority 3: reduce the all-CQ NTT suffix duplication

The current dual endpoint shares the prologue, frontend, tables, and epilogue,
but still has a large endpoint-specific Stage12/Stage345 suffix.

A new generator should model:

```text
shared Stage345 arithmetic
  -> generic block-major store finalizer
  -> direct-CQ transpose/store finalizer
```

The first gate is a block-level prototype. Measure branch count, register
parking, text size, and cycles. Do not rebuild the rejected all-row rowspec
line.

## 7. Remaining Neon Opportunities

### 7.1 High-value, not fully exhausted

#### A. NTT plus canonical-byte dual output for `r` and `r1`

Both paths immediately serialize a forward NTT result:

```text
poly_ntt(r/r1) -> poly_tobytes_gt_canonical
```

The transformed polynomial is still needed in NTT-domain form, so this cannot
be a bytes-only endpoint. A valid experiment emits:

```text
block-major NTT output
+ canonical bytes while final values are register-resident
```

This can remove pack-side reload/gather work. It will increase NTT code size,
so it must be evaluated as a cycle/size trade rather than assumed beneficial.

#### B. Batch keygen serialization

The all-CQ route serializes three CQ polynomials. A single internal
`tobytes_cq3` call could share constants, loop setup, and cross-polynomial
load/arithmetic latency:

```text
h CQ, f CQ, hinv CQ -> three canonical byte strings
```

The mixed production path can at least batch the two CQ values `h` and
`hinv`; `f` remains BPQ.

#### C. Cross-polynomial hierarchical base inversion

Keygen currently performs independent hierarchical inversion for `f` and `g`.
After both denominator trees prove nonzero, their roots could be combined so
the common case uses one field inversion and hierarchical recovery for both
polynomials.

This is an algorithm/call-graph experiment, not a local ASM patch. It must
preserve deterministic coin-selection behavior and the failure/retry order.

#### D. Code-size-aware Slothy templates

The current fastest generated kernels duplicate schedules for many fixed
groups. A second optimization objective can schedule one reusable two-group
template with pointer increments:

```text
minimize cycles subject to a maximum template size
```

The decap F2 pair pipeline is the clearest first target because its 12 unrolled
pairs occupy about 12 KB.

### 7.2 Open but requires real boundary removal

Inverse Stage123 still writes stripe scratch before Stage45 consumes it. A
source-order pair schedule was flat. The next valid candidate must remove
loads/stores through a live-register or consumption-order handoff; merely
rescheduling the same scratch traffic is not enough.

### 7.3 Already implemented or already rejected

Do not count these as new optimization ideas:

- rminus1 inverse lazy twiddle-1 through len16: selected production.
- Stage45 row-end reduction and final branchfold/factor fusion: selected.
- direct-Q31 encapsulation byte contract: selected.
- canonical unpack U1 and keygen pack P1: selected.
- standalone rminus1 stage123-scratch conversion: correctness passed but the
  direct producer pair was slower than production.
- all-row rowspec/direct-offset expansion: code-size/front-end cost did not
  justify promotion.
- broad canonical serialization cross-chunk scheduling: did not justify a
  global speed replacement.
- simple `ld4` versus `ldr+trn` base-input substitution: neutral.
- forward twiddle-1 deletion under the broad input contract: rejected by range
  proof/counterexample work.

## 8. Suggested Next Gates

For code size:

```text
Gate S1: rebuild compact F1 decap verify as a size-opt backend
Gate S2: one internal-ABI inverse row body, three fixed calls
Gate S3: compact canonical pack/unpack size build
```

For speed:

```text
Gate N1: block-level shared Stage345 arithmetic with two store finalizers
Gate N2: NTT block-major + canonical-byte dual-output endpoint for r/r1
Gate N3: batched CQ keygen pack
Gate N4: two-polynomial hierarchical baseinv model
```

Each gate must use:

```text
differential/KAT and cross-decap
ABI sentinel
same-binary paired PMU where possible
unique replacement full-KEM binary
cycles, instructions, .text, and symbol address metadata
```
