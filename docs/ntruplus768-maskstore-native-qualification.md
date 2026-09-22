# GT768 Mask/store：Native 與 paired qualification

2026-09-22，branch `avx2-gt-ntt`。

**Encap 收益已在主設定得到 paired 支持，但整體 qualification 未通過。**
原因是主設定 Keygen 有顯著 regression，以及兩組 ASLR-off Encap CI
仍跨零。保留 experiment；未修改 clean production、不掃有利 link order。

## Candidate 與 correctness

獨立 disposable campaign：
`/home/nuc/src/supercop-maskstore-qualification-20260922`。
Implementation：
`avx2-gt32-maskstore-exp-sc20260831`。

從 frozen current GT 安裝，只改 `pack.s` 中一個既有 lazy serializer
emission，保留原 section、symbol、5120-byte cage、highrange tail jump。
不安裝 triad 的三個測試 bodies，不安裝 deterministic test wrapper。
額外的三個 aligned masks 共96 bytes；Eager、prefixed hash buffer 都未整合。

核對 reachable call graph 後，**實際改動只服務 Encap**：

- Encap r 使用 lazy entry，ciphertext 使用 highrange→lazy entry。
- Decap recovered-r 使用獨立的 centered serializer，這次沒有改。
- Keygen 使用 P serializer，這次沒有改。

這修正了實作開始時「可能一起改到 Decap」的假設；
installer manifest 已修正，不能將 Decap／Keygen 的 cycle 變化歸因於新的 arithmetic。

驗證 actual installed files，而非僅研究 wrapper：

- 100個不同 deterministic keypairs，逐 byte 比較 PK/SK/CT/SS transcript。
- Valid Encap/Decap、invalid PK、noncanonical CT、canonical-but-invalid CT
  的 return／失敗 shared-secret 行為一致。
- Current／candidate 普通和 ASan/UBSan 四種 builds transcript 一致。
- LeakSanitizer 在本環境有 ptrace 限制，初次 check 在 functional pass 後停止；
  final check 沿用既有 `detect_leaks=0` 政策。**沒有宣稱 leak detection 通過。**
- 所有 Native builds 的 SUPERCOP try/measure 完成；measure.c 未修改。
- Installed 與 Native linked serializer 的全部 operands、實際 constant bytes、
  def/use、alignment 對照 serious model；725 instructions、peak7、無 stack/spill。
- Final source snapshot、ELF hashes、run logs、逐 launch 96 observations 全部保留。
  Clean／pristine 未修改。

## Native：唯一 Official baseline 與兩個 GT versions

Pinned SUPERCOP 20260831，lock 不更新；CPU1/performance/turbo disabled。
未修改 `crypto_kem/measure.c`，正常 compiler selection，
每實作9個 fresh processes、每 operation864 observations，StQ1/2/3完整保存。
本輪三者都選 GCC15.2.0、O2 recipe。Counter 都是 `default-perfevent`，
不是 RDPMC。SUPERCOP cpuid 字串為 `unknown_CPU_ID_`，另保存 host topology，
不能把這個字串當成已辨識的 CPU 型號。

| Operation | Official StQ2 | Current GT StQ2 | Mask/store StQ2 | Mask−Current | Mask−Official |
|---|---:|---:|---:|---:|---:|
| Keygen | 21564.27 | 21272.14 | 21259.40 | −12.75 | −304.88 |
| Encap | 28140.69 | 28268.28 | 28170.90 | **−97.38** | **+30.21** |
| Decap | 19447.67 | 19200.22 | 19206.75 | +6.52 | −240.93 |

Mask−Current 的 index-matched direction 為 Keygen5/9、Encap7/9、Decap3/9。
這些是**串行獨立 campaign**，不是 ABBA causal paired evidence，
所以不直接把 −97.38 當成 serializer patch 的精確收益。
也不能稱 Mask/store Encap 已贏 Official；本次點估計仍 +0.107%。
Keygen／Decap 相對 Official 的較大收益屬於既有 GT 路線，
不是本輪未執行於它們的新 serializer。

## Fixed-ELF paired：candidate 對 frozen Current GT

共同 O3GC recipe。四組設定，每組16個 ABBA/BAAB blocks、
64 fresh launches；主設定事先固定 normal/ASLR-on，不挑最好看的設定。
通用 paired manifest 的 `official` 欄在此代表 **Current GT**，
不是 pinned SUPERCOP Official；兩種比較不可混淆。

| Setting | Encap paired mean Δ | Bootstrap95% CI | Favorable blocks |
|---|---:|---:|---:|
| **normal / ASLR-on（主）** | **−95.38** | **[−154.35, −44.32]** | **14/16** |
| normal / ASLR-off | −75.96 | [−338.71, +108.57] | 8/16 |
| reversed / ASLR-on | −101.49 | [−240.35, −4.48] | 13/16 |
| reversed / ASLR-off | −22.49 | [−79.47, +30.33] | 10/16 |

主設定 Keygen：**+64.63 cycles，CI [+18.38,+116.74]**，
只有3/16 favorable blocks。其餘三組 Keygen CI跨零，
因此不是「四組都顯著退步」，但主設定 regression 已足以阻止 qualification。
Decap 四組 CI均跨零，沒有穩定增益或顯著回退結論。

normal/ASLR-off Encap 的 paired median 是 +9.85、paired mean 是−75.96；
寬 CI 和8/16 blocks明確顯示不確定性，不可只引用負 mean。
所有 blocks、raw observations、bootstrap estimator 結果均保留，
沒有丟掉不利樣本或再跑到有利為止。

## Machine 與因果限制

Common O3GC 正常／reversed 的兩組 control/candidate：

- `.text` 同為64407 bytes；lazy function cage 同為5120。
- `.rodata` 56808→56936：linked 增128 bytes，不能把96-byte mask payload
  誤報成完整 section delta；另含 placement/padding差異。
- 每種 placement 內，Keygen、Encap、Decap、centered pack、lazy pack
  的 entry地址和symbol size都與 control相同。
- Lazy hot body 從4543→4255 bytes，但 cage padding吸收差額。
- Keygen／Decap 的 C/ASM source paths 未改。

這些檢查**不能證明** Keygen 回退一定是 I-cache、constant-cache、
branch predictor 或任何單一原因。Cycle-only evidence 支持的是
「目前完整映像沒有通過全 operation qualification」，
不是「刪掉這些 permutation 本身無效」。

## 決策

1. 同 M serializer 的模型、ASM、primitive、serious polynomial-island 收益保留。
2. 完整 Encap 在預先固定的 ASLR-on主設定有正面 paired evidence。
3. ASLR-off confirmation不足、主設定 Keygen regression，**本次不 promotion**。
4. 不疊加 eager、不自行拓展 centered serializer、不重新挑 link order。
   是否再做 whole-image attribution需下一次明確決策。

## Artifacts／重跑

Experiment：
`ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_gt32_tile4_official_001`。
Campaign results：`results/maskstore-native-qualification-20260922/`。

- `installed-check-final/`：100-key transcripts、sanitizer與installed audit。
- `native-{official,current,candidate}/`：Native raw data/run.out、九次重跑、compiler。
- `fixed-*/`、`paired/`：四種配置、256 fresh launches、CI與symbol placement。
- `installed-sources/`、`qualification-summary.json`：來源凍結、linked proof、
  Native三方差值與gate verdict。

```sh
python3 tools/qualify_pack_maskstore.py --campaign-root /home/nuc/src/supercop-maskstore-qualification-20260922 --stage native
python3 tools/qualify_pack_maskstore.py --campaign-root /home/nuc/src/supercop-maskstore-qualification-20260922 --stage fixed
python3 tools/close_maskstore_qualification.py
```

以上是此 campaign 的續跑／closure 命令，不應覆寫既有 paired資料。
獨立 rerun 必須另建新的 campaign/result identity。
