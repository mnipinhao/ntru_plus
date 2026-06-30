# NTT32 rowspec PMU conclusion

狀態：暫停 production integration，保留實驗檔案與 PMU harness。

## 結論

`gt_block_major_poly_ntt_shadow_base_row_specialized_prototype` 與
`gt_block_major_poly_ntt_shadow_base_row_specialized_slothy_prototype`
correctness 都通過，但不應該進 production。

理由不是 correctness 或指令數，而是 Pi 5 PMU 的實測 cycle 沒有贏：

- row-specialized 拿掉 deterministic `cmp/sub #0x300/csel` scatter wrap。
- static instruction count 明顯下降。
- 但 full NTT cycle 比 production 慢，NTT32-only 也只有 unscheduled rowspec
  約略打平，Slothy rowspec 反而變慢。
- rowspec code size 明顯增加，I-cache / front-end 風險上升。

## Pi 5 PMU result

設定：

- host: `pi@100.99.191.9`
- command: `taskset -c 3`
- `NTESTS=31`
- `NITERATIONS=10000`
- `NWARMUP=100`
- perf: user-level `perf_event_open`

Full forward NTT:

| variant | cycles/call | instr/call | IPC | text size | vs production |
|---|---:|---:|---:|---:|---:|
| production | 3132.723 | 3999 | 1.2765 | 12080 | baseline |
| shadow_base | 3192.985 | 4003 | 1.2534 | 12096 | +1.9% |
| shadow_base_slo | 3375.591 | 3937 | 1.1663 | 12032 | +7.8% |
| rowspec | 3231.732 | 3406 | 1.0539 | 16880 | +3.2% |
| rowspec_slo | 3252.709 | 3280 | 1.0084 | 16352 | +3.8% |

NTT32-only row kernels:

| variant | cycles/call | instr/call | text size | vs production |
|---|---:|---:|---:|---:|
| production | 2118.927 | 2724 | 3888 | baseline |
| shadow_base | 2106.521 | 2724 | 3888 | -0.6% |
| shadow_base_slo | 2230.195 | 2658 | 3840 | +5.3% |
| rowspec | 2112.556 | 2127 | 8672 | -0.3% |
| rowspec_slo | 2186.408 | 2001 | 8160 | +3.2% |

## Decision

目前不要把 rowspec / rowspec_slo 接到 `GT_NTT_ASM` 或
`gt_production` KEM path。

保留內容：

- `asm/my_ntt_shadow_base_prototype.s`
- `asm/my_ntt_shadow_base_slothy.s`
- `asm/my_ntt_shadow_base_row_specialized_prototype.s`
- `asm/my_ntt_shadow_base_row_specialized_slothy_prototype.s`
- `asm/slothy/ntt32_shadow_base_*`
- `aarch64-bench/bench_gt_ntt_variants_pmu.c`
- `aarch64-bench/bench_ntt32_*_wrapper.S`
- `aarch64-bench/scripts/write_gt_ntt_variant_textsizes.py`

下一步改做 basemul PMU benchmark：

- `poly_basemul`
- `poly_basemul_add` / `poly_basemul_add32`
- `poly_basemul_rminus1`
- `poly_basemul_scaled_r_input`
- `rminus1/scaled final st4 register contract` current vs old-store

先只做 benchmark + objdump count，不動 NTT32 production、不碰 invntt fusion。
