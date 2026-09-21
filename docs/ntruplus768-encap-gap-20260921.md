# NTRU+768 Encap：目前差距與 AVX2 / NEON 解讀

日期：2026-09-21。這是既有證據的整合，不是新 benchmark。
目前 branch 已由 `avx2-gt-ntt-864-1152` 改為 `avx2-gt-ntt`；
歷史 campaign 的 branch 字串、source hash、ELF hash 不回寫。
本次只有 local branch rename，沒有 push、刪除或改名遠端 branch。

## 1. 目前比較的是誰

- Official：SUPERCOP 20260831，`ntruplus768/avx2`，以 lock 為準。
- GT：`avx2-gt32-clean`，不是被拒絕的 wavefront 或 serializer-unify。
- 平台：Intel Core Ultra 7 155H，既有正式 campaign 使用 CPU 1、performance、turbo off。
- Native normal compiler selection、same-ELF component、region PMU 分開判讀。

最近 Native 記錄：`results/encap-wavefront-native-20260921/summary.json`。
每個 implementation 9 fresh processes，每個 operation 864 observations。

| Operation | Official StQ2 | current GT StQ2 | GT − Official |
| --- | ---: | ---: | ---: |
| Keygen | 21600.63 | 21248.06 | −352.57 |
| Encap | 28085.76 | 28176.59 | +90.82（約 +0.32%） |
| Decap | 19437.83 | 19190.22 | −247.62 |

Official 選 GCC 15.2 O2；GT 選 GCC 15.2 O3。這是 Native 的合法選型差異，
不是相同 compiler 下的因果拆解。這批是串行 Native runs，不能稱為 ABBA paired。

Encap 的歷史 Native delta 曾為 +237.63、+29.26；它們來自不同 campaign。
不能把 +237.63 → +90.82 說成這輪 code optimization 的收益，也不能平均三批
資料製造一個精確的「目前固定 debt」。共同結論是：尚未證明完整 Encap 穩定勝出。

## 2. 真正的 Encap graph

```text
PK bytes → decode + validate → h(M) ──────────────────────────┐
coins + hash_f(pk) → hash_h → CBD1 → r coefficients           │
                       → GT frontend → AoS scratch → NTT32 → r(M)
                                                           ├→ retained arithmetic state
                                                           └→ Q24 bytes → hash_g
message + hash_g bytes → SOTP → m coefficients                │
                       → GT frontend → AoS scratch → NTT32 → m(M)
                                                            │
h(M), r(M) → general quartic BaseMul → +m(M) → ciphertext Q24 bytes
→ shared-secret copy / required clear
```

Encap 沒有 inverse NTT，也沒有 BaseInv。它不是 `2F → B → inverse`。
`r` 有 arithmetic 與 hash 兩個 consumer；m 是 transformed addend。
h 已由 PK 承載在 NTT-domain，不應額外做一次 Forward。
serializer 不可破壞之後 h×r 仍要使用的 r state。

Current source：
`ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/clean/avx2-gt32-clean/encap.c`。
其 scratch 含 h/r/m/c/work 五份 1536-byte array；這是 allocation 事實，
不能把全部 bytes 直接當作相對 Official 的額外 timed traffic。

## 3. 哪些地方贏，哪些地方落後

以下是 survey 的 operation-region PMU，單位是該 PMU 的 core cycles，
不是上表 Native StQ2；不能直接加減來解釋 +90.82。

| Region | GT − Official core cycles | 已觀察到的 machine 差異 |
| --- | ---: | --- |
| 兩次 Forward | −195.78 | instructions −1030、loads +252、stores −290 |
| general BaseMul | −17.22 | instructions −170、loads +105、stores −12 |
| r-state → hash-input wire bytes | 約 +22.71 | loads +96、stores +61 |
| ciphertext serialization | 約 +21.12 | loads +96、stores +61 |
| PK decode region | 約 +18～26，依 placement | 額外 decode/layout/validation 工作；不能省略 validation |

### Forward：已兌現收益，但不免費

GT3×32 消除 inter-axis twiddle；ring embedding/top split/twist、DFT3、
NTT32 則仍存在。CRT mathematical permutation 不等於 AVX2 免費搬資料。
目前 frontend → terminal 留一份 1536-byte AoS boundary，即每 Forward
48 stores + 48 reloads。M terminal 把 quartic AoS 轉 coefficient planes。
較多 loads 與 constant traffic 是成本，但實測少指令、少 stores 的收益仍較大。

### BaseMul：M 的好處確實被 arithmetic consumer 使用

同一 YMM 中同 degree、不同 leaf 的排列，讓 quartic products 可直接 SIMD。
但 wire serializer 的 ownership 不同，M 並不是所有 consumer 的最佳 presentation。
這是 producer/consumer trade-off，不是 M layout 全面失敗。

### 兩次 serialization：目前最清楚的局部額外工作

M planes → wire leaf/degree pairing → canonicalization → 12-bit packing。
`r` 要做一次供 hash_g；`h×r+m` 再做一次供 ciphertext。
Official 的 transform/arithmetic/wire geometry 與 GT 不同；GT 的 arithmetic
優勢不能免除 external byte-order contract。現有 Q24 masks 已把 mapping 融入
codec，並非只剩一個顯然可刪除的 adapter 函式。

函式名中的 `lazy10788` / `highrange12699` 不是本輪實測 range 證明。
最新模型給 Forward 15592、post-add 17448 的安全 envelope，serializer v=9
完整 signed-i16 硬體對照已通過。不能為符合歷史名稱額外插 reduction。

### 完整 caller residual：存在，但尚不能精確定價每個機制

matched polynomial island 已量到 normal −57.27、reversed −64.04 cycles。
shared prework/middle/tail 沒有呈現穩定的大額局部 GT penalty。
因此不能憑 Native 小幅落後，就反推某個 Forward stage 慢了固定 +238。

較早 current GT vs Official fixed-ELF（16 blocks，各 64 launches）：

| Placement / ASLR | Encap paired mean | block-bootstrap 95% CI |
| --- | ---: | --- |
| normal / off | −2.80 | [−64.45, 52.05] |
| normal / on | +18.34 | [−109.62, 120.86] |
| reversed / off | −6.37 | [−43.41, 31.82] |
| reversed / on | +74.51 | [17.58, 138.20] |

支持的結論：完整 caller 對 placement/ASLR 敏感，前三組沒有明確 winner。
不支持的結論：已證明 residual 全部是 I-cache、DSB、frontend starvation，
或已識別哪條指令負責多少 cycles。舊報告的「主要 frontend delivery」說法
在此降格為機制假說；sampling 不可用，沒有充分的因果 PMU attribution。

最近 Native image `.text/.rodata`：Official 40599/5416 B，GT 64919/60520 B。
這是整個 ELF 的 footprint，不等於 hot working set；不能由大小直接證明瓶頸。

## 4. 已測過的捷徑及其限制

- Serializer unify：刪 3840 B text，正確性通過；四種 placement Encap
  仍比 current 慢約 132～217 cycles。不能再把「共用函式、縮 code」當保證。
- 局部 D16/D8 wavefront A1：每 Forward 少 8 stores + 8 reloads，完整
  polynomial island 約 −17.15；但 Native Encap 比 current +214.23。
  候選未 promotion。更大 image / layout 是可能原因，尚非已證因果。
- A2：net 少 9+9，island 只約 −2.63、7/9 同向；未進 Native winner gate。
- 精確 marginal range：15605 → 15592，改善有限；不是大量可刪 reduction 的證據。

## 5. 為何 NEON 的 GT 大收益不能直接期待在 AVX2 重現

### 相同數學，machine realization 不同

GT 只保證適當索引下 inter-axis twiddles 可消失，不保證 routing、register
allocation、range repair、wire packing 與 caller integration 都更便宜。

### Register geometry

AArch64 有 32 個 128-bit SIMD registers；常規 x86-64 AVX2 有 16 個 YMM。
兩者名義總容量均為 4096 bits，但一個是更多獨立小向量，另一個是更寬、較少
register names。GT 多 row/cohort/constant/temp 的排程可能更需要獨立名稱；
另一方面 AVX2 每條 16-bit vector instruction 處理 16 lanes，NEON 是 8，
AVX2 也有寬度收益。ABI、常數佔用與微架構都會影響實際可用性。
不能說 NEON register bytes 較多，也不能只按 register 數預測 cycles。

### Routing geometry

AVX2 `vpshufb` 在兩個 128-bit halves 內分別運作。需要跨 half 的 ownership
轉換必須另用可跨 lane 的指令；但並非所有 AVX2 permutation 都受此限制。
因此把 NEON 128-bit packet 直接倍寬，常常不是最便宜的 AVX2 layout。

### Arithmetic idioms

本 repo 的 AArch64 research source 可見固定常數的
`sqrdmulh → mul → mls` sequence；目前 AVX2 Official/GT 大量用
`vpmullw → vpmulhw → vpmulhw(q) → vpsubw` Montgomery sequence。
前者有固定常數 companion 與 range 前提；不能套到任意 runtime×runtime
BaseMul，也不能用 3 vs 4 instructions 宣称某 ISA 一定較快。
這個 source 例子不是整個當前 NEON production 的完整 arithmetic audit。

### 比較基準與收益歸因

AVX2 Official 已是手寫 SIMD；目前 GT 的 P/M/J1/Q24、batch inversion、
scheduling 收益不是全部屬於 GT 定理，Official 也已具有 batch inversion。
NEON 的大收益可能含 baseline 版本、融合、reduction、codec 等其他改進。
本輪沒有把 NEON 的同版本 Official、hash policy、compiler、native boundary
重新凍結並重測，因此不報兩種 ISA 的 speedup 比值，也不宣稱已證明 ISA 是主因。

參考 ISA 原始文件：
- Arm AAPCS64 SIMD registers: https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst
- Intel instruction reference: https://cdrdv2-public.intel.com/789581/325383-sdm-vol-2abcd.pdf
- 本地 NEON sequence example: `ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/invntt_stage123_pair_pipeline/stage123_pair_pipeline.opt.S`。

## 6. 現在該怎麼理解研究方向

1. 已證實的 arithmetic win 保留；不因 Native Encap 小輸就全面否定 GT。
2. 最明確的局部 cost 是兩次 M→wire 和 PK ingress，但新提案要有新機制，
   不重做已失敗的 serializer unify / 展開式 fusion。
3. Forward 還能研究，但必須讓 credit 活到 caller；少 memory ops 的 A1 已提供反例。
4. 對 residual 的下一次診斷要同 frozen image、同 compiler 與 controls，
   不能拿歷史 component cycles 拼出 Native 的精確損益表。
5. 要解釋 NEON/AVX2 差距，另做同版本、同 boundary 的跨 ISA ledger，
   分開 GT 数學、layout、reduction、codec、compiler／CPU 效應。

結論：GT Forward 的收益已存在；768 Encap 尚缺穩定的 whole-caller win。
「AVX2 上 GT 收益較小」目前是 implementation/caller-level 的觀察，
還不是 Good–Thomas 對 AVX2 的一般性限制。

## 證據索引

- `results/encap-wavefront-native-20260921/summary.json`（最近 Native）。
- `docs/ntruplus768-gt-vs-official-survey.md`（歷史 PMU / source analysis）。
- `docs/ntruplus768-next-priorities-20260920.md`（paired / rejected candidates）。
- `docs/ntruplus768-forward-redesign.md`（A/B/C、wavefront boundaries）。
- `docs/avx2-range-proof-refinement.md`（range 精化與限制）。
