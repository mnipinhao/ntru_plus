# P3B38 — 分窗 RA + scheduling

結論：**不採用本次 allocation，維持 P3B37。**
六個成對 process medians 都未勝出。測得的差距很小，沒有達成
預設目標的 >1% Forward 改善；也不把這個結果解讀為所有 RA 都不可能有收益。

## 為什麼補做這輪

P3B37 鎖住 v0–v31，只能回答固定 allocation 下的 scheduling 問題。
P3B38 保持完全相同的數學與 instruction DAG，先讓內部值重新選 register，
再固定新 allocation 做 scheduling，檢查能否解除 register 重用造成的假相依。
不是刪除 reduction，也沒有改變 coefficient layout、R0 scale 或記憶體 boundary。

## 實作與限制

- Local Mac Slothy 0.2.0，使用
  /Users/chenpinhao/slothy_and_ra/.venv/bin/python。
- Target 是 neoverse_n1_experimental proxy；Cortex-A76 結論以 Pi 5 為準。
- 第一個 513-instruction global functional RA 在 30 秒回傳 UNKNOWN，
  不代表 UNSAT。原始 log 保留在 build/global-ra-timeout.log。
- 完成版本：factor 16、step 0.05 的分窗 RA，fixed order、no spill；
  接著同樣分窗 scheduling，鎖住 RA 產出的 physical allocation。
- RA 約 13.073 秒；RA + scheduling 約 46.006 秒。
- RA 改變 458 條指令的 register 使用，仍是 513 instructions。
  Window boundary 固定，因此不等同整段 global RA 的自由度。
- x0–x3 與 v13–v15 保留原使用方式；v13 是 routing table、v14 是 q，
  v15 是既有固定常數。內部 vector definitions 可重命名，但出口仍須回到
  wrapper 要求的原 physical registers。

Live-out vectors:
v31,v1,v9,v26,v20,v24,v30,v29,v22,
v19,v21,v23,v8,v10,v12,v6,v27,v0，以及 v13–v15。
Pointer updates: x0 +256，x1 不變，x2 +336，x3 +512。
沒有新增 coefficient load/store 或 wrapper save/restore。

## 正確性 gates

1. Contracts、static authoring checks、contract comparison 通過。
2. Slothy RA 與 scheduled full-region DFG self-check 都通過。
3. 獨立 SSA audit 驗證原版 → allocated → scheduled：
   output expressions、load addresses、pointer increments 完全一致。
   RA instruction-DAG order 不變，schedule 僅改順序。
4. Audit 的 arithmetic/address corruption negative controls 通過。
5. Pi full-KEM valid/tampered 8 cases、instrumentation equivalence 通過，
   cross-version public key/ciphertext differences = 0。
6. 完整 2F + D1 + I 對 int64 schoolbook 32 cases 通過。
7. 每個 Forward process 的 guard 256 cases 與 serialized equivalence
   64 cases 通過。
8. No spill；兩版 Pass-2 object text 都是 4544 bytes。

沒有新增算術 rewrite，因此沿用 P3B35 的 natural input [-3,4]、
Forward abs <=26731 range closure；並非一般任意 int16 input API。
LLVM selftest 在本機未啟用，不能把 Slothy self-check 說成 LLVM execution
test；實際執行驗證由 Pi 完成。

## 相同 boundary 的 complete Forward

Pi pi@100.99.191.9，taskset core 3，三輪各正反順序，
採六個 process medians 的 median；包含共同 input reset，未減去 overhead。

| 版本 | cycles | instructions | branches |
|---|---:|---:|---:|
| P3B37 baseline | 3517.086 | 4303.148 | 68.032 |
| P3B38 RA + schedule | 3522.816 | 4303.148 | 68.032 |
| 凍結 SUPERCOP comparator | 3853.359 | 3736.137 | 57.030 |

P3B38 多 5.730 cycles，約 +0.163%。不跨輪拿先前 3518.28 直接相減。
Instruction count、branch count 與 text size 均未改善。
Final throttle status = 0x0，temperature 67.5 C。
SUPERCOP comparator 沿用 campaign 的 20260627 / SHAKE256 source；
尚未核對為 upstream 最新版。沒有新增 full-KEM cycle claim。

## 檔案、重現與決策

- prepare.py：重用 P3B37 exact-region extraction / contract gates。
- optimize.py：local RA-first / window scheduling 設定。
- run_pi.py：independent exact-DAG audit、bounded staging、Pi correctness / PMU。
- test_audit.py：audit negative controls。
- score.py：保存 generic parser 輸出，明確處理 timeout-setting false positive。
- build/candidate.sym.S、allocated.S、scheduled.S：三個階段的 assembly。
- build/slothy.log、solver-result.json、environment.txt：Slothy provenance。
- build/post-audit.json、source-hashes.json、objects.log：對應 source/object。
- build/measurement.json、forward-*.log、kem-check.log、product.log：實機 evidence。
- build/sync：限定上傳 bundle；其中 t1=P3B37，raw=P3B38。

在本資料夾：

    python3 prepare.py
    /Users/chenpinhao/slothy_and_ra/.venv/bin/python optimize.py
    python3 run_pi.py --validate --prepare
    python3 run_pi.py --run --repeat --summarize
    python3 test_audit.py
    python3 score.py

prepare/staging 預期 fresh build/sync，避免覆蓋舊 measurement。
Generated artifacts 都放在 gitignored build/，不複製進 production。

Skill score 是 investigate：分窗 model estimates 無法直接相加成完整
Forward cycles，不能補造 aggregate estimate；實機差距也在 1% neutral
threshold 內。工程決策是 **不採用這次候選、保留 P3B37**。
不需要更多相同設定的 scheduling 調參；下一個有價值的 gate 應回到可證明
減少運算或 routing 的 DAG 變更，而不是把這輪當作 global RA 不可能的證明。
