# GT768：eager qualification、identity-only serializer、固定 M network

日期：2026-09-22。Branch：`avx2-gt-ntt`。這三項是分開的實驗，
沒有把 eager、identity deletion 或 parked prefixed hash-buffer 疊加。
本文件後段的 network 是模型，不是新 ASM 或已測性能。

## 1. Eager BaseMul qualification

### 算術與包裝

Eager 把原有 R² finalizer 提前到每個 quartic output 完成時，
省下 36 stores＋36 reloads。276 Montgomery chains、M ABI、`e=0`、
λ、獨立 add-m、hash staging 不变。原始與候選的 signed-word expression DAG
及 arithmetic-expression multiset 相同，包含 Montgomery low-word wrap。

九次 SUPERCOP-derived polynomial 測量：BaseMul −27.83 cycles；完整
polynomial island −47.23 cycles，兩者均 9/9 同方向。
這不是完整 Native Encap，不能用它直接 promotion。

Production-shaped qualification 區分兩種包裝：

1. **Encap-only namespaced**：EnCap 換 eager，Decap 保留原 general-M。
   這使原 body 與 eager 共存，O3GC normal `.text` +704 B、`.rodata` +960 B。
2. **Shared in-place**：只替換原 general-M emission，保留原 `.text` section
   及 constant table；Encap 與 Decap 的 general-M 呼叫共同使用 eager。
   Keygen 不呼叫這個 entry。沒有複製 body、沒有 test wrapper 安裝進 Native。

中間一版 shared installer 誤引入新 per-function text section，讓 entry
額外移動 576 B，已標 `SUPERSEDED.md`。修正不是 padding/link-order 搜尋；
中間版的所有來源和數據仍保留，不從三批 Native 結果挑最漂亮的一批。

驗證包括既有 10003 primitive raw/oracle cases、alias、canary、guard pages、
range-expression proof；新增 shared 路徑的 **100 distinct deterministic keys**，
對 current GT 驗證 Encap/Decap、invalid PK、非 canonical 及 canonical-invalid CT，
並通過 C wrapper ASan/UBSan。Native 自己的 correctness/try/checksum 同樣執行。
這不是將 100 組單一 key 的 coins 冒充 100 組獨立 key。

### 方法與結果檔

- Pinned SUPERCOP 20260831；pristine `/home/nuc/supercop-20260627` 未修改。
- CPU1、performance、turbo disabled；SMT sibling `1-2`，未關閉 sibling。
- 實際 `cpucycles` backend：`default-perfevent`；不是聲稱 RDPMC，也不是
  whole-process perf stat。
- Native：未修改 `crypto_kem/measure.c`、正常 compiler selection、各 9 fresh
  processes、每 operation/launch 96 observations、pinned stabilized quartiles。
- Fixed：共同 O3GC，四種 placement/ASLR 各16 ABBA/BAAB blocks、64 launches。
  這裡 paired runner 的欄名 `official` 指 **frozen current GT control**，
  不是 SUPERCOP Official；真正 Official 另列 Native 三方比較。
- 主設定預先固定 normal/ASLR-on；不平均挑選 placement 來掩蓋回退。
- `qualification-summary.json` 保存 source snapshots、ELF hash、linked body
  audit、compiler、symbol placement、逐 launch quartiles、Native deltas 與 CI。

Encap-only 包裝沒有通過：Native candidate/current/Official 分別為
28486.21 / 28163.13 / 28126.49 Encap cycles，所選 recipes 分別 `-O` / `-O3` /
`-O2`，不能把 Native 差值純粹歸給 eager。共同 O3GC 的主設定 Encap
−35.13 cycles、CI [−98.69,+26.64]；Decap +91.24、CI [+41.02,+143.01]。
因此不 promotion。此結果保存在 `results/eager-qualification-20260922/`。

### Shared in-place 最終 qualification：未通過，不改 clean

下表是**同一個最終 campaign** 的 Native StQ2；三個 implementation 各9次 fresh
process。Official/current/eager 所選 compiler 為 gcc15.2.0 `-O2` / `-O3` / `-O2`。

| Native cycles | Official | Current GT | Shared eager | eager − current | eager − Official |
|---|---:|---:|---:|---:|---:|
| Keygen | 21580.56 | 21224.34 | 21330.57 | +106.23 | −249.99 |
| Encap | 28253.82 | 28186.30 | 28323.80 | +137.50 | +69.98 |
| Decap | 19470.50 | 19189.44 | 19122.01 | −67.43 | −348.49 |

这些不是 paired causal deltas，compiler selection 本身是 Native evidence 的一部分。
不因選到的 recipe 不利就強制 O3 後把它改稱正常 Native selection。

共同 O3GC fixed-ELF，**candidate − current GT**；括號為 block-bootstrap95% CI：

| Setting | Encap | Keygen | Decap |
|---|---:|---:|---:|
| **normal／ASLR-on（主設定）** | −20.24 [−44.84,+6.92] | +59.42 [+35.57,+84.52] | −20.34 [−45.21,+4.73] |
| normal／ASLR-off | −94.92 [−147.05,−39.59] | +96.38 [+82.19,+110.26] | −41.68 [−59.19,−23.72] |
| reversed／ASLR-on | −109.43 [−187.11,−27.67] | +49.94 [+20.45,+78.46] | −52.09 [−103.46,−5.93] |
| reversed／ASLR-off | −52.49 [−111.15,+0.96] | +55.78 [+42.95,+68.92] | +3.10 [−31.45,+37.57] |

主設定 Encap 10/16 favorable blocks，但 CI 跨零；Keygen 僅1/16 favorable，
四組都有顯著正 delta。Keygen source/arithmetic 未改，這是未釐清的 whole-image
回退；沒有 PMU/額外因果對照，不把它硬命名為某一個 frontend/cache bottleneck。

Linked audit確認 general-M entry 的地址在正常與反向各自 control/candidate 間
完全相同（normal39168、reversed33824），函式684→655 B，data loads132→96、
stores84→48。這仍不能保證整個 image 的其他位置、dependency或caller會更快。
normal整體 `.text` 均64407 B，`.rodata`56808→56840 B；函式縮小29 B不等於
整個 ELF 必然縮小29 B，metadata及alignment也要列出。

結論：**qualification 已做完但 performance gate 未通過，eager 不進 clean。**
不從 ASLR-off 或 reversed 挑較大的勝幅，不疊上 serializer 掩蓋失敗，也不繼續
掃 favorable link orders。原始結果在
`results/eager-shared-inplace-qualification-20260922/qualification-summary.json`。
因 current-GT no-regression gate 已失敗，本輪不再額外做 Official-vs-eager 的
paired confirmation；已完成的 paired comparison 不冒稱那一組比較。

## 2. 只刪 14 個 identity `vpermq`

新增獨立符號 `ntruplus768_exp001_pack_identity14`；對 frozen current M
只刪 `vpermq $0xe4, same_ymm, same_ymm` 的14次出現。
`0xe4` 的 qword indices 是 `[0,1,2,3]`，AVX2 flags 不變，因此它們確實是
沒有資料效果的指令。其他算術、operands、store order、mask 都保持不變。

保留 lazy entry 的5120 B cage（padding 位於 ret 之後，不在 hot path）、32-byte
alignment；ciphertext highrange entry 也保留原有的一次 tail jump。
最初測試漏掉這次 jump，該批明確標 superseded；下表只採修正後結果。

| 同 ELF，normal/ASLR-on，3 fresh processes | Candidate − current M | 勝出 launches |
|---|---:|---:|
| r packing | −6.65 cycles | 3/3 |
| c packing | −8.85 cycles | 3/3 |
| r Forward＋retained state＋hash input bytes | −0.40 cycles | 2/3 |
| 完整 polynomial island | −17.56 cycles | 3/3 |

完整 island launch deltas：−19.04、−14.92、−20.13 cycles。
這是 **SUPERCOP-derived diagnostic**，不是 Native，也不是 production qualification。
不相加 r/c isolated cycles 代替完整 island。未變更函式的 timing differences
是同碼 controls，不宣稱額外收益。

驗證：65536 個 shifted full-i16 向量掃描（每個 lane 掃過全部 int16 值）＋
10003 random vectors；獨立 scalar wire oracle；immutability、canary、guard-page
尾端；100 deterministic Encap vectors、invalid PK/CT、sanitizer。
Linked audit 比對完整 instruction sequence，恰好少14條 identity；沒有 spill。
所有 compile inputs 已按原本記錄的 SHA-256 存成快照。

結論：**identity-only 可以進 serious pricing；本轮未升 production。**

## 3. 同一 M ABI：非 identity 不是全都要獨立執行

實際 reachable serializer 的48個 qword permutations：

| immediate | qword ownership | 次數 |
|---|---|---:|
| `0xe4` | `[A,B | C,D]` | 14 |
| `0xb1` | `[B,A | D,C]` | 11 |
| `0x4b` | `[D,C | A,B]` | 12 |
| `0x1e` | `[C,D | B,A]` | 11 |

`|` 是128-bit half boundary；每個字母是一個64-bit qword，含4個 int16。
這些 permutation 都保留 adjacent coefficient pairs，所以能交換到
canonicalization 與 `vpmaddwd [1,4096,...]` 後面。原因是前者 lane-wise，
後者的係數對在每個 qword 內保持不變，且每對使用同樣的常數。

新的 model 保留全部144個 transpose unpacks：

```text
M planes
  → 原 transpose
  → 原 v9 reduction / sign correction
  → 原 paired VPMADDWD
  → 一次 PSHUFB（換成 ownership-specific mask）
  → 原地址與寬度的 stores（選擇先寫哪個來源 half）
```

例如 `0x4b` 需要 `[D,C | A,B]`。不先跨 half 交換整個 YMM：
low half 的既有 byte mask 輸出 packed `[A,B]`，high half 輸出 `[D,C]`；
先 extract high half 到 xmm14、寫低地址16 B，再把 low half 寫到 `offset+12`。
**仍先写低地址，再写高地址**，否則兩個16 B stores 的4 B overlap會出錯。
最後 packet 仍只寫16＋8＋4 B，不超出1152 B輸出。

`0xb1` 則只需把原 packing mask 改為（每 half）
`[8,9,10,12,13,14,0,1,2,4,5,6,128,128,128,128]`。
原 mask 本就要讀取，並不是新增一次 shuffle 再宣稱省下一次 shuffle。

| 每次 serializer | 原 current M | Identity-only ASM | Mask/store model |
|---|---:|---:|---:|
| `vpermq` | 48 | 34 | 0 |
| transpose unpacks | 144 | 144 | 144 |
| 全 routing instructions | 288 | 274 | 240 |
| hot instructions | 773 | 759 | 725 |
| data loads / stores | 48 / 97 | 48 / 97 | 48 / 97 |
| constant operands | 98 | 98 | 98 |
| Barrett vectors | 48 | 48 | 48 |
| peak model YMM | 7 | 7 | 7 |
| packing mask bytes | 32 | 32 | 128 |

Mask/store model 已驗768 owners、48 packets、全部store地址/寬度/順序，
1536 signed impulses、zero/boundary、128 random polynomials；獨立 scalar wire
oracle exact；v9 reducer完整65536域重驗；generator重跑 identical。
Concrete instruction operands 與 def/use model allocation 通過，但 **沒有新增此方案
ASM、沒有 linked proof、沒有 timing**。

### 與舊 TF1 的區別，以及仍未知的部分

舊 TF1 已透過 transpose orientation 吸收11個 symmetric swaps，並刪14 identity；
這不是本次的新發現。新 model 另處理23個 cross-half cases：把半部內順序融入
既有 packing mask，把 half ownership 表達為相同 store 地址的來源選擇。
它不依賴換 M ABI，不重建另一份 M，也不把轉換丟給 Forward／BaseMul／decode。

仍有代價：多96 B masks；23個 packet 的 extract 要在 first store 前完成，
dependency 改變。省48條指令不等於省48 cycles。下一關應將此 model
單獨落 ASM，對 original 與 identity-only controls 比較完整 materialized Encap island。

**144個 transpose unpacks 尚未找到更便宜的替代 network。** 它们把不同 degree
planes 合成 wire 所需的 quartet/pair，確實在做 ownership 工作；不能單靠換 store
地址刪掉。同時也沒有證明144是 AVX2的全域下界。它們必須和真正的 identity、
可合併到其他必要指令的非 identity、12-bit packing的byte selection區分開。
PK decode 本輪沒有修改或宣稱收益。

## 後續：Mask/store 已落成 ASM

同 M ABI 的三向 caged 短測已完成，完整 polynomial island：
Current 2798.44、Identity-14 2791.08、Mask/store 2764.36 cycles。
Mask/store 比 Current −34.08、比 Identity-14 −26.72，兩者均3/3同方向。
詳細 gate、限制與 raw campaign 見 [Mask/store 三向報告](ntruplus768-maskstore-triad.md)。
本節 supersede 上面的「尚未 ASM/timing」進度，不改寫先前歷史結果。
Eager 維持 parked；Mask/store ready for serious，不是 production promotion。

## 4. 重跑

從 `avx2_gt32_tile4_official_001` experiment：

```sh
python3 tools/generate_encap_fn_eager.py --check
make encap-fn-eager-check encap-fn-eager-sanitize eager-shared-check
python3 tools/run_encap_fn_short.py --supercop-root /home/nuc/supercop-20260627 --tag NEW-SERIOUS-TAG --launches 9

python3 tools/generate_pack_identity14.py --check
make pack-identity14-check
python3 tools/run_encap_fn_short.py --supercop-root /home/nuc/supercop-20260627 --tag NEW-ID14-TAG --candidate identity14
python3 tools/research_pack_mask_network.py --check
```

Native 使用 repo `scripts/prepare_supercop.py` 建立**新的** disposable root 後：

```sh
python3 tools/qualify_encap_eager.py --campaign-root NEW-CAMPAIGN-ROOT --stage native --shared-body --result-tag NEW-QUAL-TAG
python3 tools/qualify_encap_eager.py --campaign-root NEW-CAMPAIGN-ROOT --stage fixed --shared-body --result-tag NEW-QUAL-TAG
python3 /home/nuc/src/ntru_plus/scripts/summarize_supercop_paired.py --campaign results/NEW-QUAL-TAG/paired --parameter 768
python3 tools/close_eager_qualification.py results/NEW-QUAL-TAG
```

Installer預設使用本次已通過的九-launch source qualification；若 control source
變更會依 hash 拒絕，須另建立新 qualification，不得繞過。
