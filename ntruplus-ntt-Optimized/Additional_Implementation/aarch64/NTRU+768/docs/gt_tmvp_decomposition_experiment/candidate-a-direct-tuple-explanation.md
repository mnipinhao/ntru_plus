# Candidate A direct tuple route

日期：2026-06-23

## 目標

這條路線不是新的候選分支。它是 Candidate A 的 direct tuple 版本：

```text
NTT32 stage5 done
  -> directly store tuple layout
  -> basemul uses ld4 from tuple layout
```

重點是避免：

```text
ASM store block-major layout
  -> C copy/reorder
  -> tuple layout
```

最後一個寫 memory 的 forward ASM 應該直接寫成下一個 kernel 要 load 的形狀。

## Layout contract

Candidate A direct tuple memory layout：

```text
tuple_index(branch,row,k32,lane) =
  branch*384 + row*128 + 4*k32 + lane
```

byte offset：

```text
branch*768 + row*256 + 8*k32 + 2*lane
```

NTT32 stage5 live-out register shape：

```text
q[k].h[0..3] = branch0 lanes 0..3 for fixed row,k
q[k].h[4..7] = branch1 lanes 0..3 for fixed row,k
```

所以 direct store 可以是：

```asm
str d(q[k]),  [branch0_row_ptr]
ext qhi, q[k], q[k], #8
str d(qhi),   [branch1_row_ptr]
add branch0_row_ptr, branch0_row_ptr, #8
add branch1_row_ptr, branch1_row_ptr, #8
```

這裡不需要 `st4`。`st4` 是 basemul output 若要維持 tuple layout 時自然使用的
store；forward NTT final store 最自然的是 low/high D stores。

## 已改名

舊的臨時 tuple-route 命名已改成：

- `poly_gt_tmvp_candidate_a_direct_tuple_kem.c`
- `asm/candidate_a_direct_tuple_basemul.S`
- `asm/slothy/candidate_a_direct_tuple_boundary_symbolic.s`
- `docs/gt_tmvp_decomposition_experiment/candidate-a-direct-tuple-explanation.md`
- Makefile target：
  - `test_kem_gt_tmvp_candidate_a_direct_tuple_c`
  - `test_kem_gt_tmvp_candidate_a_direct_tuple`

## Direct store implementation state

新增 direct-store symbolic NTT32 source：

- `asm/slothy/ntt32_to_tuple_symbolic.s`

它從 `asm/slothy/ntt32_symbolic.s` 分出來，保留 stage1-5 arithmetic，只把
stage345 final store 從舊 block-major scatter：

```asm
str d_out, [scatter_ptr]
str d_hi,  [scatter_ptr + 768]
scatter_ptr += 24 with wrap
```

改成 Candidate A direct tuple：

```asm
str d_out, [scatter_ptr]
str d_hi,  [scatter_hi]
scatter_ptr += 8
scatter_hi  += 8
```

新增 wrapper：

- `asm/my_ntt_candidate_a_direct_tuple.s`

它定義：

```asm
.equ MY_NTT_DIRECT_TUPLE, 1
.equ MY_NTT_NO_POLY_ALIAS, 1
.include "asm/my_ntt.s"
```

`asm/my_ntt.s` 在 `MY_NTT_DIRECT_TUPLE` 模式下會 export：

```text
gt_candidate_a_direct_tuple_poly_ntt
```

並讓每個 row call：

```asm
x10 = dst + 256*row
x11 = dst + 768 + 256*row
bl _ntt32_8way_to_tuple
```

## Basemul contract

tuple memory 每 8 個 k32 leaf 是連續 64 bytes：

```text
[k0 l0 l1 l2 l3][k1 l0 l1 l2 l3] ... [k7 l0 l1 l2 l3]
```

basemul load：

```asm
ld4 {vA0.8h, vA1.8h, vA2.8h, vA3.8h}, [a], #64
ld4 {vB0.8h, vB1.8h, vB2.8h, vB3.8h}, [b], #64
```

output 若維持 tuple layout：

```asm
st4 {vR0.8h, vR1.8h, vR2.8h, vR3.8h}, [r], #64
```

`asm/candidate_a_direct_tuple_basemul.S` 目前重用 promoted `base_gt.opt.s`
schedule，但 lambda table 改成 row/k tuple order。

## Slothy result

Slothy 不在 Pi5 跑。這輪使用：

```text
ssh pinhao@172.25.166.141 -p 51208
```

該 host 是 Fedora/x86_64，只用來跑 Slothy 產生 AArch64 asm。

輸入：

```text
asm/slothy/ntt32_to_tuple_symbolic.s
```

輸出：

```text
asm/slothy/ntt32_8way.to_tuple.n1.opt.s
```

Slothy 結果：

```text
stage12 stripe0..7: selfcheck OK, each stripe around 22 cycles
stage345 block0: selfcheck OK, 101 cycles
stage345 block1: selfcheck OK, 114 cycles
stage345 block2: selfcheck OK, 114 cycles
stage345 block3: selfcheck OK, 114 cycles
```

產物 layout check：

```text
str d?, [x10] count: 32
str d?, [x11] count: 32
add x10, x10, #8 count: 0
add x11, x11, #8 count: 0
exact #24 scatter step: none
csel scatter wrap: none
```

所以這版已經不是：

```text
ASM store A layout -> C copy/reorder -> B layout
```

而是：

```text
NTT32 stage5 done -> direct D stores to tuple layout
```

## KEM verification

因為 Slothy host 是 x86_64，完整 KEM correctness/timing 在 Pi5 跑；Pi5 只用來
build/test，沒有在 Pi5 跑 Slothy。

ASM target，這是 batch baseinv 前的初始 direct-tuple ASM 結果：

```sh
make -B test_kem_gt_tmvp_candidate_a_direct_tuple
taskset -c 3 ./build/test_kem_gt_tmvp_candidate_a_direct_tuple
```

結果：

```text
count: 0
KEYGEN 2309 ticks
ENCAP   920 ticks
DECAP   861 ticks
```

C fallback target：

```sh
make -B test_kem_gt_tmvp_candidate_a_direct_tuple_c
taskset -c 3 ./build/test_kem_gt_tmvp_candidate_a_direct_tuple_c
```

結果：

```text
count: 0
KEYGEN 4579 ticks
ENCAP  2937 ticks
DECAP  3947 ticks
```

這裡的 C fallback 是 `ntt.c` forward NTT 加 C layout conversion，主要用來確認
Candidate A direct tuple KEM wiring 的 correctness，不是最終性能目標。

## Current interpretation

這輪完成的是「真正 direct tuple store」：

```text
NTT32 stage5 done
  -> str low D to [x10,#offset] branch0 tuple row
  -> str high D to [x11,#offset] branch1 tuple row
  -> basemul uses tuple ld4
```

正確性已過；但目前 KEM ticks 還不夠好。最可能的成本來源是：

```text
1. forward NTT32 direct tuple 用 64 個 D-store；目前已移除 x10/x11 #8 pointer updates。
2. stage345 block 的 Slothy schedule 對 memory writeback 形狀雖正確，但不一定是全局最省的 final-store schedule。
3. basemul 目前仍是 promoted base_gt.opt.s route，還不是為 direct tuple KEM 重新整體排過。
4. inverse side 仍接 block-major inverse ASM，forward tuple -> basemul -> inverse handoff 還不是完整共同最佳化。
```

下一個可推進 gate：

```text
1. 對 ntt32_to_tuple 的 final store 做更精準的 schedule/cost split。
2. 對 basemul direct tuple load/store 重新確認 lane order 與 instruction count。
3. 跟 gt_production / candidate_a_batch8 的完整 KEM target 做同機比較。
```

## 2026-06-23 ldp/final-store round

這輪做了三類改動：

```text
1. NTT32 final store:
   str D, [x10,#offset] / str D, [x11,#offset]
   不再用 add x10,#8 / add x11,#8 推進 pointer。

2. Phase123 load:
   legal input pairs 改 ldp：
     q10/q11 = [src,#6*128] and [src,#6*128+16]
     q4/q5   = [src,#0*128] and [src,#0*128+16]
     q6/q7   = [src,#2*128] and [src,#2*128+16]
     q8/q9   = [src,#4*128] and [src,#4*128+16]
   high pairs 保留 ldr，因為 ldp q offset range 不夠：
     q12/q13 = #8*128 and #8*128+16
     q14/q15 = #10*128 and #10*128+16

3. twist/precompute pair:
   q1/q2 改成 ldp [twist_ptr],#32。
```

這裡有一個重要踩雷點：Phase123 input pair 是相鄰 16 bytes，不是相隔
128 bytes。錯誤地改成 `q11=[src,#7*128]`、`q13=[src,#9*128]`、
`q15=[src,#11*128]` 會讓一般 `gtntt` 和 Candidate A direct tuple 都變成
`count:100000`。目前已用 forward contract test 固定住：

```text
gt_test/test_candidate_a_direct_tuple_ntt_contract.c

seed=0..7 mismatches=0
total_mismatches=0
```

Stage345 放大 Slothy range 的結果：

```text
pair-region / larger stage345 region 目前沒有得到可用 schedule。
主要問題是 region 內 label/adr handling，加上 split window 出現 infeasible。
目前正式產物仍採 block-level stage345 Slothy。
```

Twiddle = 1 lazy reduction：

```text
目前不建議 lazy 掉 line 95 類型的 power-0 reduction。
Phase123 raw DFT output bound 約 3*(q-1)=10368。
若 power-0 reduction 直接 identity，下一層加減可到 20736，再下一層可到
41472，超過 signed int16 range。
除非重新給更緊 input bound 或插入其他 reduce，否則不能安全刪。
```

Pi5 same-harness KEM 結果，batch baseinv 前：

```text
target                                count  KEYGEN  ENCAP  DECAP
test_kem_stock                            0     946    922    790
test_kem_gt_production_opt                0    2255    898    767
test_kem_gt_tmvp_asm_gtntt                0    2893   1351   1468
test_kem_gt_tmvp_candidate_a_direct_tuple 0    2309    920    861
```

相對 `gt_tmvp_asm_gtntt`，Candidate A direct tuple：

```text
KEYGEN: 20.2% faster
ENCAP : 31.9% faster
DECAP : 41.3% faster
```

相對 `gt_production_opt`，Candidate A direct tuple 目前仍慢：

```text
KEYGEN: 2.4% slower
ENCAP : 2.4% slower
DECAP : 12.3% slower
```

`test_kem_stock` 是此 folder 內的 stock ASM path，不一定等於外部
`ntruplus-KpqC-Final/.../test` baseline；不要把它直接當 KPQC Final 結論。

2026-06-24 batch baseinv 後的 Pi5 same-harness KEM 結果：

```text
target                                count  KEYGEN  ENCAP  DECAP
test_kem_stock                            0     946    924    791
test_kem_gt_production                    0    2257    899    771
test_kem_gt_production_opt                0     964    897    767
test_kem_gt_tmvp_candidate_a_direct_tuple 0    1012    921    861
```

這代表 Candidate A direct tuple 的 KEYGEN 主要瓶頸確實是 scalar
`poly_baseinv()`。新的 tuple batch baseinv 把 Candidate A KEYGEN 從
`2309 ticks` 降到 `1012 ticks`，但它仍然比 `gt_production_opt` 慢約
5.0%。這一版的 tuple baseinv 還有 public lambda gather；後續已改成固定
tuple-order lambda table，見下一段。

相對幅度：

```text
Candidate A direct tuple KEYGEN: 2309 -> 1012 ticks, -56.2%, 2.28x faster
Candidate A vs gt_production_opt after batch baseinv:
  KEYGEN +5.0%, ENCAP +2.7%, DECAP +12.3%
```

## 2026-06-24 tuple baseinv lambda table

Candidate A direct tuple 的 `poly_baseinv_gt_tuple_batch()` 已移除 runtime
`tuple_lambda8()` gather。現在 `poly_gt_baseinv_batch.c` 直接使用固定
`gt_tuple_baseinv_lambda[2][12][8]`，table 內容由同一個公開 mapping 產生：

```text
physical_j = (32 * row + 3 * k32) mod 96
lambda     = gt_rowbitrev_lambda[branch][physical_j]
```

這讓 tuple baseinv inner loop 從：

```text
tuple_lambda8(lambda_buf, branch, block)
vld1q_s16(lambda_buf)
```

變成：

```text
vld1q_s16(gt_tuple_baseinv_lambda[branch][block / 8])
```

Pi5 `test_gt_baseinv_batch` rebuild/run 結果：

```text
gt_baseinv_batch_correctness: ok
gt_scalar_block_baseinv_ticks: 758
gt_batch_block_baseinv_ticks: 112
gt_scalar_tuple_baseinv_ticks: 773
gt_batch_tuple_baseinv_ticks: 112
```

也就是 tuple batch baseinv 從 `127 ticks` 追平 block-major 的 `112 ticks`。

Pi5 same-harness Candidate A direct tuple KEM，在目前 stock-support +
tuple-input inverse NTT wiring 上：

```text
target                                  count  KEYGEN  ENCAP  DECAP
test_kem_gt_tmvp_candidate_a_direct_tuple   0     963    896    765
```

相對上一個同 wiring 的 Candidate A row `991 / 896 / 766`：

```text
KEYGEN: 991 -> 963 ticks, -2.8%
ENCAP : unchanged
DECAP : unchanged within noise
```

## 2026-06-24 stock support ASM wiring

Candidate A direct tuple KEM 現在只保留跟 transform/base arithmetic 有關的
自訂 `poly_*`：

```text
poly_ntt
poly_invntt
poly_baseinv
poly_basemul
poly_basemul_add
```

support 類 API 改回使用 stock support ASM：

```text
poly_cbd1
poly_sotp_encode
poly_sotp_decode
poly_tobytes
poly_frombytes
poly_crepmod3
poly_sub
poly_triple
```

Makefile 上的實作方式：

```text
CANDIDATE_A_DIRECT_TUPLE_KEM_C_SOURCES
  += $(STOCK_SUPPORT_ASM)

test_kem_gt_tmvp_candidate_a_direct_tuple_c
test_kem_gt_tmvp_candidate_a_direct_tuple
profile_kem_gt_tmvp_candidate_a_direct_tuple
  += -DGT_TMVP_USE_STOCK_SUPPORT_ASM
  += -DGT_TMVP_USE_TUPLE_INVNTT_ASM
```

`poly_gt_tmvp_candidate_a_direct_tuple_kem.c` 裡的 C support implementation
仍保留 fallback，但在 `GT_TMVP_USE_STOCK_SUPPORT_ASM` 開啟時不會編譯，
避免跟 `asm/add.s`、`asm/crepmod3.s`、`asm/pack.s`、`asm/cbd.s` 產生
duplicate symbol。

Pi5 same-harness KEM 結果：

```text
target                                  count  KEYGEN  ENCAP  DECAP
test_kem_gt_tmvp_candidate_a_direct_tuple   0     991    896    781
test_kem_gt_tmvp_candidate_a_direct_tuple_c 0    3261   2913   3869
```

相對上一輪 batch baseinv 後的 Candidate A direct tuple ASM 結果
`1012 / 921 / 861`，改回 stock support ASM 後：

```text
KEYGEN: 1012 -> 991 ticks, -2.1%
ENCAP :  921 -> 896 ticks, -2.7%
DECAP :  861 -> 781 ticks, -9.3%
```

## 2026-06-24 tuple-input inverse NTT wiring

Before this change, Candidate A direct tuple used this inverse path:

```text
tuple NTT-domain input
  tuple_to_block_major()
  gt_block_major_poly_invntt()
  canonical output
```

The new path is:

```text
tuple NTT-domain input
  gt_tuple_poly_invntt()
  canonical output
```

The arithmetic pipeline is the same production inverse NTT pipeline.  Only the
row-stage123 input loads change:

```text
block-major input row load:
  physical_j = (32*row + 3*k32) mod 96
  byte offset = 8*physical_j

direct-tuple input row load:
  row base = branch + row*256 bytes
  byte offset = row base + 8*k32
```

So the new entry removes the full 768-coefficient tuple-to-block-major memory
pass before inverse NTT.

Validation:

```text
make -B test_candidate_a_direct_tuple_ntt_contract
seed=0..7: ntt_mismatches=0, invntt_mismatches=0
total_mismatches=0
```

Pi5 same-harness KEM result after tuple-input inverse NTT:

```text
target                                  count  KEYGEN  ENCAP  DECAP
test_kem_gt_tmvp_candidate_a_direct_tuple   0     991    896    766
```

Relative to the previous stock-support Candidate A direct tuple row
`991 / 896 / 781`:

```text
KEYGEN: unchanged
ENCAP : unchanged
DECAP : 781 -> 766 ticks, -1.9%
```

Profiler result:

```text
poly_invntt: 103 -> 88 ticks
dec_valid : 780 -> 765 ticks
```
