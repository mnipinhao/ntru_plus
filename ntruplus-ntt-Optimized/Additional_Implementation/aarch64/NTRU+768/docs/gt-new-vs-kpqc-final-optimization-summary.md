# GT new 相對 KPQC final 的 production 優化總覽

更新日期：2026-07-10

> 這份是 internal production audit。面向 KPQC 作者、以演算法與實作概念為主的
> 短版請看 `gt-ntruplus768-optimization-summary-for-kpqc.md`。

這份文件回答三個問題：

1. 現在所稱的 `GT new` 到底是哪一個 build。
2. 它相對未修改的 `KPQC final` 做了哪些演算法、資料 layout、跨 kernel contract 與 ASM 排程優化。
3. 這些優化目前在 Raspberry Pi 5 Cortex-A76 上帶來多少 cycle 收益。

本文只把目前實際由 Makefile link 進 `gt_production_default` 的路徑列為
production。`experiments/` 下的其他 prototype 不會因為曾經通過 correctness
或 PMU 就算進 GT new。

## 1. 結論先行

目前 GT new 在 Pi 5、portable `NO_CE` hash path 下，相對未修改的
KPQC final：

| KEM operation | KPQC final | GT new | 少掉的 cycles | cycle reduction | speedup |
|---|---:|---:|---:|---:|---:|
| keygen | 39966 | 37966 | 2000 | 5.004% | 1.053x |
| encap | 39013 | 37590 | 1423 | 3.648% | 1.038x |
| decap | 35180 | 32482 | 2698 | 7.669% | 1.083x |

GT new 現在確實三項都快於 KPQC final，但還沒有達到原先的 scheme-level
`20%` 目標。更重要的是，GT new 的 retired instructions 仍比 KPQC 多
`0.4%` 到 `2.4%`；目前的 cycle 優勢主要來自 Cortex-A76 上較高的執行效率，
不是整體指令數已經顯著少於 KPQC。

## 2. 比較對象與量測方法

### 2.1 GT new

`GT new` 是目前 `gt_production_default`，實際 feature flags 由
`gt_production_variants.mk` 定義：

```text
GT_PRODUCTION_USE_SCALED_KEYPAIR
GT_PRODUCTION_USE_RMINUS1_DECAP
GT_BASEINV_BATCH_USE_ASM_FINISH
GT_BASEINV_USE_FQINV15_ASM
GT_BASEINV_USE_HIER_K8
GT_BASEINV_USE_HIER_K8_TREE
GT_PRODUCTION_USE_KEYGEN_SAMPLE_NTT_MUL3
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
GT_PRODUCTION_USE_INVNTT_LAZY_TWIDDLE1_LEN16
```

此外，generic forward NTT default 已經是：

```text
G1R123+S2
```

舊 GT forward NTT 仍可用以下 build flag 重建：

```text
GT_PRODUCTION_USE_LEGACY_NTT=1
```

### 2.2 KPQC final

`KPQC final` 直接 link 未修改目錄：

```text
ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768
```

主要 production files 是：

```text
poly.c
asm/ntt.s
asm/base.s
asm/add.s
asm/crepmod3.s
asm/pack.s
asm/cbd.s
```

KPQC final 本身已經不是 naive C baseline。例如它的 `poly_baseinv` 已經使用
closed-form quartic numerator/determinant 加 24-vector batch inversion。因此本文不會
把「closed-form + batch inversion」本身誤寫成 GT 對 KPQC 新增的優化；GT 的差異是
後續的 inverse chain、batch tree、finish ASM 與 scaled-R contract。

### 2.3 Full-KEM benchmark contract

最新三方 benchmark 條件：

```text
host:          Raspberry Pi 5, Cortex-A76
core:          core 3 pinned
hash backend:  portable NO_CE for all variants
NTESTS:        61
NITERATIONS:   2000 calls/sample
NWARMUP:       100
input:         deterministic derand setup
counter:       Linux perf cycle/instruction counter
date:          2026-07-10
```

每個 binary 在量測前都先跑 keygen/encap/decap correctness。表中的「時間」以
`cycles/call` 表示，不換算成 ns；Pi 5 的 DVFS 與實際 clock 會讓 wall-clock
換算增加不必要的不確定性。

### 2.4 本文的 benchmark 證據分級

本文使用三種數據，不能混為同一種比較：

1. `2026-07-10 current three-way`：GT new、GT legacy、未修改 KPQC final 的
   current full-KEM separate-binary 比較。只有這一組用來回答「現在 GT 比 KPQC
   快多少」。
2. `same-binary promotion A/B`：同一 binary、相同 input、交替 call order，
   用來判定 G1R123+S2、SAMPLE-DAG、HIERK8、Q31 等單一變更是否真的移動 cycles。
3. `historical stock logical-stage PMU`：用來解釋 scaled-R、rminus1、support kernel
   的局部方向。這些通常是較早日期或不同 caller contract，不能直接加總，也不能
   當成 current KPQC full-KEM 的逐項分解。

## 3. Current full-KEM benchmark

### 3.1 Cycles

| Operation | KPQC final | GT legacy | GT new | New vs KPQC | New vs legacy |
|---|---:|---:|---:|---:|---:|
| keygen | 39966 | 37982 | 37966 | -5.004% | -0.042% |
| encap | 39013 | 37755 | 37590 | -3.648% | -0.437% |
| decap | 35180 | 32629 | 32482 | -7.669% | -0.451% |

這裡的 `GT legacy` 只把 generic forward NTT 換回舊 GT 版本；SAMPLE-DAG、
HIERK8、Q31、rminus1 與其他 GT production 選項都和 GT new 相同。

keygen 不會呼叫 generic `poly_ntt`，而是走 keygen-only triple NTT。因此 new 與
legacy 的 16-cycle 差不能歸因給 G1R123+S2，應視為 separate-binary layout/cache
差異。

Cycle distribution 很窄：

| Operation | Variant | p10 | p50 | p90 |
|---|---|---:|---:|---:|
| keygen | KPQC final | 39963 | 39966 | 39970 |
| keygen | GT new | 37960 | 37966 | 37973 |
| encap | KPQC final | 39010 | 39013 | 39018 |
| encap | GT new | 37584 | 37590 | 37599 |
| decap | KPQC final | 35179 | 35180 | 35182 |
| decap | GT new | 32476 | 32482 | 32490 |

### 3.2 Retired instructions 與 CPI

| Operation | KPQC instr | GT new instr | GT vs KPQC | KPQC CPI | GT CPI |
|---|---:|---:|---:|---:|---:|
| keygen | 80801 | 81147 | +0.428% | 0.4946 | 0.4679 |
| encap | 103980 | 105124 | +1.100% | 0.3752 | 0.3576 |
| decap | 72677 | 74406 | +2.379% | 0.4841 | 0.4365 |

這是目前結果最重要的判讀：GT new 做的 instruction 比 KPQC 多，但 CPI 較低。
GT 的 Good-Thomas/block-major pipeline 使用更多結構化 vector work，卻能在 A76 上
維持較高 IPC，因此總 cycles 仍較少。

## 4. 三條 KEM production data flow

### 4.1 Keygen

KPQC final 的概念流程：

```text
SHAKE -> cbd1 -> triple (+ e0 for f) -> generic NTT
      -> quartic closed-form/base batch inverse
      -> generic basemul for h and hinv
      -> pack/hash
```

GT new：

```text
SHAKE -> cbd1
      -> SAMPLE-DAG: triple/add1 fused into a dedicated Slothy NTT input DAG
      -> poly_baseinv_scaled_r
           closed-form numerator/determinant
           -> hierarchical k=8 denominator tree
           -> one fqinv15 ASM inverse on the tree root product
           -> ASM finish
           -> inverse output retains the keygen scaled-R contract
      -> poly_basemul_scaled_r_input for h and hinv
           consumes scaled-R inverse
           -> omits a redundant final Montgomery correction
      -> pack/hash
```

Keygen 的主要增量不是 G1R123+S2；是 `SAMPLE-DAG + HIERK8 + scaled-R`。

### 4.2 Encap

```text
hash_f/hash_h
  -> cbd1(r)
  -> G1R123+S2 poly_ntt(r)
  -> tobytes/hash_g/sotp_encode(m)
  -> G1R123+S2 poly_ntt(m)
  -> encap-only direct32 Q31 basemul_add contract
  -> poly_tobytes(ciphertext)
```

Encap 一次使用兩次 generic forward NTT，所以 G1R123+S2 的固定 instruction
減少會出現兩次。Q31 只服務最後立即接 `poly_tobytes` 的 ciphertext boundary。

### 4.3 Decap

```text
frombytes(c, f, hinv)
  -> poly_basemul_rminus1(c, f)
  -> poly_invntt_from_rminus1
  -> poly_crepmod3
  -> G1R123+S2 poly_ntt(m1)
  -> poly_sub
  -> generic poly_basemul(c-m1, hinv)
  -> tobytes/hash_g/sotp_decode
  -> cbd1(r1)
  -> G1R123+S2 poly_ntt(r1)
  -> tobytes/constant-time verify
```

Decap 的第一個 basemul/InvNTT 使用配對的 rminus1 Montgomery contract；後面的
verify basemul 仍需要一般 arithmetic-correct output，不能使用 encap Q31 byte
contract。

## 5. 所有目前 production 優化

### 5.1 Good-Thomas 3 x 32 transform 與 GT block-major layout

GT 把每個 96-point branch transform 分解為互質的 `3 x 32` Good-Thomas 結構：

```text
top split / branch twist
  -> DFT3 (Phase123)
  -> NTT32 Stage12 + Stage345
  -> row-bitrev block-major quartic output
```

最後仍停在 192 個 quartic base blocks，也就是每個 base operation 處理
`X^4 - lambda`；這不是把整個 768-degree ring完全拆成 scalar pointwise products。

Physical block `j` 已經對應 row-bitrev Good-Thomas frequency coordinate，
`gt_rowbitrev_lambda[branch][j]` 也依相同 physical order 排好。這讓後續 basemul、
baseinv 不需要先轉回 GT-natural order。

主要 source：

```text
ntt.c
asm/gt/ntt/poly_ntt.n1.opt.S
asm/gt/ntt/poly_ntt_tables.inc
```

### 5.2 Generic forward NTT: G1 producer/consumer fusion

G1 是目前 generic `poly_ntt` 的主體，重點不是單一 butterfly，而是把原本跨
memory boundary 的 producer/consumer 重新組合：

1. Phase123 的 U01 shared prefix 每個 iteration 只計算一次，再產生三個 row。
2. Stage12 的 block0、block1、block2 output 直接留在 semantic-regalloc 指定的
   vector registers。
3. Stage345 block0/1/2 直接吃這些 live handoff，不把同一批 Q values 先 store
   到 scratch 再 load 回來。
4. block3 因 q0 必須保留 modular constant、31 個 data-capable Q registers 不足，
   仍使用 Stage12 scratch。這是刻意保留的可行 sweet spot，不是假裝 full no-scratch。
5. 三個 row 都放進同一個 self-contained `poly_ntt` symbol；不再透過每-row `bl`
   呼叫切斷整個 producer/consumer schedule。

Production symbol 約 `14904` text bytes，換來較少 dynamic instructions；這也使
full binary text 從 legacy GT 的 `152449` bytes 增加到 `162225` bytes。

### 5.3 R123: Stage345 reduction-tail Slothy scheduling

`R123` 對 G1 的 Stage345 block1、block2、block3 arithmetic/reduction tail 做
schedule-only Slothy 重排：

```text
arithmetic semantics: unchanged
reduction semantics:  unchanged
layout/scatter:        unchanged
register assignment:  validated
```

block0 的 inherited live-in/stack-handoff window無法在 hard constraints 下穩定求解，
所以 production 保留原 G1 block0，而不是硬塞一個 spill candidate。

### 5.4 S2: high-half `umov + str`

Stage345 final scatter 原本有很多：

```asm
ext  vtmp.16b, vsrc.16b, vsrc.16b, #8
str  dtmp, [addr]
```

S2 在 register/liveness audit 證明安全的 site 改成：

```asm
umov xTmp, vsrc.d[1]
str  xTmp, [addr]
```

兩者在 little-endian AArch64、8-byte store、相同 address 下語意等價。R123+S2
每個 row 有 28 個 safe replacement，另有 4 個 site 因 contract/liveness 原因保留
原 `ext+str`。`xTmp` 都是 caller-saved、site 前後 dead，而且不 alias address、
state 或 twiddle registers。

### 5.5 G1R123+S2 的實際收益

最可信的增量證據是 same-binary legacy/new paired harness：

| Scope | legacy p50 | G1R123+S2 p50 | paired delta p50 | instruction delta | win rate |
|---|---:|---:|---:|---:|---:|
| encap NTT r | 2692.752 | 2646.128 | -45.294 | -263 | 61/61 |
| encap NTT m | 2692.560 | 2645.751 | -45.767 | -263 | 61/61 |
| decap NTT m1 | 2690.608 | 2645.740 | -44.489 | -263 | 61/61 |
| decap NTT r1 | 2690.883 | 2645.751 | -44.977 | -263 | 61/61 |
| full encap | 37718.332 | 37614.476 | -106.243 | -526 | 61/61 |
| full decap | 33315.364 | 33225.502 | -88.853 | -526 | 61/61 |

full KEM 的 cycle movement 大致符合「每次 KEM 兩個 generic NTT」的預期。
candidate 的 L1I refill 略增，但 backend stalls 下降；目前收益不是 function
alignment 偶然造成。

### 5.6 Keygen SAMPLE-DAG: 把 triple/add1 融入 NTT input DAG

KPQC/一般 keygen 會先 materialize：

```text
poly_triple(a)
optional coeff[0] += 1
poly_ntt(a)
```

GT keygen 專用 symbol 改為：

```text
poly_ntt_mul3(a)      = NTT(3*a)
poly_ntt_mul3_add1(a) = NTT(3*a + e0)
```

這不是單純 C wrapper。input scaling 和 add1 已進入新的 Phase123 symbolic DAG，
再由 Slothy 一起排程；後段仍接既有 NTT32 row kernels。它只用於 keygen，不取代
generic `poly_ntt`。

Promotion same-binary data：

| Window | old | SAMPLE-DAG | delta |
|---|---:|---:|---:|
| post-CBD sample path x2 | 6367 | 6046 | -321 cycles |
| full keygen | 38777 | 38469 | -308 cycles |

### 5.7 Baseinv: 在 KPQC batch inverse 上再做的優化

KPQC final 已經做：

```text
8-way closed-form quartic numerator/determinant
24 denominator vectors
one batch inversion tree
finish numerator * denominator^-1
```

GT 沿用相同數學策略，但 production keygen path增加四件事。

#### A. 15-multiply `fqinv` ASM chain

KPQC `poly.c` 的 `fqinv_neon` 是 16 次 `fqmul_neon` exponentiation chain。
GT 使用：

```text
asm/gt/baseinv/poly_baseinv_fqinv15.S
symbol: gt_fqinv15_asm
```

以 15 次 modular vector multiply 完成 field inverse，再做 final Montgomery
normalization。這是 production linked ASM，不是 C prototype。

#### B. Hierarchical k=8 denominator tree

24 個 denominator vectors 分成：

```text
8 groups x 3 vectors
```

每組先形成 group product，再對 8 個 group products 做 tree batch inverse，最後把
inverse 分配回每組三個 denominator。它仍只有一次真正的 `fqinv15`，不是做八次
scalar inversion。

不同 multiplication order 可能得到不同 int16 representative，但 KEM pk/sk byte
differential 已通過，因此 production 不額外插入每步 canonicalization。

#### C. HIERK8 tree scheduling

`GT_BASEINV_USE_HIER_K8_TREE` 選擇固定 8-group tree shape，減少一般 flat prefix/
suffix chain 的 dependency 與 instruction cost。tree 本身目前是 C/NEON；真正的
inverse core 與 finish loop 是 ASM。

#### D. ASM finish

`baseinv_batch_finish24_n1_asm` 批量完成 24 個 quartic numerator 與 denominator
inverse 的正負號乘法，取代逐 block C/NEON finish loop。

HIERK8 promotion same-binary data：

| Window | old flat | HIERK8 tree | delta |
|---|---:|---:|---:|
| scaled baseinv x2 | 9419 | 9231 | -188 cycles |
| full keygen | 38777 | 38599 | -178 cycles |

SAMPLE-DAG + HIERK8 一起使用時：

```text
full keygen 38777 -> 38294 cycles, delta -483 cycles
```

兩個 local delta 不應直接相加當成任何新環境的預測；上面的 `-483` 是實際組合
same-binary full-keygen measurement。

### 5.8 Scaled-R keygen contract

GT keygen 使用：

```text
poly_baseinv_scaled_r
poly_basemul_scaled_r_input
```

base inverse output 刻意保留一個適合下一個 basemul 的 Montgomery scale。一般
basemul 內部會得到 `a*b*R^-1`，再做 final correction；當第二個 operand 已經是
`b*R` 時，raw product 已經是正常 `a*b`，因此 `poly_basemul_scaled_r_input` 可以
省掉 final correction。

這是跨 kernel 的 contract 優化，不是兩個 ABI-compatible kernel 的單獨替換。
歷史 production-vs-stock logical-stage PMU：

```text
keypair basemul x2: 5284.328 -> 4076.917 cycles, -22.8%
```

### 5.9 GT basemul / basemul_add 8-way quartic pipeline

GT block-major memory 一次放 8 個 quartic products。production basemul body 用：

```text
ld4:  從 8 個 interleaved quartic blocks 取出 a0/a1/a2/a3 vectors
NEON: 同時計算 8 個 X^4-lambda quartic products
st4:  把四個 coefficient vectors 交錯回 block-major memory
```

shared body 是 Slothy-scheduled ASM。`poly_basemul_add` 則把 one-stripe generated
body直接 include 在 24-iteration loop 中，避免每個 stripe 額外 `bl/ret`。

主要 files：

```text
asm/gt/basemul/poly_basemul_body.inc
asm/gt/basemul/poly_basemul.S
asm/gt/basemul/poly_basemul_add.S
asm/gt/basemul/poly_basemul_add.n1.opt.inc
```

必須注意：generic GT basemul 並不是每個 isolated ABI 都比 KPQC/stock 快。歷史
logical-stage PMU 中，decap verify 的 generic basemul 約慢 7%；GT 的總收益來自
rminus1、scaled-R、Q31 等 caller-specific contracts，而不是宣稱 generic kernel
全面勝出。

### 5.10 Encap-only direct32 Q31 byte contract

一般 `poly_basemul_add` 必須產生 arithmetic-correct centered int16 polynomial。
encap 的結果卻只會立即進入 `poly_tobytes`，因此 GT 為這一個 boundary 建立較窄
的 byte-equivalence contract：

```text
quartic 32-bit accumulator P + c
  -> Q31 signed reduction with C=621199 for q=3457
  -> int16 output acceptable to immediate poly_tobytes
```

它省掉 generic product Montgomery fold/add32 finalizer 的一部分工作，但不允許：

```text
替代 generic poly_basemul_add
供 decap arithmetic consumer 使用
把 output 當作一般 centered representative
```

Promotion evidence：

| Window | generic path | Q31 path | delta |
|---|---:|---:|---:|
| direct basemul_add | 2902.047 | 2486.768 | -415.279 cycles (-14.3%) |
| full encap | 38804.372 | 38336.448 | -467.924 cycles (-1.21%) |

full encap 只改善約 1.2%，因為 encap 大部分時間仍在 SHAKE/hash 與兩個 NTT。

### 5.11 Decap rminus1 basemul/InvNTT contract

第一個 decap product 不需要先變成一般 Montgomery-normalized polynomial再進
InvNTT。GT 使用：

```text
poly_basemul_rminus1
  -> output 保留額外 R^-1
poly_invntt_from_rminus1
  -> final branchfold constant table 吸收 R^-1
  -> normal R^0 representative
```

這省掉 basemul 的 final correction，同時維持 `poly_crepmod3` 需要的 signed
representative contract。歷史 logical-stage PMU：

```text
first decap basemul: 2639.695 -> 2028.098 cycles, -23.2%
```

單獨 GT rminus1 InvNTT 在同一份舊 PMU 中約比 stock InvNTT 慢 1.6%，但前面的
rminus1 basemul 節省較大，因此配對 data flow 才是正確的比較單位。

### 5.12 InvNTT production pipeline

normal 與 rminus1 wrapper共用 `poly_invntt.n1.opt.inc`，active path 包含：

1. 直接從 physical block-major input load，不先 gather 完整 row。
2. Stage123 output直接寫成 Stage45 consumption order 的 stripe scratch。
3. Stage45 arithmetic 與 row-end Barrett reduction fuse，並使用 Slothy schedule。
4. post DFT3 不做一輪中間 reduction。
5. untwist、branch merge、final scaling 合併進 branchfold constant table。
6. final store 前做 output reduction，保證 `poly_crepmod3` representative contract。
7. rminus1 wrapper只切換 branchfold constants，不複製另一套 inverse pipeline。

主要 files：

```text
asm/gt/invntt/poly_invntt.S
asm/gt/invntt/poly_invntt_rminus1.S
asm/gt/invntt/poly_invntt.n1.opt.inc
```

這些優化主要是讓 GT inverse pipeline 自己不被 gather、分離 reduction 與 final
scale 拖慢；它不是目前 GT 相對 KPQC 最大的 isolated win。

### 5.13 Support kernels

目前 GT production link：

```text
asm/gt/support/poly_support.n1.opt.S
asm/gt/support/poly_cbd_sotp.S
```

`poly_support.n1.opt.S` 包含 Slothy/N1 排程的：

```text
poly_sub
poly_triple
poly_crepmod3
poly_frombytes
poly_tobytes
```

`poly_cbd_sotp.s` 提供：

```text
poly_cbd1
poly_sotp_encode
poly_sotp_decode
```

歷史 direct substage comparison 顯示：

```text
tobytes / hash_g input packing: 約 -12% 到 -13%
frombytes:                      約 -4.6% 到 -8.4%
crepmod3:                       約 -3.1%，但總共只有約 383 cycles
SOTP encode/decode:             幾乎持平
```

因此 support ASM 有穩定的小收益，但不是 full KEM 差距的主要來源。

## 6. 每項優化的 production status 與已知收益

| 優化 | 使用路徑 | 做法摘要 | 最可信的已知收益 | Production |
|---|---|---|---:|---|
| GT 3x32 row-bitrev layout | 所有 GT arithmetic | 96-point Good-Thomas，quartic block-major | 整體 pipeline 基礎，不能單獨歸因 | yes |
| G1 live handoff | generic forward NTT | Stage12 block0-2 直接交給 Stage345 | 包含在每 NTT 約 -45 cycles | yes |
| R123 | generic forward NTT | Slothy 排 block1-3 reduction tails | 包含在每 NTT 約 -45 cycles | yes |
| S2 | generic forward NTT | safe `ext+str` 改 `umov+str` | 包含在每 NTT 約 -45 cycles | yes |
| SAMPLE-DAG | keygen only | triple/add1 進 Phase123 symbolic DAG | full keygen -308 cycles | yes |
| fqinv15 ASM | keygen baseinv | 15-multiply inverse chain | linked current backend；無單獨 current full-KEM delta | yes |
| HIERK8 tree | keygen baseinv | 24 den = 8 groups x 3 | full keygen -178 cycles | yes |
| SAMPLE + HIERK8 | keygen | 上述兩者組合 | full keygen -483 cycles | yes |
| scaled-R | keygen public arithmetic | baseinv output scale 給 basemul，省 final correction | basemul x2 歷史 -22.8% | yes |
| Q31 direct32 | encap only | byte-contract reduction | full encap -468 cycles (-1.21%) | yes |
| rminus1 | decap first product | basemul 留 R^-1，InvNTT constants補回 | first basemul 歷史 -23.2% | yes |
| InvNTT fused path | decap | stripe scratch、stage45 reduce fusion、branchfold | GT internal optimization；isolated vs stock非主要 win | yes |
| support N1 ASM | all KEM paths | pack/unpack/sub/crepmod3 scheduling | pack約 -12% 到 -13% | yes |

## 7. 目前不是 production 的路線

下列內容不應算進「GT new 相對 KPQC final」的 production 優化：

```text
NTT32 row-specialized / shadow-base candidates
Candidate A direct-tuple / tuple TMVP experiments
U01 E/G/H 中未被 G1 production吸收的 candidates
full F0123 live-all allocator (register deficit)
twiddle=1 lazy-reduction semantic candidates
st1 high-half lane variant
S4 audited appendix candidate
InvNTT row-buffer/post prototypes
basemul -> InvNTT stage123scratch split prototype
crepmod3 fused InvNTT
flat k-way extra-inversion baseinv
delta-divstep baseinv backends
decap verify direct byte finalizer prototypes
```

其中一d釋。

## 8. Correctness 與 release gates

目前 GT new 的重要 gates：

```text
G1R123+S2 full poly_ntt differential: pass
G1R123+S2 ABI sentinel:              mask 0x0
same-binary paired KEM mismatches:    0 / 2562 checks
SAMPLE-DAG/HIERK8 release guard:      pass
Q31 release guard:                    pass
Q31 arithmetic misuse call sites:     0
scheme KEM test:                      count 0
100k KEM regression:                  count 0
```

promoted G1R123+S2 與 legacy GT 的 deterministic KAT response byte-for-byte
相同：

```text
PQCkemKAT_2336.rsp SHA-256
dca76b32748655990289002a05f7b1d648334d7ded05845c7fe3f1449d26690f
```

## 9. Active production source index

Build/source-of-truth：

```text
Makefile
gt_production_variants.mk
kem.c
```

Forward NTT：

```text
asm/gt/ntt/poly_ntt.n1.opt.S
asm/gt/ntt/poly_ntt_tables.inc
asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S          # legacy/sample row-kernel dependency
```

Keygen sample NTT：

```text
asm/gt/ntt/poly_ntt_mul3.S
asm/gt/ntt/poly_ntt_mul3_add1.S
experiments/keygen_sample_ntt_fusion/gt_frontend_mul3/
```

注意：這兩個 file 仍在 `asm/gt/experiment/`，而檔頭註解也保留早期
benchmark-only 說法；但現在 Makefile確實會把它們 link 進 production default。
判定 production identity 時以 Makefile 與 `gt_production_variants.mk` 為準。

Inverse NTT：

```text
asm/gt/invntt/poly_invntt.S
asm/gt/invntt/poly_invntt_rminus1.S
asm/gt/invntt/poly_invntt.n1.opt.inc
```

Base inverse：

```text
poly_gt_baseinv_batch.c
asm/gt/baseinv/poly_baseinv_fqinv15.S
asm/gt/baseinv/poly_baseinv_batch_finish.n1.opt.S
```

Base multiplication：

```text
asm/gt/basemul/poly_basemul_body.inc
asm/gt/basemul/poly_basemul.S
asm/gt/basemul/poly_basemul_add.S
asm/gt/basemul/poly_basemul_scaled_r_input.S
asm/gt/basemul/poly_basemul_rminus1.S
asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.S
```

Support：

```text
asm/gt/support/poly_support.n1.opt.S
asm/gt/support/poly_cbd_sotp.S
```

## 10. Benchmark 與重現入口

Current 三方 raw results：

```text
aarch64-bench/results/gt_production_g1r123s2_threeway/summary.md
aarch64-bench/results/gt_production_g1r123s2_threeway/summary.json
```

G1R123+S2 same-binary paired results：

```text
aarch64-bench/results/u01v3_g1_r123_paired_kem/summary.md
aarch64-bench/results/u01v3_g1_r123_paired_kem/summary.json
```

主要 production benchmark command：

```sh
cd ntruplus-ntt-Optimized/aarch64-bench

make -B bench VARIANT=gt_production_default \
  BENCH_MODE=kem_keygen CYCLES=PERF NTESTS=61 NITERATIONS=2000 NWARMUP=100

make -B bench VARIANT=gt_production_default \
  BENCH_MODE=kem_enc CYCLES=PERF NTESTS=61 NITERATIONS=2000 NWARMUP=100

make -B bench VARIANT=gt_production_default \
  BENCH_MODE=kem_dec CYCLES=PERF NTESTS=61 NITERATIONS=2000 NWARMUP=100

make -B bench VARIANT=kpqc_final \
  BENCH_MODE=<kem_keygen|kem_enc|kem_dec> \
  CYCLES=PERF NTESTS=61 NITERATIONS=2000 NWARMUP=100
```

執行時仍要用 `taskset -c 3` pin 到同一個 Pi 5 core，並確保兩邊都維持
`USE_SHAKE_ASM=0`，否則這份比較就不再是同一個 hash backend。

## 11. 現況判讀

目前能確定的事：

1. GT new 對 KPQC final 的 full-KEM cycle win 是真實且穩定的，範圍約
   `3.6%` 到 `7.7%`。
2. keygen 的主要 GT-specific 收益來自 SAMPLE-DAG、HIERK8 與 scaled-R。
3. encap 的 arithmetic 收益主要來自兩次 forward NTT 加 Q31 byte contract，
   但 hash 仍占大部分時間。
4. decap 的主要 GT-specific 收益來自 rminus1 first product、兩次 forward NTT
   與整體 GT base pipeline。
5. generic basemul、InvNTT、baseinv並非每個 isolated window 都勝過 KPQC；
   caller-specific scale/layout contract 才是 GT 整體變快的關鍵。
6. 距離 20% 目標仍有明顯差距。只再省幾十 cycle 的 NTT/store peephole 不足以
   把 3.6%-7.7% 推到 20%；後續若仍鎖定 polynomial path，需要更大的 algorithm/
   cross-kernel change，或重新評估 hash backend 在完整 KEM 中的占比。
