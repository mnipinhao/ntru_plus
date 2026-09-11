# P7 — GT864 Inverse CT feasibility

## 結論

P7 的判定是：

\[
\boxed{\text{CT 的局部效益成立；但「改用 CT」並不是目前整體 Inverse 的解法}}
\]

目前 GT NTT16 已經是真正的 Cooley–Tukey DIT，不是只有名稱像 CT：
右輸入先乘 twiddle 並 reduction，之後才形成 `u+v`、`u-v`。它把
bit-reversal 吸收到 P8 座標，沒有增加完整 polynomial permutation；在
`|input| <= 3456` 下，CT 也確實避免了 GS sum path 至少一次必要的 range
cut。因此固定現有 GT ABI 時，保留 CT 是正確選擇。

但 Pi 5 的完整 call-site 邊界仍是：

| Inverse | cycles | 差距 |
| --- | ---: | ---: |
| selected SUPERCOP Official, GS | 4,118.050 | baseline |
| GT production, CT NTT16 | 7,013.950 | +2,895.900 (+70.32%) |

原因不是 CT 本身，而是 GT 完整路徑還包含 12 次 inverse NTT9、P8
materialization、七次 NTT16 kernel、864 次 `UMOV` + 864 次 scalar
`STRH`、完整 `center864` pass，以及 1,792-byte scratch 初始化／清除。
P7 沒找到只把 CT 換成 GS 就能刪除這些成本的證據，所以沒有建立或接入
新的 production assembly。

## Gate status

| Gate | 狀態 | 證據 |
| --- | --- | --- |
| 從 dependency 判斷 CT/GS | Pass | GT `fqmul(right)` 後 add/sub；Official 先 add/sub 再乘 difference |
| 864 FR0 與 natural output coordinate bijection | Pass | 864/864 coordinates，各自無重複 |
| N=16 ordering machine-check | Pass | 10,000 random vectors，CT/GS/DFT 零 mismatch |
| 額外完整 bit-reversal pass | Pass | 0 bytes；bit-reversal 在 P8 address/state assignment |
| CT range benefit | Pass | CT 可保持 int16；unreduced GS sum path 第四層到 55,296 |
| scale/domain closure | Pass | R^-1 進 I9；terminal table 補回 R 並融合 inverse scale/twist；raw R0 出口 |
| fixed ABI 下 CT 比 GS 有較小 arithmetic DAG | Partial | CT 少一個 GS range cut；twiddle mul 數量本質相同 |
| 整體 CT 比 Official 快 | Fail | GT 慢 2,895.900 cycles |
| 有足夠靜態新 DAG，值得進 Slothy/assembly | Fail | CT 已實作；CT→GS 無法刪 P8/scatter/center |

所以 P7 是「完成並收斂」，不是 production promotion。

## A. 實際 butterfly 分類

### GT inverse NTT16：CT DIT

C oracle 的核心 dependency 是：

```text
u = value[left]
v = fqmul(value[right], inverse_twiddle)
value[left]  = u + v
value[right] = u - v
```

也就是 twiddle multiplication 位於 butterfly 輸入側。四層依序是
`length = 2,4,8,16`，這是 radix-2 decimation-in-time CT。production
`lazy_i16`/`lazy_itail` 是這個 DAG 的排程、lazy-identity 版本；雖然 Slothy
把 instructions 大幅交錯，dependency 並沒有變成 GS。

GT inverse NTT9 不是二輸入 radix-2，因此不能硬貼「整個函式是 binary
CT/GS」標籤。它是 paper-oriented 的兩層 radix-3 direct inverse DFT；
每個 B3 的 weighted inputs 先乘 `rho/eta` 類常數再形成 sums，屬於
twiddle-on-input、CT-side 的資料流。GT NTT16 內沒有混合 GS layer。

### selected Official inverse：GS DIF

Official level 6 的 dependency 是：

```text
difference = right - left
left       = left + right
right      = fqmul(difference, zeta)
```

這是 Gentleman–Sande decimation-in-frequency。後續 levels 延續相同方向，
並在 sum path 接近 int16 上限時插入 Barrett range cut。

## B. Ordering 與一個 N=16 例子

GT FR0 leaf 的實體 index 是：

```text
24*(top*18 + row*2 + column/8) + 8*component + column%8
```

其意義是：

```text
top       = 0,1
row       = 0..8       (NTT9 frequency)
column    = 0..15      (NTT16 frequency)
component = 0,1,2      (最後 degree-3 leaf)
```

BaseMul 直接在同一個 `(top,row,column)` leaf 上做 degree-3 product，因此
Forward → BaseMul 沒有 ordering bridge；R^-1 BaseMul 的輸出也直接是
Inverse 的 FR0 輸入。

Pass 1 對固定 `(top,component,8-column block)` 載入九個 registers：

```text
v_r = [F(top,r,c+0,component), ..., F(top,r,c+7,component)]
```

inverse NTT9 後 registers 變為 `u_s`；8x8 `TRN` network 把 register=row、
lane=column 改為 register=column、lane=s。production P8 進一步把兩個 top
放在同一個 Q register 的 low/high halves。

對 NTT16，抽象 input columns 是：

```text
c natural:  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
CT state:   0  8  4 12  2 10  6 14  1  9  5 13  3 11  7 15
```

也就是 `state[bit_reverse4(c)] = q_c`。CT 執行 `2→4→8→16` 後，state
位置就是 natural `t=0..15`。最後 top recombination：

```text
high = (beta-alpha)^-1 * (B-A)
low  = A - alpha*high
```

寫回 natural coefficient：

```text
low:  3*(s + 9*t)        + component
high: 3*(s + 9*(t + 16)) + component
```

同一個 machine-check 也證明 GS 的對偶：natural input 經 `16→8→4→2`
得到 bit-reversed output；再按相同 `bit_reverse4` 解讀才是 natural DFT。
10,000 組完整隨機 N=16 vectors 都與直接 DFT 一致。

## C. Permutation 與 memory ledger

沒有獨立的完整 polynomial bit-reversal。bit-reversal 是 P8 的 store/load
座標與 register assignment，不是額外 read+write pass。

真正存在的是 Good-Thomas 兩個 axis 之間的 P8 boundary：

| 動作 | bytes |
| --- | ---: |
| FR0 input read | 1,728 |
| P8 write | 1,728 |
| padded P8 read | 1,792 |
| natural scatter write | 1,728 |
| center read + write | 1,728 + 1,728 |
| tail-padding initialization | 256 writes |
| complete scratch wipe | 1,792 writes |

演算法 transform 本身仍是兩次 coefficient load/store boundary；額外的是
canonicalization pass 與 scratch lifecycle。scratch 大小是 1,792 bytes，
其中 main 1,536、tail 256。

Pass 1 的 8x8 transpose 使用 `TRN1/TRN2`，不是 secret-dependent gather。
Pass 2 載入 P8 後沒有完整 reorder buffer；但 natural output ABI 導致每個
coefficient scalar scatter。

## D. Forward/Inverse core sharing

Forward 與 Inverse 共用的是數學 factorization 與 FR0 leaf ABI，不是同一份
assembly core：

- 同樣是 `2 × 9 × 16 × degree-3` leaf coordinates。
- Forward K1 直接產生 FR0；D1/BaseInv/BaseMul 直接消費該 ABI。
- Inverse 使用負指數 roots、inverse twist、`inv9/inv16`、R^-1 correction
  與 top recombination。
- Forward 的 top split、T1 tail、one-bank helper 與 Inverse 的
  `packed_i9/lazy_i16/lazy_itail` 沒有共用 macro 或 register allocation。

目前未共用的原因主要是 axis direction、twiddle ordering、terminal scale、
range closure、輸出 layout 和已各自完成的排程，而不只是尚未抽函式。
硬共用一個 core 會失去現有 CT/P8 packing 與 Forward K1 的 producer ABI。

## E. Layer merge 與 register blocking

`lazy_i16` 一次載入 16 個 packed-top Q registers，在 registers 內完成全部
四層 radix-2 NTT16、terminal scale、top recombination，再散寫結果；中間
不回 P8。這已經是完整四層 merge，且 arithmetic leaf 沒有 stack spill。

主路徑每次處理：

```text
q_c = [A_c(s0..s3), B_c(s0..s3)]
```

共有 `3 components × 2 s-halves = 6` calls。tail 再用一個 call 處理
`s=8 × 3 components × 2 tops`。CT 的 bit-reversed input placement已在
producer/P8 解決，所以沒有先跑 reorder kernel。

CT 確實容許四層 merge；但「CT 才能 merge」不成立，GS 也可持有 16 states。
CT 的實際優點是 range，而不是少載入 16 states。

## F. Reduction 與 range

目前 reachable chain 是：

```text
R^-1 BaseMul output <= 2497
I9 peak             <= 22473
I9 terminal twist   <= 3456
I16 exact peak      <= 30939
terminal raw R0     <= 6912
centered R0         <= 1728
```

對每個 fixed multiplication，Algorithm 10 是
`MUL + SQRDMULH + MLS`。已知 15 個 `b=1` NTT16 butterflies 中，14 個完整
mulmod 已由 correlation-aware proof 刪除；最後一個保留 quotient+`MLS`
range reset，但省略真正的 `MUL b=1`。

用不依賴 correlation 的簡化 range 對比：

```text
CT: 3456 -> 6912 -> 10368 -> 13824 -> 17280
GS: 3456 -> 6912 -> 13824 -> 27648 -> 55296
```

CT 的 twiddled branch 每層回到 `<q`，所以未乘的 path 只線性成長。GS 的
sum path 逐層倍增，第四層超過 signed int16，至少需要一次中途 reduction。
Official 正是在 level 4 後對 sum registers做 Barrett cut。這是 P7 確認的
真實 CT 優勢。

但 GT 仍有很多 reduction：七個 NTT16 blocks 合計 455 `MUL`、462
`SQRDMULH`、462 `MLS`；十二個 inverse9 blocks 再各有 37 組；
`center864` 又執行 108 `SQRDMULH+MLS` pairs。CT 沒有把 terminal scale、
top recombination或 canonicalization 變免費。

## G. Final scale / twist / Montgomery

BaseMul-for-Inverse 刻意輸出 R^-1。I9 的 arithmetic 保持該 representation；
I9 terminal table融合 `inv9 * lambda_c^{-s}`。NTT16 terminal table再融合：

```text
inv16 * zeta_top^{-t} * R-correction
```

因此 top recombination 後是 raw R0，而不是仍帶 R^-1。最後 `center864`
只選 canonical centered representative，不再做 domain conversion。

main 與 tail table 分開，是因為 main lanes是四個 s、tail lanes是三個
components 加 padding；不能假設兩張表可互換。P7 沒發現多乘或少乘一個 R。

## H. BaseMul 與 incomplete leaf

此 NTT 是 incomplete transform。`2×9×16 = 288` leaves，每個 leaf 保留
degree 3，所以共有 `288×3 = 864` coefficients。BaseMul 是 degree-3 cubic
leaf multiplication，不是 scalar pointwise multiplication。

FR0 的 `(top,row,column,component)` ordering同時是 Forward output、D1/
BaseInv/BaseMul input/output與 Inverse input。R^-1 BaseMul只改 scale 和
representative bound，不改座標。P7 的 864-coordinate bijection與既有
完整 product/KEM tests共同排除 pairing/twiddle錯位；沒有額外 BaseMul reorder。

## I. Constant-time 與 correctness

- N=16 CT/GS ordering：10,000 random vectors，零 mismatch。
- FR0 與 natural maps：各 864 coordinates，完整 bijection。
- Inverse wrapper loops、table addresses與scratch addresses只依 public counters。
- arithmetic leaf 沒有 data-dependent branch或stack spill。
- BaseInv 的 failure branch不屬於此 Inverse entry。
- production 沒有改動，因此沿用最近已通過的 256 inverse inputs、256
  R^-1 BaseMul→Inverse chains、alias、canary、AAPCS、scratch wipe、KAT與
  malformed-ciphertext gates。
- AArch64 feature scan：4 files、0 warnings；secret-independent conservative
  scan：4 files、0 warnings。Neon pattern scan列出319個既有 review prompts
  （173 fixed multiply-high、98 lane operation、48 transpose），均屬本報告
  已納入的 reduction/routing inventory，不是新增 correctness failure。

## J. Cost diagnosis and next gate

以目前 source stream 展開次數估計，GT leaf cores在 public wrapper之前約
9,903 instructions：

| core | calls | dynamic instructions |
| --- | ---: | ---: |
| `packed_i9` | 12 | 3,660 |
| `lazy_i16` | 6 | 4,404 |
| `lazy_itail` | 1 | 670 |
| `center864` | 1 | 1,169 |

selected Official assembly依固定 loops展開約 3,820 instructions。兩者不是
相同 transform representation，因此不能把差額當作單一 kernel speedup
預測；但它清楚說明為何「GT 已用 CT」仍不等於完整 Inverse 比 Official 快。

最大的可見 routing問題是 terminal scatter：七個 NTT16 kernels合計
864 `UMOV` + 864 `STRH`。先前 A2 控制已把它機械替換為 `ST1 lane`；雖少
634 instructions，完整 Inverse反而慢 484.157 cycles，因此不重開該方向。

P7 對「改 CT/GS」沒有找到值得進 Slothy 的新 DAG。不能因此直接跳到
consumer fusion；更新後的 roadmap 是：

1. **P7-B0 — Inverse core decomposition**：在相同 production ABI 下分別量
   inverse9、NTT16 arithmetic/scale/recombine、terminal scatter、center與
   wrapper/scratch lifecycle。
2. **P7-B1 — Inverse NTT optimization**：只攻實測最大的 NTT/routing區域；
   必須真的刪 arithmetic或routing，且完整 Inverse和Decaps都變快。
3. **P8 — raw-Inverse-to-ternary**：P7-B之後才刪獨立 center pass，並在
   `Inverse + conversion` 和完整 Decaps邊界判定，不能冒充NTT core收益。
4. **P9 — new ToBytes routing**：只有靜態少約829 instructions和101 reads
   才重開。
5. **P10 — BaseInv redesign**：保留為Keygen-only gap，不可遺忘。

Machine-readable evidence在 `results.json`；重跑：

```bash
python3 experiments/gt864-native-asm/inverse-p7-ct-feasibility/audit.py
```
