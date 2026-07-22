# NTTRU AVX2 精華

這份文件只保留 Gregor Seiler 的 NTTRU AVX2 實作中，對 NTRU+768 最有價值的
設計觀念。完整逐檔證據、遠端測試環境與限制另見
[`nttru-avx2-comparison-guide.md`](nttru-avx2-comparison-guide.md)。

## 一句話總結

這份 AVX2 實作真正厲害的地方，不是某一條神奇指令，而是它把整條 pipeline
一起設計：

```text
一般 coefficient layout
    -> NTT 一邊算、一邊改成 terminal-block SoA
    -> basemul / baseinv 直接消費 SoA，不做額外 transpose
    -> inverse NTT 反向融合 shuffle
    -> pack 成 protocol bytes
```

每一層都盡量同時保留多條互不相依的 Montgomery multiplication chain，用有用的
運算填滿乘法 latency；twiddle 也事先排成 consumer 要的 YMM lane 形狀。

## 先釐清參數差異

NTTRU 與目前 NTRU+768 都有 768 個 coefficients，環的形狀都是

```text
Z_q[X] / (X^768 - X^384 + 1),
```

但其餘重要 contract 不同：

| 項目 | NTTRU | NTRU+768 |
| --- | ---: | ---: |
| 模數 | `q=7681` | `q=3457` |
| 序列化寬度 | 13 bits | 12 bits |
| NTT layers | 8 | 7 |
| terminal blocks | 256 個 cubic blocks | 192 個 quartic blocks |
| 每個 block | 3 coefficients | 4 coefficients |

所以可以學排程、register layout、shuffle 與 table packing；不能直接搬 twiddle、
Montgomery constants、reduction、base polynomial 公式或 range bounds。

## `pack` 的功能是什麼？

`pack` 是「polynomial 與 byte string 之間的序列化」，不是 NTT，也不是
`vpack*` 指令的泛稱。

程式中的 polynomial 每個 coefficient 用一個 `int16_t` 保存，因此 768 個
coefficients 在記憶體中占 1536 bytes。但 NTTRU 的 coefficient 只需要 13 bits，
public key 或 ciphertext 不應浪費成每個 16 bits：

```text
768 * 13 / 8 = 1248 bytes.
```

[`pack.s`](../third_party/NTTRU/avx2/pack.s) 有三個實際 exported functions：

| Function | 功能 |
| --- | --- |
| `poly_pack_uniform` | 768 個 13-bit coefficients 壓成 1248 bytes |
| `poly_unpack_uniform` | 1248 bytes 還原成 768 個 coefficients |
| `poly_pack_short` | 把 `{-1,0,1}` short coefficients 轉成 2-bit symbols 再壓縮 |

`poly_pack_uniform` 每輪讀 256 個 coefficients，也就是 16 個 YMM，經過固定的
shift/add 網路後寫出 416 bytes。三輪剛好是 1248 bytes。它不把資料逐項交回
scalar code，因此可以避免 768 次 scalar bit manipulation。

`poly_pack_short` 先對 `{-1,0,1}` 加一，得到 `{0,1,2}`，再把八組 2-bit values
疊進一個 16-bit word。每輪 128 coefficients 變成 32 bytes。

`pack` 的用途包括：

- 形成 public key、secret key 與 ciphertext 的協定 bytes；
- 提供 hash/KDF 所需的唯一 byte representation；
- 減少傳輸與儲存大小；
- 在解密端把收到的 bytes 還原成 polynomial。

對 NTRU+768 的啟示是「照 12-bit contract 重新推導一組對稱的 pack/unpack vector
network」，不是把 NTTRU 的 13-bit shift constants 搬過來。任何改動都必須 byte-
exact 通過 KAT 與 round-trip tests。

## 什麼是 SoA？

SoA 是 Structure of Arrays。它的對照是 AoS，Array of Structures。

假設 NTT 結束後，每個 terminal cubic block 有三個 coefficients
`(c0,c1,c2)`。一般直覺的 AoS 排法是：

```text
block0: c0 c1 c2
block1: c0 c1 c2
block2: c0 c1 c2
...
```

也就是記憶體看起來像：

```text
b0.c0, b0.c1, b0.c2, b1.c0, b1.c1, b1.c2, ...
```

但 AVX2 的 lane-wise multiplication 希望一條指令同時計算許多 block 的同一欄。
因此 NTTRU 的 SoA 讓 16 個 blocks 這樣排列：

```text
YMM0 = [b0.c0, b1.c0, ..., b15.c0]
YMM1 = [b0.c1, b1.c1, ..., b15.c1]
YMM2 = [b0.c2, b1.c2, ..., b15.c2]
```

如此一條

```text
vpmullw YMM0_a, YMM0_b, YMM_product
```

就同時計算 16 個 cubic blocks 的 `a.c0 * b.c0`。不需要 gather，也不需要在
`basemul` 前做一個完整 polynomial transpose。

NTRU+ production terminal block 是 quartic，所以相同概念會是四個 vectors：

```text
YMM0 = 16 blocks 的 c0
YMM1 = 16 blocks 的 c1
YMM2 = 16 blocks 的 c2
YMM3 = 16 blocks 的 c3
```

SoA 的代價是 NTT 必須產生這個 layout，inverse NTT 也必須懂得如何消費或反轉
它。真正的效能判斷必須看完整 pipeline：

```text
2 * forward NTT + basemul + inverse NTT.
```

如果 forward NTT 自己變快，卻在 basemul 前新增 768-coefficient transpose，通常
不值得。這也是目前 NTRU+768 Good-Thomas SoA 實驗最重要的設計原則。

## 什麼是「雙 determinant exponentiation 排程」？

更精確的名稱是：

> 兩條獨立 determinant-vector exponentiation chains 的交錯排程。

它不是一種不同的數學 exponentiation，也不是把兩個 determinants 相乘後一起
求 inverse。

NTTRU 的 terminal block 是 cubic。對每個 block 做 inverse 時，先算 adjugate 與
determinant，再用 Fermat：

```text
det^-1 = det^(q-2) = det^7679 mod 7681.
```

[`baseinv.s`](../third_party/NTTRU/avx2/baseinv.s) 一次處理正 zeta 與負 zeta 兩組
blocks，得到兩個互不相依的 determinant vectors：

```text
A = 16 lanes 的 positive-zeta determinants
B = 16 lanes 的 negative-zeta determinants
```

也就是一次有 32 個 field inversions，但以兩個 YMM vectors 表示。固定 addition
chain 會做：

```text
A^2, B^2
A^4, B^4
A^8, B^8
...
A^7679, B^7679
```

關鍵是 assembly 不會等 `A^2` 的完整 Montgomery chain 全部結束後才開始 `B^2`。
它會交錯發出：

```text
A 的 mul-low
B 的 mul-low
A 的 mul-high
B 的 mul-high
A 的 correction
B 的 correction
```

當 CPU 等待 A 的乘法結果時，可以執行 B 的獨立乘法。這叫 instruction-level
parallelism，目的是隱藏 latency；結果仍等價於各自獨立求 inverse。

NTRU+768 目前不是對每個 denominator 各做一次 `q-2`。它先把 12 個 YMM
denominator vectors 做 Montgomery batch inversion，只付出一次 field inversion，
再反向展開。因此不能用 NTTRU 的整段 exponentiation 取代 batch inversion。

真正值得借的是：在 NTRU+ 那「唯一一次」field exponentiation 裡，也找兩條或
更多互不相依的 squaring/multiplication work 交錯；並讓 batch prefix/suffix products
的 register order 直接配合後面的 adjugate scaling。

## AVX2 核心算術：packed 16-bit Montgomery multiplication

六支 kernel 共用的基本模式，是在 16 個 signed 16-bit lanes 上做 Montgomery
product。概念上是：

```text
aq    = low16(a * qinv)
lo    = low16(aq * b)
hi    = high16(a * b)
corr  = high16(lo * q)
r     = hi - corr
```

對固定 twiddle `zeta`，table 會事先同時存好：

```text
zeta*qinv, zeta.
```

hot loop 便可以直接以 `vpmullw`/`vpmulhw` 消費，不必臨時 broadcast、計算
`zeta*qinv` 或整理 lanes。

精華不是這四步本身，而是排程方式：先發出四到六條互不相依的 low products，
再發 high products，再一起做 corrections，最後才 butterfly add/sub。這比一個
butterfly 從頭做到尾更容易填滿 execution ports。

## 六支檔案各自的精華

| 檔案 | 最值得看的東西 | 不可直接搬的東西 |
| --- | --- | --- |
| [`ntt.s`](../third_party/NTTRU/avx2/ntt.s) | 多條 Montgomery chains 分組、levels 2--7 fusion、shuffle 融入 stages、consumer-oriented stores | 8-layer schedule、twiddles、cubic output permutation |
| [`invntt.s`](../third_party/NTTRU/avx2/invntt.s) | forward shuffle 的反向實作、稀疏 reduction checkpoints、final scaling fusion | normalization constants、checkpoint ranges |
| [`basemul.s`](../third_party/NTTRU/avx2/basemul.s) | 16-block cubic SoA、premultiplier reuse、正負 zeta 共用排程 | cubic formulas、zeta table offsets |
| [`baseinv.s`](../third_party/NTTRU/avx2/baseinv.s) | 兩條 determinant-vector chains 交錯、adjugate/inversion/scaling fusion、zero-mask aggregation | `a^7679` chain、cubic determinant、手動 stack ABI |
| [`reduce.s`](../third_party/NTTRU/avx2/reduce.s) | 六個 YMM unroll、branch-free canonicalization | `q=7681` 的 bit-13 folding identity |
| [`pack.s`](../third_party/NTTRU/avx2/pack.s) | 完全 vectorized 13-bit pack/unpack、2-bit short packing | 所有 13-bit shifts 與 byte counts |

## `ntt.s` / `invntt.s` 最值得抄的是「安排」，不是「算式」

Forward NTT 前兩個 wide-stride levels 分開處理；後面 levels 2--7 在較小工作集內
融合。隨著 butterfly distance 變小，layout conversion 也依序使用：

- `vperm2i128` 做跨 128-bit half 的重排；
- `vpunpcklqdq` / `vpunpckhqdq` 做 64-bit group 重排；
- shift + `vpblendd` 做 32-bit group 重排；
- shift + `vpblendw` 做 16-bit lane 重排。

這個順序反映 butterfly distance，而不是任意 shuffle。inverse 則反方向消費相同
physical layout。讀這兩支檔案時，應把每個 shuffle 問成：

1. 它在改哪一個 butterfly distance？
2. 它的輸出是否正好是下一個 stage 或 basemul 要的 layout？
3. 能否和前一個 arithmetic stage 的 store 合併？

## `reduce.s` 為什麼短，卻不該先移植？

NTTRU 利用：

```text
7681 = 8192 - 511 = 2^13 - (2^9 - 1).
```

若 `x = low13 + 8192*high`，則 modulo 7681：

```text
x = low13 + 511*high
  = low13 - high + (high << 9).
```

所以 reducer 可以用 mask、shift、add/sub 完成。這是 `q=7681` 的特殊禮物。
`q=3457` 沒有同一個 identity。對 NTRU+ 最有用的不是照抄，而是學它的研究方法：

1. 從 modulus 尋找適合 packed-int16 的特殊分解；
2. 證明完整 input range 不 overflow；
3. 窮舉 congruence 與 exact output image；
4. 最後才 benchmark 是否勝過目前 Montgomery/Barrett reducer。

## 其他容易忽略的優點

### Twiddle table 是執行排程的一部分

`consts.c` 不是被動資料。它將 twiddle 依照 stage、重複次數、lane order，甚至
`factor*qinv`/`factor` pair 預先展開。較大的 read-only table 換掉 hot-loop 的
broadcast、shuffle 與 scalar address arithmetic。

### Lazy reduction 是經過選點，不是少做幾次 `%q`

Forward/inverse 不會每個 butterfly 都 canonicalize。它只在 range 快碰到
signed-int16 邊界或下一個 multiplication precondition 前 checkpoint。這個技巧只有
在每一層 input/output bound 都明確時才安全。

### Failure aggregation 不在每個 lane branch

`baseinv.s` 用 `vpcmpeqw` 找 zero determinants，再把兩個 YMM masks OR/reduce 成
單一 scalar return value。loop body 的控制流與 lane 值無關。這個 pattern 可用來
避免每個 terminal block 的 data-dependent branch，但上層是否 retry 仍需獨立做
constant-time/security 分析。

## 對 NTRU+768 的實驗優先序

### P0：只改 schedule，不改數學 contract

在 production `ntt.s`、`invntt.s`、`basemul.s` 中標出每條 Montgomery chain 的
dependency DAG。做 schedule-only candidate：

```text
all independent mul-low
-> all independent mul-high
-> all corrections
-> butterfly updates
```

保持 twiddle、layout、reduction points 與 ABI 完全相同。先跑 differential/KAT，
再在 Ryzen 9700X 比較 cycles、instructions 與 code size。

### P1：table 與 consumer layout audit

逐一檢查 NTRU+ twiddle 是否已經以 consumer 需要的 lane shape 保存。只把確定可
移到 public generated table 的 broadcast/shuffle 移出去。同時以完整
`2*NTT + basemul + invNTT` 判斷 layout，不接受孤立 transform 變快但多一次
full-polynomial transpose 的方案。

### P2：batch inversion 內部排程

保留目前 12-vector Montgomery batch inversion。只研究：

- prefix products 是否能交錯兩條獨立 chains；
- 唯一一次 `fqinv` addition chain 是否有可並行的 squaring/multiply；
- suffix 展開能否和四個 adjugate coefficient scaling pipeline；
- denominator vectors 是否已按 consumer order 保存。

### P3：12-bit serialization

以 generator 推導 NTRU+ 的 12-bit pack/unpack network，要求：

- 所有 768 coefficients round-trip；
- arbitrary 12-bit boundary values round-trip；
- public key/ciphertext bytes 與既有 KAT byte-exact；
- malformed input 的 canonicality contract 不變；
- 實際 KEM path 有 measurable gain。

### 暫不做：照搬 `reduce.s`

除非先找到 `q=3457` 對 packed-int16 明顯有利的新 congruence 與完整 range proof，
否則不要因為 NTTRU reducer 指令短就優先仿作。

## 閱讀時最重要的五個問題

看到任何一段 AVX2 assembly，都用這五題檢查：

1. 一個 YMM 的 16 lanes 現在各代表哪 16 個數學對象？
2. 哪些 multiplication chains 彼此獨立，可以交錯隱藏 latency？
3. 這個 shuffle 是數學 permutation、stage layout，還是單純補救前一層的 store？
4. 此處為什麼可以 lazy？下一個 reduction checkpoint 的 range proof 是什麼？
5. 此 kernel 的 output layout 是否讓下一個 consumer 零轉換地直接使用？

能回答這五題，就抓到這份 NTTRU AVX2 的真正精華了。

## 驗證邊界

NTTRU revision `65bb4da35944d0ee2ce8462de86e479486904625` 已在 Ryzen 7
9700X 上編譯並通過 upstream polynomial、NTRU PKE 與 KEM 測試，細節與 timing
見長版文件。這只證明 upstream harness 沒有觀察到錯誤；它不證明移植到 NTRU+
後的 correctness、range safety、KAT compatibility 或 constant-time behavior。
