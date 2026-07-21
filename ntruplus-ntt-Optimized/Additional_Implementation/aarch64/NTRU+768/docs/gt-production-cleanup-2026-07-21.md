# GT production cleanup, 2026-07-21

This cleanup makes the selected NTRU+768 AArch64 GT KEM path auditable without
changing its arithmetic or wire format. Production code, generic primitive
APIs, and historical experiments now have explicit ownership boundaries.

## Production ownership

The selected source closure is defined by `gt_production_sources.mk`,
`gt_production_variants.mk`, and the scheme `Makefile`.

```text
gt/
  README.md                 production data-flow guide
  keygen_bpq_cq.[ch]        private BPQ/CQ keygen contract
  decap_backend.h
  decap_verify.c            canonical decapsulation endpoint

asm/gt/keygen_bpq_cq/       keygen-only BPQ/CQ assembly
asm/gt/decap/               decapsulation-only assembly
asm/gt/ntt/                 generic production forward NTT
asm/gt/invntt/              generic and paired rminus1 inverse wrappers
asm/gt/basemul/             generic and caller-specific pointwise kernels
asm/gt/support/             canonical serialization and support kernels
```

`GT_PRODUCTION_KEM_SOURCES` is the minimal KEM runtime closure.
`GT_PRODUCTION_GENERIC_API_SOURCES` contains standalone `poly_invntt`,
`poly_baseinv`, and generic pointwise entrypoints used by differential tests
and component profilers. Those diagnostics are no longer linked merely because
the full KEM is benchmarked.

## Selected KEM paths

```text
keygen:
  cbd1
    -> fused mul3/mul3+add1 NTT to BPQ
    -> BPQ prepare to CQ
    -> hierarchical K=8 inversion with fqinv15
    -> mixed BPQ x CQ basemul
    -> BPQ/CQ canonical pack

encapsulation:
  canonical unpack U1
    -> generic GT forward NTT
    -> direct-Q31 basemul_add and canonical-byte endpoint

decapsulation first product:
  poly_basemul_rminus1
    -> poly_invntt_from_rminus1

decapsulation verification product:
  GT forward-order left operand + canonical hinv bytes
    -> canonical pointwise backend
    -> canonical product bytes
```

BPQ and CQ are represented by distinct private C types with compile-time size
and alignment checks. This prevents an accidental layout mix at C call sites
while retaining the existing `poly` storage ABI.

## Removed production ambiguity

- The promoted keygen backend moved from generic `asm/gt/{ntt,baseinv,basemul,support}`
  paths into `asm/gt/keygen_bpq_cq/`.
- The promoted decapsulation backend moved out of `experiments/` into
  `gt/` and `asm/gt/decap/`; its symbols no longer carry the old F2 prototype
  name.
- Rejected generators, Slothy logs, bridges, and old candidate wrappers are not
  part of the production commit. Previously tracked revisions remain available
  through Git history instead of being duplicated under an in-tree archive.
- The production rminus1 inverse wrapper emits only its block-major entrypoint.
  Tuple and BPQ inverse entries remain available to explicit experiment
  wrappers. This removed 16,384 bytes from the scheme test binary's text
  section (`157707` to `141323` bytes) without changing the active inverse body.
- `make check-production-layout` reports 53 production files and zero
  `experiments/` or `archive/` dependencies.

## Verification gates

The final source closure was rebuilt and tested on Raspberry Pi 5 AArch64:

```text
test_kem_gt_production_default: pass
PQCkemKAT_2336.rsp SHA256:
  22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
BPQ/CQ differential cases: 1000/1000 pass, ABI mask 0x0
decap backend differential: 0 mismatches, ABI mask 0x0
production inverse: 0 mismatches, ABI mask 0x0
production layout dependencies: 0
```

The ABI sentinels cover `x19-x28` and the AAPCS64-preserved low 64-bit halves
of `v8-v15`.

## Pi 5 benchmark

Environment: Cortex-A76 core 3 pinned, portable `NO_CE` SHAKE, 31 samples,
2000 calls per sample, 100 warmups. The full-KEM harness uses deterministic
inputs and verifies each setup before timing.

| Operation | KPQC p50 cycles | GT p50 cycles | GT reduction |
|---|---:|---:|---:|
| keygen | 39979 | 36357 | 9.06% |
| encapsulation | 39057 | 37582 | 3.78% |
| decapsulation | 35182 | 32860 | 6.60% |

Representative production-path components:

| Component | KPQC cycles | GT cycles | GT reduction |
|---|---:|---:|---:|
| generic forward NTT | 3614 | 2873 | 20.50% |
| keygen sample NTT f | 3642 | 2645 | 27.38% |
| keygen sample NTT g | 3639 | 2652 | 27.12% |
| keygen baseinv + basemul contract | 6694 | 5709 | 14.71% |
| encap basemul_add + pack | 3027 | 2900 | 4.20% |
| decap first basemul + inverse | 6594 | 5577 | 15.42% |
| decap verify product to bytes | 3425 | 3282 | 4.18% |

The full result, including generic diagnostics, actual KEM-path attribution,
and symbol metadata, is in
`aarch64-bench/results/gt_production_cleanup_final_2026-07-21/summary.md`.

## Remaining organization work

The production closure is now understandable, but the repository still holds
many default-off optimization experiments and historical result directories.
They should be pruned or archived by experiment family in separate commits so
that unrelated AVX2, baseinv, serialization, and forward-NTT work is not mixed
with this production cleanup.
