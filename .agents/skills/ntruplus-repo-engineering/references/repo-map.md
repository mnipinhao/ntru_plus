# NTRU+ Repository Map

Read this reference to select an implementation lane or find build, KAT,
benchmark, and security entrypoints.

## Roots

Derive the checkout instead of using an absolute user path:

```sh
REPO_ROOT="$(git rev-parse --show-toplevel)"
```

| Root | Role |
| --- | --- |
| `ntruplus-KpqC-Final` | Frozen clean baseline and comparison source |
| `ntruplus-ntt-Optimized` | Active scalar, Cortex-M-oriented, AVX2, AArch64, experiment, and benchmark workspace |
| `bench` | Cross-implementation KAT and cycle comparison front door |

## Implementation Matrix

Each listed family contains `NTRU+768`, `NTRU+864`, and `NTRU+1152` unless
noted otherwise.

| Lane | Active path | Frozen comparison path |
| --- | --- | --- |
| Scalar reference | `ntruplus-ntt-Optimized/Reference_Implementation/<PARAM>` | `ntruplus-KpqC-Final/Reference_Implementation/<PARAM>` |
| Scalar optimized | `ntruplus-ntt-Optimized/Optimized_Implementation/<PARAM>` | `ntruplus-KpqC-Final/Optimized_Implementation/<PARAM>` |
| Cortex-M-oriented | `ntruplus-ntt-Optimized/Cortex-M_Optimized_Implementation/<PARAM>` | None in the frozen root |
| AVX2 | `ntruplus-ntt-Optimized/Additional_Implementation/avx2/<PARAM>` | `ntruplus-KpqC-Final/Additional_Implementation/avx2/<PARAM>` |
| AArch64 | `ntruplus-ntt-Optimized/Additional_Implementation/aarch64/<PARAM>` | `ntruplus-KpqC-Final/Additional_Implementation/aarch64/<PARAM>` |
| KAT vectors | `ntruplus-ntt-Optimized/KAT/<PARAM>` | `ntruplus-KpqC-Final/KAT/<PARAM>` |

`<PARAM>` is exactly `NTRU+768`, `NTRU+864`, or `NTRU+1152`.

The Cortex-M-oriented Makefiles currently default to a host C compiler. Treat
that directory as a source lane until a real MCU toolchain, board, and timing
harness are explicitly selected. AVX2 and AArch64 code require compatible
hosts; do not use emulated or local incompatible timing for performance claims.

Existing NTRU+768 GT production work is a special AArch64 route owned by
`ntruplus-gt-kernel-engineering`.

## Build and KAT

From the selected implementation directory, inspect before executing:

```sh
make -n test
make -n PQCgenKAT_kem
```

Then run only targets confirmed by that Makefile. Do not assume every parameter
set or lane has identical source coverage merely because a target name exists.

Use the unified comparison front door from `bench`:

```sh
make PARAM_SET=NTRU+768 compare-kat
make PARAM_SET=NTRU+768 compare
make impl-compare-kat IMPL_A=../path/a IMPL_B=../path/b
make impl-compare IMPL_A=../path/a IMPL_B=../path/b LABEL_A=a LABEL_B=b
```

Keep `IMPL_A` and `IMPL_B` on the same parameter set. Architecture-specific
comparisons still require a compatible host. Preserve generated run metadata
and do not overwrite checked-in KAT vectors under either `KAT/<PARAM>` tree.

## GT Benchmarking

`ntruplus-ntt-Optimized/aarch64-bench` contains the GT/KPQC and PMU targets.
Inspect its active Makefile and route through `ntruplus-gt-kernel-engineering`
before building or running those targets.

## Security and Failure Analysis

Both source roots contain:

- `scripts/decryption_failure/decryption_failure.ipynb`
- `scripts/security/LATTICE_ESTIMATOR_OF_MALB/`
- `scripts/security/NTRU_ESTIMATOR_OF_NISTPQCR3_NTRU/`

The NTRU estimator README records `gp -q params.gp` from its own directory. The
lattice-estimator folder records its upstream revision. Confirm dependencies,
tool revision, parameter file, and assumptions before running or comparing
results. Changes to parameters or distributions also require scheme/algebra
review; estimator output alone is not a production-security decision.
