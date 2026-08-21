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

**Checkpoint D completed; NTT9-first adjusted-NTT16 implementation selected next.**

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
matches its scalar source-table oracle, retaining CT output order. It does not
by itself establish a complete transform result. The complete correctness-first
path now matches pinned Official AVX2
`poly_ntt` for its `[-3,4]` small-input contract. NTT16 lanes remain four-bit
reversed and NTT9 rows remain two-trit reversed; the generated oracle performs
the mapping instead of inserting cosmetic permutations.

The paired transform result is deliberately diagnostic. It includes the
explicit gather/pre-twist adapter, eight materialized correctness-first NTT16
islands, scalar NTT9, and scatter to Official's packed layout. It does not
qualify the candidate or justify a SUPERCOP/KEM run.

## Pipeline co-design checkpoint

`STRUCTURE.md` records the linked Official-vs-GT structure audit. `LAYOUT.md`
selects the provisional native terminal ABI spanning forward, BaseMul/BaseInv,
and inverse. `CHECKPOINT-C.md` records the explicit assembly island. C0 is a
zero-frame, call-free port of the verified shear and all NTT16 stages, with a
register-only macro over `ymm0..ymm8`. C1 is correctness-valid but rejected
because its split representation doubles vector Montgomery multiplies. C0 is
selected for the next straight-line NTT9 checkpoint; neither result is
production-qualified.

Checkpoint C2 then tested terminal-coefficient pair packing before starting
NTT9. It halves Montgomery chains, but the complete two-island transform is
46.8% slower because operand compression, row reconstruction, and the initial
shear boundary dominate. C2 is retained as a negative experiment. Checkpoint D
is paused while the physical AVX2 orientation is reassessed.

Checkpoint C3 refines that conclusion. Official-style persistent sum/difference
routing reduces one row-pair from 72.619 to 50.413 cycles and routing from 44
to 18 instructions. Terminal pairing remains viable; C2's per-layer canonical
reconstruction is the rejected choice. The next gate is a complete nine-row
shear→C3 path, still before NTT9.

Checkpoint C4 completes that gate. The natural-input nine-row pair is 17.9%
faster than two C0 islands, has zero intermediate materialization, and leaves
all rows in persistent S/D form. NTT9 work is reopened only for a kernel that
consumes this representation directly.

Checkpoint D adds the pinned Official T0/T3x3/T2x4 stage baseline and a
hand-written D-A NTT9 that directly consumes persistent S/D. D-A is bit-exact
but 27.4% slower than Official's two radix-3 layers. C4 from-Z is 11.0% faster
than Official's four radix-2 layers, while C4 natural is 32.9% slower and
reproduces a 208-cycle orientation tax. The D-B oracle proves that moving NTT9
first turns the shear into `rho^(-vp)` and that this phase can be absorbed into
distance-dependent NTT16 twiddles without extra Montgomery chains. See
`CHECKPOINT-D.md`.
