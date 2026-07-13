# GT basemul PMU benchmark

狀態：已建立 aarch64-bench PMU harness，production path 不變。

## Harness

新增 target：

```sh
cd /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench
make bench_gt_basemul_variants_pmu \
  GT_BASEMUL_PMU_NTESTS=31 \
  GT_BASEMUL_PMU_NITERATIONS=10000 \
  GT_BASEMUL_PMU_NWARMUP=100 \
  SUDO=
```

測量內容：

- `poly_basemul`
- `poly_basemul_add`
- `poly_basemul_add32`
- `poly_basemul_rminus1`
- `poly_basemul_rminus1_oldstore`
- `poly_basemul_scaled_r_input`
- `poly_basemul_scaled_r_input_oldstore`

`oldstore` 只用來 benchmark final `st4` register-contract patch before/after。
Production 不會定義 `GT_BASEMUL_STORE_RMINUS1_OLD_MOV_CONTRACT`。

Correctness：

- PMU harness built-in differential: `total_mismatches=0`
- `make test_gt_basemul_opt`: ok
- `make test_gt_basemul_opt_ldrtrn_load4`: ok
- `make test_gt_basemul_add32_full_pipeline_inline`: ok
- `make test_gt_basemul_accumulate`: ok

Pi 5 kernel 這次沒有提供 generic `l1d_store_miss`，所以該欄位是 `na`。

## Formal Pi 5 PMU result

設定：

- host: `pi@100.99.191.9`
- CPU pinning: `taskset -c 3`
- `NTESTS=31`
- `NITERATIONS=10000`
- `NWARMUP=100`
- metric: median over samples, subtracting empty-loop overhead

| variant | cycles/call | instr/call | IPC | L1I miss | L1D load miss | text | static insns | ld4 | ldp_qd | st4 | uzp | mov_vec | reduce-class |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `poly_basemul` | 2898.019 | 2489.000 | 0.8589 | 5 | 28119 | 464 | 116 | 2 | 0 | 1 | 14 | 0 | 83 |
| `poly_basemul_ldrtrn_noadd` | 2924.566 | 2969.000 | 1.0152 | 20 | 27800 | 544 | 136 | 0 | 4 | 1 | 30 | 0 | 83 |
| `poly_basemul_add` | 3008.712 | 2803.000 | 0.9316 | 7 | 43420 | 512 | 128 | 3 | 0 | 1 | 22 | 0 | 87 |
| `poly_basemul_add32` | 3008.250 | 2803.000 | 0.9318 | 6 | 43305 | 512 | 128 | 3 | 0 | 1 | 22 | 0 | 87 |
| `poly_basemul_rminus1` | 2130.996 | 1913.000 | 0.8977 | 6 | 28181 | 368 | 92 | 2 | 0 | 1 | 14 | 0 | 59 |
| `poly_basemul_rminus1_oldstore` | 2178.541 | 1985.000 | 0.9112 | 5 | 28163 | 368 | 92 | 2 | 0 | 1 | 14 | 3 | 59 |
| `poly_basemul_scaled_r_input` | 2108.164 | 1913.000 | 0.9074 | 5 | 27414 | 368 | 92 | 2 | 0 | 1 | 14 | 0 | 59 |
| `poly_basemul_scaled_r_input_oldstore` | 2155.884 | 1985.000 | 0.9207 | 5 | 27376 | 368 | 92 | 2 | 0 | 1 | 14 | 3 | 59 |

## Interpretation

`poly_basemul_add` and `poly_basemul_add32` are the same production inline
add32 code path in this harness.  The measured difference is noise-level.

The existing `ldrtrn_noadd` load experiment is correct but not faster:

| pair | current | ldrtrn_noadd | delta |
|---|---:|---:|---:|
| cycles/call | 2898.019 | 2924.566 | ldrtrn +0.92% |
| instr/call | 2489.000 | 2969.000 | ldrtrn +480 insns |
| static insns | 116 | 136 | ldrtrn +20 |
| input load shape | 2 `ld4` | 4 `ldp q,q` + 16 extra `uzp` | no cycle win |

Conclusion for load/store layout: do not expand this ldrtrn path to
`rminus1`, `scaled_r_input`, or `add32` yet.  It removes `ld4`, but the extra
deinterleave network costs more than it saves on Pi 5 for current noadd
basemul.

The final-`st4` register-contract patch is a clean win:

| pair | current | old-store | delta |
|---|---:|---:|---:|
| rminus1 cycles/call | 2130.996 | 2178.541 | old-store +2.23% |
| rminus1 instr/call | 1913.000 | 1985.000 | old-store +72 insns |
| scaled cycles/call | 2108.164 | 2155.884 | old-store +2.26% |
| scaled instr/call | 1913.000 | 1985.000 | old-store +72 insns |

The +72 dynamic instructions are exactly `24 blocks * 3 mov` from the old
contract:

```asm
mov v8.16B, v5.16B
mov v9.16B, v6.16B
mov v10.16B, v18.16B
st4 {v8.8H, v9.8H, v10.8H, v11.8H}, [x0], #64
```

Current conclusion:

- Keep the current final-`st4` register contract in `poly_basemul_body.inc`.
- Do not revert to old-store.
- This is a small but real win, about 2.3% on the rminus1/scaled basemul
  kernels.
- The `ldrtrn_noadd` load experiment was correct but slower, so its benchmark
  wrapper and target were removed; this document keeps the historical result.
- Next basemul work should move to larger effects such as add/accumulation path
  shape or cross-kernel layout, not this `ld4` to `ldp+uzp` noadd variant.
