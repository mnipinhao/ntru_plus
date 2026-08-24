# GT32 experiment archive

This directory contains default-off research gates.  None of these files is
part of the GT Clean production source list.  Each numbered experiment owns
its generator, generated evidence, status, reproduction target, and any
benchmark-only implementation.

The production implementation remains the parent directory.  A research
result is copied there only after whole-operation qualification; keeping an
experiment here does not select it at build or run time.

The numbered work after the original representation wave is summarized in
[GT32_EXPERIMENT_INDEX_030_059.md](GT32_EXPERIMENT_INDEX_030_059.md).  That
index is the decision map for experiments 030 through 059E, including
supersession, fixed-geometry versus exact-image evidence, the formal
Official/GT benchmark, and current reopening rules.

## Encap consumer-native retirement

[Experiment 068](gt32_encap_consumer_abi_068/) derives the exact checked
mapping from B3 terminal accumulators to all Q24 packet slots, then tests two
implementations that never materialize a complete ordinary M-domain sum.  The
shared-core shape loses to 032 through repeated frontend transitions; the
fully-inline mutation removes the dispatch but becomes a 12-KiB MITE-heavy
body and also loses.  The typed ABI remains mathematically viable, but both
tested executable shapes are rejected and no full Encap gate is opened.

[Experiment 069](gt32_encap_consumer_abi_069/) tests the remaining bounded-
specialization premise.  Cluster sizes 2/3/4/6 are generated; the 3- and
4-block middle points are executed.  They recover only 2--4 core cycles of
DSB/MITE delivery versus fully inline and remain 21--24 core cycles behind
032.  Simple partitioning does not reduce the total unique 12-KiB path, so the
consumer-native campaign is paused pending a genuinely reusable compact
microkernel rather than another clustering or scheduling mutation.

[Experiment 070](gt32_encap_mprime_layout_070/) performs the pure-generator
search for an Encap-specific M-prime leaf order. It finds a correct layout in
which B3 needs only lambda-table relabeling and Q24 becomes one uniform loop,
but only 4 of 12 blocks can be formed by relabeling the current shared Forward
deposit masks. The other eight require block-dependent lane routing, modeled
at 96 extra vector operations per Forward polynomial. Since this fails the
zero-extra producer premise, no ASM gate is opened. The result is scoped to
the searched uniform microkernel and current Forward terminal families.

[Experiment 071](gt32_encap_mprime_terminal_071/) fixes that M-prime and
searches the remaining S4/S5 producer premise. It grants every block all
322,560 affine four-bit output gauges independently—more freedom than the
shared production loop—and freely relabels the current deposit masks. The same
eight blocks remain nonzero because their target permutations are nonlinear.
The optimistic one-destination-per-degree lower bound is therefore 32 extra
vector operations per Forward, above the 16-operation ASM eligibility limit.
No 072 executable gate is opened; only a genuinely non-affine terminal network
that replaces existing movement can reopen this scope.

## Progressive M formation coverage

[Experiment 030](gt32_n5_progressive_soa_030/) audits the proposed
NTRU-Prime-inspired progressive-SoA line.  It records that Stage4/Stage5 joint
M formation was already covered by the global physical-layout and plane-N16
gates, and closes the remaining affine packed-to-M terminal question at an
exact 12-instruction minimum over all 720 semantic bit-axis assignments.  The
result is scoped: arbitrary non-affine blend DAGs are not claimed impossible.

## Spec-gated Encap lifetime work

[Experiment 031](gt32_encap_lifetime_031/) isolates the four-polynomial Encap
scratch schedule.  It treats pre-`G` `Encodeq(r_hat)` bytes, canonical public-
key rejection and final ciphertext bytes as immutable Algorithm-12 edges.  The
separate B3-final-store add-m proposal is recorded as 032 proof obligations
and is not mixed into the 031 correctness gate.

## Research wave 013–029: final conclusion

This wave tested whether cross-R3/qword packets, degree-8 leaves, pair-native
`vpmaddwd`, delayed reduction, or merge/inverse basis conjugation can replace
the current AVX2 QBM→merge→inverse architecture.

The combined conclusion is:

```text
The alternative representations are mathematically viable in several local
cuts, but under the current AVX2 i16 ABI they either add normalization,
materialization, shuffle pressure, or Montgomery chains before reaching the
same coefficient consumer.  The current QBM→merge→inverse/DFT3 chain is near
architecture closure for the standard API and present producer contracts.
```

This is not an instruction-count-only conclusion:

- 016 and 024 are executable cycle/PMU hard stops;
- 021 is a structural rank proof;
- 027 is a correctness correction discovered by native ASM differential;
- 028 exhaustively proves a Montgomery-chain lower bound for the direct
  conjugated DFT3 family;
- 029 proves the zero-new-chain producer character condition fails for three
  of four difference-lane classes.

## Gate map

### Cross-R3/qword packet trajectory

| Gate | Result | Meaning |
|---|---|---|
| [013](gt32_cross_r3_qword_semantic_packet_013/) | semantic/routing pass | 64-bit qword semantics can cross R3, but range remained open |
| [014](gt32_cross_r3_qword_b3_inverse_range_014/) | hard stop | required selective normalization erases the routing credit |
| [015](gt32_qword_kem_caller_closure_015/) | caller closure pass | current KEM callsites can consume the typed bound without extra repair |
| [016](gt32_qword_forward_asm_016/) | executable performance stop | correct qword Forward loses on cycles despite the semantic closure |

The useful result is the typed range/caller proof from 015; the persistent
qword Forward architecture is not selected.

### Degree-basis and degree-8 trajectory

| Gate | Result | Meaning |
|---|---|---|
| [017](gt32_degree_basis_commutation_017/) | static stop | current degree-basis transform cannot be absorbed for free |
| [018](gt32_degree8_incomplete_ntt_018/) | algebra pass | degree-8 incomplete NTT is mathematically valid |
| [019](gt32_degree8_packet_schedule_019/) | static hard stop | direct degree-8 packet materialization is too expensive for current QBM |
| [020](gt32_streamed_lhs_rhs_evaluation_020/) | static hard stop | fixed rank-12 streamed contraction does not close on AVX2 |
| [021](gt32_degree8_first_cut_impossibility_021/) | structural proof | one rank-one first-cut stream cannot realize the required contraction |

Degree-8 algebra remains possible, but it needs a genuinely coupled producer
or a different ISA/decomposition; rearranging the current materialization is
closed.

### Pair-native QBM and reduction trajectory

| Gate | Result | Meaning |
|---|---|---|
| [022](gt32_qbm_pair_maddwd_022/) | static reject | local pair packing shows no instruction-class deletion |
| [023](gt32_qbm_cross_factor_packing_023/) | conditional stop | cross-factor density does not close under current i16/pre-REDC contract |
| [024](gt32_qbm_atomic_asm_024/) | cycle/PMU hard stop | atomic dual output adds real port 5/11 pressure and loses 35–39 TSC |
| [025](gt32_qbm_wide_consumer_025/) | static stop | direct wide consumer cannot remove the present reducer safely |

024 supersedes instruction-count speculation for the current atomic packing:
the extra routing is a measured backend cost.

### Merge-basis and conjugated-inverse trajectory

| Gate | Result | Meaning |
|---|---|---|
| [026](gt32_qbm_producer_native_merge_basis_026/) | superseded | Gate A rank proof remains valid; Gate B used the wrong scale relation |
| [027](gt32_unweighted_merge_asm_027/) | semantic stop | native ASM exposed that `45 Mont + 48 blend` is not an equivalent graph |
| [028](gt32_conjugated_dft3_synthesis_028/) | chain lower-bound stop | direct scaled DFT3 raises the whole chain from 115 to at least 144 Montgomery chains |
| [029](gt32_character_compatible_producer_029/) | producer-family stop | only one of four lane classes is character-compatible at zero new chain cost |

The correction chain is important:

```text
026 proposed absolute-weight propagation
  -> 027 replaced it with exact candidate/current propagation
  -> 028 tested direct DFT3 consumption of that exact scale
  -> 029 tested the only zero-cost diagonal producer family
```

Do not quote 026 Gate B chain/range/permutation numbers as correctness or
performance evidence.  Use 027–029.

## Current closure and reopening rules

Closed under the current AVX2 target and standard persistent ABI:

- local atomic dual-output packing;
- immediate wide-consumer reduction removal;
- unweighted merge followed by permutation/blend repair;
- direct conjugated DFT3 with at most two rank-one Montgomery updates;
- zero-new-chain diagonal producer character relabeling;
- current degree-8 materialized or fixed-rank streamed cuts.

Still open only when the mechanism changes materially:

- a non-diagonal coupled producer that deletes a complete operation class;
- an existing producer chain that selectively forms the difference coordinate;
- a prepared-key time/memory representation outside the standard API cost;
- a new DFT3 factorization outside 028 with a proved chain count below three;
- a different decomposition or wider ISA.

## Reproduction policy

Run `make check` inside an experiment directory.  Checks must preserve the
committed generated evidence; `clean` may remove build products but not source
or status files.  Cycle results must include their stored JSON and matched
normal/reversed methodology.  Static gates must state the exact searched
family so that a local stop is not mistaken for a universal impossibility.
