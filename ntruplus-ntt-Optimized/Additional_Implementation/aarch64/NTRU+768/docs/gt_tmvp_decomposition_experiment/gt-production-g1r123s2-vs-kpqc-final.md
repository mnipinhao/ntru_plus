# GT Production G1R123+S2 三方 Benchmark

日期：2026-07-10

## 比較版本

- `GT new`：目前 production default，forward NTT 為 G1R123+S2。
- `GT legacy`：promotion 前的 GT production forward NTT，使用
  `GT_PRODUCTION_USE_LEGACY_NTT=1` 重建。
- `KPQC final`：`ntruplus-KpqC-Final` 未修改版本。

三者都使用 portable `NO_CE` hash path。Pi 5 Cortex-A76 core 3，
`NTESTS=61`、`NITERATIONS=2000`、`NWARMUP=100`。輸入與 KEM randomness
由 aarch64-bench deterministic derand setup 產生；每個 binary 在量測前
先完成一次 keygen/encap/decap correctness check。這輪 CPU governor 是
`ondemand`，run 結束時為 1.6 GHz，`throttled=0x0`。

Promotion correctness 補充：new 與 legacy 的 deterministic
`PQCkemKAT_2336.rsp` byte-for-byte 相同，SHA-256 為
`dca76b32748655990289002a05f7b1d648334d7ded05845c7fe3f1449d26690f`。

## Full-KEM cycles

| Operation | KPQC final | GT legacy | GT new | New vs KPQC | New vs legacy |
|---|---:|---:|---:|---:|---:|
| keygen | 39966 | 37982 | 37966 | -5.004% | -0.042% |
| encap | 39013 | 37755 | 37590 | -3.648% | -0.437% |
| decap | 35180 | 32629 | 32482 | -7.669% | -0.451% |

## Retired instructions

| Operation | KPQC final | GT legacy | GT new | New vs KPQC | New vs legacy |
|---|---:|---:|---:|---:|---:|
| keygen | 80801 | 81147 | 81147 | +0.428% | 0.000% |
| encap | 103980 | 105650 | 105124 | +1.100% | -0.498% |
| decap | 72677 | 74932 | 74406 | +2.379% | -0.702% |

## 判讀

G1R123+S2 每次 generic forward NTT 固定少 263 retired instructions，所以
encap 與 decap 各少 526 instructions。三方 separate-binary cycle 結果也都顯示
new GT 比 legacy GT 快。

keygen 的 new/legacy instructions 完全相同，因為 production keygen 使用
specialized triple NTT，不會呼叫 generic `poly_ntt`。keygen 的 16-cycle 差不能
歸因給 G1R123+S2，應視為 binary layout/cache 差異。

GT new 對 KPQC final 的 cycle 優勢是 3.6% 到 7.7%，但 instructions 仍多
0.4% 到 2.4%。這表示目前 GT 的 cycle 優勢來自 Cortex-A76 上較好的執行效率，
尚未達到原定 20% scheme-level 目標。

同一 binary 的 legacy/new paired harness 仍是判斷 NTT promotion 收益的主要證據：
encap median `-106.243` cycles、decap median `-88.853` cycles，兩者都是
61/61 paired wins。三方 benchmark 用來回答整體 GT 與 KPQC final 的位置。

完整 percentiles、raw outputs、binary metadata：

- `aarch64-bench/results/gt_vs_kpqc_after_invntt_promotion_2026-07-10/summary.md`
- `aarch64-bench/results/u01v3_g1_r123_paired_kem/summary.md`
