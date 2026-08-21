# GT32-CROSS-SYMBOL-SHARED-CODE-CENSUS-047

Static census of the frozen GT Clean exact ELF.  This is not another loop or
compact-body experiment.  It asks whether unchanged fast executable cores are
duplicated across retained production symbols.

The census records symbol size/callers, basic blocks, exact-byte duplicates,
RIP/branch-normalized duplicates, and register-shape candidates.  Only the
first two duplicate classes may support direct outlining; register-shape
matches are heuristic ABI-compatibility leads, not savings claims.

GT Clean production is never modified by this experiment.

## Decision

The census found no byte-identical basic block shared by different selected GT
symbols.  Relocation-normalization exposes only 96 gross bytes of small shared
prologues.  Larger normalized matches exist in B3, NTT M/P, and centered/lazy
Q24, but none is a zero-repayment outline: each would add per-iteration or
per-packet control flow, mode dispatch, or endpoint repair.

No ASM experiment is opened.  See `RESULTS.md` and `generated/census.json`.
