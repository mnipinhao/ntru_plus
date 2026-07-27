# Reproducible Full-KEM Benchmark

This companion benchmark compares GT-Optimized with the frozen KPQC-final
NTRU+768 AArch64 implementation. It builds each implementation in a separate
binary and calls the actual public KEM API:

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
- A local copy of KPQC final for NTRU+768

## Run

From this directory:

```sh
python3 run_benchmarks.py \
  --kpqc-root /path/to/ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768 \
  --core 3 \
  --output results/my-run
```

The runner:

1. Builds GT-Optimized and KPQC final with the same compiler and optimization
   flags.
2. Pins each process to the selected CPU.
3. Runs key generation, encapsulation, and decapsulation in balanced
   `KPQC/GT` and `GT/KPQC` order.
4. Checks KEM correctness in every benchmark binary.
5. Writes raw stdout, environment metadata, source-tree hashes, and a JSON
   summary.

Useful overrides:

```sh
CC=gcc CFLAGS="-O3 -fomit-frame-pointer" \
python3 run_benchmarks.py --kpqc-root ... --core 3 --output ...
```

The default workload is 31 samples, 2,000 operations per sample, and 100
warmups. Override it with `--tests`, `--iterations`, or `--warmups`.

The component-level figures in `NTRU+768/docs/BENCHMARKS.md` describe the
measured production call graph. This compact handoff harness intentionally
focuses on the decisive public full-KEM totals.

The release tracks the generated JSON and Markdown summaries for the reference
run under `results/pi5-reference-20260725/`. Raw samples and build logs are
reproducible outputs and are intentionally not tracked on the mainline.
