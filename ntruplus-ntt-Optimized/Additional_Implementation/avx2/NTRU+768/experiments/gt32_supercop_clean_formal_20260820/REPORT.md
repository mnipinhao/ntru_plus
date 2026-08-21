# GT Clean versus Official: SUPERcop-style formal benchmark

Date: 2026-08-20

## Decision

The fresh production GT Clean binary wins Keypair and Decap and loses Encap.
The direction is stable across paired launch blocks:

| Operation | Official StQ2 | GT Clean StQ2 | GT - Official | Relative | favorable blocks | paired 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| Keypair | 21,475.49 | 21,172.51 | **-302.98** | **-1.411%** | 16/16 | [-313.42, -276.44] |
| Encap | 28,032.71 | 28,277.95 | **+245.24** | **+0.875%** | 2/16 | [+152.15, +301.70] |
| Decap | 19,342.40 | 19,153.83 | **-188.57** | **-0.975%** | 16/16 | [-245.19, -133.74] |

Negative deltas favor GT Clean.  Official therefore remains the strict default
if one implementation must win all three standard API operations.

## What this benchmark answers

This is an implementation-performance benchmark, not an intrinsic mechanism
gate.  It deliberately includes each implementation's real code shape,
linked layout, PIE relocation, and resulting microarchitectural delivery.

No equal-size cage or address normalization is used.  The binaries are fresh,
independent SUPERcop builds.

## Method

- Official Main: SUPERcop `crypto_kem/ntruplus768/avx2`.
- GT Clean: freshly exported as
  `crypto_kem/ntruplus768/avx2-gt32-clean-20260820` from the production root.
- Compiler: GCC 15.2.0, `-march=native -mtune=native -O3 -fwrapv -fPIC
  -fPIE -ffunction-sections -fdata-sections -Wl,--gc-sections`.
- Both implementations built as independent PIE measure executables.
- CPU: Intel Core Ultra 7 155H, pinned to logical CPU 1 (P-core).
- Linux: 7.0.0-14-generic.
- ASLR: enabled (`randomize_va_space=2`).
- Turbo: enabled; intel_pstate, `balance_performance` EPP.
- 16 balanced blocks, alternating `Official/GT/GT/Official` and reverse order.
- 64 fresh process launches total: 32 per implementation.
- 96 native cycle observations per launch and operation, 3,072 per
  implementation and operation.
- SUPERcop stabilized quartiles; StQ2 is the primary typical-cycle estimate.
- Paired block deltas and bootstrap intervals are secondary robustness checks.

## Stabilized quartiles

| Implementation | Operation | StQ1 | StQ2 | StQ3 |
|---|---|---:|---:|---:|
| Official | Keypair | 21,321.53 | 21,475.49 | 21,677.98 |
| GT Clean | Keypair | 21,048.57 | 21,172.51 | 21,325.97 |
| Official | Encap | 27,938.83 | 28,032.71 | 28,577.90 |
| GT Clean | Encap | 28,057.01 | 28,277.95 | 28,728.52 |
| Official | Decap | 19,234.99 | 19,342.40 | 19,511.66 |
| GT Clean | Decap | 19,046.30 | 19,153.83 | 19,318.76 |

## Binary identity

| Implementation | SHA-256 | `.text` | `.rodata` |
|---|---|---:|---:|
| Official | `74ed0018af8799ad7c4806c1d30b95e987f4a364c01e783f0087993d418c910b` | 42,007 B | 5,384 B |
| GT Clean | `a07285363784aa2246f1256c7c255c862f2ec46796d3a64e4ee45fbd0d82013e` | 64,343 B | 21,576 B |

Both files are ELF `DYN` position-independent executables.

## Correctness prerequisite

The production GT Clean source passed its functional test and regenerated the
canonical 100-vector KAT files before export:

```text
PQCkemKAT_2336.req  36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa
PQCkemKAT_2336.rsp  22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

The source-manifest precheck reported only a stale hash for `README.md`; every
C, assembly, header, constant, and interface file matched.  This documentation
hash mismatch does not affect either executable and was not silently repaired
during the benchmark.

## Comparison with the preceding formal run

The preceding ASLR-on table-GC record reported approximately:

```text
Keypair  -304 cycles
Encap    +151 cycles
Decap    -229 cycles
```

The fresh run reports:

```text
Keypair  -303 cycles
Encap    +245 cycles
Decap    -189 cycles
```

Keypair is almost unchanged.  Decap remains a clear win.  Encap remains a
clear loss but its exact gap moved by roughly 94 cycles, consistent with the
040 finding that real linked-layout delivery is part of the production result.
The variation changes the magnitude, not the selector decision.

## Artifacts

- `ENCAP-ATTRIBUTION.md`: fresh PMU confirmation and the current causal
  decomposition of the Encap loss.
- `build/official-measure`: fixed Official benchmark ELF.
- `build/gt-clean-measure`: fixed GT Clean benchmark ELF.
- `results/supercop_style_aslr_on.json`: full launches, observations,
  stabilized quartiles, paired blocks, and confidence intervals.
- `results/raw/`: all 64 native SUPERcop outputs.
- `tools/run_supercop_style.py`: reproduction and analysis driver.
- `results/encap_full_loop_pmu.json`: eight-block full-Encap PMU confirmation.
