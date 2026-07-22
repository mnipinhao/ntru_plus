# NTRU Prime truncation AVX2 精華

這份文件整理
[`NTRU_Prime_truncation`](https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation)
的 AVX2 實作中，對目前 NTRU+768 最有學習價值的觀念。完整逐檔分析、遠端
驗證與數據限制另見
[`ntru-prime-truncation-avx2-comparison-guide.md`](ntru-prime-truncation-avx2-comparison-guide.md)。

## 一句話總結

NTTRU 是「把既有 NTT pipeline 排得很漂亮」的教材；這份 NTRU Prime
實作更值得學的是：

> 先選一條會自然產生 16 個平行子問題的代數分解，再寫 AVX2。

一個 YMM 有 16 個 signed 16-bit lanes。作者不是把原本的算法硬塞進
YMM，而是用 truncated Rader-17 、Good–Thomas 3-by-2 與 16-by-16
transpose，讓「16 個獨立的小 polynomial」正好落在 16 lanes 上。

## 先釐清：它不是 NTRU+ 的另一支 NTT

| 項目 | NTRU Prime truncation | NTRU+768 |
| --- | ---: | ---: |
| scheme coefficients | 761 | 768 |
| 模數 | `q=4591` | `q=3457` |
| scheme ring | `x^761-x-1` | `x^768-x^384+1` |
| 乘法中間環 | `Phi_17(x^96)`，degree 1536 | native-ring NTT，192 個 quartic blocks |
| 最後的小乘法 | 192 個 size-8 products | 192 個 quartic products |
| API | 完整 `mulcore` / `polymul` | `ntt` / `basemul` / `invntt` / `polymul` |

雖然兩邊都出現 `192`，數學對象完全不同。可以學代數路徑、lane layout、
transpose fusion、Montgomery 排程與表格生成；不能直接搬 Rader tables、
twiddles、reduction constants、Bruun/Karatsuba 公式或最後的 ring fold。

## `truncation` 到底在 truncate 什麼？

sntrup761 的兩個 degree-at-most-760 polynomials 相乘，product degree 最高是
1520。作者先在 degree-1536 的

```text
Z_4591[x] / Phi_17(x^96)
```

中完成乘法，再回到 `x^761-x-1`。因為 1520 沒有超過 1536，可以在最後
正確回收並 fold。

一般 size-17 Rader transform 會處理 17 個成分，但 `Phi_17` 對應的是 16 個
nontrivial components。Truncated Rader 只留這 16 個有用成分：

```text
17 的 prime structure
    -> 移除不屬於 Phi_17 的 trivial component
    -> 16 個有用成分
    -> 正好是 YMM 的 16 個 int16 lanes
```

這是這份實作最核心的技巧：它先從數學上消掉不適合 vectorization 的
部分，不是留給 assembly 用 padding 或 don't-care lanes 補救。

## 完整 pipeline

[`__avx2.c`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/__avx2.c)
的 `_mulcore` 是閱讀入口：

```text
761 coefficients + zero padding
    |
    | truncated Rader-17
    v
16 個 size-96 cyclic problems
    |
    | Good–Thomas 3 x 2 + twist
    v
48 個 cyclic + 48 個 negacyclic size-16 problems
    |
    | twist + 16 x 16 transpose
    v
每個 YMM 的 16 lanes = 16 個獨立 polynomial 的同一 coefficient
    |
    | CT/Bruun + size-8 Karatsuba
    v
inverse transpose/twist -> inverse GT -> inverse Rader
    |
    v
fold x^761 = x + 1 + final scaling
```

對每一個 input，`_mulcore` 會做：

- 6 次 `__asm_rader17_truncated`；
- 1 次 `__asm_3x2_pre`；
- 3 組 cyclic 與 3 組 negacyclic 的 `twist_transpose_pre`。

乘法區會做 3 次 cyclic 與 3 次 negacyclic size-16 kernels，每次同時處理
16 個獨立 polynomials。後半段再對稱地反轉這些表示。

## 兩種 `friendly` 是什麼？

### Vectorization-friendly

簡化地說，一個轉換若可以寫成 `M tensor I_16`，那麼 `M` 的每一個 scalar
operation 都可以一次作用在 16 個並行資料上，不需要把 lane 一個一個拆出來。
Truncated Rader 與 Good–Thomas 部分就是刻意產生這種 shape。

### Permutation-friendly

當剩下 16 次小 polynomial 乘法時，AVX2 沒有 Neon 那種方便的
vector-by-scalar halfword multiplication。作者因此先 transpose 16 個同型小問題：

```text
transpose 前：一個 polynomial 的 16 coefficients 在同一塊
transpose 後：一個 YMM 是 16 個 polynomials 的同一 coefficient
```

這樣 `vpmullw` / `vpmulhw` 就能做 16 個獨立 rings 的同一步驟。這個「先重排
instances，再讓 lane-wise arithmetic 變自然」的想法，比某一條 shuffle
instruction 更值得學。

## `twist + transpose` 是最適合立刻借鏡的寫法

`twist_transpose_pre` 不會先掃一次整個 array 做 twist，再掃一次做
transpose。它在同一個 unrolled 16-by-16 network 中：

1. load 每個 row；
2. 乘上該 row 的 public Montgomery twist；
3. 用 `vpunpck*` 從 16-bit、32-bit、64-bit 逐層交錯；
4. 最後用 `vperm2i128` 交換 128-bit halves；
5. 直接 store 成下一支 size-16 kernel 要的 layout。

`twist_transpose_post` 反向完成同一件事。這種 fusion 同時省掉額外的 full-array
pass 與中間材料化，與目前 NTRU+768 GT SoA/native layout 實驗非常相關。

## Assembly 寫法的其他精華

### 固定乘數預先存 `factor*qinv`

[`basemul_core.inc`](../third_party/NTRU_Prime_truncation/avx2/avx2_bench/basemul_core.inc)
有專門的 `montgomery_mul_precompute` 形式。當其中一個 operand 是 public fixed
factor 時，table 同時存 factor 與 factor*qinv，hot path 可少一個 low multiply。

### `x2` / `x3` / `x4` macros 是 latency schedule，不只是少寫幾行

它會先發出多條獨立 low products，再一起做 high products、corrections 與更新。
CPU 等待一條 multiply chain 時，可以執行另一條。這與 NTTRU 最值得學的
Montgomery scheduling 原則相同。

### Cyclic 與 negacyclic 直接做兩支專用 kernel

`basemul.S` 將 `x^16-1` 與 `x^16+1` 拆成不同的 straight-line path。這會增加
code size，卻能移除 hot path 中的 branch、符號選擇與多餘 shuffle。要學的是如何
用完整 pipeline 數據決定「要不要用 code footprint 換少幾條指令」。

### Stack 被當成可預測的 scratch，但 ABI 寫法不該照抄

Rader 與 size-16 kernels 會手動把 stack 對齊到 32 bytes，並預留 0x600、0xa00 或
0xb00 bytes scratch。這讓 16 個 YMM 都可專注在目前 arithmetic wave，但也帶來
stack traffic、code size 與 unwind metadata 問題。NTRU+ 可學 scratch lifetime 規劃，不該
照搬這個手寫 prologue。

## 對 NTRU+768 最實際的實驗優先序

### P0：lane semantics 表先於 assembly

為每一個 GT stage 寫出：

```text
YMM number -> lane number -> 數學對象 -> 下一個 consumer
```

如果無法簡單說明 lane 7 代表什麼，就不應先寫 shuffle。

### P1：將 public twist 與本來就必須做的 permutation 融合

找目前 GT frontend/inverse 中必然存在的 transpose 或 layout conversion，只做一個
candidate：在同一批 load/register/store 內合併 fixed Montgomery twist。算術、range
checkpoint 與輸出 layout 必須不變。

### P2：先數有用子問題，再選 transform

每個新 transform 先統計：

- 真正有用的 terminal blocks；
- padding / don't-care blocks；
- full-polynomial permutations；
- lane occupancy；
- 完整 `2*forward + basemul + inverse` 的轉換成本。

這份 NTRU Prime 實作的主要加速來自小乘法數量從前作的 768 個降到 192
個，不是某一層 butterfly 快了幾條 cycles。

### P3：同時保留 boundary 與 full-path benchmark

像上游一樣保留 Rader/GT/transpose/small-mul 層級的定位數據，但 NTRU+ 的
採用決定一定要看完整 polymul。一支轉換單獨變快，卻新增一次 768-
coefficient transpose，往往是負優化。

## 驗證與數據邊界

已將 revision `3eb881fb4aa83a9c424a121acefb1b8d35cf6f93` 放到 Ryzen 7
9700X，以 `-march=x86-64-v3 -mtune=znver5 -mprefer-vector-width=256`
編譯。明列上游 Makefile 漏掉的 common sources 後：

- naive-vs-`mulcore` 逐項比較通過；
- fold 後的 761 個 `polymul` coefficients 逐項比較通過；
- twiddle generator self-check 通過；
- binary 中沒有 ZMM 或 opmask registers。

同一台主機上遊 harness 五次 pinned runs 的 median-of-medians 是：

| Operation | raw TSC ticks |
| --- | ---: |
| NTRU Prime `mulcore` | 5,852 |
| NTRU Prime `polymul` | 6,042 |
| NTRU+768 production `polymul`（只作背景） | 1,884 |

最後一列不能拿來說 NTRU+ 是 3.2 倍快。兩邊的 scheme、ring、modulus、中間
dimension、output contract 與 timing harness 都不同。NTRU Prime harness 使用未序列化
`rdtsc` 與未初始化的 benchmark arrays；NTRU+ harness 使用 `lfence/rdtscp`、
initialized rotating inputs 與 warmup。這些數字只能證明「量級與重點在哪裡」，
不是同契約效能排名。

另外，上游 `Makefile` 在目前 revision 有兩個 source-list 問題：將
`COMMON_SOURCEs` 誤寫成 `COMMON_SOURCE`，而且 `test` / `bench` 另外漏列
`ring.c`。所以 README 的 `make test` / `make bench` 會 link 失敗。本次保持
upstream checkout 不變，實際可重現的明列 source 指令已記在完整文件。

## 閱讀時反覆問的六個問題

1. 這個 YMM 的 16 lanes 現在是「16 個 coefficients」還是「16 個獨立 rings」？
2. 這個 algebraic map 為什麼產生 16 的倍數？
3. 這個 permutation 是數學上必要，還是前一層 layout 造成的補救？
4. twist 能不能和必要的 load/transpose/store 融合？
5. 這些 Montgomery chains 哪些彼此獨立，可以交錯隱藏 latency？
6. 這個小 kernel 的加速有沒有降低完整 polymul，還是只把成本移到其他邊界？

能回答這六題，就抓到這份 AVX2 實作真正值得學的部分了。
