# GT768 fixed-M serializer：Current／Identity-14／Mask-store

2026-09-22。結論：Mask/store 已通過 ASM correctness 與 linked audit，
並在三個 fresh processes 的完整 materialized polynomial island 都勝出。
**Ready for serious pricing；不是 Native／production winner。**
Eager BaseMul 停留在前輪未通過 qualification 的狀態，本輪未使用。

## 比較範圍

- C：current clean M serializer 的原樣展開，namespaced control。
- I：只刪除 14 個同 register 的 identity `vpermq $0xe4`。
- M：同一 M ABI，全部 48 個 qword permutation 由既有 byte-mask 與
  store source selection 吸收。
- Forward、decode、BaseMul、add-m、materialized boundaries 全部不變。
  未引入 eager、add-m fusion 或 prefixed-hash-buffer experiment。
- Polynomial island 從 PK bytes、r/m coefficients 到 r hash **input bytes**
  與 ciphertext bytes；不包含 hash_g 本身，也不稱 Native Encap。
  完整 deterministic research Encap 用於 correctness，維持原 hash staging。

## 真正刪掉了什麼

| 每次 pack，linked 熱路徑 | C | I | M |
|---|---:|---:|---:|
| Instructions，含 inherited vzeroupper/ret | 773 | 759 | 725 |
| Routing | 288 | 274 | 240 |
| Transpose unpacks | 144 | 144 | 144 |
| vpermq | 48 | 34 | 0 |
| Barrett vectors | 48 | 48 | 48 |
| Input loads | 48 | 48 | 48 |
| Output stores，包括最後小寬度 stores | 97 | 97 | 97 |
| Constant memory operands | 98 | 98 | 98 |
| Peak live YMM | 7 | 7 | 7 |
| Hot bytes，至 ret 為止 | 4543 | 4459 | 4255 |
| Function cage bytes | 5120 | 5120 | 5120 |

M 比 C 多 96 bytes 的 masks；沒有多一次 shuffle 或 constant operand。
對 23 個 cross-half packet，extract 必須提前到第一個 store 之前；
此依賴變化存在，不能把 48 條指令直接換算成 cycle。

所有版本保留現有的一個 `vzeroupper`，沒有順手增刪。
Entry 和 constant table 都是 32-byte aligned；三個 entry 相隔 5120 bytes，
本 ELF addresses 分別為 0x3c20、0x5020、0x6420。Cages 的 padding 在 ret 後。
Highrange entry 各保留一次 tail jump，使用相同的 32-byte cage。
這控制了 spacing/alignment，**不代表三者具有同一個 code address**；
cache set、caller wrapper placement 等差異仍可能存在，尚待後續 confirmation。

重要 ownership 細節：16-byte stores 每 packet 在 offset 0、12 重疊，
必須保持低地址 store 在前。M 改的是來源 half，不是任意交換寫入次序。
最後 packet 保留 16+8+4-byte writes，不超過 1152-byte output。
144 個 transpose unpacks 仍負責 degree-plane → wire ownership；
本輪沒有證明它們冗餘，也沒有證明它們是下界。

## Correctness 與 linked gate

- 65536 shifted signed-i16 vectors：每個 physical lane 遍歷完整 signed-word domain；
  另外 10003 random full-word vectors、1536 ±impulses、zero、alternating boundary。
- Independent scalar wire oracle；ASM 與 current bytes exact，r/input immutable。
- Input/output canaries 和 guard-page ends。輸入1536 bytes、輸出1152 bytes；
  合約是不同 buffers，不宣稱支援未定義的 overlapping alias。
- v9 reducer 的 full signed-i16 model exhaustive；沒有新增 reduction/range假設。
- 100 deterministic Encap vectors、valid Decap、invalid PK/CT 行為，以及
  ASan/UBSan C wrapper 通過。覆蓋是**一個 key 下的100組 coins**，
  不是100個 independent keypairs；不取代下一輪 qualification。
- Linked instructions 的全部 operands/immediates 與模型逐一對照，
  每個 RIP-relative constant 的實際32 bytes亦逐一驗證。
  Def/use replay peak7；無 stack、spill、call、secret branch/index。
- ASM memory safety 另有 guard/canary，不以 C sanitizer 代替。
- Generator `--check`、來源與 ELF hashes 保存；clean manifest 未變。

## Cycle-counter 短測

Pinned SUPERCOP 20260831 `cpucycles()`，實際 backend **default-perfevent**，
不是 RDPMC。CPU1、performance、turbo disabled，normal/ASLR-on 預先固定。
同 ELF、common O3GC、同一 state address、8組實際CBD1/SOTP input banks；
對每次 invocation 都先 reset、warmup、再 reset，全部在計時區間外。
Operation/function selection 在計時區間外，timed region 只有匹配 indirect call。

三向順序為 ABC/BCA/CAB/CBA/BAC/ACB，重複16次；
每個 variant/region 每 launch 96 observations，3 fresh processes。
StQ1/2/3 使用 pinned estimator；下面是 pooled StQ2，非 median，也不是 PMU score。

| Cutpoint | C | I | M | I−C | M−I | M−C |
|---|---:|---:|---:|---:|---:|---:|
| r pack | 467.92 | 456.36 | 446.28 | −11.56 | −10.08 | −21.64 |
| c pack，含既有 highrange tail jump | 466.93 | 458.79 | 445.64 | −8.14 | −13.15 | −21.29 |
| r Forward → retained state + hash bytes | 1133.46 | 1128.97 | 1108.92 | −4.49 | −20.06 | −24.54 |
| 完整 polynomial island | 2798.44 | 2791.08 | 2764.36 | −7.36 | −26.72 | **−34.08** |

完整 island 的三次 launch：

| Delta | Launch 0 | Launch 1 | Launch 2 |
|---|---:|---:|---:|
| I−C | −6.21 | −9.17 | −5.54 |
| M−I | −29.29 | −22.58 | −28.92 |
| M−C | −35.50 | −31.75 | −34.46 |

所有 cutpoints、三種 delta 均3/3同方向。只能說本配置短測中，
**非 identity absorption 的額外收益保留到完整 island**。
不把 isolated pack cycles 相加預測 caller；也不把前輪 Identity-14 的
−17.56 和本輪 −7.36 混用，它們來自不同 ELF/harness。
同一批資料沒有挑最快 placement，更没有從三個 variant 挑樣本。

## Serious pricing：獨立九個 fresh processes

2026-09-22 後續授權已執行。Campaign：
`results/pack-maskstore-triad-serious-20260922/`。
未修改候選 ASM 或 C benchmark；只將 runner 的 launch 數參數化，
並加入逐 launch 前後的 host controls／counter identity／來源不變檢查。
Short 與 serious 的 ELF hash 不同，但差異僅非載入的 `.strtab`；
所有 allocated sections、code/data、addresses 完全相同，驗證保存在
`verification.json`。不是重選 placement。

每個 variant/cutpoint 共864 observations，三方六向 counterbalance 與
相同 input addresses 維持不變。CPU1/performance/turbo-disabled/
normal-ASLR-on；backend 為 `default-perfevent`。
再次通過 correctness、sanitizer、linked audit、generator/model check；
240個測試資料集的 Python StQ 計算與 pinned C `stq_longlong` 相同。

| Cutpoint | Current StQ2 | Identity StQ2 | Mask/store StQ2 | I−C | M−I | M−C |
|---|---:|---:|---:|---:|---:|---:|
| r pack | 466.94 | 457.89 | 446.21 | −9.05 | −11.68 | −20.73 |
| c pack | 466.91 | 458.17 | 446.77 | −8.74 | −11.40 | −20.14 |
| r state + hash bytes | 1135.43 | 1131.47 | 1111.61 | −3.96 | −19.86 | −23.82 |
| 完整 polynomial island | 2801.61 | 2791.37 | 2765.49 | −10.24 | **−25.88** | **−36.12** |

完整 island 的 StQ1/2/3：

| Variant | StQ1 | StQ2 | StQ3 |
|---|---:|---:|---:|
| Current | 2782.64 | 2801.61 | 2822.82 |
| Identity-14 | 2774.79 | 2791.37 | 2809.88 |
| Mask/store | 2748.35 | 2765.49 | 2784.30 |

M−C 的9個 launch delta：
`[-38.17, -31.25, -38.21, -38.63, -32.58, -34.96, -37.88, -33.50, -36.67]`。
完整 island 的 I−C、M−I、M−C 都9/9同方向；M−I 範圍
−32.33到−20.33 cycles。M 對 C 與 I 在其餘三個 cutpoints 也全部9/9。
唯一平手是 r dual-output 的 I−C 一次為0，因此該項為8勝1平，
不能概括說全部 comparisons 都9/9。

結論：**本固定配置的 serious polynomial-island gate 通過**。
M−C 約−1.29%；非 identity absorption 的增量仍存在，
不是只有 identity deletion 的效果。不將兩次 pack 的 isolated delta
相加預測 island，也不由此推導 Native Encap cycle。
來源、clean manifest、ELF campaign內均未變；raw資料重算檢查通過。

這輪尚未驗證 reversed placement、ASLR-off、Native KEM 或 production。
下一步可提出獨立 serializer-only Native candidate qualification；
須檢查三個 KEM operations 與 placement controls，不能直接改 clean。
Eager 和 prefixed-hash-buffer experiment 仍然不整合。

重跑 serious（新 tag，不覆寫歷史）：

```sh
python3 tools/run_pack_triad.py --supercop-root /home/nuc/supercop-20260627 --tag NEW-SERIOUS-TAG --launches 9
python3 tools/close_pack_triad.py --tag NEW-SERIOUS-TAG
```

## Native qualification 後續

已完成 serializer-only Native 與四種 paired controls：
Native Encap 對 Current GT −97.38，但對 Official +30.21 cycles；
主設定 paired Encap −95.38、CI排除零，同時 Keygen +64.63 的CI也排除零。
ASLR-off Encap confirmation不足，故**不進 clean production**。
詳見 [Native qualification 報告](ntruplus768-maskstore-native-qualification.md)。
這補充後續進度，不改寫上面的 serious island 結論。

## 短測時的下一關判斷（歷史）

優先對 Mask/store 做獨立9-process serious pricing，保留 I/C attribution；
之後才考慮 Native 與 placement/ASLR qualification。短測的三點不足以建立
production confidence interval。本輪未跑 serious、Native，未改 clean。
Eager 維持 parked；不擴張 transpose／新 ABI。

## Artifacts 與重跑

Experiment：`ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_gt32_tile4_official_001`。

有效 campaign：`results/pack-maskstore-triad-20260922/`，包含：
raw launch CSV/stderr、summary StQ與三種delta、metadata/來源快照、ELF hash、
symbol/section表、三個 annotated disassemblies、linked audit、closure tests。
另兩個帶 short/exact-short 名稱的目錄只保存 audit 開發過程，**沒有 timing**；
原因與有效 campaign 指向已寫入各自 README。

```sh
python3 tools/generate_pack_triad.py --check
python3 tools/research_pack_mask_network.py --check
make pack-maskstore-check
python3 tools/run_pack_triad.py --supercop-root /home/nuc/supercop-20260627 --tag NEW-TRIAD-TAG
```

Runner 不修改 sysfs；不符合 host preflight 時停止。Re-run 使用新 tag，
不覆寫本次原始資料。Full source/lock identity 以 campaign metadata 為準。
