# NTRU+768／864／1152 AVX2 transform-shape survey

日期：2026-09-10  
範圍：NTRU+768、NTRU+864、NTRU+1152；x86-64 AVX2  
研究 branch：`experiment/avx2-ntruplus864-1152-polymul-001`

## 結論先行

這份 survey 的結論不是「Good–Thomas 一定優於 Official」，而是：

1. **768 的既有 GT32 證據已足以完成診斷，不值得在第一輪再占用新
   prototype 名額。** 它證明 transform 與 BaseMul 可以有競爭力，但
   inverse terminal、wire codec、caller-specific layout 和 code footprint 都可能
   把局部收益吃掉。768 不是單純的 arithmetic failure，也不是一個可直接套到
   864／1152 的成功模板。
2. **864／1152 應共用 `2_top × 9 × 16` 的 semantic mapping、root oracle 與
   stage-order 研究，但不能共用一份不加修改的 AVX2 physical schedule。** 1152
   的 residual degree 4 可以自然形成 `4 q × 4 j = 16 lanes` 的 AoS packet；864
   的 residual degree 3 沒有同樣的矩形 16-lane packet，且 Official 864 已經為
   wire／NTT format 額外使用 pack/unpack。
3. **目前證據最支持 hybrid，而不是 pure GT-first 或重新照抄 Official。** 具體
   形式是：保留 contiguous/top-split-friendly presentation，讓 NTT9 與 NTT16 的
  早期層在自然 presentation 中執行，只在真正 consumer 需要時才轉成
   coefficient-plane／wire ABI。1152 的 persistent-AoS、Natural-Q 與 caller
   attribution 已經提供 machine evidence；但 native SUPERCOP Encap 仍輸，因此
  不能把這個方向宣稱為 production winner。
4. **第一輪最多新增兩個 prototype：**
   - `P1 — GT9X16-STAGEORDER-TILE`：從真實 top-split output 開始，公平比較
     NTT9-first hybrid 與 NTT16-first／blocked alternative，停在相同 semantic
     component ABI。
   - `P2 — GT9X16-MULTIROW-WAVEFRONT`：只在 P1 選出的路線上，研究兩-row
     以上的 NTT9→NTT16 boundary，量化少掉的 materialization 是否抵得過
     register pressure、constant traffic 與 ILP 變化。

因此第一輪的推薦不是三套完整 implementation，而是：

```text
既有 768 證據完成診斷
        ↓
P1 決定 864／1152 的 stage order 與 physical packet family
        ↓
P2 決定 selected family 是否值得跨 axis 保留更多 live state
        ↓
才決定各參數是否進 full Forward/BaseMul/Inverse/KEM
```

## 1. 問題、證據等級與不在範圍內的工作

本輪只研究

\[
R_n=\mathbb F_{3457}[X]/(X^n-X^{n/2}+1),
\qquad n\in\{768,864,1152\}.
\]

不研究 cyclic test ring、extension-field/lifting、其他 NTRU/NTRU Prime
參數，也不在 survey 階段產生 production source。正式效能 baseline 仍是
[`bench/supercop.lock`](../bench/supercop.lock) 固定的 SUPERCOP 20260627；公開
SUPERCOP 網頁只用來確認 benchmark 生態與 implementation naming，不替換 branch
內的 pinned baseline。[1]

本文件把證據分成三層：

- **Published/Official**：NTRU+ specification、Official AVX2 source、radix-3 與
  NTTRU 文獻。
- **Repository-measured**：此 branch 已保存的 linked-object、paired benchmark、
  KAT 與 native SUPERCOP 結果。
- **Derived hypothesis**：root divisibility、register live-set、stage-order 成本模型；
  這些只用來挑 prototype，不當成效能結論。

## 2. 數學限制：哪些 shape 是合法主線？

Official specification 將 NTT 定義成 GCRT：

\[
R_q \cong \prod_{i=0}^{n/d-1}
\mathbb Z_q[x]/(x^d-\zeta^{\operatorname{index}[i]}),
\qquad \ell=3n/d,
\]

並採用「initial radix-2 → radix-3 → radix-2，直到 residual degree `d`」的
順序。規格也明確說 radix-3 先於後續 radix-2，是為了避免 BaseMul 需要額外的
precomputation table。[2]

| 參數 | initial R2 | R3 layers | later R2 layers | `d` | `ζ` | `ℓ=3n/d` | 本輪 semantic shape |
|---|---:|---:|---:|---:|---:|---:|---|
| 768 | 1 | 1 | 5 | 4 | 22 | 576 | `2 × 3 × 32 × I4` |
| 864 | 1 | 2 | 4 | 3 | 9 | 864 | `2 × 9 × 16 × I3` |
| 1152 | 1 | 2 | 4 | 4 | 9 | 864 | `2 × 9 × 16 × I4` |

這三個 residual degree 不只是 implementation 選擇；它們決定 BaseMul／BaseInv
的 component ring。Official 對 `d=3` 與 `d=4` 分別給出 cubic 與 quartic
BaseMul，而 quartic BaseInv 又會降成 `z=x²` 的 quadratic inversion。[2]

### 2.1 排除 864 的 d=2／d=1 uniform binomial route

因為 `q-1=3456`，同一套 base-field binomial CRT 至少需要 `ℓ=3n/d` 整除
3456：

| 864 residual `d` | `3n/d` | divides 3456? | 判斷 |
|---:|---:|---:|---|
| 3 | 864 | yes | 本輪合法主線 |
| 2 | 1296 | no | 不能直接用同一 base-field route |
| 1 | 2592 | no | 不能直接用同一 base-field route |

所以 `864=2×27×8×I2` 或 scalar stop 不能只憑整數分解納入同一比較；要做它們
就必須另開 extension/lifting 研究，超出本輪範圍。

### 2.2 備選 depth-change 只記錄，不實作

若固定 `d=4,3,4` 的 CT／GT／hybrid 都失敗，下一輪才考慮：

\[
768:2\times3\times64\times I_2,
\qquad
1152:2\times3\times64\times I_3.
\]

兩者都對應 `ℓ=1152`，可共享抽象 transform；但 residual BaseMul、BaseInv、
serializer 與 register geometry 會改變，不能在本輪偷偷混入。

## 3. Official AVX2 baseline 告訴我們什麼？

Survey 使用本地 Official mirror commit
`0c249d5828b90e8dd5de2c8405323d5ee2a0ce41`（2026-07-25），並以 pinned
SUPERCOP implementation tree 作正式 performance identity。Official repository
同時提供 reference、optimized C、AVX2 與 ARMv8-A NEON source。[3]

三套 Official AVX2 forward 都是 in-place mixed-radix：先 top radix-2，再執行
一層或兩層 radix-3，最後 fused radix-2 stages。它的主要 machine 優勢是：

- input 已是 contiguous polynomial backing；
- stage schedule 與 index/root order 是共同設計；
- code 以 loops 重用，不需要為每個 leaf 展開一份大 straight-line body；
- terminal representation 已與其 BaseMul/BaseInv 相容。

但 Official physical ABI 並非沒有成本。特別是 864 的
[`poly.c`](../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+864/poly.c)
在 byte I/O 前後明確呼叫 `poly_ntt_pack()`／`poly_ntt_unpack()`；768 與 1152
同位置沒有這組 wrapper。這是 `d=3` physical layout 不可直接用 1152 成本按
`3/4` 縮放的實際證據。[4]

NTRU+ v1.1 的公開說明也指出，停止深度同時受 key-generation inversion 次數與
precomputation table 大小影響，並將 radix-3 layer 改成 Hassan–Yayla 的 `n`
multiplication 版本。[5][9] 因此 shape 不能只用 isolated Forward 或 BaseMul
決定；BaseInv 與 wire caller 是一級成本。

## 4. 768：GT 到底輸在哪裡？

### 4.1 答案：不是單一原因，也不是 GT core 必然較慢

768 現有證據把四個區域拆得相當清楚：

| 區域 | Repository evidence | 判斷 |
|---|---|---|
| input formation / Forward core | lazy GT native Forward 曾在相同 binary 比 Official 約快 14%，isolated earlier winner 也約快 2% | core 可競爭；不是 decomposition 的必然失敗 |
| BaseMul / representation | native-layout BaseMul 可直接消費 GT state；`2×Forward+BaseMul` 的 lazy boundary 有約 4.3% credit | persistent consumer-native state 有價值 |
| Inverse terminal | d4-AoS 的 NTT32 core 約 456–460 TSC，但 terminal DFT3 再加約 78–92；完整 inverse 約 868–880，落後 Official 約 498 | 某些 physical mapping 的 terminal 是硬 blocker |
| wire/caller boundary | 早期 scalar GT pack 約 4046 cycles，Official pack 約 226；後來 AVX2 codec 大幅補回，但 frontend/code geometry 仍可逆轉局部指令收益 | serializer 與 code footprint 可主導 KEM |

上述數字來自不同 campaign，不能相加成新的總效能預測；它們只用來做
attribution。原始紀錄見
[`GT768 BENCHMARK_RESULTS.md`](../ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/gt_ntt/BENCHMARK_RESULTS.md)
與
[`d4-AoS STATUS.yml`](../ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_gt_d4_aos_official_api/STATUS.yml)。
完整 clean GT768 的正式 fixed-ELF 結果更能說明現況：

| Operation | ASLR on GT−Official | ASLR off GT−Official | production interpretation |
|---|---:|---:|---|
| keypair | −270.17 | −331.91 | GT 勝 |
| encap | +207.92 | +110.00 | Official 勝 |
| decap | −209.63 | −222.43 | GT 勝 |

詳細方法與 ELF hashes 見
[`NTRU+768/clean/avx2-gt32-clean/BENCHMARK.md`](../ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/clean/avx2-gt32-clean/BENCHMARK.md)。這個結果禁止兩種過度簡化：

- 不能說「GT768 整體沒有競爭力」；它在兩個 operation 勝出。
- 不能說「GT transform 贏，所以應直接 promotion」；Encap 仍穩定退步。

### 4.2 768 的 classification

768 應歸入：

\[
\boxed{\text{core arithmetic competitive; terminal/caller/code-shape multi-cause}}
\]

不是「主要只輸 input layout」，也不是「核心 mapping 全面較慢」。現有 clean
implementation 已經採用 caller-specific `M`／`P` layouts 與 Q24 native codec，
避免 generic `P↔M` conversion；這正是最值得移植到 864／1152 的 lesson。
[`LAYOUTS.md`](../ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/clean/avx2-gt32-clean/LAYOUTS.md)

### 4.3 對第一輪計畫的決策

768 **不新增 prototype**。保留目前 arithmetic champion 與 clean KEM 作
diagnostic/control；除非新構想能刪掉一整個 pack、inverse materialization 或
caller boundary，否則不再為局部 butterfly 或另一個 d4-AoS layout 開支線。

## 5. 864／1152 的共同 semantic model 與不同 physical geometry

兩者都能寫成：

\[
(b,p,q,j),\quad
b\in[0,2),\ p\in[0,9),\ q\in[0,16),\ j\in[0,d).
\]

- `b`：top split branch；
- `p`：NTT9 coordinate；
- `q`：NTT16 leaf；
- `j`：residual coefficient，864 有 3 planes，1152 有 4 planes。

共同的 consumer-plane ABI 可以抽象成：

```text
V[b,p,j] = lanes q=Q[0..15]
```

即一個 YMM 是同一 `(b,p,j)` 的 16 個 `q` leaves。於是完整 transformed state
需要：

| parameter | vectors | bytes |
|---|---:|---:|
| 864 (`d=3`) | `2×9×3 = 54` | 1728 |
| 1152 (`d=4`) | `2×9×4 = 72` | 2304 |

### 5.1 1152 的 NTT9-friendly AoS packet

1152 可以讓固定 `(b, q-block)` 的九個 GT rows 同時常駐：

```text
R0..R8 = nine p coordinates
each YMM lane packet = 4 q leaves × 4 residual j = 16 int16
```

兩層 radix-3 在 `R0..R8` 上 lane-wise 執行，不改 q/j ownership。之後 NTT16
的 D8/D4 可繼續吃 AoS；到 D2/D1 或 terminal consumer 真正需要 coefficient
planes 時才 transpose。這是目前 1152 persistent-AoS hybrid 的核心。

### 5.2 864 不能逐字複製這個 packet

864 的 `d=3` 使 `q-block × j` 無法用矩形方式恰好填滿 16 lanes：

```text
4 q × 3 j = 12 lanes     (留下 4 lanes)
5 q × 3 j = 15 lanes     (留下 1 lane)
```

所以 864 至少有三種 physical family：

1. **plane-major**：固定 `j`，九個 YMM 對 16 個 q leaves 做 NTT9；一次只處理
   一個 plane，避免 ragged packet，但跨 plane 的 terminal/BaseMul schedule 不同。
2. **ragged/padded AoS**：保留 NTT9 row locality，接受 unused lanes 或跨 packet
   ownership；可能增加 mask/routing。
3. **Official-like packed ABI**：沿用其六-vector terminal grouping與
   pack/unpack convention，讓 transform 與 codec 共同決定 layout。

因此「864／1152 共研」應理解成共用 coordinate oracle、twiddle identity、stage
order 與 benchmark cutpoint；**不是同一份 unrolled assembly 改常數即可**。

## 6. 三種資料流的比較

### 6.1 CT-first / Official-like mixed radix

```text
contiguous coefficients
  → top R2
  → radix-3 layer(s)
  → radix-2 layers
  → Official terminal ABI
```

優點：input 形成便宜、in-place、code compact、BaseMul table 與 index order 已共同
設計。缺點：它的 internal layout 不一定是 MA2、serializer 或其他新 consumer
最便宜的 ABI；若硬接新的 consumer，projection 可能把收益吃掉。

### 6.2 GT-first / fully explicit 9×16

```text
top split
  → form nine-row GT packets
  → complete NTT9
  → materialize/transpose
  → complete NTT16
  → component ABI
```

優點：NTT9 可用九個 independent row registers、root identity清楚，便於
component-level oracle。缺點：entry formation、9→16 axis boundary、terminal
transpose 與 code expansion 都是顯式成本；如果只量已預排好的 NTT9 input，會
系統性高估它。

### 6.3 Hybrid / delayed representation boundary

```text
top-split-friendly AoS
  → NTT9 while rows are natural
  → keep AoS through early NTT16 stages
  → convert only at late D2/D1 or direct consumer epilogue
```

目前 repository evidence 最支持這一類。1152 最新 native attribution 在「真實
coefficient input → transformed state」邊界量到 GT 1486.25、Official 1495.13，
GT 約 `−8.88 cycles`；但完整 native SUPERCOP Encap 仍為 `+672.27 cycles`
regression。也就是 transform 本身已到 parity，失敗主要在 serialization、PK
ingress、MA2/ciphertext tail，而不是 NTT9 arithmetic。[6]

這也呼應 NTTRU 的一般教訓：NTT 的價值必須連同 ring representation、
inversion 與完整 KEM dataflow 判斷，而不是只看單顆 transform。[7]

## 7. 六項 machine worksheet

下表是 prototype 前必填的同一 taxonomy；`?` 表示需要 P1/P2 實測，不能拿
估算冒充結果。

| 項目 | 768 existing GT32 | 864 `9×16×I3` | 1152 current hybrid |
|---|---|---|---|
| 1. input/output layout | caller-specific P/M；16 leaves/plane | 三-plane physical packet 尚未選定；Official codec 有 pack/unpack | top-split AoS → Natural/Wire consumer planes |
| 2. peak live-set | 多個已驗證 kernel zero-spill；完整 code footprint 偏大 | plane-major NTT9 可用 9 data；ragged packet需另算 | NTT9 block為 9 data + constants/temp；完整 linked peak 16/16 |
| 3. cross-128-bit operations | row/codec dependent | d3 pack/unpack 是主要未知 | late D2/D1 transpose與wire orientation為主要來源 |
| 4. materialization/reload | caller codec 已高度 specialization | 尚未量；不能由 1152 ×3/4 推算 | NTT9→NTT16 仍有完整 72-store +72-reload boundary |
| 5. range/reduction | lazy Forward 已證明可省 terminal reductions | 必須依 real d3 schedule重證 | 最新 linked Forward：40 Barrett vectors，proved envelope約 ±21333 |
| 6. arithmetic | d4 terminal/BaseInv較重；core曾勝 | d3 BaseMul/BaseInv source較小，但 pack成本存在 | 296 Montgomery chains；NTT9與NTT16 count已可 attribution |

1152 最新 linked Forward 的具體 ledger是：296 Montgomery chains、40 Barrett
vectors、488 routing、144 data loads、144 data stores；其中 72 intermediate
stores + 72 reloads 是刻意保留的 NTT9→NTT16 boundary。完整說明見
[`FORWARD-FLOW`](../ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/experiments/avx2_gt9x16_official_001/CHECKPOINT-WIRE-MONOTONE-NATIVE-ATTRIBUTION-V3-FORWARD-FLOW.md)。

## 8. 只新增兩個 prototype

### P1 — `GT9X16-STAGEORDER-TILE`

**要回答的唯一問題：** 從真實 top-split backing 開始，NTT9-first hybrid 是否
仍比 NTT16-first／blocked alternative 少付總 movement？

共同 cutpoints：

```text
input:
  unchanged top-split output

output:
  same semantic (b,p,q,j), same root identity,
  same scale/Montgomery exponent, same range contract
```

Control：現有 1152 NTT9-first persistent-AoS path；864 使用同一 semantic oracle
建立 d3 baseline。Candidate 只准改 stage order/packet schedule，不准改 radix-3
formula、twiddle identity、residual degree或 consumer semantics。

至少實作一個 branch、足以暴露 axis conversion 的一至兩個 tiles；不只量
`NTT9 alone`。必報：

- producer loads與 first-stage formation routes；
- stage內 Montgomery／Barrett；
- 9↔16 axis boundary stores/reloads/routes；
- final ABI formation；
- peak YMM與 cross-half instructions；
- linked `.text/.rodata`。

P1 的停止規則：若 NTT16-first 需要 whole-array transpose、額外 BaseMul table，或
在同 semantic boundary 沒有 clear structural credit，就關閉它，不擴成完整
Forward。

### P2 — `GT9X16-MULTIROW-WAVEFRONT`

**前提：** 只使用 P1 選出的 stage order。若 NTT9-first 保留，P2 專門研究
NTT9→NTT16 materialization；若 P1 選出其他順序，P2 對應其最昂貴 axis
boundary。

目前 1152 的 one-row W1 feasibility control 理論上只刪 8 stores + 8 reloads；
它不是目標上限。P2 直接研究 two-row／multi-row，但要把「能否放進 16 YMM」
和「是否值得」分開。

在每個 residual plane對應一個 packet pass、且 packet map已證明可行的暫定模型
下，低-temp R3 schedule 的保守 live-set 是：

\[
L(d,k)=9\text{ data}+3\text{ constants}+1\text{ temp}+(d-1)k
      =13+(d-1)k,
\]

其中 `k` 是跨 q-block 保留的 rows。於是：

| residual `d` | `k=1` | `k=2` | implication |
|---:|---:|---:|---|
| 4 | 16 | 19 | 1152 one-row可滿寄存器；two-row需 early death、memory-form constants或partial consumer |
| 3 | 15 | 17 | 864 多一格餘裕，但 two-row仍不會自然落在16以內 |

P2 不是「把 constant 全丟 memory」的單一版本，而應在同一 generator 中枚舉：

- selective memory-form q/twiddle operands；
- 每個 radix-3 group完成後立刻 early-kill；
- 只把 retained rows 提前跑 D8/D4，D2/D1仍 materialize；
- two-row interleave是否保留足夠 independent Montgomery chains。

只有 linked object 同時做到 `stores+reloads` 明確下降、zero spill、沒有等量新增
constant traffic，才進 Native SUPERCOP。768 已有 negative example：手工跨 pair
wavefront 雖只多少量指令，卻因 multiply-level ILP變差而退步，證明 memory-op
數不能直接換算 cycles。

## 9. 各參數的選型結論

### NTRU+768

**推薦：** freeze 既有 caller-specific GT32/P/M/Q24 evidence；production 仍由
operation-level結果決定。若未來重開，只接受能刪除完整 boundary 的 hybrid，
不再做 generic d4-AoS 或 isolated butterfly。

**已知風險：** code/constant footprint、inverse terminal DFT3、Encodeq/Decodeq與
caller frontend interaction。

**最小下一步：** 本輪無新 prototype；只把它當 P1/P2 的負面與正面設計案例。

### NTRU+864

**推薦優先 shape：** `2×9×16×I3` hybrid，但 physical ABI 必須由 P1 重新選；
不能照搬1152的 `4q×4j` AoS packet。第一候選是 plane-major NTT9 或
Official-like packed d3 baseline，再用 consumer-inclusive cost決勝。

**已知優勢：** 與1152共用 `ℓ=864` root/index identity與兩層 radix-3 + 四層
radix-2 semantic graph；cubic component只有三個 coefficient planes，但其實際
BaseMul/BaseInv machine cost仍需獨立量測。

**主要風險：** 三-plane lane fragmentation與既有 pack/unpack可能使 routing／
codec 成本非線性增加。

**最小下一步：** P1 先做 d3 exact packet map與一個 branch的 linked schedule；
未通過前不開 full Forward。

### NTRU+1152

**推薦優先 shape：** 保留 current NTT9-first persistent-AoS hybrid 作 research
baseline；不做 full CT-first rewrite。Forward 已接近 Official，native Encap失利
主要在 caller edges。

**主要風險：** 72-vector NTT9→NTT16 materialization、15 KiB級 straight-line
code與完整 KEM frontend/caller interaction。

**最小下一步：** 用 P1 公平排除 NTT16-first；若 current hybrid仍勝，再讓 P2
研究 multi-row wavefront。即使 P2 kernel勝出，也必須回到 native SUPERCOP
`enc_cycles` 才能 promotion。

## 10. Benchmark 與 promotion 規則

Prototype 可以先用 repository differential與同-ELF diagnostic選方向，但正式
decision只接受 branch workflow中的兩層：

1. **Native SUPERCOP KEM**：pristine `crypto_kem/measure.c`、正常 compiler
   selection、獨立 implementation directory；比較 `keypair_cycles`、
   `enc_cycles`、`dec_cycles`。
2. **Fixed common-compiler paired replay**：只用來 attribution placement／ASLR／
   compiler；不能取代 native headline。

所有 prototype benchmark 都必須：

- 從相同 input residency與相同 semantic cutpoint開始；
- 在相同 output ABI、scale、root identity與range contract結束；
- 報 1× attribution 與 caller multiplicity，但不把不同 campaign delta直接相加；
- 保存 linked opcode、ELF hash、`.text/.rodata`、symbol placement、compiler與
  pinned SUPERCOP hashes；
- isolated NTT9、prepared layout或 custom measure 不得稱為 SUPERCOP native
  result。

公開 SUPERCOP 確實列出 NTRU+768/864/1152 的 `avx2` implementations，且同一
primitive在不同 machine/compiler下數字可大幅不同；這支持以 pinned snapshot與
本機 Native SUPERCOP為 source of truth，而不是引用網站上一個最快數字。[1][8]

## 11. 最後決策矩陣

| 問題 | 現在答案 | confidence | 還缺什麼 |
|---|---|---|---|
| GT768 是否因 transform core必然慢而失敗？ | 否 | high | 無；既有 kernel/KEM evidence足夠 |
| 768 是否已是全 operation production winner？ | 否，Encap仍輸 | high | 新 complete-boundary architecture才值得重開 |
| 864/1152 是否可共享研究？ | 可共享 semantic/root/stage-order，不可假設相同 physical schedule | high | P1 d3 linked map |
| 1152 current Forward是否值得保留？ | 是，已到 Official parity附近 | high | cross-machine Native SUPERCOP仍是 promotion必要證據 |
| 應先 NTT9 還是先 NTT16？ | 現有證據偏 NTT9-first hybrid，但 NTT16-first尚未公平 producer-inclusive排除 | medium | P1 |
| 72-store/reload boundary值得打開嗎？ | 值得，但 one-row credit很小且multi-row有register/ILP風險 | medium | P2 |
| 是否應現在改 residual depth？ | 否 | high | 固定-depth families都失敗後才重開 |

第一輪完成的判準因此是：P1、P2 足以讓 864 與 1152 各選一條值得完整實作的
資料流；不是三個參數都已跑出 production winner。

## Sources

1. Daniel J. Bernstein et al., SUPERCOP KEM implementation/result index；branch
   內正式 snapshot 為 20260627：
   [primitive list](https://bench.cr.yp.to/primitives-kem.html)、
   [20260627 example results](https://bench.cr.yp.to/results-kem/amd64-rome0.html)、
   [pinned lock](../bench/supercop.lock)。
2. NTRU+ Team, *NTRU+ Specification*, §6.2、Table 5、Appendix B：
   [official repository PDF](https://github.com/ntruplus/ntruplus/blob/0c249d5828b90e8dd5de2c8405323d5ee2a0ce41/Supporting_Documentation/NTRU%2B.pdf)。
3. NTRU+ Team, official source repository and AVX2 implementations:
   [ntruplus/ntruplus](https://github.com/ntruplus/ntruplus/tree/0c249d5828b90e8dd5de2c8405323d5ee2a0ce41)。
4. NTRU+ Team, NTRU+864 AVX2 byte/NTT packing wrapper:
   [NTRU+864 `poly.c`](https://github.com/ntruplus/ntruplus/blob/0c249d5828b90e8dd5de2c8405323d5ee2a0ce41/Additional_Implementation/avx2/NTRU%2B864/poly.c)。
5. NTRU+ Team, “NTRU+ version update v1.1,” 2023-09-16：
   [KPQC bulletin](https://groups.google.com/g/kpqc-bulletin/c/mQ3FGgxtu4c)。
6. 本 repository 的 1152 native evidence：
   [`FORWARD-FLOW`](../ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/experiments/avx2_gt9x16_official_001/CHECKPOINT-WIRE-MONOTONE-NATIVE-ATTRIBUTION-V3-FORWARD-FLOW.md)、
   [`NATIVE-REBASE2`](../ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/experiments/avx2_gt9x16_official_001/CHECKPOINT-WIRE-MONOTONE-NATIVE-REBASE2.md)。
7. Vadim Lyubashevsky and Gregor Seiler, “NTTRU: Truly Fast NTRU Using NTT,”
   TCHES 2019(3)：[IACR ePrint 2019/040](https://eprint.iacr.org/2019/040.pdf)。
8. SUPERCOP, NTRU+864 AVX2 example result page：
   [amd64 rumba3](https://bench.cr.yp.to/web-impl/amd64-rumba3-crypto_kem-ntruplus864.html)。
9. Chenar Abdulla Hassan and Oğuz Yayla, “Radix-3 NTT-Based Polynomial
   Multiplication for Lattice-Based Cryptography,” 2022：
   [IACR ePrint 2022/726](https://eprint.iacr.org/2022/726.pdf)。
