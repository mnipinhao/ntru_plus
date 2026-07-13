# GT Decision Ledger

Last reconciled: 2026-07-13
Repository commit: `99d160e5`

Treat this as a dated routing aid, not immutable truth. Recheck the active
Makefile, linked object, and
[optimization scoreboard](../../../../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/optimization_scoreboard.md)
before acting. A `closed-by-default` entry blocks production promotion, not
read-only investigation or explicitly requested benchmark-only work.

## NTT32 Row-Specialized and Shadow-Base Family

- Status: `closed-by-default` for the previously measured production family.
- Scope: the rejected NTT32 row-specialized/shadow-base variants only; do not
  generalize this to every future Stage345 layout or to the currently linked GT
  production NTT.
- Evidence: [rowspec PMU conclusion](../../../../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt_tmvp_decomposition_experiment/ntt32-rowspec-pmu-conclusion.md).
- Reopen when: a new exact layout/output contract, linked benchmark-only target,
  differential oracle, and same-binary Pi5 comparison address the recorded
  regressions.

## Basemul `ldrtrn_noadd` and Oldstore Families

- Status: `closed-by-default` for production; retain historical comparisons as
  benchmark-only where already present.
- Scope: the recorded `ldrtrn_noadd` expansion and oldstore wrapper contracts,
  not all future basemul instruction schedules.
- Evidence: [call-path and pipeline PMU](../../../../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt_tmvp_decomposition_experiment/basemul-callpath-and-pipeline-pmu.md)
  and [production variant audit](../../../../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt_tmvp_decomposition_experiment/kem-production-variant-audit-2026-06-30.md).
- Reopen when: a materially different store/output contract or target profile
  has exact differential correctness and full-path PMU evidence.

## Fused `crep3` Production Default

- Status: `closed-by-default`.
- Scope: the measured fused decapsulation wrappers, not independent support
  kernel cleanup.
- Evidence: [fused-crep3 full-path PMU](../../../../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt_tmvp_decomposition_experiment/crep3-fused-fullpath-pmu.md).
- Reopen when: a new wrapper contract passes decapsulation/KEM differential
  tests and demonstrates a repeatable same-binary full-path win.

## InvNTT Row-Buffer/Post Fusion

- Status: `paused` and default-off.
- Scope: the documented row-buffer/post fusion proposal; do not block unrelated
  InvNTT boundary cleanup.
- Evidence: [row-buffer/post PMU](../../../../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt_tmvp_decomposition_experiment/invntt-rowbuffer-post-pmu.md).
- Reopen when: an exact producer/consumer memory contract removes the identified
  handoff cost and passes ABI, boundary-range, and full-KEM checks.

## Branchfold LDP and Lane-Store Variants

- Status: `closed-by-default` for the recorded variants.
- Scope: those exact load/store schedules, not all branchfold or store work.
- Evidence: [production stage PMU breakdown](../../../../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt_tmvp_decomposition_experiment/gt-production-kem-stage-pmu-breakdown.md).
- Reopen when: a new schedule changes the dependency or memory contract and has
  isolated plus full-path Pi5 evidence.

## Hash Backend

- Status: `separate-scope`, not a permanent rejection.
- Scope: keep hash changes outside non-hash kernel comparisons so both sides use
  the same CE/NO_CE policy.
- Evidence: [non-hash substage PMU](../../../../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt_tmvp_decomposition_experiment/gt-production-nonhash-substage-pmu.md).
- Reopen when: the user explicitly requests hash-backend work and the target CPU
  feature, assembler, constant-time, and same-policy benchmark plan are clear.

## Q31 Encap Byte Contract

- Status: `production-scoped` to encapsulation followed by `poly_tobytes`.
- Scope: do not substitute it for generic `poly_basemul_add`, decapsulation, or
  arithmetic-representative consumers.
- Evidence: [production variant audit](../../../../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt_tmvp_decomposition_experiment/kem-production-variant-audit-2026-06-30.md)
  and the current optimization scoreboard.
- Reopen consumer scope only when an exact byte/representation proof, release
  guard, differential tests, and full-path measurement cover that consumer.
