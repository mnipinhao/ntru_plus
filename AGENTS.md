# NTRU+864 / 1152 AVX2 optimization instructions

These instructions apply to the
`experiment/avx2-ntruplus864-1152-polymul-001` branch.

## Required startup

Before modifying files:

1. Run `git branch --show-current` and `git status --short`.
2. Confirm the branch is
   `experiment/avx2-ntruplus864-1152-polymul-001`.
3. Read `WORKFLOW.md` and
   `docs/avx2-864-1152-polymul-workflow.md` completely.

If the checkout is detached or on another branch, stop and report the mismatch
before making changes.

## Directory ownership

- Never modify `ntruplus-KpqC-Final/`; it is the frozen correctness baseline.
- Import performance baselines from the SUPERCOP release pinned in
  `bench/supercop.lock`, not from the frozen repository copy.
- Put unfinished optimization work only below the parameter-specific
  `experiments/` directories documented in the workflow.
- Put shared GT9x16 models and generators only below
  `ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/gt9x16/`.
- Do not modify a parameter-directory root implementation while exploring a
  candidate.
- Treat `clean/avx2-fastest-clean/` as promotion-only. It must not contain
  runtime selectors, rejected variants, raw benchmark output, or research
  history.
- Keep `bench/` implementation-neutral. Parameter-specific exploratory
  benchmarks belong inside the corresponding experiment.

## SUPERCOP source of truth

- Never modify a pristine SUPERCOP snapshot.
- Install candidates under new implementation names in a disposable SUPERCOP
  campaign copy.
- Use unmodified SUPERCOP `crypto_kem/measure.c` for formal KEM measurements.
- Label custom primitive measurements as `supercop-derived-poly`, never as
  native SUPERCOP results.
- Do not promote from repository-local timing or an isolated-kernel win.
- Formal promotion requires native SUPERCOP measurement and fixed-ELF paired
  evidence using the policy in the workflow.

## Experiment and promotion rules

- Namespace candidate symbols so Official and candidate can coexist in one
  benchmark image.
- Keep scalar and schoolbook oracles independent of candidate AVX2 layouts.
- Keep small-input and general mod-q multiplication contracts separate.
- Run generator, correctness, range, ABI, and constant-time gates before
  performance measurements.
- Record rejected candidates and reasons in `STATUS.yml`; do not silently
  replace prior experiment evidence.
- Promote only complete caller paths. Keygen, encapsulation, and decapsulation
  may select different source-resolved winners.
- Production contains no runtime candidate selector and must build without the
  experiment tree or generator.
- Produce the final KpqC-style package through the documented non-overwriting
  exporter; never assemble it manually.

The detailed workflow document is authoritative for paths, commands,
measurement labels, gates, and release requirements.
