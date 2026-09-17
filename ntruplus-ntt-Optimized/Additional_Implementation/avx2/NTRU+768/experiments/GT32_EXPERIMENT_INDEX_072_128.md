# GT32 experiment decision ledger: 072--131

This file is the durable record for the late architecture campaigns.  It
keeps the conclusions, measured scale, invalid results, and reopening rules
without requiring every generated binary, raw `perf.data`, or superseded
workspace to live in Git.

The production baseline is the four-slot E0V implementation introduced by
commit `b2a4bea` (with its promotion and geometry contract in the production
documentation).  Experiments 094--105 are already committed and retain their
full evidence.  Experiment 127 remains as a compact profiling package, and
128 remains as the current generator/search package.

## Retention policy

| Class | Git policy | Reason |
|---|---|---|
| Production source, qualification scripts and layout audits | keep | Defines the shipped implementation contract |
| Open/current generator gates | keep complete | Needed to reproduce or extend the active search |
| Profiling campaigns | keep scripts and parsed summaries | Raw PMU/LBR captures are large and rebuildable |
| Superseded or closed architecture campaigns | keep this ledger; archive workspace | Conclusion and reopening condition matter more than build products |
| Invalid measurements | keep only an explicit invalidity note | Must not be reused as performance evidence |

The recoverable local archive made during this cleanup is
`/home/nuc/src/ntruplus-experiment-archive-20260915/`.  It is not part of the
repository and is not required to build or qualify GT Clean.

## 072--083: transferred techniques, normalized D4, and alternate D1/D2 cuts

| Gate | Durable result | Decision |
|---|---|---|
| 072 NEON/Hwa transfer survey | Selected pooled ninth-product, quotient-estimator and non-affine terminal probes | survey complete |
| 073 pooled ninth product | Four mixed Montgomery chains can be pooled into one; about `-0.8..-1.1 TSC/block`, but with extra routing | local mechanism pass only |
| 074 shift/ALU Q24 quotient | Exact over the required range, but executable loses about `+2.43 TSC/4-vector batch` | closed for the tested estimator |
| 075 non-affine M-prime terminal | No direct 4/5/6-operation replacement was found | bounded synthesis scope closed |
| 076 normalized D4 B3 | Correct zero-spill 9-product lowering; twelve blocks win about `-27.7 TSC` / `-45 core cycles` | local pass |
| 077 normalized D4 in KEM | Explicit normalization bridge adds 120 Montgomery chains and loses Encap about `+226 cycles` | current bridge closed |
| 078 basis absorption | Producer needs at least 120 chains to replace 84 deleted product chains; constant relabeling cannot absorb the normalization | current absorption family closed |
| 079 Late-D2 immediate repayment | Correct, but loses roughly `+113..116 cycles` | immediate-i16 realization closed |
| 080 global sign-by-Q identity | Proved the 64-root orbit and removed the standalone CRT premise | semantic pass; enabled 081 |
| 081 inverse64 executable | QBM is near parity, but inverse64 topology remains roughly `+135.5 TSC` behind even with free endpoint routing | current AVX2 inverse64 realization closed |
| 082 transfer audit | Closed several 1152/Hwa ideas that do not transfer to NTRU+768; retained caller-topology questions | audit complete |
| 083 D1 dual-terminal | Composite-map credit exists, but immediate coupling still loses; Official hash path remains ordinary materialize-and-serialize | tested D1 coupling closed |

Reopen normalized D4 only if the normalization is absorbed into operations
that already exist.  Reopen D2 only with a different inverse64 factorization,
QBM-produced inverse state, or another change that deletes an inverse work
class rather than another transpose mutation.

## 084--093: Hwa-style Encap topology and virtual sum

This campaign's durable production result is intentionally small:

```text
B3(h,r) -> product M
Forward(m) -> message M
two-source Q24(product, message)
```

The semantic sum exists but is never materialized as a complete polynomial.
The final selected topology is the original/current caller order, not G2B.

| Gate range | What it established |
|---|---|
| 084--085 | G2B exposed a useful caller-topology/lifetime cut, but its standalone caller credit was image-sensitive |
| 086--087 | Virtual-sum Q24 deletes 48 product/sum stores and 48 reloads; the linked suffix wins about `-27.4 core cycles` |
| 088--090 | Expanded/factorial/caged images showed that G2B and whole-caller signs were sensitive to executable geometry |
| 091 | Block-caged callers proved current-order + virtual sum in two controlled geometries; G2B did not earn the same qualification |
| 092 | Natural production relink made Encap much faster but moved unrelated Keypair/Decap substantially, exposing shared-image geometry collateral |
| 093 | Geometry-preserving integration retained Encap credit (`-42.6` ASLR-off, `-26.9` ASLR-on) while Keypair/Decap remained neutral |

The implementation and its RX-tail/link-layout contract were promoted into GT
Clean and are covered by the production `IMPLEMENTATION.md`, `QUALIFICATION.md`,
`BENCHMARK.md`, and `qualified/` audit tools.  The 084--093 workspaces are
therefore superseded by production source plus this ledger.

## 094--105: committed production refinements and QL2 research

These experiments are already committed and remain in Git.  The important
baseline transition is:

- 094 rejected blind five-to-four scratch compaction as a cycle claim;
- 095 proved the safe four-slot lifetime assignment;
- `b2a4bea` is the selected four-slot E0V production baseline;
- 096--098 found no stable production winner from data-order or isolated tail
  phase searches;
- 099 recorded the formal baseline comparison with Official;
- 100--101 measured and then closed the persistent B3-input presentation cut;
- 102--104 established QL2 as a real Encap convergence optimization, while
  shared-image Decap collateral prevented promotion over `b2a4bea`;
- 105 tested the bounded virtual-product seam.

Do not delete or archive these directories independently: their source and
evidence are already part of Git history.

## 106--126: GT6 outer / NTT16 / degree-4 campaign

The corrected decomposition is `2 x 6 x 16` with degree-4 leaves.  The family
is mathematically valid, and it yielded several reusable local observations,
but it did not close the production gap.

### Baseline and measured gap

- 106--110 established the GT6 outer mapping, native NTT16 S1/S2 layouts and
  direct producer variants.
- 111 found a real selective-reduction win: keep S1 difference lazy and center
  only the sum.  It deletes 24 centering invocations / 168 instructions and
  wins about `-50.6 core cycles` (`-76.6 TSC`).
- 112 connected the lazy Forward result to degree-4 B3 without restoring the
  removed center.
- 113 attempted a full KEM comparison before the complete compatible chain
  existed.  Its performance number is **invalid and must not be cited**.
- 114 then performed the correct component census: versus production, GT6
  Forward costs about `+331 core cycles`, native scale BaseMul about `+205`,
  and `2F+B` therefore starts about `+867 core cycles` behind.

### Wide producer and representation search

| Gate | Result |
|---|---|
| 115 | Terminal coefficient planes improve the GT6-local `2F+B3` by `-21.3 cycles`, but production debt remains about `+838 cycles` |
| 116 | Plain reordering of four radix-2 layers cannot produce the desired wide-native stage order |
| 117 | Exact 4x4 CT factorization and producer relabeling are valid; pure address-only middle Stockham is not |
| 118 | Naive wide-load frontend is zero-spill but loses `+21.7 core cycles` |
| 119 | Current fused CT producer family still needs an extra mixing layer; closed for the current factorization |
| 120 | Branch-late factorization is a real local frontend win: `-26.7 core cycles`, 16/16 |
| 121 | P2 partial-transpose Forward is correct/zero-stack but about `+403 core cycles` per Forward; full-island repayment is unresolved |
| 122 | Plane-native P2 BaseMul beats F4-T by about `160 core cycles`, but leaves roughly `+644 core cycles` to repay |
| 123 | AoS-native F4 BaseMul mutations lose (`+337` best tested); retain plane-native BaseMul |
| 124 | Coefficient-plane inverse-entry cut wins about `-59..-60 core cycles` |
| 125 | That credit survives the complete inverse: about `-57.2 core cycles`, both orders |
| 126 | Demand-driven partial B3 transposes all lose (`+10.8` best); tested seam closed |

The family is not rejected algebraically.  It is paused because the remaining
producer/Forward debt is hundreds of cycles, while the best measured BaseMul
and inverse-side credits do not repay it.  A meaningful reopen premise must
jointly eliminate the broadcast-heavy producer and the B3 presentation cost;
another local transpose or S3/S4 scheduling pass is insufficient.

## 127: exact-image Encap profiling

This compact package is retained because it is the current component-level
diagnostic baseline.  Experiment 099's same-binary result was:

```text
Official Encap  28106.01 cycles
GT Encap        28358.48 cycles
GT - Official    +252.47 cycles
paired estimate  +266.19, 95% CI [218.08, 318.38]
```

Mapped leaf intervals include Decode `+33.5`, CBD `+24`, Forward(r) `-50.25`,
r serialization `+45.75`, SOTP `+12.25`, Forward(m) `-45.5`, B3 `-14`, and
final add/serializer `+16` cycles.  These intervals are not additive ownership
of the whole delta.  L1D-pending sampling (`GT 83` versus `Official 13`) is a
useful contextual signal, not proof of one component owner.

Raw `perf.data` and LBR capture directories are archived outside Git.  Parsed
JSON, analysis scripts, documentation, and reproduction instructions stay in
the experiment directory.

## 128: mixed CT/GS and split-radix-inspired range search

The generator enumerated all `2^20 = 1,048,576` CT/GS packet-mode choices.
`5,504` are exact transforms, but none reaches the existing B3-safe bound
without the checkpoint.  The best exact candidate has final bound `17,388`
versus the required `10,788`.

No ASM or benchmark was opened because the requested operation-class deletion
was absent.  This closes the enumerated packetwise CT/GS family, not every
possible mixed-radix transform; a reopen requires cross-packet cancellation,
a different factorization, or a downstream consumer contract that accepts the
wider bound.

## 129: NTRU Prime AVX2 whole-pipeline transfer audit

The source-backed audit followed `radix_3x2.S`, `twist_transpose_pre/post`,
the cyclic/negacyclic FFT16 BaseMul calls, and `_mulcore`'s final fold/scale as
one dataflow contract.  The direct mechanisms are already represented in
GT Clean by the fused wide frontend/DFT3 deposit, TILE4-to-M/P typed terminal,
native consumers, Late-SoA, E0V and QL2 work.  The reference's strongest
remaining property—a shared two-Forward/BaseMul/inverse workspace ending at
one coefficient-domain scale/fold—has no matching standard NTRU+768 KEM caller.

No new ASM or benchmark was opened.  Reopen only for a real caller seam that
deletes work beyond the existing typed contracts, a different leaf
factorization, or an actual coefficient-to-coefficient polymul API.  See
`gt32_ntruprime_pipeline_transfer_129/` for the reproducible source audit and
machine-readable transfer matrix.

## 130: consumer-aware Forward reduction gate

Gate 128's best exact checkpoint-free NTT32 ended at `|x|<=17388`, but was
rejected against the stale `10788` B3 ceiling.  Gate 130 propagates that same
per-Q candidate through the selected general-B3 lambda tables, R-squared
finalizer, message addition, and the full-signed-int16 Q24 contract established
by 032R.  Both the r-only and r+m profiles are safe without adding a terminal
center or any consumer reduction; their maximum final serialized-input bounds
are 20294 and 19258 respectively.

The consumer gate passes, and zero-spill ASM confirms a robust local
`-33.0/-33.3` core-cycle win (16/16 in both matched placements). However, 128
also assumed an NTT32 input bound of 1728. Starting from the selected
frontend's conservative 5275 bound, the candidate's S3 GS pre-add reaches
42200, so signed-word safety is not proven. The result is retained as
`FAST_BUT_RANGE_UNQUALIFIED`; production is unchanged. Reopen only with a
tighter producer-aware reachable-range proof or an input contract that really
guarantees 1728, not by silently adding back a reduction.

## 131: exact S3-GS ternary reachable range

The producer-aware proof requested by 130 is exact and negative. Enumerating
all `3^6` inputs for every frontend leaf, then composing the eight disjoint Q
supports, finds a reachable S3 pre-add of 34781. A generated ternary witness
wraps to -30755 under `vpaddw` and makes the real candidate disagree with the
control modulo q. The specific 130 factorization is closed for the Encap
ternary-input contract; its `-33 TSC` credit remains a target for a different
checkpoint-deleting factorization.

## Current actionable state

```text
Production baseline:  b2a4bea four-slot E0V
Encap profiler:        127 retained compactly
Current range search:  128 retained completely
QL2:                   qualified Encap mechanism, not promoted due collateral
GT6:                   paused; large producer/Forward repayment remains
Normalized D4:         local pass, explicit KEM normalization bridge rejected
Hwa virtual sum:       promoted and represented by production source/docs
```

Large or superseded experiment workspaces are not build dependencies.  Restore
one from the external archive only when its stated reopen condition is met.
