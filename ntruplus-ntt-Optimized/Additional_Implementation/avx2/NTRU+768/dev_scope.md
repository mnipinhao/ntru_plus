# NTRU+768 AVX2 Good–Thomas 重設計：完整 Scope

這一版先把你的六項決定鎖定，整個專案不再研究 full-input NTT，也不再做 direct NTT32 baseline。目標是針對 NTRU+768 的實際使用路徑，聯合設計：

[
\boxed{
\text{Forward NTT}
+\text{basemul}
+\text{baseinv}
+\text{CT inverse NTT}
+\text{NTT-domain serialization ABI}
}
]

NTRU+768 的官方 decomposition 最終是 192 個 degree-4 component rings，且 scheme 直接序列化 NTT-domain 的 public key、secret-key components 與 ciphertext，因此 layout、canonical representation、basemul range 不能各自獨立決定。 

---

# 0. 已確定的設計決策

## 0.1 參數

[
q=3457,\qquad n=768,\qquad d=4,
]

[
R_q=\mathbb Z_q[x]/(x^{768}-x^{384}+1).
]

使用 primitive 576-th root：

[
\zeta=22,\qquad \phi=\zeta^{96}.
]

最後得到 192 個：

[
\mathbb Z_q[x]/(x^4-\alpha_i).
]

官方 NTT 是 initial radix-2、一次 radix-3、五次 radix-2；新設計只是把一次 radix-3 與五次 radix-2 重組成 Good–Thomas (3\times32)。

---

## 0.2 Forward 只有 small-input contract

不做 generic centered-(q) input 版本。

唯一輸入契約暫定：

[
\boxed{-3\le a_i\le4}
]

這涵蓋：

* (f=3f'+1)
* (g=3g')
* (r\in{-1,0,1})
* (m\in{-1,0,1})

NTRU+ 的 keygen、encap、decap 中所有 coefficient-domain forward NTT 都來自這類 small polynomials。

---

## 0.3 Top butterfly 不做完整 reduction

直接沿用官方 top butterfly 的 small-input 特化。

已知官方 bound 可記為：

[
-2891\le B_{\rm top}\le2896,
]

所以：

[
|B_{\rm top}|<q.
]

因此 Stage 0 不插 Montgomery／Barrett reduction。

這個 bound 要直接寫進 verification contract，而不是只留在註解。

---

## 0.4 NTT32 只研究 B、C

不再實作 direct cyclic32 baseline。

### Candidate N32-B

[
z^{32}-1=(z^{16}-1)(z^{16}+1)
]

先 split：

* cyclic16 half；
* negacyclic16 half。

再將 negacyclic16 twist 成 cyclic16，兩半共用 cyclic16 instruction skeleton。

### Candidate N32-C

把：

* branch global twist；
* Good–Thomas wrap correction；
* DFT3 preweights；
* cyclic32 split；
* negacyclic16 local twist；
* cyclic16 twiddles；

盡可能 composition 成 fully weighted NTT32 schedule。

---

## 0.5 Forward 輸出只有兩類 contract

### `ntt_lazy`

[
|a_i|<B_{\rm lazy}.
]

(B_{\rm lazy}) 不先硬寫死成 (3q)。先以 (3q) 為第一版，之後依完整 Forward、basemul、reducer proof 放寬。

### `ntt_canonical`

內部 canonical 建議使用 centered：

[
-\frac{q-1}{2}\le a_i\le\frac{q-1}{2},
]

即：

[
-1728\le a_i\le1728.
]

要序列化時再融合轉成：

[
0\le a_i<q.
]

不建議維護兩套獨立 NTT canonical kernels；應是：

```text
ntt_canonical_centered
encodeq_from_centered_gt
```

後者同時完成：

* centered (\to [0,q))
* GT order (\to) specification order
* 12-bit packing

`Encodeq` 本身要求輸入在 ([0,q))。

---

# 1. Table generator 與 indexing 的定位

## 1.1 Generator 不代表 runtime 查大表

Table generator 應永遠保留，因為它是整個實作的 single source of truth。

它負責產生：

* root exponents；
* Good–Thomas forward／inverse maps；
* branch twist；
* wrap correction；
* NTT32-B／C execution schedule；
* basemul (\alpha) lane order；
* inverse scaling；
* GT order 與 specification order 的 mapping；
* symbolic range metadata。

但 optimized assembly 不一定使用「完整二維陣列加 runtime index」。

## 1.2 最快版本應是 generated static indexing

最佳方向通常是：

```text
generator
    ↓
產生固定 offsets / masks / sequential constants / unrolled schedule
    ↓
assembly 只做 pointer increment 或固定 displacement
```

而不是：

```text
runtime 計算 exponent
runtime 做 modulo
runtime 做 irregular table lookup
```

在 AVX2 上，順序載入一張按 execution order 排好的常數表，通常比 runtime 算 index 更快。

所以兩者並不衝突：

[
\boxed{
\text{generator 作為正確性來源，generated indexing 作為最快實作}
}
]

## 1.3 建議 generator 產出三種 representation

### Reference tables

```text
gt_preweight_ref[2][3][32]
alpha_ref[192]
forward_index_ref[192]
inverse_index_ref[192]
```

用於 C reference 與測試。

### Optimized constant stream

```text
forward_constants_B[]
forward_constants_C[]
inverse_constants_B[]
inverse_constants_C[]
```

完全按照 assembly load 順序排列。

### Static indexing description

```text
load offsets
store offsets
vpblend masks
vperm indices
lane-to-component maps
```

第一版可直接讀完整 generated tables；優化版再把規律 index 轉成固定 offset／pointer rotation。Generator 本身不應被移除。

---

# 2. 全域資料 ABI

內部 NTT-domain layout 固定為：

```text
[branch][k3][k32_block][degree][lane]
```

維度為：

```text
branch     = 2
k3         = 3
k32_block  = 2
degree     = 4
lane       = 16
```

總共有：

[
2\cdot3\cdot2=12
]

個 AVX2 quartic blocks。

每個 block：

```text
YMM degree 0
YMM degree 1
YMM degree 2
YMM degree 3
```

線性 layout：

```text
for branch in 0..1:
    for k3 in 0..2:
        for block32 in 0..1:
            degree0[16]
            degree1[16]
            degree2[16]
            degree3[16]
```

這份 ABI 同時供：

* `ntt_lazy`
* `ntt_canonical`
* `basemul`
* `baseinv`
* `invNTT`
* `Encodeq/Decodeq`
* (\hat r=\hat r') equality check

NTRU+ 的 degree-4 basemul 與 base inversion 都直接依賴四個 coefficient planes，因此這份 ABI 必須先於 kernel 實作固定。 

---

# 3. Forward NTT Scope

完整 Forward：

```text
Input [-3,4]
    ↓
Stage F0: top split, no full reduction
    ↓
Stage F1: x^4 striding + GT pack + branch preweight + DFT3
    ↓
Stage F2: NTT32-B or NTT32-C
    ↓
Stage F3a: lazy output
or
Stage F3b: canonical centered output
```

---

## 3.1 Stage F0：Top split

輸入：

[
f=f_L+x^{384}f_H.
]

輸出：

[
F_+=f_L+\phi f_H,
]

[
F_-=f_L+\phi^{-1}f_H.
]

實作維持官方 small-input butterfly：

* 不做完整 Montgomery reduction；
* 不先 store 成官方 top-split layout；
* 直接供 Stage F1 做 striding／GT packing。

Invariant：

[
F_\pm\equiv f\bmod(x^{384}-\phi^{\pm1}),
]

[
-2891\le F_\pm[i]\le2896.
]

---

## 3.2 Stage F1：Fused GT pack + DFT3

令：

[
y=x^4.
]

每個 branch 有四個 length-96 planes。

Good–Thomas input CRT mapping 使用：

[
n=64n_3+33n_{32}\pmod{96}.
]

這是同時滿足

[
n\equiv n_3\pmod 3,
\qquad
n\equiv n_{32}\pmod {32}
]

的 CRT inverse；`32*n3 + 3*n32` 是 frequency-side mapping，不能用在
input coordinate。

GT output frequency mapping 固定為：

[
k=32k_3+3k_{32}\pmod{96}.
]

每個 input coefficient 需要 branch preweight：

[
F_s^{-n}.
]

Branch 與 root convention 固定為：

* branch 0: `y^96 = phi`，`F0 = 2`，`F0^96 = phi^-1`；
* branch 1: `y^96 = phi^-1`，`F1 = 22`，`F1^96 = phi`。

因 modulo-96 wrap，正確 preweight 是：

[
F_s^{-((64n_3+33n_{32})\bmod96)}.
]

第一版由 generator 直接產生：

```text
preweight[branch][n3][n32]
```

Stage F1 一次完成：

1. 讀取 top-split data；
2. (x^4)-striding；
3. 3-way GT row construction；
4. branch twist／wrap correction；
5. simplified DFT3；
6. store 成三條 contiguous length-32 rows。

DFT3：

[
d=B-C,
]

[
t=\omega_3d,
]

[
Y_0=A+B+C,
]

[
Y_1=A-C+t,
]

[
Y_2=A-B-t.
]

NTRU+ 規格的 radix-3 layer也使用相同型態的簡化，避免直接做六個 independent constant products。

---

# 4. NTT32-B Scope

## 4.1 結構

輸入為 cyclic32：

[
A(z)\in\mathbb Z_q[z]/(z^{32}-1).
]

先做：

[
A_+=A_0+A_1,
]

[
A_-=A_0-A_1,
]

其中 (A_+) 位於：

[
z^{16}-1,
]

而 (A_-) 位於：

[
z^{16}+1.
]

取 primitive 32nd root (\tau)，(\tau^{16}=-1)，對 (A_-) 做：

[
A_-[j]\mapsto A_-[j]\tau^j.
]

轉成 cyclic16。

## 4.2 實作目標

```text
split32
    cyclic half ───────────┐
                           ├─ same cyclic16 skeleton
    negacyclic half → twist┘
```

共用的是：

* instruction skeleton；
* permutation sequence；
* register allocation。

不一定共用：

* exact constants；
* range；
* light-butterfly位置。

## 4.3 必須比較的兩種 B 子版本

### B1：cyclic half 不額外 reduction

只對 negacyclic half 的 twist做 reduction，cyclic half保持 split 後的較大 range。

優點：少 multiplication。

缺點：兩半 range 不對稱，cyclic16 kernel 可能需要額外 reduction。

### B2：cyclic half identity-reduce

對 cyclic half 做 multiplication-by-one／等價 reduction，negacyclic half 做 twist。

兩半都縮回小範圍，再共用完全相同的 cyclic16 range schedule。

優點：

* range 最乾淨；
* code 最一致；
* inverse 容易對稱。

缺點：增加 identity multiplications。

Candidate B 內部也要實測 B1、B2，而不是先假設 identity reduction 一定浪費。

---

# 5. NTT32-C Scope

Candidate C 不再清楚區分：

```text
global twist
split
local twist
cyclic16 twiddle
```

而是讓 generator 將所有 diagonal constant multiplications composition 成一張 weighted butterfly schedule。

## 5.1 Generator 的 schedule node

每個 butterfly node至少描述：

```text
input lane pair
output lane pair
constant exponent
Montgomery representation
light / multiplying butterfly
input bound
output bound
```

## 5.2 最佳化目標

依序優先：

1. 所有 16-bit add/sub 不溢位；
2. 最終輸出 (\le B_{\rm lazy})；
3. 減少 modular multiplications；
4. 減少 constant loads；
5. 減少 shuffle uops；
6. 減少 code size。

Candidate C 的核心不是「table 比 B 小」，而是：

[
\boxed{
\text{相鄰的 constant multiplications 只做一次}
}
]

代價是某些原本的 light butterflies 會變成 multiplying butterflies。

---

# 6. Forward Range Proof Scope

只做 small-input path，但必須對 B、C 各自做完整 per-stage／per-lane proof。

## 6.1 需要追蹤的不是單一全域 bound

每一層要追蹤：

```text
branch
k3
cyclic / negacyclic half
lane group
degree plane
```

因為：

* light butterfly 路徑與 multiplying butterfly 路徑 bound 不同；
* Candidate B 的 cyclic／twisted half 不同；
* Candidate C 的常數分布不均。

## 6.2 每個 cut 保存四個 invariant

```text
algebraic invariant
layout invariant
range invariant
Montgomery-scale invariant
```

至少 cuts：

```text
after top split
after GT preweight
after DFT3
after split32
after local twist
after each cyclic16 layer
final lazy output
final canonical output
```

## 6.3 `B_lazy` 的選擇原則

不是「能裝進 int16 的最大值」，而是：

[
\boxed{
\text{Forward 能自然輸出，且 basemul 能直接消化的最大值}
}
]

因此：

[
B_{\rm lazy}
============

\min(
B_{\rm forward},
B_{\rm basemul},
32767
).
]

第一版：

[
B_{\rm lazy}=3q
]

作為保守 ABI。

後續依 proof依序測：

[
4q,\quad5q,\quad6q.
]

不建議直接把 ABI 寫死成 (8q)，因為即使能存進 16-bit，也未必適合 basemul。

---

# 7. 32-bit Accumulation 是否能放寬 `ntt_lazy`？

## 結論

[
\boxed{\text{可以，而且很可能能由 }3q\text{ 放寬到 }6q}
]

但前提是 basemul 使用 direct quartic formula 加 exact 32-bit accumulation，而不是傳統逐項 16-bit Montgomery multiplication，也不是純 16-bit Karatsuba。

## 7.1 理論上的主要 bound

Quartic output中最多有四個乘積相加。

若兩個 lazy operands 都滿足：

[
|a_i|,|b_i|<B,
]

使用 signed 32-bit exact accumulator，需要：

[
4B^2<2^{31}.
]

因此：

[
B<\sqrt{2^{29}}\approx23170.
]

相對於 (q=3457)：

[
\frac{23170}{3457}\approx6.70.
]

所以整數倍 safe candidate：

[
\boxed{B_{\rm lazy}=6q=20742}
]

而：

[
7q=24199
]

已使：

[
4(7q)^2>2^{31}.
]

所以不使用 64-bit accumulation 的情況下，(6q) 是很自然的最高候選。

## 7.2 `vpmaddwd` pairwise bound

每次 `vpmaddwd` 先算兩個乘積並相加：

[
2B^2<2^{31}.
]

對 (B=6q)：

[
2B^2\approx8.6\times10^8<2^{31},
]

安全。

再將兩個 pair sums 相加：

[
4B^2\approx1.72\times10^9<2^{31}.
]

也安全。

## 7.3 (\alpha)-weighted terms

不能先累加三個 (B^2) 再直接以 16-bit (\alpha) 相乘。

應先算：

[
a_i'=\alpha a_i\bmod q
]

並縮回 centered small range，再用：

[
a_i'b_j
]

進入 `vpmaddwd`。

此時最壞通常仍是：

[
c_3=a_0b_3+a_1b_2+a_2b_1+a_3b_0,
]

也就是四個 (B^2)，所以 (6q) bound 仍是主限制。

## 7.4 32-bit reducer 是必要條件

basemul 必須具備接受：

[
|T|<4B_{\rm lazy}^2
]

的 32-bit reduction kernel，並輸出 centered：

[
|c_i|\le q/2.
]

要 separately 證明：

* Barrett approximation error；
* signed 32-bit input range；
* AVX2 lane packing；
* Montgomery scale；
* no overflow in correction step。

## 7.5 Wide lazy 與 Karatsuba 的衝突

Karatsuba需要形成：

[
a_i+a_j.
]

若 (B=6q)：

[
2B=12q=41484>32767.
]

所以純 16-bit Karatsuba 無法接受 (6q) lazy input。

因此設計分支很明確：

```text
wide lazy  → direct formula + 32-bit accumulation
narrow lazy → direct or Karatsuba 都可比較
```

若最後要放寬到 (5q/6q)，basemul baseline 應改成 direct `vpmaddwd`，而不是把 Karatsuba當主方案。

---

# 8. Basemul Scope

輸入：

```text
GT SoA
|a_i|, |b_i| < B_lazy
```

輸出：

```text
centered canonical
|c_i| <= q/2
```

選擇 basemul 在這裡完成 canonicalization，有三個好處：

1. inverse CT 的 input range 很小；
2. NTT-domain addition 前比較安全；
3. serialization／comparison 不必再處理 basemul 的大 lazy range。

## 8.1 Basemul candidates

### BM-A：direct + 32-bit accumulation

主方案，支援 (B_{\rm lazy}) 最寬。

### BM-B：quartic Karatsuba

只保留作 narrow-lazy benchmark。

### BM-C：asymmetric expanded operand

對反覆使用的：

* (\hat h)
* (\hat f)
* (\hat h^{-1})

預先儲存：

* (\alpha a_i)
* pair sums
* reordered degree planes

用空間換時間。

NTRU+ 規格中的 quartic product公式正好是 direct 4×4 structured matrix-vector product。

---

# 9. Baseinv Scope

Baseinv 不直接接受 wide-lazy input。

介面固定：

```text
input:
    centered canonical NTT-domain

output:
    centered canonical NTT-domain
```

degree-4 inversion使用官方結構：

[
a(x)=\widetilde a_0(x^2)+x\widetilde a_1(x^2),
]

降成 degree-2 ring inversion。

192 個 scalar denominators 使用 batch inversion／Montgomery trick：

* prefix products；
* 一次 field inversion；
* backward recovery。

Batch inversion 將多個 inversions轉成一次 inversion和線性數量的 multiplications。

---

# 10. Inverse NTT Scope

Inverse 必須與 B／C 各有一個成對版本。

```text
invNTT-B
invNTT-C
```

共同要求：

* inverse 使用 Cooley–Tukey style；
* 直接吃 GT SoA layout；
* 不做 standalone bit reversal；
* 不先 canonical permutation；
* normalization、untwist、top CRT 融進最後 stages。

## 10.1 Inverse NTT32-B

Forward B：

```text
split
cyclic16
twisted cyclic16
```

Inverse B：

```text
CT inverse cyclic16 on both halves
inverse local twist on former negacyclic half
inverse split merge
```

可把：

* (16^{-1})
* inverse local twist
* Montgomery correction

融合進 cyclic16 最後一個 multiplying layer。

## 10.2 Inverse NTT32-C

由 generator 根據 Forward weighted schedule產生 inverse schedule。

不能只是將 constants 反向排列；要同時處理：

* permutation inverse；
* inverse constants；
* CT dataflow；
* scaling；
* Montgomery domain。

## 10.3 Inverse DFT3

使用簡化 inverse radix-3：

[
t_1=\omega_3(\hat a_1-\hat a_2),
]

[
t_2=\hat a_0-\hat a_1-t_1,
]

[
t_3=\hat a_0-\hat a_2+t_1,
]

再得到未除以 3 的 outputs。NTRU+ 規格已給出這種 reduced inverse radix-3 形式。

不要單獨乘 (3^{-1})。

## 10.4 Final inverse fusion

最後一個 fused pass 同時做：

```text
inverse GT permutation
inverse branch preweight
remaining 3^-1 / 32^-1
top CRT
Montgomery correction
coefficient-order writeback
```

Top CRT：

[
H=(\phi-\phi^{-1})^{-1}(F_+-F_-),
]

[
L=F_+-\phi H.
]

不應有 standalone：

```text
untwist pass
normalization pass
top CRT pass
```

---

# 11. Serialization 與 equality Scope

NTRU+ 直接儲存／傳輸 NTT-domain objects，且 decapsulation 會比較：

[
\hat r=\hat r'.
]



因此需要：

```text
encodeq_gt()
decodeq_gt()
ntt_equal_canonical()
```

## `encodeq_gt`

一次完成：

```text
GT SoA
→ specification component order
→ centered to [0,q)
→ 12-bit packing
```

## `decodeq_gt`

一次完成：

```text
12-bit unpack
→ canonicality check
→ specification order to GT SoA
→ [0,q) to centered
```

## equality

不直接比較 lazy values。

兩邊必須：

* 都 canonical centered；或
* 都 encode成同一 canonical byte representation。

---

# 12. 驗證 Scope

## Algebraic tests

每一 stage 和 C reference 比較：

```text
top split
GT pack
DFT3
NTT32-B
NTT32-C
basemul
baseinv
invNTT
```

## Exhaustive／random range tests

* exhaustive small coefficient combinations能做的局部 kernel；
* random full polynomials；
* adversarial max-bound patterns；
* all-positive／alternating-sign patterns。

## Generator assertions

至少驗證：

[
\zeta^{576}=1,
]

[
\zeta^{288}=-1,
]

[
\phi=\zeta^{96},
]

[
F_0^{96}=\phi^{-1},
\qquad
F_1^{96}=\phi,
]

以及每個 GT slot 的 quartic modulus在 GT↔Official component mapping 後，
必須逐項與官方 `index[192]` 一致。

## End-to-end identities

[
\operatorname{invNTT}(\operatorname{NTT}(a))=a,
]

[
\operatorname{invNTT}
(
\operatorname{basemul}(\operatorname{NTT}(a),\operatorname{NTT}(b))
)
=

ab\bmod(x^{768}-x^{384}+1).
]

---

# 13. Benchmark Scope

每個 kernel記錄：

```text
cycles
loads
stores
shuffle uops
multiply uops
code size
constant-table size
```

比較項目：

```text
official
N32-B1
N32-B2
N32-C
```

但 project baseline 不再另外實作 direct N32-A。

最先 benchmark：

[
\boxed{
\text{top split}
+x^4\text{-striding}
+\text{GT pack}
+\text{DFT3}
}
]

第二個：

[
\boxed{
\text{NTT32-B vs NTT32-C}
}
]

第三個：

[
\boxed{
B_{\rm lazy}=3q,4q,5q,6q
\text{ 對 Forward + basemul 總成本的影響}
}
]

不能只看 NTT cycle；真正 metric 是：

[
\boxed{
\text{NTT}*{\rm lazy}
+
\text{basemul}*{32\text{-bit}}
}
]

因為放寬 lazy range 可能讓 NTT 更快，但讓 basemul reducer 更慢。

---

# 14. 實作里程碑

## Phase 1：Generator／Reference

* root convention
* GT maps
* reference tables
* C NTT32-B
* C NTT32-C
* C inverse
* exact range tracer

## Phase 2：Fused Front End

* official top butterfly
* stride-4
* GT pack
* DFT3
* first AVX2 benchmark

## Phase 3：NTT32-B

* B1 asymmetric range
* B2 identity-reduced
* register-resident cyclic16
* exact output bound

## Phase 4：32-bit Basemul

* direct quartic `vpmaddwd`
* 32-bit reducer
* test (3q,4q,5q,6q)
* determine final (B_{\rm lazy})

## Phase 5：NTT32-C

* weighted schedule generator
* AVX2 kernel
* compare B total cost

## Phase 6：Inverse CT

* inverse B
* inverse C
* fused inverse DFT3／GT／CRT

## Phase 7：Baseinv／Serialization

* batch baseinv
* Encodeq/Decodeq fused permutation
* canonical equality

## Phase 8：Full NTRU+ Integration

* keygen
* encap
* decap
* official compatibility
* end-to-end cycles

---

# 最後鎖定的核心目標

第一版先設定：

[
B_{\rm lazy}=3q.
]

但 scope 內正式保留：

[
B_{\rm lazy}\in{3q,4q,5q,6q}.
]

若 direct 32-bit basemul 與 reducer proof 成立，最有希望的終點是：

[
\boxed{B_{\rm lazy}=6q}
]

因為：

[
4(6q)^2<2^{31},
]

但：

[
4(7q)^2>2^{31}.
]

因此 32-bit accumulation 的確可能讓 Forward 不必縮到 (3q)，甚至有機會讓 NTT32-B／C 的自然輸出直接進 basemul；最終 bound 應由「Forward range + exact basemul accumulator + reducer」三者共同決定，而不是由 NTT 單獨決定。
