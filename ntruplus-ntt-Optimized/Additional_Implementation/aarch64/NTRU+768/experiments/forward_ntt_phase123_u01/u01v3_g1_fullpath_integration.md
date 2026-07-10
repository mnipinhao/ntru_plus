# U01v3 G1 完整 poly_ntt / KEM 整合結果

狀態：G1、G1+S2、G1R123、G1R123+S2 均通過 correctness 與 ABI；production default 未改。

## 完整路徑

G1 原本的 same-coverage ABI 是 `x0=dst, x1=src, x2=scratch`。完整
`poly_ntt` wrapper 改成公開 ABI `x0=dst, x1=src`，並配置 1696-byte
stack frame，其中 1536 bytes 是三個 row 的 Stage12 scratch。整個 G1 body
直接展開在 wrapper 內，沒有額外 helper `bl`。

完整 KEM binary 仍然要 link `my_32ntt.opt.s`，因為 keygen 的
`poly_ntt_triple_scheduled` 仍呼叫 `_ntt32_8way`。generic `poly_ntt` 選到
G1 時不會走這個 row kernel；保留它只是滿足另一個 public entry 的連結依賴。

## S2 組合 contract

未排程 G1 每 row 有 32 個 high-half store：

- 27 sites 可安全把 `ext+str d` 改成 `umov+str x`。
- 5 sites 因 source 或 ext temp live range 重疊，保留原形狀。
- 三 row 共 81 次動態替換。

R123 排程後是 28 safe / 4 kept，三 row 共 84 次動態替換。每個 scalar
temporary 都是 site-local dead caller-saved GPR，且不 alias address/base。

## Correctness

Pi5 結果：

- full `poly_ntt` differential：20480 calls，mismatches = 0。
- out-of-place / in-place：pass。
- G1、G1+S2、R123、R123+S2 ABI sentinel：`x19-x28` 與 `d8-d15` mask = 0。
- 四個 drop-in KEM variants：pass。

## Pi5 paired direct poly_ntt PMU

設定：core 3，PMU cycles/instructions，`NTESTS=61`，
`NITERATIONS=20000`，五種 rotated order，共 305 samples。

| Variant | cycles median | instructions | CPI | delta vs A |
|---|---:|---:|---:|---:|
| A production | 2705 | 4010 | 0.6746 | 0 |
| G1 | 2693 | 3747 | 0.7187 | -12 |
| G1+S2 | 2669 | 3747 | 0.7123 | -36 |
| G1R123 | 2687 | 3747 | 0.7171 | -18 |
| G1R123+S2 | 2659 | 3747 | 0.7096 | -48 |

關鍵 paired delta：

- G1R123 - G1：median -7 cycles，range -13..+1。
- G1R123+S2 - G1+S2：median -11 cycles，range -23..-4。
- G1R123+S2 - production：median -48 cycles，約 -1.77%。

所有 G1 variants 的 symbol size 都是 14904 bytes，instruction count 也相同；
R123 與 S2 的差異是 schedule / instruction form，不是刪除額外指令。

## KEM-context one-NTT

所有 drop-in binary 的 `poly_ntt` address 都是 mod32=16、mod64=48，因此下表
不受 variant 間 function alignment 差異影響。

| Site | A | G1 | G1+S2 | G1R123 | G1R123+S2 |
|---|---:|---:|---:|---:|---:|
| encap_ntt_r | 2708.9 | 2692.8 | 2659.8 | 2683.2 | 2658.1 |
| encap_ntt_m | 2708.9 | 2691.6 | 2659.7 | 2681.5 | 2657.3 |
| decap_ntt_m1 | 2706.9 | 2691.0 | 2661.5 | 2679.3 | 2659.8 |
| decap_ntt_r1 | 2703.2 | 2693.0 | 2660.1 | 2683.7 | 2657.9 |

R123 對 G1 在四個 site 穩定省 9.3..11.7 cycles。R123+S2 對 G1+S2
再省 1.6..2.3 cycles；方向一致，但累積收益小於 direct harness。

## Full KEM 判讀

generic `poly_ntt` 不在 optimized keypair hot path，因此 keypair instructions 完全
相同，cycle 差只視為 noise。encap/decap totals 是跨不同 binary 量測，波動量大於
R123 的單次 10-cycle 收益；其中 encap total 甚至與兩個 one-NTT site 的方向矛盾，
不能拿來否定 kernel boundary 的 paired 結果。

目前 kernel 最佳是 G1R123+S2，但仍維持 experiment-only/default-off。raw logs：

- `aarch64-bench/results/u01v3_g1_r123_fullpath_pmu_long.out`
- `aarch64-bench/results/u01v3_g1_r123_kem_context_pmu_run.log`

## Same-binary full-KEM closure

後續已用同一個 binary 直接配對 A production 與 B G1R123+S2，消除上面跨 binary
full-KEM 結果的主要不確定性。61 組、每組 2000 次、AB/BA 交替的結果如下：

- encap：paired median `-106.243` cycles，p10/p90 =
  `-113.653/-100.240`，61/61 win。
- decap：paired median `-88.853` cycles，p10/p90 =
  `-101.116/-82.876`，61/61 win。
- encap/decap 都少 526 retired instructions，對應兩次 generic `poly_ntt`。
- 四個 KEM-context NTT site 各少 263 instructions，paired median 分別為
  `-45.294/-45.767/-44.489/-44.977` cycles，全部 61/61 win。
- 2562 次 paired correctness checks：0 mismatch。

因此前一節的「跨 binary full-KEM 暫時不可判讀」已被新 harness 解決。
G1R123+S2 後續已正式提升為 GT production default；原本路徑透過
`GT_PRODUCTION_USE_LEGACY_NTT=1` 保留作 regression baseline。
完整分布、frontend/backend counters 與 linkage audit 在：

- `aarch64-bench/results/u01v3_g1_r123_paired_kem/summary.md`
- `experiments/forward_ntt_phase123_u01/g1_stage345_reduction_slothy/u01v3_g1_r123_s2_candidate_summary.md`
