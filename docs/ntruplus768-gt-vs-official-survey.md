# NTRU+768 AVX2：Good–Thomas 與 SUPERCOP Official 深度 Survey

## 1. 結論先行

這次 survey 的結論不是「GT 適合／不適合 AVX2」這種二分答案，而是：

1. **目前 GT32 Forward 是真實的 machine-level win。** 在相同 counted region 內，兩次 Forward 相對 Official 約少 `1030` 條 retired instructions、少 `290` 次 stores，雖然多約 `252` 次 loads，仍少約 `196` 個 core cycles。GT 的 Forward 優勢不是由 wrapper copy 造成，也不是單純由較少 memory traffic 造成。
2. **GT 的完整 Encap 仍不是 winner。** 最新 Native SUPERCOP StQ2 是 `+237.63 cycles`（`+0.85%`）。GT 的 Forward 與 general BaseMul 已贏，但兩個 Q24 serializer、decode／glue、code placement 與完整 caller interaction 抵消了收益。
3. **Keygen 與 Decap 在最新 Native SUPERCOP 勝出。** Keygen `-333.60 cycles`（`-1.54%`），Decap `-196.50 cycles`（`-1.01%`）。不過 clean candidate 的 matched Keygen harness 仍缺，因此不能把 Keygen 的全部收益簡化成「GT 或 batch inversion」。兩邊現在都有 hierarchical batch inversion。
4. **可移植的收益很多。** M/P consumer-specific layout、typed Montgomery scale、Q24 codec、batch inversion與 scheduling 並非 Good–Thomas 定理本身；它們原則上也可能套到 Official decomposition。相反地，`3×32` coprime factorization 消除兩軸之間的 twiddle，才是 GT 本身的數學收益。
5. **目前限制是 realization 與 caller integration，不是 GT32 decomposition 已被否決。** Encap 的 matched full-caller delta會隨 normal／reversed placement 改變方向；Native 才是勝負依據，component 與 PMU只用來解釋機制。

因此目前判斷是：

| Operation | Native 判斷 | GT decomposition 判斷 |
|---|---:|---|
| Keygen | GT 勝 | 有利，但尚不能把全部收益歸因於 GT |
| Encap | Official 勝 | Forward 有利；caller integration／wire edges 仍不合格 |
| Decap | GT 勝 | GT representation 在後半 caller 有可量測收益 |
| 全 KEM production | 不 promotion | Encap regression 尚未解決 |

## 2. 凍結版本與證據層級

- SUPERCOP：`20260831`
- Official：`crypto_kem/ntruplus768/avx2`
- Official tree SHA-256：`8db00172e705b67e231b63708295781d65681fef2c7422d717fe91ab48d576e7`
- GT：`crypto_kem/ntruplus768/avx2-gt32-clean`
- GT source manifest SHA-256：`ad2e77ca349cb3454641a5bbce2acbdeb7f1f9586e11c4b735cbedd9e9a089a6`
- Official measure ELF SHA-256：`0c8f80685dba3a4838f5352c92b2f174fa322dceb0c57cadb4f246882c5c37bc`
- GT measure ELF SHA-256：`93fe30861439ecd96eea8c28881d7ddcf507bdc01bd606655cc1dc2ec2a2da18`
- CPU：Intel Core Ultra 7 155H，P-core CPU 1，SMT sibling `1-2`
- Governor：`performance`
- Intel turbo：disabled (`intel_no_turbo=1`)

所有benchmark process固定在CPU 1；SMT sibling CPU 2有記錄但未off-line，也沒有同步scheduler trace。因此本報告不宣稱host完全無干擾，而是保留fresh-process dispersion、placement／ASLR controls與raw observations來呈現這項限制。

三種證據不能互換：

| 證據 | 回答的問題 | 不能回答的問題 |
|---|---|---|
| Native SUPERCOP | 真實 KEM operation 誰快 | 哪個 primitive 導致差值 |
| same-ELF component／caller | 差值位於哪個 boundary | 不能取代 Native promotion |
| region PMU／linked audit | 指令、load/store、frontend 機制 | 不能把 isolated cycles 相加預測 KEM |

Native 使用未修改的 `crypto_kem/measure.c` 與 normal SUPERCOP compiler selection。Matched component 使用相同 ELF 與共同 harness；PMU 使用 `perf_event_open` 限定 operation region，模式選擇、reset、input generation 與驗證均在 counted loop 外。

本機的 `perf record` sampling另以`cpu_core/cycles/u`與generic `cycles:u`嘗試；前者產生空sample section，後者的hybrid event組合無法啟動，因此標為unavailable。本報告不使用sampling百分比或`perf annotate` cycle claim；region-controlled、無multiplexing的`perf stat` counters與linked disassembly仍可用。

Correctness gate包括100組 frozen deterministic KAT；Official與GT的request／response SHA-256完全相同。GT KAT另以 AddressSanitizer與UndefinedBehaviorSanitizer執行。兩個implementation各通過32組valid／tampered API trials、invalid-PK zeroization、input immutability與output canaries。Public KEM API不宣告overlapping buffers，因此本報告不虛構alias支援。

## 3. 最新 Native SUPERCOP 座標

每個 implementation 9 個 fresh processes；每個 operation 共 864 observations。

| Operation | Official StQ1 / StQ2 / StQ3 | GT StQ1 / StQ2 / StQ3 | GT − Official StQ2 | 百分比 |
|---|---:|---:|---:|---:|
| Keygen | 21469.51 / **21612.54** / 21789.13 | 21145.09 / **21278.94** / 21416.19 | **−333.60** | **−1.54%** |
| Encap | 27970.37 / **28083.78** / 28429.93 | 28061.91 / **28321.41** / 28621.13 | **+237.63** | **+0.85%** |
| Decap | 19296.80 / **19436.27** / 19568.62 | 19106.39 / **19239.78** / 19366.06 | **−196.50** | **−1.01%** |

若只把各自第 `i` 個 fresh launch 並列，Keygen、Decap 均為 GT 9/9 較快，Encap 為 GT 0/9 較快。這只是方向一致性描述；兩組是分開啟動的 Native campaign，**不是** fixed-ELF ABBA paired claim。

先前 fixed-placement evidence 曾出現 normal／ASLR-off Encap 有利、reversed／ASLR-on 不利的差異；新的 Native campaign則穩定顯示 GT Encap 較慢。因此不能挑某個 placement 宣稱 GT Encap 勝出。

## 4. 數學層：GT 真正省掉什麼

### 4.1 共同問題

兩邊都計算模 `q=3457`、模多項式

```text
x^768 - x^384 + 1
```

的 NTT-domain quartic factors。兩邊都需要：

- top split；
- 3-point structure；
- 32-point radix-2 structure；
- terminal quartic BaseMul／BaseInv；
- Montgomery reductions、lazy range 管理與 inverse normalization。

Official 與 GT 並不是「一邊用 Montgomery、另一邊不用」。兩邊 AVX2 都大量用

```text
vpmullw + vpmulhw + vpmulhw(q) + vpsubw
```

形成 16-bit Montgomery chain。Official top split 對小輸入可直接用 raw `-722` 乘法，這是 caller range specialization，不代表整條 Official NTT 改用 Barrett。

### 4.2 GT 本身的數學收益

`gcd(3,32)=1`，Good–Thomas／prime-factor mapping 把 transform index寫成 `(k3,k32)`。在適當 CRT permutation 下，3 軸與 32 軸之間不需要 Cooley–Tukey 的 inter-axis twiddle：

```text
F96  ≅  F3 ⊗ F32        (up to input/output permutation)
```

因此可真正歸因於 GT 的收益是：

- 3 軸與 32 軸之間的 twiddle chain 消失；
- 兩軸 arithmetic 可各自排程；
- terminal quartic leaf identity 可預先固定到 consumer layout。

但以下不是 GT 定理免費給的：

- CRT index permutation／physical lane assignment；
- frontend twist、top split 與 normalization；
- NTT32 D2/D1 後的 transpose；
- M/P/Q24 physical ABI；
- BaseInv batching；
- wire serializer 與 equality。

它們可能讓 GT implementation 更快，也可能成為 GT realization 的成本。

### 4.3 Arithmetic ledger

| 成本 | Official | GT32 clean | 分類 |
|---|---|---|---|
| top split | raw small-input split | frontend 內完成 | 仍執行 |
| radix-3 | Official level 1 | frontend DFT3 | 搬移／重排 |
| 3×32 inter-axis twiddle | decomposition需要的 stage constants | coprime mapping消除 | **GT 消失** |
| radix-2 D16…D1 | in-place stages | terminal M/P stages | 仍執行 |
| terminal transpose | Official internal/wire geometry | M/P coefficient planes | 搬移 |
| P range repair | generic Official range policy | `P_CENTER_BASEINV_L3` | caller-specific |
| batch inversion | hierarchical batch inversion | hierarchical batch inversion | 兩邊都有 |
| Forward scale | Official contract | F0 `e=0` | 相同 residue，typed ABI |
| J1 scale | internal contract | explicit `e=1` | typed relocation |
| scale BaseMul | inverse scaling | M `e=-1` | 仍執行 |

所以「GT Keygen 贏是因為 GT 有 batch inversion」已不成立；最新版 Official 也有 hierarchical batch inversion。需要比較的是 tree geometry、J1 scale、P layout、products 與 serialization的整體資料流。

## 5. GT layout：實際 lane ownership

GT frontend 的中間 tile layout為：

```text
tile   = 2*k3 + branch          // 0..5
vector = Q / 4                 // 0..7
lane   = 4*(Q % 4) + c         // c = quartic degree 0..3
```

一個 YMM 的 16 個 int16 lanes可畫成：

```text
128-bit low half                         128-bit high half
Q0:c0 c1 c2 c3 | Q1:c0 c1 c2 c3 || Q2:c0 c1 c2 c3 | Q3:c0 c1 c2 c3
```

`Q` 是 physical NTT32 leaf，對 logical `k32` 為 5-bit bit reversal。Frontend 共 6 tiles × 8 YMM = 48 YMM = 1536 bytes。

M layout則把 coefficient degree改成 plane：

```text
YMM(c0): q0.c0 q4.c0 q8.c0 q12.c0 q1.c0 ... q15.c0
YMM(c1): q0.c1 q4.c1 q8.c1 q12.c1 q1.c1 ... q15.c1
YMM(c2): ...
YMM(c3): ...
```

其 lane-q order 是：

```text
[0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15]
```

這讓 BaseMul、inverse core 與 M packer直接按 quartic degree做 SIMD arithmetic。P 仍是 coefficient-plane，但 leaf order針對 Keygen 的 Forward→J1 BaseInv→F0×J1→Q24 pipeline選定。

### 5.1 一個具體 wire → GT 例子

Serialized coefficient slots `0..3` 對應：

```text
logical k32 = 22
physical Q  = 13
tile        = 0
frontend AoS word offsets = 52,53,54,55
M physical lane          = 7
M plane word offsets     = 7,23,39,55
```

這說明「相同四個數值」在 frontend 是一個 quartic packet，在 M 是四個 plane 的同一 lane。D2/D1 terminal transpose正是把前者轉成後者。

Q24 每 24-byte packet含 16 個 12-bit coefficients，等於四個 quartics／一個 TILE4 vector。GT codec同時做 canonical check、12-bit pack/unpack、leaf mapping及 M/P deposit；不先建 Official coefficient-order temporary。

## 6. Forward register-flow

### 6.1 Official：in-place staged transform

#### Stage O0：small-input top split

```text
entry
→ ymm3..5 = lower coefficient vectors；ymm6..8 = upper vectors
→ vpmullw(-722), vpaddw, vpsubw
→ six output vectors寫回原 poly
→ top-factor branches形成
→ layout仍是 Official in-place coefficient/stage order；scale未改
```

選 raw `vpmullw` 是因 Keygen/Encap caller輸入很小，bound仍在 signed-i16；不用多付完整 Montgomery chain。

#### Stage O1：radix-3

```text
entry
→ A/B/C 三組 vectors
→ fixed-constant Montgomery products + add/sub
→ 三個 radix-3 outputs寫回
→ range經 stage-specific reduction控制
```

#### Stage O2…O6：radix-2

早期 stage用 contiguous vectors；後期 stage依序用 `vperm2i128`、unpack／shuffle形成 half與qword butterfly pairing。Official 直接在原 poly 上逐 stage load/store，因此沒有額外保留輸入 wrapper。Survey 的 headline沒有把 harness copy算入 Official Forward。

### 6.2 GT frontend：coefficient → six GT tiles

```text
Stage G-FRONTEND
→ entry: coefficient-domain small polynomial；ymm15=q；ymm0..5為load/rotation set
→ top split + GT_BLEND3 + fixed Montgomery twist + DFT3_WIDE_STORE
→ exit: six tile AoS，每YMM為四個Q leaf × quartic c0..c3
→ e=0；small caller bound，frontend observed max約2896
→ consumer: ntruplus768_ntt_m_avx2 或 ntruplus768_ntt_p_avx2
```

八個 unrolled iterations，每次移動 input/output/twiddle pointers。它用更多常數與 straight-line instructions，換取把 radix-3、twist與 GT permutation共同形成 terminal能直接消費的 packet。

### 6.3 GT terminal：D16／D8／D4

每個 tile進入時：

```text
ymm0..7  = 8 packed AoS vectors
ymm15    = q
ymm14    = terminal byte-shuffle mask
ymm8..13 = butterfly/Montgomery temporaries
```

`FR_RAW_CROSS4` 做 D16 raw sum/difference；`FR_MONT_CROSS4` 做 D8/D4：

```text
vpmullw(qinv, high)
vpmulhw(factor, high)
vpmulhw(q, low-product)
vpsubw                 // Montgomery result
vpaddw/vpsubw           // butterfly outputs
```

離開 D4 後仍是 packed quartic AoS；leaf identity已沿 D16/D8/D4分裂，scale維持 F0 `e=0`。

### 6.4 D2／D1 與 terminal transpose

```text
D2: vperm2i128 形成跨128-bit half pairing
D1: vpunpcklqdq/vpunpckhqdq 形成qword pairing
transpose:
  4 × vpshufb
  dword unpack
  qword unpack
  4 × stores，得到 c0/c1/c2/c3 planes
```

M terminal保留一般 range。P terminal在 early terminal插入 `P_CENTER_BASEINV_L3`：兩個 `vpmulhrsw` 加 `vpmullw/vpsubw`，把 BaseInv-sensitive streams recenter，再使用 P 專用 D1 constants與 P leaf order。M/P 因下一個 consumer不同而分流，並不是同一 layout改名。

### 6.5 Register與boundary成本

GT frontend與terminal是兩個 function：

```text
coefficients
→ frontend
→ 1536-byte materialized AoS
→ M/P terminal
→ 1536-byte consumer planes
```

這個 boundary保留 48 vector stores + 48 reloads，並在 function boundary各有 `vzeroupper`。但 PMU顯示整個兩-forward region仍少 stores且更快，因此不能僅憑 boundary存在就判定應做 zero-copy。要刪除它，必須在同一 Native caller中證明 register pressure、OoO decoupling與text footprint沒有反噬。

## 7. Linked machine ledger與PMU

### 7.1 靜態 reachable code

| Symbol | `.text` | 靜態 instructions | vector mul | routing | loads | stores | constant operands |
|---|---:|---:|---:|---:|---:|---:|---:|
| Official `poly_ntt` | 1792 B | 342 | 88 | 32 | 57 | 25 | 6 |
| GT frontend | 3917 B | 685 | 216 | 96 | 144 | 48 | 59 |
| GT M terminal loop body | 1056 B | 195 | 48 | 48 | 9 | 8 | 34 |
| GT P terminal loop body | 1046 B | 195 | 52 | 40 | 9 | 8 | 36 |

GT terminal loop body執行 6 次；Official也包含 loops。此表只用來看 dependency與working set，不能直接以靜態數量比較 runtime。

### 7.2 Region PMU：兩次 Forward

| 兩次 Forward | Official | GT | GT − Official |
|---|---:|---:|---:|
| cycles/op | 1524.66 | 1328.88 | **−195.78** |
| instructions/op | 4691.37 | 3661.37 | **−1030.00** |
| loads/op | 640.09 | 892.09 | **+252.00** |
| stores/op | 488.06 | 198.06 | **−290.00** |

Frontend group另外觀察到 GT 約少 946 個 DSB-delivered uops，MITE略增約12，`uops_not_delivered`沒有惡化。這支持較少 instruction／store work，而不是證明 I-cache 或 DSB 是唯一瓶頸。

### 7.3 General BaseMul

| General BaseMul | GT − Official |
|---|---:|
| cycles | **−17.22** |
| instructions | **−170.00** |
| loads | +105.00 |
| stores | −12.00 |

M coefficient planes讓 quartic arithmetic直接向量化，仍然用較多 loads，但少 instruction與stores並得到小幅 cycle credit。

### 7.4 Serializer成本

| Region | cycles | instructions | loads | stores |
|---|---:|---:|---:|---:|
| recovered-r Q24 serializer，GT−Official | **+22.71** | +59.99 | +96.00 | +61.00 |
| ciphertext Q24 serializer，GT−Official | **+21.12** | +61.00 | +96.00 | +61.00 |

GT codec雖避免 Official intermediate layout，卻在現有实现中付出更多 gather、canonicalization與packet stores。這是已證實的 realization cost，不是 GT decomposition 必然成本。

### 7.5 GT standalone component座標

修正後 harness用真實 BaseInv產生 J1，inverse tail也從合法 inverse-core output開始。3 fresh processes的 SUPERCOP-derived StQ2：

| Component | cycles |
|---|---:|
| frontend | 458.76 |
| M terminal / full | 648.15 / 890.71 |
| P terminal / full | 655.76 / 908.60 |
| BaseInv J1 | 1195.42 |
| F0×J1 | 622.38 |
| general / scale BaseMul | 725.89 / 638.01 |
| inverse core / tail / full | 632.68 / 589.08 / 973.43 |
| Q24 unpack M | 395.88 |
| Q24 pack M centered / lazy / highrange | 438.24 / 485.76 / 487.00 |
| Q24 pack P | 456.21 |
| Q24 equality M | 345.11 |

這些是各自重設輸入的 standalone numbers；`frontend + terminal != full` 是 cache、measurement boundary與pipeline interaction的結果，不能相加。

## 8. Caller producer–consumer graph

### 8.1 Keygen

```text
coins → SHAKE/CBD → f,g coefficient polynomials
      → GT frontend → P Forward
      → J1 BaseInv (hierarchical batch inversion)
      → F0×J1 products
      → P-native Q24 pk/sk serialization
      → hash_f / clear
```

GT 的 P layout讓 Forward output直接服務 BaseInv與兩個 F0×J1 products，J1的 `e=1` scale作為型別而非事後修正。Native Keygen快333.6 cycles。但舊的 production-shaped Keygen harness使用較早的 experiment realization，結果與 clean Native相反，已標為**不合格 attribution**；不能用它解釋當前 clean candidate。

結論：Keygen勝出已由 Native證明；勝因仍需 clean-specific matched harness才能在 P Forward、BaseInv tree、products、codec間精確分帳。

### 8.2 Encap

```text
PK bytes → Q24 decode/check → h(M)
coins/prehash → r coefficient
r → M Forward ─┬→ arithmetic state
               └→ Q24 bytes → hash_g
SOTP → m coefficient → M Forward
h,r,m → general BaseMul/add
→ Q24 ciphertext bytes → clear
```

`r` 是 dual consumer；只量 `r Forward` 會漏掉 hash serializer。Same-ELF normal placement顯示：

- two forwards：`−292.40 cycles`，9/9同方向；
- general BaseMul：`−31.93 cycles`，9/9；
- recovered-r serializer：`+29.34 cycles`；
- ciphertext serializer：`+35.22 cycles`；
- full Encap：`+90.08 cycles`，方向不穩。

reversed placement保持 component方向，但 full Encap變為 `−102.65 cycles`。這證明完整 caller受 code placement／frontend interaction影響；而最新 Native normal selection為 `+237.63 cycles`。因此：

```text
GT Forward win + GT BaseMul win
!=
GT Native Encap win
```

Waterfall的 instruction/load/store差值穩定，但獨立 prefix的cycle相減會受placement與warm state放大；本報告不用它們硬湊 Native residual。

### 8.3 Decap

```text
CT/SK bytes → decode
→ scale BaseMul → inverse core/tail → crepmod3
→ recovered message Forward
→ recovery general BaseMul
→ recovered-r Q24/hash_g
→ SOTP/hash_h
→ reencryption/equality → clear
```

Normal cumulative attribution的主要 phase（GT−Official）：

| Phase | TSC delta | core-cycle delta | instruction delta |
|---|---:|---:|---:|
| decode | +72.16 | +48.21 | +197 |
| first BaseMul+inverse+crep | +77.21 | +45.12 | −314 |
| recovered-r construction | **−145.54** | **−83.77** | **−770** |
| reencryption/equality | +132.38 | +108.34 | −277 |
| final cumulative | −34.72 | — | — |

reversed placement的 final cumulative約 `−145.29`；最新 Native為 `−196.50`。前半 decode／first product有明確 debt，後半 recovered-r path有明確 credit，reencryption與cleanup則高度placement-sensitive。

GT modulo equality可能避免完整 serialization pass，但目前證據只支持「後半 caller有收益」，不能把全部 Native Decap win單獨歸給 equality。

## 9. 已證實、推論與未知

### 已證實的節省

- valid caller domain的 GT two-Forward region較快，且少 retired instructions與stores。
- M general BaseMul有小幅穩定 machine credit。
- Native Keygen與Decap勝出。
- P/M consumer-specific representations可在不改外部KEM bytes下工作。
- 兩邊都有 hierarchical batch inversion。

### 已證實的額外工作

- GT Forward比Official有更多 retired loads。
- frontend→terminal保留1536-byte materialized boundary。
- GT兩個serializer各多約96 loads與61 stores，並各慢約21–23 core cycles。
- Encap decode region多約70 instructions與105 loads，約慢18–26 core cycles（依placement）。
- GT hot Forward code與constant operands較大；整個 installed candidate的`.text/.rodata`也較大。

### 機制推論

- Forward勝因主要是 instruction/store geometry及consumer-aware terminal，而非load reduction。
- Encap失利主要在 Forward之外，且有顯著code-placement／full-caller interaction。
- Keygen收益很可能來自 P/J1/F0×J1/Q24共同設計，但尚未完成clean-specific matched分帳。

### 尚未驗證

- GT frontend→terminal fusion／wavefront在完整caller是否比materialized boundary快。
- GT的哪些 arithmetic savings可移植到Official decomposition。
- exact clean Keygen Native win的component waterfall。
- Encap約`+238` Native residual中，hash/SHAKE邻接、entry boundaries與code placement各占多少。
- 其他AVX2微架構是否重現155H的結果。

## 10. 下一步三個優化提案

本輪不實作，排序依完整caller可處理的實測成本與證據品質。

### Priority 1：Encap full-caller hot closure，而非再磨 Forward

**邊界**：`PK decode → r/m Forward → BaseMul/add → two wire outputs`，保持數學、M layout與public API不變；先做clean candidate的same-ELF cumulative cutpoints與前置固定placement，找出約`+238` Native residual。

**依據**：Forward約`−196 core cycles/2×`、BaseMul約`−17`，但 Native Encap仍`+238`；full caller在normal/reversed間改方向。最大未知不是Forward arithmetic，而是caller integration／frontend placement。

**可驗證假說**：如果 compact entry organization、相鄰symbol placement或消除不必要function boundary能穩定保留component credit，full-caller delta應在四種placement均改善。

**停止條件**：fixed source/ELF下，normal/reversed、ASLR on/off方向仍不一致，或改善只存在單一placement。

### Priority 2：M→wire serializer共同設計

**邊界**：保持M arithmetic state與wire ABI，重新設計 recovered-r 與 ciphertext 的 M-plane gather/canonicalize/Q24 packet path；不把完整serializer塞回Forward terminal。

**依據**：兩個serializer合計約`+44 core cycles`，每個多約96 loads與61 stores；這是直接可處理、跨placement方向一致的已測 debt。

**可驗證假說**：以8-YMM／128-coefficient packet或consumer-native gather刪除完整M reload/pass，應同時下降loads與stores，而不只是換shuffle network。

**停止條件**：caller-shaped `r→state+hash bytes`與`MA2/add→ciphertext`任一沒有穩定負delta；isolated pack win不算。

### Priority 3：Decap ingress→scale BaseMul→inverse edge

**邊界**：CT/SK Q24 decode到scale BaseMul與inverse input，保持M ABI、scale `e=-1`與inverse arithmetic；尋找decode直接形成consumer-native packets或減少first-product materialization。

**依據**：normal attribution中decode約`+48 core cycles`、first product+inverse約`+45`；GT後半已快，前半是最清楚的剩餘Decap debt。

**可驗證假說**：direct ingress或producer/consumer packet schedule能刪除一個resident pass，並保留Native Decap勝勢。

**停止條件**：只少靜態instructions但caller cumulative無穩定改善，或需要改public/wire semantics。

Forward frontend→terminal wavefront暫不列前三。它可能刪48 stores+48 reloads，但目前Forward已是winner，而且過去經驗顯示memory boundary可能幫助OoO；只有clean full-caller attribution再次指出Forward是最大可處理debt時才重開。

## 11. 重跑與資料位置

主要machine-readable summary：

```text
results/ntruplus768-gt-vs-official-survey-20260920/summary.json
```

Native raw data：

```text
results/ntruplus768-gt-vs-official-survey-20260920/native-official/
results/ntruplus768-gt-vs-official-survey-20260920/native-gt32/
```

Linked audit（含symbol-level disassembly）：

```text
results/ntruplus768-gt-vs-official-survey-20260920/forward-linked-audit-v3.json
```

Matched caller／PMU：

```text
ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/
  experiments/avx2_gt32_tile4_official_001/results/
  ntruplus768-gt-vs-official-survey-20260920/
```

重跑 Native：

```sh
python3 scripts/run_supercop_benchmark.py \
  --campaign-root /home/nuc/src/supercop-campaign-unified-20260920-001 \
  --parameter 768 --implementation avx2 --cpu 1 \
  --mode native-kem --fresh-launches 9 --require-frequency-control \
  --result-dir results/ntruplus768-gt-vs-official-survey-20260920/native-official

python3 scripts/run_supercop_benchmark.py \
  --campaign-root /home/nuc/src/supercop-campaign-unified-20260920-001 \
  --parameter 768 --implementation avx2-gt32-clean --cpu 1 \
  --mode native-kem --fresh-launches 9 --require-frequency-control \
  --result-dir results/ntruplus768-gt-vs-official-survey-20260920/native-gt32
```

Region PMU：

```sh
survey_exp=ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_gt32_tile4_official_001
python3 scripts/run_ntruplus768_region_pmu.py \
  --binary "$survey_exp/build/bench_tile4_gt32_kem" \
  --cpu 1 --fresh-processes 3 --iterations 4096 \
  --region encap.E2_two_forwards \
  --region encap.E3_general_basemul \
  --region encap.E4b_serialize_rhat \
  --region encap.E4c_serialize_chat \
  --output "$survey_exp/results/ntruplus768-gt-vs-official-survey-20260920/region-pmu"
```

## 12. 最終判斷

> 這個 GT realization 的 Forward 已經贏，不代表所有收益都來自 GT；這個 GT realization 的 Encap 還輸，也不代表 Good–Thomas 不適合 AVX2。

現有證據支持的精確說法是：**Good–Thomas 3×32 提供了可轉成cycles的 arithmetic／stage-organization機會；目前AVX2 realization已在Forward、Keygen及Decap兌現一部分，但M/P/wire ABI與完整caller的互動尚未在Encap兌現。** 下一階段應先解釋並縮小完整caller residual，再決定要改GT realization、做hybrid，或把consumer-aware技巧移植到Official。
