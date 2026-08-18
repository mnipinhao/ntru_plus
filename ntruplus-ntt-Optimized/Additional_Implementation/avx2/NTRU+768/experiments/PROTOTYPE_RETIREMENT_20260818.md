# Legacy AVX2 GT prototype retirement record

The active research line is `experiment/avx2-gt32-tile4-official-001`.  The
older `avx2-gt-ntt-prototype` worktree is not a second production candidate.

Before retirement, the two independent technical results that were not
semantically replaced by the GT32/TILE4 work were copied here:

1. `wave31_invntt_branch_fold/`: exhaustive algebraic proof, generated ASM,
   correctness harnesses, KEM differentials, and PMU summaries.  Its folding
   mechanism is subsumed by the current GT32 T9 `MATRIX_PAIR` tail; the old ABI
   assembly remains unlinked.
2. `official_invntt_ct/` with `avx2_gt_d4_aos_official_api/`: the independent
   Official inverse CT/lane-native negative control and its complete source and
   generated-table dependency.

The remaining prototype implementations are superseded by the current GT32
generator, TILE4 N5/B3/I1/T9 kernels, typed P/M layouts, Q24 codec, clean
SUPERcop-style export, and formal KAT/benchmark records.  Old Wave19--Wave32
sources and coherent-contract variants remain historical implementation
iterations, not inputs to the current selector.

Repository skills, root build wiring, generic AVX2 benchmark edits, machine
notes, and raw build output were intentionally not merged as part of this
cryptographic-result migration.  They are not required to build, test, or
reproduce the current GT32 branch.

Verification after migration:

- Wave31 exhaustive generator/proof and correctness/linkage/KEM checks pass.
- Current GT32 `make CC=gcc check` passes.
- Official inverse CT `make test` and canonical-CT impossibility proof pass.
- No clean backend or production selector source was changed by the migration.
