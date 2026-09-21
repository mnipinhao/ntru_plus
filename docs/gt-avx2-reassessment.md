# GT-AVX2-REASSESS：Good–Thomas 在 NTRU+ AVX2 的收益與代價

日期：2026-09-20  
Branch：`avx2-gt-ntt-864-1152`  
Official source：SUPERCOP `20260831`（`bench/supercop.lock`）  
Qualification host：Intel Core Ultra 7 155H，CPU 1，performance governor，turbo disabled

## 結論

目前證據不支持「Good–Thomas 不適合 AVX2」，也不支持「GT transform 本身已經
比 Official 好」。較精確的結論是：

> **GT 的數學分解只有在 physical layout、input ownership、terminal arithmetic、
> serializer 與 caller reuse 一起選對時，才可能轉成 AVX2 cycles。**

三個參數給出三種不同答案：

| 參數 | 現在可下的結論 | 不可下的結論 |
|---|---|---|
| 768 | GT32 完整實作具有競爭力；Native Keygen、Decap 勝出 | 不能把勝因全歸給 GT decomposition；Encap 不是穩定 winner |
| 864 | 目前 MR32 terminal realization 輸；完整 GT 尚無 qualified KEM | 不能用一個 D3 tile 否決 GT9×16 |
| 1152 | GT 對 preserve-input wrapper 接近 parity，但對 Official 原生 in-place Forward 約慢 92 cycles；tail 仍明顯慢 | 不能再說最新版 GT Forward 已與 Official 原生 kernel parity |

這次最重要的校正，是把 Forward 拆成兩個不同問題：

```text
native-inplace:
    coefficient buffer → transform in the same buffer

preserve-input:
    coefficient buffer → copy → native-inplace transform
```

Official 的 production primitive 是前者。GT candidate 多半是 out-of-place，保留原
coefficient input。若 caller 不需要保留 input，把 copy 算到 Official 會錯估 GT
的相對位置；若 caller 的確需要保留 input，copy 又是真實成本。兩個數字都應保留，
不能用其中一個冒充普遍答案。

Machine-readable summary 位於
[`reassessment-summary.json`](../results/gt-avx2-reassess-20260920/reassessment-summary.json)。

## 1. Gate A：量測證據校正

### 1.1 修正內容

Component harness 現在明確輸出：

```text
forward_small_native_inplace_cycles
forward_small_preserve_input_cycles
forward_general_native_inplace_unqualified_cycles
forward_general_preserve_input_unqualified_cycles
```

`forward_general` 暫時標為 `unqualified`。數字仍可用於觀察 input-value timing
stability，但在每個 implementation 的 caller range 與 differential contract 完成
前，不參與架構判斷。

1152 原本的 `h4_exact_egress` 已改名為：

```text
gt_tail_decode_ma2_egress
```

因為它實際包含 PK decode／validation、MA2 arithmetic 與 ciphertext serialization，
不是孤立 egress。

舊 PMU baseline 在 4096 次 timed loop 裡每次重跑整串 `strcmp`，而前面的
component 會提早離開，造成負 retired instructions／loads。現在 mode 只在 loop 前
解析一次，component 與 baseline 使用相同 switch／loop geometry；若仍有任何負
counter，該 component 會被標記 invalid，而不是截成零。

PMU 的 4096-bank forward runs 刻意避免重複 transform 同一個已改寫 input。它們
適合解釋 instructions、loads、stores 與 working-set 效果，不作 headline cycles；
正式 component cycles 仍使用 SUPERCOP `cpucycles()` 與 StQ。

### 1.2 修正後 serious component 座標

下表為 fixed-common O3GC、9 fresh processes、pooled StQ2。它們是
`supercop-derived-component`，不是 Native KEM 數字。

| n | path | StQ2 cycles | contract |
|---:|---|---:|---|
| 768 | Official Forward | 955.36 | native in-place |
| 768 | Official Forward | 979.96 | preserve input |
| 768 | GT M Forward | 884.91 | out-of-place, M ABI |
| 768 | GT P Forward | 902.82 | out-of-place, P ABI |
| 864 | Official Forward | 1098.27 | native in-place |
| 864 | Official Forward | 1125.70 | preserve input |
| 1152 | Official Forward | 1399.66 | native in-place, same component ELF as GT |
| 1152 | Official Forward | 1502.20 | preserve input, same component ELF as GT |
| 1152 | GT Forward | 1491.79 | out-of-place, wire-monotone ABI |

1152 的解讀因此是：

```text
GT - Official preserve-input ≈ -10.41 cycles
GT - Official native-inplace ≈ +92.13 cycles
```

舊 parity 結論回答的是第一個問題；Native caller 通常更接近第二個問題。這個
差異本身就是 representation／ownership 成本，不能從結果中偷偷刪除。

### 1.3 證據等級

| 類別 | 意義 |
|---|---|
| Native SUPERCOP | 完整 KEM production headline |
| Matched serious component | 同 compiler／host 的 attribution，可判斷指定 boundary |
| Linked static audit | 證明機器形狀，不直接預測 cycles |
| Feasibility／map | 證明 mapping 或 schedule 可行，不是 performance rejection |
| Unimplemented hypothesis | 尚無 machine 結論 |

NTT16-first 屬最後兩類：現有 early-plane schedule 有 `+216` routes 警訊，但沒有
合格的 `<=16 YMM` full-branch challenger，因此不能記成「實測輸」。相反，1152
W1 是真正 performance rejection：它確實刪除 8 stores＋8 reloads，但 Native
Encap 約退步 184 cycles。

## 2. Gate B1：數學成本 ledger

三組都維持同一個 NTRU+ quotient ring、`q=3457` 與相同 residual component
degree。GT 沒有改 scheme，也沒有讓 terminal BaseMul 自動消失。

| n | Official semantic factorization | GT semantic factorization | residual ring |
|---:|---|---|---|
| 768 | initial R2 → R3 → five R2 | `2 × 3 × 32 × I4` | quartic |
| 864 | initial R2 → two R3 → four R2 | `2 × 9 × 16 × I3` | cubic |
| 1152 | initial R2 → two R3 → four R2 | `2 × 9 × 16 × I4` | quartic |

GT 的主要數學 credit 是把互質 axes 分開，消除一般 mixed-axis FFT 會需要的
inter-axis twiddle。這不等於「沒有 twiddle」：ring embedding、GT indexing、
radix-3 constants、NTT16 twiddles、output scale 與 terminal factors仍存在。

### 2.1 運算的四種狀態

| 項目 | 目前狀態 | 說明 |
|---|---|---|
| mixed-axis twiddle | **消失** | GT decomposition 的直接數學 credit |
| beta twist（1152） | **被吸收** | T0-beta 將固定 beta 併入既有 radix-2 twiddle |
| alpha normalization（1152） | **仍執行** | frozen paper-R2 DAG 下尚有 72-vector normalization budget |
| NTT9→NTT16 state | **被搬家／materialize** | axes 可交換不代表 live state 可免費交換 |
| Barrett repair | **部分消失** | 1152 scale-1 lazy path由72降至40；這是 range specialization，不是 GT 自動收益 |
| terminal BaseMul／BaseInv | **仍執行** | residual cubic／quartic arithmetic不因GT消失 |
| wire/hash conversion | **依 caller 決定** | 可由 consumer-native ABI 消除或轉移，與純分解不同 |

1152 current Forward 的 linked ledger為：

```text
Montgomery chains                  296
Barrett vectors                     40
routing vectors                    488
initial/final data loads/stores  72 / 72
NTT9/NTT16 boundary             72 / 72
.text                         about 15.4 KiB
peak YMM                            16
```

因此「GT 省 twiddle」與「GT implementation 算得少」不是同義句。alpha、range
repair、terminal transpose 與 constant traffic可能把 algebraic credit吃回。

864 也修正了一個常見誤解：固定 `(branch,p)` 的 48 個 `(q,j)` words 正好填滿
三個 YMM。問題不是 `3` 無法整除 `16` 而浪費 lanes；問題是 q-major/j-minor
ownership跨 vector，轉成 coefficient planes需要18-route network。

## 3. Gate B2：register-flow／machine view

### 3.1 NTRU+768 GT32

```text
Stage: shared frontend
input:  coefficient-domain small polynomial
AVX2:   grouped loads → top split → fixed twists → radix-3 formation
output: six TILE4 groups, each eight YMM, stored in private scratch
math:   form the 2 × 3 axes of 2 × 3 × 32 × I4
state:  scale/layout changes to GT tile ownership; input remains available
why:    expose homogeneous NTT32 work and independent multiply chains
next:   P terminal for Keygen or M terminal for Encap/Decap
```

```text
Stage: M/P NTT32 terminal
input:  one TILE4 group
AVX2:   raw D16 → Montgomery D8/D4 → packed D2/D1 → final deposits
output: M coefficient planes, or P/J1-oriented Keygen state
math:   complete the 32-axis transform
state:  M and P are deliberately different physical ABIs
why:    remove a later generic P↔M conversion
next:   M BaseMul/BMScale/inverse, or P BaseInv/F0×J1
```

```text
Stage: terminal consumers
M:      general BaseMul, scale BaseMul, inverse core/tail, Q24 codec/equality
P:      hierarchical batch BaseInv and F0×J1 products
effect: representation persists across the caller rather than returning to a
        human-readable canonical NTT layout
```

Serious component values：

| component | Official | GT | GT−Official |
|---|---:|---:|---:|
| Forward M vs native Official | 955.36 | 884.91 | −70.45 |
| BaseInv vs J1 BaseInv | 1242.97 | 1194.40 | −48.57 |
| general BaseMul | 720.92 | 727.55 | +6.63 |
| inverse | 991.83 | 970.58 | −21.25 |

這些不是可直接相加的 waterfall；input/output ABI 不同。它們證明目前 GT32
pipeline可競爭，但無法分離「GT decomposition」和 P/M/J1/Q24 co-design 各自占
多少收益。

### 3.2 NTRU+864 packed T3 research

```text
Stage: packed T3 boundary
input:  three YMM = 48 q-major/j-minor words
AVX2:   3 vperm2i128 + 9 vpshufb + 6 vpor for packed→plane
output: three coefficient planes of sixteen q leaves
math:   unchanged cubic component ownership
state:  layout changes; scale/root do not
why:    coefficient-plane cubic arithmetic and inverse consume this form
next:   cubic BaseMul/BaseInv or inverse entry
```

MR32 嘗試以 `vpmaddwd` 計算三組 pair products，但必須補 singleton products、
signed-32 reduction、repack 與 routing。Linked object由115增至131 instructions；
serious tile由248.96增至260.20 cycles。被否決的是這個 realization，不是完整 GT。

### 3.3 NTRU+1152 GT9×16

```text
Stage: top split
input:  1152 small coefficients
AVX2:   existing arithmetic，寫入2304-byte split backing
output: branch-major AoS state
math:   initial radix-2 / branch formation
state:  no GT consumer plane yet
next:   NTT9 persistent-AoS
```

```text
Stage: NTT9
input:  nine rows in AoS packets
AVX2:   two radix-3 layers, alpha/beta/rho/kappa fixed-constant arithmetic
output: 72 vectors
math:   transform p axis
state:  AoS orientation retained
next:   currently store all72, then NTT16 reloads all72
```

```text
Stage: NTT16 and terminal formation
input:  reloaded AoS rows
AVX2:   D8/D4 in AoS → D2/D1 → unpack/transpose → wire-monotone planes
output: scale-1 r/m state for MA2 and serializer
math:   transform q axis
state:  late conversion only when consumers require it; peak16/16 YMM
next:   r fanout to MA2+hash, m to MA2
```

W1 證明少 memory operations未必更快：linked code精確少8 loads、8 stores、16
instructions，沒有新增 arithmetic／constant operands，Native仍退步。原因不能只
靠 instruction count定論；live ranges、ILP、frontend與caller placement都仍可能
主導。

NTT16-first 目前只有 feasibility gap：若它先形成 coefficient planes，最可信的
收益是刪掉72-store／72-reload boundary；但現有 exact early-plane network多216
routes，且尚無 `<=16 YMM` full-branch schedule。這是「未驗證」，不是「已輸」。

## 4. Gate B3：caller representation lifecycle

### 4.1 Keygen

```text
sample f/g
→ triple
→ Forward f/g
→ BaseInv f/g (with retry semantics)
→ BaseMul products
→ key serialization
→ hash_f
```

768 GT 的 P/J1 layout服務 BaseInv與後續F0×J1，Native Keygen穩定勝出。這是完整
caller evidence，但同時包含 decomposition、layout與batch inversion，不能標成
純 Forward credit。1152 exp017沒有替換 Keygen algorithm；其 Native Keygen
delta主要是完整 ELF placement/control，不是 GT Keygen結果。

### 4.2 Encap

```text
PK bytes → decode/validate h ───────────────────┐
hash_f/hash_h → CBD r → Forward ──┬→ hash_g   │
                                  └→ arithmetic│
SOTP → m → Forward ────────────────────────────┤
                                               ↓
                                   MulAdd / MA2
                                               ↓
                                    ciphertext bytes
```

`r` 是雙 consumer；`h` 從 bytes 進入。這就是為什麼 isolated Forward winner不等於
Encap winner。768 Encapsulation目前 pooled Native約+29 cycles，fixed ELF又受
ASLR／placement影響，不能 promotion。1152 exp017 已採 streaming H3 ingress、MA2、
direct r serializer與H4 exact tail，但仍有：

```text
Official decode + BaseMul + add + serialize  1635.60 cycles
GT decode + MA2 + exact egress                1987.51 cycles
delta                                         +351.92 cycles
```

再加上 GT Forward 對原生 Official 的約+92 cycles／forward，足以說明為何完整
Encap仍落後；不能再把差距只歸因於 hash。

### 4.3 Decap

```text
decode c/f/hinv
→ BaseMulScale
→ inverse + crepmod3
→ recovered message Forward
→ recovery BaseMul
→ recovered-r bytes + hash_g
→ SOTP decode + hash_h
→ reencryption/equality
```

768 persistent M layout、native modulo-q equality與inverse tail共同形成 Native
Decap win。1152 exp017沒有替換這條 Decap path，因此其約+30-cycle Native delta不
能當成 GT Decap結果。

## 5. Gate C：反證原型決策

本輪保留最多兩個 ASM slot，實際使用 **0/2**。原因不是缺少想法，而是沒有一個
尚未定價的小改動能乾淨區分 decomposition與representation：

| 參數 | 收益可移植性提案 | implementation-limit 提案 | 本輪決策 |
|---|---|---|---|
| 768 | 將 consumer-native codec/layout移到Official CT | 刪完整Encap boundary或做placement-robust caller | 都不是局部ASM；不開 |
| 864 | Official packed ABI直接服務新的GT consumer | packed cubic MR32/reduction/repack | current MR32已輸；需新完整schedule才重開 |
| 1152 | Official native Forward接GT H3/H4 tail | NTT16-first或新NTT9 DAG | adapter會混淆歸因；W1已輸、NTT16-first尚無schedule |

Reopen條件：

- **768**：候選必須刪除完整 Encap pass／materialization，或在四種 placement／ASLR
  下保持 caller win。
- **864**：提出包含 packed cubic arithmetic、signed reduction、repack與inverse
  handoff的 exact schedule，並超過真正18-route boundary budget。
- **1152**：提出可執行的 `<=16 YMM` NTT16-first／blocked schedule，或 materially
  different NTT9 arithmetic DAG；不能只重做 W1/W2 memory trade。

## 6. 最終判斷

| 參數／operation | 判斷 |
|---|---|
| 768 Keygen | 保留 GT winner |
| 768 Encap | 證據混合；production promotion保留 Official |
| 768 Decap | 保留 GT winner |
| 864 全部 | GT證據不足；保留 Official，MR32 realization rejected |
| 1152 Keygen | Official；exp017未實作GT Keygen |
| 1152 Encap | Official；current GT candidate仍穩定退步 |
| 1152 Decap | Official；exp017未實作GT Decap |

因此目前最準確的回答是：

> **AVX2 上的 Good–Thomas 不是單獨的 kernel 選擇，而是 decomposition、lane
> ownership、destructive input contract、terminal ring與caller fanout的共同設計。**
>
> 768 證明它可以成功；1152 證明 transform 對 preserve-input wrapper 的局部
> 勝出仍可能在原生 ownership與tail被逆轉；864則尚未有足夠完整的實作可以判決。

## 7. Reproduction

Corrected serious results：

```text
results/gt-avx2-reassess-20260920/serious/
results/gt-avx2-reassess-20260920/gate-a/pmu2-*/
```

重新產生 summary：

```sh
python3 scripts/generate_gt_avx2_reassessment.py
```

Native KEM headline不重跑、不改寫，沿用 pinned snapshot 的既有9-launch campaign；
本輪只修正 attribution 層，沒有修改 pristine SUPERCOP、frozen package、candidate
KEM或 clean production。
