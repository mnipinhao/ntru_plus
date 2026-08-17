# Fixed-ELF multi-launch SUPERcop benchmark (2026-08-13)

## Method

- Official Main: fixed `measure` ELF, SHA-256
  `3f5bcebcdc0f1cb4a3327b78b2fce9f92c0dac8c2691c94a0fcef9a4e3645539`.
- CleanGT: fixed `measure` ELF, SHA-256
  `d4445768731942176f2f8d40cc41316863d32af780b2d8f6858f9045d2488381`.
- Both were compiled once with the same forced SUPERcop O3+section-GC flags.
- Cycle backend: `default-perfevent`, reading
  `PERF_COUNT_HW_CPU_CYCLES` (not TSC).
- CPU affinity: CPU 1.  Its SMT sibling is CPU 2; sibling isolation was not
  available and remains an environment limitation.
- 16 paired blocks, 64 independent process launches.
- Odd blocks: Official, GT, GT, Official.
- Even blocks: GT, Official, Official, GT.
- Each launch supplies the native SUPERcop 96 observations per operation.
- Statistical unit: each launch's stabilized Q2, paired within its block.
- Primary estimate: median of 16 paired block deltas.
- Confidence interval: deterministic 100,000-resample bootstrap of the block
  median.

The ELF hashes were checked again after all launches and did not change.

## Results

Negative delta means CleanGT is faster.

| Operation | Official block-median Q2 | CleanGT block-median Q2 | GT - Official | Delta | GT wins | 95% bootstrap CI | ABBA / BAAB median |
|---|---:|---:|---:|---:|---:|---:|---:|
| Keypair | 21,488.27 | 21,420.18 | **-33.76 cycles** | **-0.157%** | 14/16 | **[-80.83, -13.42]** | -59.94 / -20.58 |
| Encap | 28,039.76 | 28,148.60 | **+113.92 cycles** | **+0.406%** | 4/16 | **[+40.04, +154.83]** | +147.75 / +71.26 |
| Decap | 19,322.21 | 19,348.58 | **+28.24 cycles** | **+0.146%** | 1/16 | **[+16.65, +50.33]** | +17.01 / +32.45 |

All three confidence intervals exclude zero.  Both order families have the
same sign for every operation, so the result is not explained by the simple
Official-first versus GT-first ordering effect.

## Decision

- CleanGT Keypair is faster on this fixed production image, but only by about
  34 core cycles (0.16%).
- CleanGT Encap is slower by about 114 core cycles (0.41%).
- CleanGT Decap is slower by about 28 core cycles (0.15%).
- The complete CleanGT backend does not beat Official Main.  Official remains
  the default full backend.
- A compile-time hybrid selector using GT Keypair and Official Encap/Decap is
  supported directionally, but the Keypair margin is small and should receive
  a separate final-image benchmark before promotion.

This is a formal SUPERcop-style multi-launch test, not a 100,000-call custom
microbenchmark.  It preserves SUPERcop's native measurement distribution and
uses 64 independently launched fixed ELFs to obtain the missing launch-level
statistics.

Artifacts:

- `tile4-supercop-fixed-elf-serious-20260813.json`
- `tile4-supercop-fixed-elf-serious-raw-20260813/`
- `tools/run_supercop_fixed_elf_serious.sh`
- `tools/analyze_supercop_fixed_elf_serious.py`
