# Historical One-off Profilers

These C programs supported the February 2026 profiling snapshot. They are
retained as historical source, not as supported benchmark entrypoints.

- They are not wired into `bench/Makefile`.
- Their assumptions and output are not comparable to current Pi 5 PMU data.
- `aarch64_comparison_profiler.c` embeds a checkout path and invokes a compiler
  at runtime; do not use it as an operational harness.
- Current cross-implementation work must use `../bench_impls.py` so KAT,
  parameter equality, compile flags, labels, and result metadata stay aligned.

The associated report is archived at
`../../docs/history/2026-02/profiling-results.md`.
