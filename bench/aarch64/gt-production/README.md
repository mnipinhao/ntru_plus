# GT-Production AArch64 Benchmark and Reports

This directory is the repository-level companion to the source-only
GT-Production release. It contains:

- the reproducible GT-Optimized versus selected-baseline full-KEM harness;
- curated Raspberry Pi 5 results under [`results/`](results/);
- the production performance and optimization reports under
  [`reports/`](reports/).

The implementation itself remains under
[`../../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768`](../../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768).

Start with:

- [`results/p0-p1-handwritten-20260729/summary.md`](results/p0-p1-handwritten-20260729/summary.md)
  for the final P0 production hardening, P1-A/P1-B handwritten assembly,
  P1-C hard-gated range proof, and authoritative Pi 5 results;
- [`reports/yang-course-study/README.zh-TW.md`](reports/yang-course-study/README.zh-TW.md)
  for the Yang course synthesis, the exact distinction between twist and
  reduction, Good's permutation, Wave 5, and the next GT optimization roadmap;
- [`reports/official-main-study/README.md`](reports/official-main-study/README.md)
  for the complete Official main, KPQC Final, and GT Production source/ABI/
  security/performance study;
- [`reports/OFFICIAL-MAIN-ADOPTION.md`](reports/OFFICIAL-MAIN-ADOPTION.md) for
  the Official-main ideas worth evaluating in GT Production;
- [`reports/OPTIMIZATION-SUMMARY.md`](reports/OPTIMIZATION-SUMMARY.md) for the
  GT versus frozen-KPQC technical summary;
- [`reports/BENCHMARKS.md`](reports/BENCHMARKS.md) for the curated production
  measurements.

## Reproducible Full-KEM Benchmark

This companion benchmark compares GT-Optimized with an explicitly selected
NTRU+768 AArch64 baseline such as Official Main or frozen KPQC Final. It builds
each implementation in a separate binary and calls the actual public KEM API:

```text
crypto_kem_keypair
crypto_kem_enc
crypto_kem_dec
```

Both binaries use the same benchmark-only deterministic `randombytes`
implementation. The deterministic generator is not part of either production
implementation and must never be used outside benchmarking.

## Requirements

- Linux/AArch64
- GNU-compatible C compiler and assembler
- Linux `perf_event_open` access to user-space CPU cycles
- `taskset`
- Python 3
- A local copy of the selected NTRU+768 AArch64 baseline

## Run

From this directory:

```sh
python3 run_benchmarks.py \
  --baseline-root /path/to/baseline/Additional_Implementation/aarch64/NTRU+768 \
  --baseline-label "Official Main" \
  --core 3 \
  --output results/my-run
```

The runner:

1. Builds GT-Optimized and the selected baseline with the same compiler and optimization
   flags.
2. Pins each process to the selected CPU.
3. Runs key generation, encapsulation, and decapsulation in balanced
   `baseline/GT` and `GT/baseline` order.
4. Checks KEM correctness in every benchmark binary.
5. Writes raw stdout, environment metadata, source-tree hashes, and a JSON
   summary.

Useful overrides:

```sh
CC=gcc CFLAGS="-O3 -fomit-frame-pointer" \
python3 run_benchmarks.py \
  --baseline-root ... --baseline-label "Official Main" \
  --core 3 --output ...
```

`--kpqc-root` remains as a legacy alias of `--baseline-root`. New output
metadata, binary names, raw-log names, and result keys consistently use
`baseline`; the real label, root, and source hash identify which baseline was
measured.

The default workload is 31 samples, 2,000 operations per sample, and 100
warmups. Override it with `--tests`, `--iterations`, or `--warmups`.

The component-level figures in [`reports/BENCHMARKS.md`](reports/BENCHMARKS.md)
describe the
measured production call graph. This compact handoff harness intentionally
focuses on the decisive public full-KEM totals.

The repository tracks the generated JSON and Markdown summaries for the reference
run under `results/pi5-reference-20260728-fqinv15-fixed/`. New result archives
belong under this directory rather than inside the production implementation
tree. Raw samples and build logs are reproducible outputs unless a comparison
report explicitly retains them for provenance.
