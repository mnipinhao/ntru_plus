# NTRU+768 AArch64 優化說明：GT 實作與 KPQC final 的差異

更新日期：2026-07-21

這份文件面向已熟悉 NTRU+ 與 KPQC final 的讀者，說明目前 GT 實作的主要
改動、演算法結構，以及 Raspberry Pi 5 上的效能結果。精確 ASM、register allocation、
prototype 與歷史 benchmark 留在內部 audit 文件。

## 1. Summary and full-KEM results

Forward NTT 先將 768-degree problem 拆成兩個 384-coefficient branches，再將每個
branch 的四條 stride-4 streams 視為 length-96 transforms。兩個 branches 合計八個
scalar transforms，正好放入 8-lane Neon vectors。每個 96-point transform 使用
Good-Thomas `96 = 3 x 32` 分解，因此 3-point 與 32-point dimensions 之間不需要
cross twiddles；實際執行形狀是 32 組 8-way DFT3，再接三個 8-way NTT32 rows。

Inverse NTT 由 KPQC final 的 Cooley-Tukey forward / Gentleman-Sande inverse 配對，
改成 Cooley-Tukey forward / Cooley-Tukey inverse。GT inverse 直接消耗 forward
保留的 bit-reversed row order，並將 normalization、untwist、branch merge 與
Montgomery factor correction 集中在 final constants path。Standalone inverse
目前仍略慢於 KPQC；實際收益主要來自與 preceding base multiplication 共用
Montgomery-factor contract。

Key generation 的 hierarchical batch inversion 方法來自 Kim、Cho 與 Park 的
*Accelerating NTRU+ Key Generation via Hierarchical Batch Inversion*。該論文提供
C 與 AVX2 實作；本工作將相同方法映射到 AArch64 Neon，並另外使用一條 15-step
field-inversion chain。15-step chain 與 hierarchical batching 是兩項不同改動，
不能把 hierarchical batching 的 full-keygen cycle delta 歸因於少一次 multiplication。

Key generation 另外使用一條 private mixed-layout contract。Fused sample NTT 將
`f/g` 直接存成 branch-pair quartic (BPQ)；baseinv prepare 在第一次需要
coefficient-wise arithmetic 時轉成 coefficient-major quartic (CQ)，hierarchical
inversion 與 finish 維持 CQ；public products 使用 BPQ x CQ mixed basemul 並直接
輸出 CQ。最後 `h/hinv` 由 CQ pack、`f` 由 BPQ P1 pack 產生 canonical bytes。
這條 contract 只用於 keygen；generic polynomial API 與 encap/decap layout 不變。

Decapsulation verification 的最後一個 product 使用 caller-specific canonical
pointwise path：右 operand 直接解成 canonical QSoA，左 operand 從 GT physical
order 以固定 public offsets gather，並將相鄰兩組 quartic products 交錯排程。這避免
先轉成 GT polynomial、做 generic basemul、再轉回 canonical bytes；內部 NTT layout
仍維持 GT order，API-visible bytes 不變。

Raspberry Pi 5 Cortex-A76、兩邊都使用 portable `NO_CE` SHAKE，且 GT 使用與
KPQC final 相同的 canonical wire serialization 時：

| Operation | KPQC final cycles | GT cycles | Cycle reduction |
|---|---:|---:|---:|
| keygen | 39948 | 36373 | 8.95% |
| encapsulation | 39011 | 37574 | 3.68% |
| decapsulation | 35181 | 32904 | 6.47% |

目前 full-KEM 是穩定的 single-digit speedup，尚未達到 20% 的 scheme-level 目標。
Mixed BPQ/CQ promotion 前的 GT keygen 是 `38264` cycles；新 backend 是 `36373`
cycles，減少 `1891` cycles（`4.94%`）。Encap/decap 與 promotion 前 GT 的差異低於
`0.1%`，符合這是 keygen-only contract 的預期。

## 2. Forward NTT

### 2.1 Good-Thomas decomposition and Neon packing

NTRU+768 使用：

```text
Rq = Zq[x] / (x^768 - x^384 + 1), q = 3457.
```

Forward path 先做 top split，得到兩個 384-coefficient branches。以 `y = x^4`
觀察每個 branch，可分成四條 length-96 streams：

```text
A0(y), A1(y), A2(y), A3(y).
```

因此 scalar transform 的總數是：

```text
2 branches x 4 streams = 8 scalar 96-point transforms.
```

每個 branch 在進入 96-point NTT 前，先對 coefficient 做：

```text
a[b, k, r] <- a[b, k, r] * F_b^(-k)

F_0 = 2
F_1 = 22
r = 0,1,2,3
k = 0..95
```

這個 twist 將 branch-specific evaluation 轉成 cyclic 96-point problem。Production
ASM 確實載入 branch/index-dependent twist table並執行 modular multiplication；
只是 twist 被融合進 top split 與 DFT3 之間，不會先 materialize 一份完整 twisted
polynomial。

八個 scalar transforms 以 Neon lanes 平行執行：

```text
top split
  -> branch-dependent twist
  -> 8-lane cyclic 96-point transforms
  -> Good-Thomas 3 x 32
  -> 32 vector DFT3 groups
  -> 3 vector NTT32 row kernels
```

這不是「兩個 branches 各產生三個 NTT，所以有六個相同 NTT」。若以 scalar
數學計數，八個 96-point transforms 會形成 `8 x 3 = 24` 個 scalar NTT32；
8-way Neon packing 將它們合併成三個 vector NTT32 row kernels。三個 rows 使用
相同的五層 radix-2 topology，但處理不同的 Good-Thomas row data。

Good-Thomas 在這裡提供：

- `3` 與 `32` 互質，因此 dimensions 之間沒有 cross-twiddle layer。
- 三個規則的 NTT32 rows 適合使用相同的 vector butterfly structure。
- DFT3 可利用 `1 + omega3 + omega3^2 = 0` 降低 multiplication cost。
- 多個 independent rows、loads 與 reductions 提供 A76 所需的 ILP。

Good-Thomas 是目前 forward NTT 的演算法骨架，但不能把全部 cycle improvement
單獨歸因於 Good-Thomas。目前沒有一個其餘 Neon packing、layout 與 scheduling
完全相同，只關閉 Good-Thomas 的 ablation baseline。

### 2.2 Output layout and performance

每個 NTT32 row 使用完整五層 Cooley-Tukey transform：

```text
natural row input
  -> five radix-2 CT stages
  -> bit-reversed frequency order.
```

Forward 不在尾端補 bit reversal，而是將 row-bit-reversed order 定義成正式的
NTT-domain physical layout。對應的 `lambda_i` table 也依相同 order 排列，因此：

```text
NTT final store
  -> quartic block-major layout
  -> basemul/baseinv directly consume the same order.
```

這省掉 NTT 後的 permutation 與 base arithmetic 前的 layout conversion。Current
ASM 也讓多個 NTT32 intermediates直接由 producer registers 交給後續 stages，減少
不必要的 scratch store/load；這是 scheduling 與 register handoff 的實作收益，
不是新的 NTT 數學。

2026-07-19 Pi 5 KEM-component harness 重測：

```text
core:          3, pinned
hash backend:  portable NO_CE
samples:       31
calls/sample:  2000
warmup:        100
```

| Forward NTT measurement | KPQC final | GT | Cycle reduction |
|---|---:|---:|---:|
| encapsulation `poly_ntt(r)` | 3458 | 2589 | 25.13% |
| encapsulation `poly_ntt(m)` | 3441 | 2588 | 24.79% |
| rotating-buffer generic `poly_ntt` | 3610 | 2869 | 20.53% |

這裡量到完整 generic `poly_ntt`，不包含 CBD、hash、base multiplication 或 inverse
NTT。Rotating-buffer benchmark 約快 20.5%，固定 KEM-component buffer 約快 24.8%-25.1%；
兩者的差異包含 memory hierarchy 與 cache working set。完整 KEM 結果仍是最終依據。

## 3. Inverse NTT

### 3.1 CT inverse and final-factor fusion

KPQC final 使用常見配對：

```text
forward: Cooley-Tukey
inverse: Gentleman-Sande
```

GT 則使用：

```text
forward: Cooley-Tukey
inverse: Cooley-Tukey with inverse roots
```

Inverse NTT32 直接接收 forward 的 bit-reversed row order，依 `len=2,4,8,16,32`
執行，輸出 natural coefficient order並帶有 32 倍 scaling。接著 inverse DFT3
帶來額外 3 倍 scaling：

```text
three inverse NTT32 rows
  -> inverse DFT3
  -> total scaling = 32 x 3 = 96.
```

CT inverse 有正確消耗既有的 bit-reversed layout，但「不需要 bit reversal」不是
CT-CT 相對 CT/GS 的新增收益，因為標準 CT-forward/GS-inverse 也能直接銜接這個
order。真正改變的是 inverse butterfly 中 twiddle multiplication、add/sub 與
reduction 的相對位置，使 final factors 可以一起安排。

Inverse tail 原本包含：

```text
1/96 normalization
untwist
top-level branch merge
Montgomery factor correction
final representative reduction
```

GT 將這些 factors 整理進 final branch constants，在 inverse DFT3 後直接完成
merge 與 reduction。Decapsulation 的第一個 base multiplication 還使用更窄的
producer/consumer contract：

```text
poly_basemul_rminus1
  -> deliberately retains an extra R^-1 factor
  -> poly_invntt_from_rminus1 selects adjusted final constants
  -> normal coefficient-domain output
```

也就是 basemul 不先正規化 representation，再讓 inverse 重做 normalization；
inverse final constants 一次吸收 `R^-1` compensation 與原有 final factors。

目前 default KEM 只有 decapsulation 呼叫 inverse，而且直接走上述 paired path；
keygen 與 encapsulation 都沒有 InvNTT。Repository 仍保留 normal `poly_invntt`，
是為了 `poly_ntt -> poly_invntt` roundtrip、generic polynomial multiplication、
fallback 與測試 API，不是因為 default KEM 還有第二個 inverse hot path。因此
standalone generic inverse benchmark 不應被當成 production decapsulation 的數字。

省略 basemul final correction 並不是單獨成立的近似：若 raw `R^-1` product 送進
normal `poly_invntt`，結果與 KAT 都會錯。現在 KAT bytes 不變，是因為
`poly_invntt_from_rminus1` 的 adjusted final constants 在 coefficient-domain output
與 serialization 之前精確補回該 factor；normal pair 與 rminus pair 已做 exact
representative、full KEM、canonical `.rsp` 與 cross-vector 驗證。

### 3.2 Current limitation

Standalone GT inverse 目前接近但仍略慢於 KPQC，所以不應把 decapsulation gain
描述成 inverse kernel 本身變快。收益來自相鄰 basemul 與 inverse 共用 factor
contract，也就是跨 kernel factor fusion。

目前 inverse 前段仍會把部分 intermediate rows 寫入 stripe scratch，後段再讀回。
理論上可嘗試讓 producer outputs 保留在 vector registers並直接交給 consumer；
但這會提高 register pressure，可能造成 spills 或限制 arithmetic scheduling。
因此它代表可能的優化空間，不是已確認的 performance win。

## 4. Hierarchical batch inversion

Hierarchical batch inversion 方法來自 Kim、Cho 與 Park 的
*Accelerating NTRU+ Key Generation via Hierarchical Batch Inversion*。原論文評估
C 與 AVX2，本工作實作 AArch64 Neon 版本。

KPQC final 已經使用 Montgomery batch inversion，因此 GT 的差異不是「首次把多個
field inversions 合成一次」。GT 改變的是 24 個 denominator vectors 的 dependency
shape：

```text
24 denominator vectors
  -> 8 independent groups x 3 vectors
  -> batch inversion of 8 group products
  -> one vector field inversion
  -> hierarchical recovery of 24 inverses
```

這保留一次真正的 field inversion，但把長度 24 的 sequential product/recovery
chain 改成多條較短且可平行的 chains，以增加 ILP。

這種改寫主要縮短 dependency depth、提高 ILP。Current K=8 tree 的 batch core
仍是 `16 + 21 + 32 = 69` 次 modular vector multiplications 加一次 field
inversion，與 24-element linear Montgomery batch 的 `3n-3 = 69` 相同；它不是
靠減少 multiplication count 取勝。再加上 GT 將一個 Montgomery factor 留給
後續 `poly_basemul_scaled_r_input`，所以 standalone baseinv 不是公平的 drop-in
比較。Current KEM-path measurement 是：

| Keygen contract | KPQC final | GT | Delta |
|---|---:|---:|---:|
| standalone baseinv | 4056 | 4514 | +11.29% |
| matching basemul | 2641 | 2022 | -23.44% |
| baseinv + matching basemul | 6693 | 6534 | -2.38% |

因此 hierarchical + batch inversion 確實是 production；目前相對 KPQC 的 paired
contract 已快 `2.38%`，但不能改寫成 GT standalone baseinv 本身較快。Production
default 只連入一份 2008-byte HIER-K8 tree backend；舊 wrapper 只保留給 kill-switch
與 benchmark-helper build，避免 duplicated KEM/backend code 造成 I-cache 與
code-placement 干擾。

第二層 total product 使用一條 15-step exponentiation chain；KPQC 使用的 chain
有 16 次 modular vector multiplications。這只證明 arithmetic chain 少一次
multiplication，不能直接推論 cycle 一定較少。現有 isolated measurement 中，
15-step ASM 約 299 cycles，16-step C/Neon 約 284 cycles；兩者實作與 scheduling
不同，因此目前沒有「15-step 單獨讓 full keygen 更快」的證據。

Hierarchical batching 的 same-binary A/B 則固定使用相同的 15-step backend：

| Window | Flat batch | Hierarchical batch | Delta |
|---|---:|---:|---:|
| two scaled polynomial inversions | 9419 | 9231 | -188 cycles |
| full keygen | 38777 | 38599 | -178 cycles |

因此 `-178 cycles` 應歸因於 hierarchical batching/tree 的 dependency shape，
不是歸因於 `fqinv` 從 16 次降到 15 次。論文應取得 hierarchical algorithm 的
credit；本工作的貢獻是 Neon realization 與目前使用的 AArch64 kernels。

## 5. Measurement scope and limitations

Full-KEM 與 forward component 數據都來自 Raspberry Pi 5 Cortex-A76、固定 core、
portable `NO_CE` SHAKE。對外解讀應維持以下界線：

- Forward NTT 在固定 KEM-component harness 約快 24.6%-25.1%，不代表 full KEM 快相同比例。
- Rotating-buffer forward benchmark 約快 20.5%，顯示 cache context 會影響比例。
- Standalone inverse 尚未快於 KPQC；decapsulation收益來自跨 kernel factor fusion。
- 15-step chain 少一次 multiplication，但目前沒有獨立 cycle win 或 full-KEM delta。
- Full KEM canonical production 目前快約 3.46%-4.78%，尚未達到 20% 目標。

## 6. References

- Good-Thomas prime-factor FFT/NTT decomposition for coprime dimensions.
- Cooley-Tukey and Gentleman-Sande NTT butterflies.
- Kim, Cho, and Park, "Accelerating NTRU+ Key Generation via Hierarchical
  Batch Inversion," 2026.
- Montgomery's trick for simultaneous field inversion.

完整 production flags、source files、correctness gates 與 internal benchmark 來源見
`gt-new-vs-kpqc-final-optimization-summary.md`。該文件是內部 audit，不建議直接作為
對外技術介紹。
