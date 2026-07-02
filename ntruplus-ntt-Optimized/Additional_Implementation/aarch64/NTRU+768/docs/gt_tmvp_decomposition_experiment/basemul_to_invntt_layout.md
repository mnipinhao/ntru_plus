# base_gt output 到 invntt input layout 對照

這份文件只處理 layout contract，不主張 cycle 數。結論先寫在前面：

`base_gt` 目前的 `st4` 產生的是 GT block-major AoS。這符合目前 `poly`
ABI，也符合 `poly_tobytes()` / `poly_frombytes()` 的 public polynomial
格式；但它不是 `invntt` stage123 最順的 consumption order。

另外要分清楚 KEM path：

- encap: `poly_basemul_add(c, h, r, m) -> poly_tobytes(ct, c)`
- decap: `poly_basemul(m1, c, f) -> poly_invntt(m1, m1)`

所以 `poly_basemul_add` 的 output 不是馬上給 `invntt` 吃。真正值得研究
`base_gt output -> invntt input` 的是 decap 的 `poly_basemul -> poly_invntt`
路線。

## 1. 目前 base_gt output: block-major AoS

`asm/gt/base_gt.S` 的 layout contract 是：

```text
coeff[branch * 384 + 4 * physical_j + lane]
```

byte offset 是：

```text
byte = branch * 768 + 8 * physical_j + 2 * lane
```

每個 `poly_basemul` / `poly_basemul_add` loop 處理 8 個連續
`physical_j`：

```text
ld4 a0,a1,a2,a3  // physical_j ... physical_j+7
ld4 b0,b1,b2,b3
...
st4 r0,r1,r2,r3  // write back same 8 consecutive physical_j
```

因此 memory 形狀是：

```text
physical_j 0: q0 q1 q2 q3
physical_j 1: q0 q1 q2 q3
physical_j 2: q0 q1 q2 q3
...
```

這裡的 AoS 是「每個 quartic block 的 4 個 coefficient 放在一起」。
`st4` 很適合這個 ABI，因為四個 result vectors 分別是 q0/q1/q2/q3，
正好 interleave 成每個 block 的四個 halfword。

## 2. invntt block-major direct-load consumption order

目前 production inverse NTT 入口 `gt_block_major_poly_invntt` 走
`INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH`。block-major path 不先把三個
row materialize 出來，而是直接從 block-major memory 用固定 offset 載入。

公式是：

```text
physical_j(k3, k32_br) = (32 * k3 + 3 * k32_br) mod 96

branch0 byte = src + 8 * physical_j
branch1 byte = src + 768 + 8 * physical_j
```

每次 direct load 建出一個 q-vector：

```text
[branch0 q0 q1 q2 q3, branch1 q0 q1 q2 q3]
```

也就是一個 vector 同時包含兩個 branch 的同一個 row/frequency slot。

三個 row 的 `physical_j` 讀取順序是：

```text
row k3=0:  0,  3,  6,  9, ..., 93
row k3=1: 32, 35, 38, 41, ..., 29
row k3=2: 64, 67, 70, 73, ..., 61
```

換句話說，block-major `st4` 寫的是 consecutive physical order；
`invntt` stage123 讀的是每隔 3 個 block 的 row order。兩者不是同一個
linear order。

## 3. row-contiguous tuple input order

The row-contiguous tuple input contract is:

```text
tuple[branch][row][k32][quartic_lane]
```

對 `invntt` stage123 來說，這個 layout 的 offset 變成：

```text
byte = branch * 768 + row * 256 + 8 * k32_br + 2 * lane
```

也就是每個 row 的 `k32` 是連續的：

```text
row k3=0: k32 0, 1, 2, ..., 31
row k3=1: k32 0, 1, 2, ..., 31
row k3=2: k32 0, 1, 2, ..., 31
```

這就是為什麼 `gt_tuple_poly_invntt` 的 stage123 load pattern 比
block-major path 乾淨：它不需要 `(32*k3 + 3*k32_br) mod 96` 這個
physical gather。

## 4. stage123 stripe scratch 是 post-stage123 layout

`STORE_STAGE123_STRIPE_SCRATCH` 的註解寫得很關鍵：

```text
scratch[64*j + 16*group] = stage123_output[j + 8*group]
stage45 consumes each stripe as [j, j+8, j+16, j+24]
```

這個 scratch layout 是 inverse row NTT32 stage123 做完之後的 layout。
所以 `base_gt` 不能只靠改 `st4` 就直接產生這個 scratch，除非同時把
invntt stage123 的 butterfly 也 fuse 進 `base_gt` 後面。

因此要分成兩種不同優化：

1. layout-only store:
   `base_gt` 只改 output memory order，讓下一個 `invntt` 讀得更順。
2. fused stage123:
   `base_gt` 做完 product 後，直接接 invntt stage123，然後 store 到
   stage45 stripe scratch。

第二種不是 `st4`/`st1` store selection 問題，而是 kernel fusion。

## 5. expected vs actual

| 項目 | 目前 base_gt `st4` | invntt block-major stage123 | tuple stage123 |
| --- | --- | --- | --- |
| branch | 一次只處理目前 branch 的 8 個 block | 每個 q-vector 同時載 branch0/branch1 | 每個 q-vector 同時載 branch0/branch1 |
| j order | consecutive physical_j | row order: `(32*k3 + 3*k32_br) mod 96` | row-contiguous `k32=0..31` |
| lane order | q0,q1,q2,q3 AoS | branch0 q0..q3 + branch1 q0..q3 | branch0 q0..q3 + branch1 q0..q3 |
| 適合的 consumer | `poly_tobytes`, block-major ABI | current `gt_block_major_poly_invntt` direct path | `gt_tuple_poly_invntt` |
| 是否等於 invntt 最佳 input | 否 | 是，但靠 gather/direct offsets | 是，offset 最簡單 |

## 6. 對 st4 / st1 的判斷

`st4` 不是錯，它剛好適合目前 block-major AoS ABI。

但是如果下一步一定是 `invntt`，那問題就變成：

```text
是否值得讓 basemul 直接輸出 row-contiguous tuple layout？
```

這時候不一定要 `st4`。可能的方向是：

- 保留 `st4`：維持 public ABI，最適合 encap `poly_basemul_add -> poly_tobytes`。
- 改成 row-contiguous stores：讓 decap `poly_basemul -> poly_invntt` 少掉
  block-major physical gather。
- fuse stage123：直接產生 stage45 stripe scratch，但這已經是
  `basemul+invntt` pipeline kernel，不是單純替換 store。

實作上還有一個限制：目前 `base_gt` 是 branch0 全部做完，再 branch1 全部
做完。可是 `invntt` stage123 的 q-vector 想同時拿 branch0/branch1。若要讓
`base_gt` 直接寫成 stage123 最想吃的 paired-branch row input，可能需要：

- 改成 branch0/branch1 paired processing；
- 或先把 branch0/branch1 各自寫 row-contiguous，再讓 tuple invntt 用兩個
  branch base pointer 組 vector；
- 或做更大的 `basemul -> invntt stage123` fusion。

## 7. 目前建議

短期不要改 encap 的 `poly_basemul_add` store。它後面接 `poly_tobytes()`，
block-major AoS 是合理的。

比較值得推的是 decap-only path：

```text
poly_basemul_to_invntt_input(m1, c, f)
gt_tuple_or_row_poly_invntt(m1, m1)
```

第一步先做 C/layout reference，確認 row-contiguous output 和現有
`gt_block_major_poly_invntt` 結果完全相同。確認後再決定 ASM 是用 scatter
`st1`、重排 source layout，還是直接做 fused stage123。

## 8. 目前實作狀態

已新增 tuple-output prototype：

```text
poly_basemul_to_tuple(a_block, b_block) -> tuple output
```

目前 production wiring 使用 Slothy n1 版本：

```text
asm/slothy/base_gt_to_tuple.slothy.s
asm/base_gt_to_tuple.n1.opt.s
asm/base_gt_to_tuple_n1_opt_wrapper.S
```

Slothy parser 不能吃原本最直接的 `ldrh offset + st4 lane` 形狀，所以 n1
input 改成：

```text
zip1/zip2 v23..v26 -> eight D tuple groups
ldp xaddr0, xaddr1 from a 64-bit offset table
str dN, [xaddr]
```

也就是用 `str d` 取代 `st4 lane`，讓 store/repack 區段能一起被 Slothy 排程。

KEM decap path 也已接成 opt-in：

```text
GT_PRODUCTION_USE_TUPLE_DECAP
poly_basemul_to_tuple(&m1, &c, &f)
gt_tuple_poly_invntt(&m1, &m1)
```

Pi5 result:

```text
test_gt_basemul_to_tuple: ok
source-order poly_basemul_to_tuple: 72 ticks
Slothy n1 poly_basemul_to_tuple:    67-68 ticks

gt_production_opt                    dec_valid 767 ticks
gt_production_opt_tuple_decap        dec_valid 774 ticks
gt_production_opt_add32_tuple_decap  dec_valid 773 ticks
```

所以目前這個 prototype 證明 layout contract 正確，也把 source-order tuple
kernel 從 72 ticks 降到 67-68 ticks；但它仍不是 KEM performance win。
同環境 baseline 的 decap 是 767 ticks，tuple-decap 是 773-774 ticks。

原因很直接：baseline decap 的核心段是

```text
poly_basemul + poly_invntt + poly_basemul = 62 + 90 + 62 = 214 ticks
```

tuple-decap 變成：

```text
poly_basemul_to_tuple + gt_tuple_poly_invntt + poly_basemul
= 67 + 90 + 62 = 219 ticks
```

也就是 tuple layout 目前沒有省掉 invntt 的 90 ticks，只是把第一個 basemul
從 62 換成 67 ticks。下一步若要讓 decap 變快，不能只做 layout-only
tuple store；要嘛讓 `basemul` 直接產生 inverse stage123 之後的 stripe scratch，
要嘛 fuse `basemul -> invntt stage123`，真的刪掉下一段 load/gather/butterfly
成本。

## 9. rminus1 stage123 scratch split prototype

2026-06-25 added a decap-only prototype to split the current rminus1 inverse
path at the stage123/stage45 boundary:

```text
poly_basemul_rminus1(&product, a, b)
gt_rminus1_block_major_to_stage123_stripe_scratch(scratch, &product)
poly_invntt_from_rminus1_stage45scratch(out, scratch)
```

Files:

```text
asm/gt/inv_my_ntt_rminus1.S
asm/slothy/production/invntt_opt.production.s
gt_test/test_gt_rminus1_stage123scratch.c
```

New ABI contracts:

```text
gt_rminus1_block_major_to_stage123_stripe_scratch(scratch, block_major)
  input : GT block-major rminus1 product
  output: three 512-byte row scratches
          scratch[row][64*j + 16*group] =
              inverse_stage123_output[row][j + 8*group]

poly_invntt_from_rminus1_stage45scratch(out, scratch)
  input : the stage123 stripe scratch above
  output: normal-domain coefficients, using the rminus1 branchfold constants
```

Pi5 result:

```text
gt_rminus1_stage123scratch_correctness: ok
poly_invntt_from_rminus1               90 ticks
block_major_to_stage123_stripe_scratch 21 ticks
poly_invntt_from_rminus1_stage45scratch 69 ticks
split_stage123scratch_invntt           90 ticks
```

Interpretation:

```text
The ABI split is correct, and the current inverse cost decomposes cleanly as:

  direct stage123 gather + stage123 arithmetic + scratch store ~= 21 ticks
  stage45 + post branchfold                              ~= 69 ticks
  full poly_invntt_from_rminus1                          ~= 90 ticks

This prototype is not expected to beat production yet because it still stores
the block-major product and then reloads it in the stage123 producer.  Its value
is that it proves the exact consumer ABI for the next real experiment:

  poly_basemul_rminus1_to_stage123scratch()

That future kernel must fuse the basemul final product registers directly into
inverse stage123 and store only the stage45 stripe scratch.  Merely adding
another layout-only product store is unlikely to win.

## 10. rminus1 direct stage123scratch producer prototype

2026-06-25 implemented the first concrete producer ABI:

```text
poly_basemul_rminus1_to_stage123scratch(scratch, a, b)
  helper: poly_basemul_rminus1_to_stage123input_tuple(tmp, a, b)
          - base_gt.S arithmetic
          - GT_BASEMUL_STORE_RMINUS1
          - GT_BASEMUL_STORE_TUPLE
          - output tmp is tuple/row-contiguous stage123 input
  then:   gt_rminus1_tuple_to_stage123_stripe_scratch(scratch, tmp)
          - existing tuple stage123 butterfly path
          - output scratch is stage45 stripe scratch

poly_invntt_from_rminus1_stage45scratch(out, scratch)
  consumes that scratch and runs stage45 + post branchfold.
```

Files:

```text
asm/base_gt_rminus1_to_stage123scratch_wrapper.S
asm/gt/inv_my_ntt_rminus1.S
asm/slothy/production/invntt_opt.production.s
gt_test/test_gt_rminus1_stage123scratch.c
kem.c
gt_test/kem_component_profiler.c
```

Correctness:

```text
gt_rminus1_stage123scratch_correctness: ok
test_kem_gt_production_opt_rminus1_stage123scratch: count: 0
```

Pi5 component result:

```text
poly_basemul_rminus1                         45 ticks
poly_invntt_from_rminus1                     90 ticks
old first decap segment                     135 ticks

poly_basemul_rminus1_to_stage123scratch      70 ticks
poly_invntt_from_rminus1_stage45scratch      69 ticks
new first decap segment                     139 ticks
```

Pi5 KEM/profile same-harness comparison:

```text
profile_kem_gt_production_opt_rminus1
  dec_valid 751 ticks
  decap component subtotal 734 ticks

profile_kem_gt_production_opt_rminus1_stage123scratch
  dec_valid 756 ticks
  decap component subtotal 736 ticks

test_kem_gt_production_opt_rminus1
  KEYGEN 961, ENCAP 898, DECAP 749

test_kem_gt_production_opt_rminus1_stage123scratch
  KEYGEN 960, ENCAP 897, DECAP 754
```

Interpretation:

```text
This prototype is correct but should not be promoted.

It removes the public block-major product ABI, but it still has a private
1536-byte tmp boundary:

  basemul -> tuple row-input tmp -> tuple stage123 -> stage45 scratch

So it does not actually delete the stage123 input memory pass.  It replaces the
old 45 + 90 first decap segment with about 70 + 69, which is slightly worse.

A true fused version would need to compute the basemul products in inverse
stage123 grouping and immediately run the stage123 butterflies in registers.
That means the basemul input side would no longer be the current cheap
consecutive 8-block ld4 pattern; it would need stride-3 row gathers such as
j, j+3, ..., plus the j+96 half.  That is a much larger kernel and may lose the
ld4 advantage, so this result is evidence to pause this route unless a better
gather plan is found.
```
```
