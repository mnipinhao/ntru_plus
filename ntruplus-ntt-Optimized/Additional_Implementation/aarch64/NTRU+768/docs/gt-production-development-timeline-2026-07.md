# GT production development timeline, July 2026

This document is the dated index for the NTRU+768 AArch64 GT production work.
It replaces the separate G1R123+S2, CT-inverse, Pi 5 benchmark, priority 0-3,
and completed benchmark-plan notes. Numbers from different dates are kept in
their original scope; the July 22 source-closure run is the current headline.

## Current production contract

The selected full-KEM path is defined by `gt_production_sources.mk` and
`gt_production_variants.mk`.

```text
keygen:
  cbd1
    -> explicit 3F+1 or 3G coefficients
    -> shared production poly_ntt
    -> fixed block-major-to-BPQ boundary
    -> BPQ baseinv prepare to CQ
    -> hierarchical K=8 inversion + fqinv15
    -> mixed BPQ x CQ basemul
    -> BPQ/CQ canonical pack

encapsulation:
  canonical unpack U1
    -> GT Good-Thomas forward NTT
    -> direct-Q31 basemul_add + canonical bytes

decapsulation first product:
  poly_basemul
    -> poly_invntt

decapsulation verification:
  canonical hinv bytes + GT NTT operand
    -> canonical pointwise backend
    -> canonical product bytes
```

The keygen baseinv is already a production hierarchical K=8 implementation.
Because `GT_PRODUCTION_USE_BPQ_CQ_KEYGEN=1`, the active full-KEM code is the
private BPQ/CQ backend:

```text
asm/gt/keygen_bpq_cq/baseinv_prepare.S
asm/gt/keygen_bpq_cq/baseinv_tree.S
asm/gt/keygen_bpq_cq/baseinv_finish.S
asm/gt/baseinv/poly_baseinv_fqinv15.S
```

The later prepare2-Slothy, paper-k8 C/Neon, and paper-full-ASM files remain
default-off experiments. They are not the implementation linked by the
selected BPQ/CQ full-KEM source closure.

## July 10: G1R123+S2 forward NTT

G1R123+S2 promoted the U01 block-first producer/consumer work and the S2
high-half store schedule into the generic GT forward NTT. The same-binary
production/candidate harness measured:

```text
encapsulation paired median: -106.243 cycles, 61/61 wins
decapsulation paired median:  -88.853 cycles, 61/61 wins
```

The historical three-binary run measured:

| Operation | KPQC final | GT before | GT G1R123+S2 |
|---|---:|---:|---:|
| keygen | 39966 | 37982 | 37966 |
| encapsulation | 39013 | 37755 | 37590 |
| decapsulation | 35180 | 32629 | 32482 |

These values predate the completed canonical GT-to-KPQC serialization
boundary. They remain valid forward-candidate evidence but are not current
wire-compatible full-KEM headline numbers. Keygen did not use generic
`poly_ntt`, so its 16-cycle movement was code placement/noise rather than a
G1R123+S2 gain.

## July 17: transform and CT-inverse audit

The production audit established these contracts:

- GT forward uses a complete Good-Thomas transform and leaves each NTT32 row
  in the row-bit-reversed order consumed by the inverse.
- GT inverse is a CT-style inverse with `len=2,4,8,16,32`, rather than the
  KPQC CT-forward/GS-inverse pairing.
- Forward and inverse share algebraic ideas but not one runtime butterfly
  body: traversal order, twiddle placement, destructive register contracts,
  and final normalization differ.
- The production decapsulation pair deliberately keeps an `R^-1` factor after
  `poly_basemul_rminus1`; `poly_invntt_from_rminus1` absorbs it in its final
  constants together with untwist, branch merge, and normalization.
- At this historical checkpoint the normal-factor inverse still owned the
  public name. On July 23 the active paired path took the ordinary
  `poly_basemul/poly_invntt` names and the normalized diagnostics moved to
  `poly_basemul_normal/poly_invntt_normal`.
- Internal GT ordering is allowed to differ from KPQC. Canonical pack/unpack
  is the external byte boundary that must agree.

The inverse Stage123-to-Stage45 stripe scratch was identified as a possible
optimization boundary, but changing it requires a real producer/consumer
handoff rather than only rescheduling the existing stores and reloads.

Detailed assembly navigation remains in:

- `docs/gt_tmvp_decomposition_experiment/ntt-production-reading-guide.md`
- `docs/gt_tmvp_decomposition_experiment/invntt-production-reading-guide.md`

## July 18-19: canonical serialization and KEM attribution

Canonical P1 keygen pack, global U1 unpack, and the F2 decapsulation
verification endpoint were validated and promoted. GT and KPQC then produced
the same KAT response hash:

```text
22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

The first canonical full-KEM rerun measured:

| Operation | KPQC final | GT canonical | GT reduction |
|---|---:|---:|---:|
| keygen | 39966 | 38307 | 4.15% |
| encapsulation | 39060 | 37717 | 3.44% |
| decapsulation | 35183 | 32868 | 6.58% |

Important attribution decisions:

- Generic primitive rows are diagnostics, not the production KEM call graph.
- Production decapsulation uses the rminus1 basemul/inverse pair.
- Keygen baseinv and matching scaled-factor basemul must be interpreted as one
  contract.
- Keygen-only P1 was retained; making P1 universal regressed other contexts.
- U1 became the selected global unpack implementation.

## July 19: hierarchical baseinv tree

The verified hierarchical K=8 tree replacement was promoted for the legacy
scaled-factor generic backend after same-binary keygen measurements showed a
stable saving. The later BPQ/CQ keygen promotion introduced its own private
ASM prepare/tree/finish path and made that path the selected full-KEM keygen
backend.

Therefore two facts are simultaneously true:

1. production already uses hierarchical K=8 base inversion;
2. the worktree contains newer default-off baseinv experiments that are not
   yet part of the selected BPQ/CQ KEM backend.

## July 20: priorities 0-3 closeout

| Work | Result | Decision |
|---|---|---|
| Component profiler attribution | Replaced stale generic decap rows with actual F2 boundary | Keep |
| InvNTT Stage123 pair scheduling | 3558.52 vs 3559.23 cycles | Reject |
| Q31 two-iteration scheduling | About -92 kernel cycles and -80.44 encap cycles | Promote |
| Whole-chunk serialization | P1/U1 retained; P2/P3 regressed | Keep selective policy |

The inverse result is important: merely overlapping the next Stage123 group's
loads did not help. Future inverse work must remove or materially change the
scratch boundary.

## July 21: BPQ/CQ keygen and production cleanup

The keygen pipeline was reorganized around private BPQ and CQ types and
caller-specific assembly. Production ownership moved under `gt/` and
`asm/gt/{keygen_bpq_cq,decap,ntt,invntt,basemul,support}`. Rejected prototypes
stopped being production dependencies.

The cleanup benchmark measured:

| Operation | KPQC final | GT production | GT reduction |
|---|---:|---:|---:|
| keygen | 39979 | 36357 | 9.06% |
| encapsulation | 39057 | 37582 | 3.78% |
| decapsulation | 35182 | 32860 | 6.60% |

The keygen baseinv-plus-basemul contract measured 5709 cycles against KPQC's
6694 cycles. This is the relevant production comparison; the standalone
generic baseinv row is not.

Full ownership details are in `gt-production-cleanup-2026-07-21.md`.

## July 22: minimal full-KEM source closure

The final source audit removed reference/generic code from the selected
full-KEM binary while retaining those APIs for tests and component profilers.
Removed full-KEM sources included `ntt.c`, `poly_gt_canonical.c`, the legacy
generic P1 pack, and inactive `poly_triple`.

| Operation | Text before | Text after | Text reduction | Cycles after |
|---|---:|---:|---:|---:|
| keygen | 144302 | 127798 | 16504 (11.44%) | 36362 |
| encapsulation | 144286 | 127782 | 16504 (11.44%) | 37575 |
| decapsulation | 144286 | 127782 | 16504 (11.44%) | 32842 |

Same-run comparison against KPQC final:

| Operation | KPQC final | GT production | GT reduction |
|---|---:|---:|---:|
| keygen | 39962 | 36362 | 9.01% |
| encapsulation | 39059 | 37575 | 3.80% |
| decapsulation | 35193 | 32842 | 6.68% |

The explicit cross-vector test loaded KPQC `sk`, `ct`, and expected `ss` into
the GT decoder and reported zero mismatches. See
`gt-production-source-closure-audit-2026-07-22.md` for symbol and code-size
details.

## July 23: production API and compact decap profile

The first decapsulation product was organized as one public transform
contract:

```text
poly_basemul
  leaves one R^-1 factor
poly_invntt
  absorbs that factor in final constants
```

The independently normalized primitive implementations now export
`poly_basemul_normal/poly_invntt_normal` in production-aware test and profiler
builds. Specialized keygen, encapsulation, and verification kernels keep
private names because their layouts or byte endpoints differ.

The compact F1 verification backend became the default after a same-binary
full-decap comparison found F2 faster by 112 cycles (about 0.34%) while F1
reduced `.text` by 9,088 bytes. F2 remains the explicit `speed` profile.
Detailed results are in
`gt-production-f1-f2-decap-profile-decision-2026-07-23.md`.

## Current interpretation

- The first July 22 table above is the historical fused-keygen closure result.
- Current production now explicitly forms `3F+1`/`3G`, calls the same
  `poly_ntt` as encap/decap, then converts block-major output to BPQ.
- The shared-NTT rerun measured `37702/37576/32872` cycles for
  keygen/encap/decap versus KPQC `39964/39066/35189`.
- The shared-NTT binary text is about 107.3 KB; detailed current results are in
  `aarch64-bench/results/gt_production_shared_ntt_2026-07-22/summary.md`.
- Use the July 21 component profile for the selected BPQ/CQ keygen contract.
- Use July 10 only as historical G1R123+S2 paired evidence.
- Do not substitute generic `baseinv`, `basemul`, or `poly_invntt` rows for
  caller-specific KEM paths.
- Current open work is maintained in `gt-production-current-backlog.md`.

## July 24: pipelined compact verification backend

The V3 gather pipeline moves all eight fixed-offset loads for QSoA group
`N+1` to the earliest safe points in group `N`'s transpose. A subsequent
Slothy pass rescheduled the shared 100-instruction multiplication/reduction
helper while preserving `q24-q31` as live-through registers.

Same-binary full-decapsulation PMU measured a 136-137 cycle reduction against
the source-order compact profile, with 61/61 paired wins, unchanged retired
instructions, and unchanged 2,880-byte function size. Differential, ABI,
full-KEM, deterministic KAT, linked-symbol closure, and clean-release checks
all pass. The `pipeline` profile is now the production default; `compact` and
`speed` remain explicit comparison profiles.
