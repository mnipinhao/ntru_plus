# NTRU+1152 AVX2 GT9x16 experiment 001

The immutable research baseline is `upstream/supercop-avx2`, imported from the
release pinned in `bench/supercop.lock`. Never edit it. Put handwritten C in
`src/`, assembly in `asm/`, reproducible generator output in `generated/`,
correctness checks in `tests/`, and experiment-specific benchmark adapters in
`bench/`.

Use a disposable campaign produced by `scripts/prepare_supercop.py`; candidate
installation refuses to target a pristine tree. Repository-local measurements
are diagnostic only. See the repository workflow document for formal gates.

## Active milestone

**GT permutation hypothesis validated; transform competitiveness not yet tested.**

The checkpoint following that named milestone now also contains the first
correctness-first full-forward path and its diagnostic competitiveness test.

## Full-forward correctness-first path

The path contains:

- a scalar proof/test of `n=16u+81v`, `k=64p+9q` over the 144-point field DFT;
- the free `H -> R` relabel and scalar `Y`/`Z` permutation oracles;
- a 27-`vpblendw` AVX2 `Z` producer;
- a debug materialized-`Y` baseline with nine additional 128-bit half combines;
- source-derived distance-8 tables cross-checked between the current scalar
  NTT and pinned AVX2 expansion, plus a fused shear→stage-8 validation path;
- a bit-exact adapter around the unchanged Official AVX2 small-input top split;
- branch-root pre-twists and a two-layer radix-3 reference NTT9;
- an offline component oracle recording every `branch × GT row × NTT16 lane`
  factor/root and all four positions in Official's packed AVX2 output;
- coefficient-by-coefficient full-forward differential tests after mod-q
  canonicalization;
- randomized signed-16-bit, centered-boundary, alias, canary, sanitizer, and
  generated-code audits.

Run `make check sanitize audit`. `make bench-local-record` produces a pinned
repository-local diagnostic; those cycle numbers are not SUPERCOP evidence.
The compiler currently represents the nine materialization operations as
`vblendps`, which is semantically equivalent to the proposed half selection.

The isolated fused stage-8 differential proves only that consuming `Z[a].low` and
`Z[a-1].high` is equivalent to materializing `Y` before the same Montgomery
butterfly. A correctness-first AVX2 routing baseline for distances 4/2/1 now
matches its scalar source-table oracle, retaining CT output order. It does
The complete correctness-first path now matches pinned Official AVX2
`poly_ntt` for its `[-3,4]` small-input contract. NTT16 lanes remain four-bit
reversed and NTT9 rows remain two-trit reversed; the generated oracle performs
the mapping instead of inserting cosmetic permutations.

The paired transform result is deliberately diagnostic. It includes the
explicit gather/pre-twist adapter, eight materialized correctness-first NTT16
islands, scalar NTT9, and scatter to Official's packed layout. It does not
qualify the candidate or justify a SUPERCOP/KEM run.
