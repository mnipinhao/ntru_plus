# Documentation Index

Use this page to distinguish current operational documentation from historical
engineering records.

## Current workflow

- [Repository workflow](../WORKFLOW.md)
- [Portable benchmark and KAT comparison](../bench/README.md)
- [Repository-local engineering skills](../.agents/skills/ntruplus-repo-engineering/SKILL.md)

## Active AVX2 Official-opt evidence (768 / 864 / 1152)

- [Current best and comparison against Official](ntruplus-avx2-official-opt-current-best.md)
- [HT Forward, R² fold and HT inverse (768)](ntruplus768-ht-forward.md)
- [HT Forward and R² fold (864/1152)](ntruplus864-1152-ht.md)
- [mlkem-native Keccak](ntruplus-avx2-keccak-mlkem-native.md)
- [Lazy Forward (864/1152)](ntruplus864-1152-official-opt.md), [2-op freeze](ntruplus768-1152-freeze2op.md), [direct 12-bit codec](ntruplus768-1152-direct-codec.md)
- [2026-09-23 overview snapshot (includes GT and component profiler)](ntruplus-avx2-overview-20260923.md)

## Active NTRU+768 AArch64 GT evidence

- [Production optimization summary](../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt-new-vs-kpqc-final-optimization-summary.md)
- [July 2026 production development timeline](../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt-production-development-timeline-2026-07.md)
- [Current production backlog](../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt-production-current-backlog.md)
- [Optimization scoreboard](../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/optimization_scoreboard.md)
- [Pi 5 benchmark flow](../ntruplus-ntt-Optimized/aarch64-bench/README_PI5.md)

## Baseline explanations

- [NTRU+768/864/1152 AVX2 transform-shape survey（中文）](ntruplus-avx2-shape-survey-768-864-1152-zh.md)
- [Frozen AArch64 NTT assembly explanation](baseline/aarch64/ntt-s-explanation.md)
- [NTTRU AVX2 精華（中文）](nttru-avx2-essence-zh.md)
- [NTTRU AVX2 reading and NTRU+768 comparison guide](nttru-avx2-comparison-guide.md)
- [NTRU Prime truncation AVX2 精華（中文）](ntru-prime-truncation-avx2-essence-zh.md)
- [NTRU Prime truncation AVX2 reading and NTRU+768 comparison guide](ntru-prime-truncation-avx2-comparison-guide.md)

## Historical records

Files under [history/](history/README.md) preserve dated decisions, commands,
and measurements. They may intentionally reference retired paths or fixed host
names and must not be used as current runbooks.
