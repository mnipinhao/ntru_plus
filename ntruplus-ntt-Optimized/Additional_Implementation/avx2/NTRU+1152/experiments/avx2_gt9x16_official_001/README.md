# NTRU+1152 AVX2 GT9x16 experiment 001

The immutable research baseline is `upstream/supercop-avx2`, imported from the
release pinned in `bench/supercop.lock`. Never edit it. Put handwritten C in
`src/`, assembly in `asm/`, reproducible generator output in `generated/`,
correctness checks in `tests/`, and experiment-specific benchmark adapters in
`bench/`.

Use a disposable campaign produced by `scripts/prepare_supercop.py`; candidate
installation refuses to target a pristine tree. Repository-local measurements
are diagnostic only. See the repository workflow document for formal gates.

## Active slice: GT row shear through a correctness-first NTT16 island

The first implementation slice now reaches through the NTT16 arithmetic, but
still stops before connecting the unchanged top split and the reference NTT9.
It contains:

- a scalar proof/test of `n=16u+81v`, `k=64p+9q` over the 144-point field DFT;
- the free `H -> R` relabel and scalar `Y`/`Z` permutation oracles;
- a 27-`vpblendw` AVX2 `Z` producer;
- a debug materialized-`Y` baseline with nine additional 128-bit half combines;
- source-derived distance-8 tables cross-checked between the current scalar
  NTT and pinned AVX2 expansion, plus a fused shear→stage-8 validation path;
- randomized signed-16-bit, centered-boundary, alias, canary, sanitizer, and
  generated-code audits.

Run `make check sanitize audit`. `make bench-local-record` produces a pinned
repository-local diagnostic; those cycle numbers are not SUPERCOP evidence.
The compiler currently represents the nine materialization operations as
`vblendps`, which is semantically equivalent to the proposed half selection.

The fused stage-8 differential proves only that consuming `Z[a].low` and
`Z[a-1].high` is equivalent to materializing `Y` before the same Montgomery
butterfly. A correctness-first AVX2 routing baseline for distances 4/2/1 now
matches its scalar source-table oracle, retaining CT output order. It does
**not** yet prove the full proposed GT transform matches the current forward
NTT: connection to the unchanged top split and reference NTT9 remains pending.
