# NTRU+768 / 864 / 1152 AVX2 optimization instructions

These instructions apply to the `avx2-gt-ntt` branch.

## Required startup

Before modifying files:

1. Run `git branch --show-current` and `git status --short`.
2. Confirm the branch is `avx2-gt-ntt`.
3. Read `WORKFLOW.md` and
   `docs/avx2-864-1152-polymul-workflow.md` completely.

If the checkout is detached or on another branch, stop and report the mismatch
before making changes.

## Directory ownership

- Import performance baselines from the SUPERCOP release pinned in
  `bench/supercop.lock`.
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

- The production performance baseline is the pinned SUPERCOP release recorded
  in `bench/supercop.lock`.
- Import upstream NTRU+768, NTRU+864, and NTRU+1152 AVX2 sources from
  `crypto_kem/ntruplus{768,864,1152}/avx2` in that snapshot.
- Never modify a pristine SUPERCOP snapshot.
- Install candidates under new implementation names in a disposable SUPERCOP
  campaign copy.
- Use unmodified SUPERCOP `crypto_kem/measure.c` for formal KEM measurements.
- Label custom primitive measurements as `supercop-derived-poly`, never as
  native SUPERCOP results.
- Formal headlines must use the pinned SUPERCOP `cpucycles()` backend and its
  stabilized-quartile estimator. Preserve the selected compiler,
  `cpucycles_implementation`, `cpucycles_persecond`, raw fresh-process output,
  CPU topology, governor, and turbo/boost state.
- Serious SUPERCOP runs require a pinned physical P-core, performance governor,
  and disabled turbo/boost. Do not silently change system frequency controls;
  stop and report a failed preflight instead.
- Repository-local `rdtscp` medians remain diagnostic. Do not relabel them as
  SUPERCOP results or use them as the performance headline.
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
- The KpqC-skeleton exporter was retired with `ntruplus-KpqC-Final/`
  (2026-09-23); define a new export path before the next release.

## Risk-tiered ASM prototype gates

- Keep promotion strict, but make a namespaced ASM prototype gate proportional
  to risk. Do not require a full research checkpoint sequence merely to learn
  the actual linked machine schedule.
- Representation, ABI, ownership, decomposition, scale, or Montgomery-domain
  changes remain high risk and require map, exact schedule, ASM, then timing.
- Arithmetic-placement or reduction changes that preserve the frozen external
  contract may proceed after a small identity/range proof, a rough machine
  budget, real structural credit, and no evident routing/temp/spill debt.
- Same-DAG instruction selection, register allocation, constant caching, and
  peepholes may proceed directly to namespaced ASM, differential testing,
  linked audit, and a short diagnostic benchmark.
- Let the linked object correct schedule estimates. Record the correction
  instead of forcing machine evidence to match a stale symbolic ledger.
- Cheap ASM authorization never relaxes correctness or promotion. Serious
  pricing still requires full differential, exact linked ABI/range/constant-
  time audit, zero unexplained spill, sanitizer, and the prescribed same-ELF
  methodology. Native KEM and production gates remain unchanged.

## GT pipeline co-design rules

- Audit the linked binary, not only C source, for hot-stage calls, frames,
  vector stack traffic, scalar loops, and compiler-inserted `vzeroupper`.
- Official forward, BaseMul/BaseInv, and inverse are the target structural
  model: call-free AVX2 leaf functions with no internal `vzeroupper`.
- Do not add `vzeroupper` as generic cleanup. Consider it only at a demonstrated
  outer AVX-to-legacy-SSE boundary and retain paired benchmark evidence.
- Co-design the terminal physical layout across forward, BaseMul/BaseInv, and
  inverse before optimizing an isolated transform.
- Preserve digit-reversed GT rows/lanes when consumers can use them directly;
  do not canonicalize merely for readability.
- Full-real benchmarks include every adapter, transpose, and scatter that still
  exists. Component microbenchmarks diagnose costs but cannot subtract them
  from end-to-end timing.
- Proceed in order: structural audit, pipeline-layout contract, single-block
  explicit AVX2 NTT16, Official-derived vector NTT9 baseline, fused-radix9
  research, then caller-complete Encap, Keygen, and Decap arithmetic islands.

## AVX2 assembly alignment rules

- Spell alignment with `.p2align`, not ambiguous bare `.align` directives.
- Align AVX2 public/internal leaf-function entries and YMM constant tables to
  at least 32 bytes (`.p2align 5`). Keep vector constants in an explicitly
  aligned read-only section.
- Treat 64-byte function or hot-block alignment as a measured code-placement
  variant, not an unconditional improvement. Record padding and code-size
  changes.
- Do not infer an aligned input/output-pointer contract from aligned code or
  constants. Use aligned vector memory operations only after the actual caller
  allocation and offset are proved aligned for every invocation; otherwise use
  unaligned operations.
- Avoid internal fall-through padding unless the aligned label is a real loop
  or branch target and the placement variant is measured. Straight-line leaf
  blocks normally need only an aligned entry.
- Audit the linked object and installed SUPERCOP ELF with `readelf`/`objdump`.
  Record section alignment and hot-symbol address modulo 32 and 64 alongside
  the source/ELF hashes. Re-run reversed-placement controls before attributing
  a win to arithmetic.
- If stack vector storage becomes unavoidable, prove the stack-alignment and
  unwind/ABI contract explicitly. Alignment is not permission to hide spills.

The detailed workflow document is authoritative for paths, commands,
measurement labels, gates, and release requirements.
