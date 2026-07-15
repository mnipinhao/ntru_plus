# NTRU+768 AVX2 Good–Thomas forward-NTT prototype

這個目錄包含 opt-in、可差分驗證的 AVX2 GT intrinsic baseline，以及 Linux ELF
上的 hybrid 手寫組語 prototype。Hybrid 版本保留 intrinsic frontend 和 NTT32
stage 1+2，將 stage 3+4+5、packed Barrett、transpose 與 16-block SoA store 放進
`gt_ntt_stage345_soa.s`。它沒有取代上層 `asm/ntt.s`，而且新的 SoA layout 還沒有
對應的 AVX2 `basemul`/`invntt`。

## 數學分解

環是

```text
R_q = Z_3457[X] / (X^768 - X^384 + 1).
```

流程分成：

```text
top split (768 -> 2 x 384)
  -> 每個 branch 拆成四條 stride-4、長度 96 的 stream
  -> branch twist，變成 cyclic NTT96
  -> Good–Thomas 96 = 3 x 32
  -> DFT3
  -> radix-2 CT NTT32（natural input -> bit-reversed output）
  -> GT CRT scatter
```

Top split 對 `i=0..383` 是：

```text
t             = Mont(a[i+384], -1033)
branch0[i]    = a[i] + t
branch1[i]    = a[i] + a[i+384] - t
```

對每個 branch 的 `k=0..95`，四個 `a[4k+lane]` 共用同一個 twist。
八條自然 stream 的固定 lane 編號是：

```text
s0..s3 = branch0 lane0..3
s4..s7 = branch1 lane0..3
```

Good–Thomas input CRT mapping 是：

```text
n = (64*n3 + 33*n32) mod 96.
```

每個 `n32` 和 stream 各有三個輸入 `x0,x1,x2`。DFT3 用一個 Montgomery
乘法完成：

```text
d  = x1 - x2
t  = Mont(d, omega3), omega3=-886
r0 = x0 + x1 + x2
r1 = x0 - x2 + t
r2 = x0 - x1 - t
```

三個結果是三條 NTT32 row；`row0/row1/row2` 因此是 DFT3 的輸出，不是
NTT32 stage 才產生的名稱。

## Frontend packing

AVX2 一個 YMM 有 16 個 int16 lane，但自然 batch 只有八條 stream。Frontend
每次一起算兩個 `n32` slot `Q`、`Q+1`：

```text
DFT3 R0 YMM = [ row0.Q.s0..s7 | row0.(Q+1).s0..s7 ]
DFT3 R1 YMM = [ row1.Q.s0..s7 | row1.(Q+1).s0..s7 ]
DFT3 R2 YMM = [ row2.Q.s0..s7 | row2.(Q+1).s0..s7 ]
```

兩個 `vperm2i128` 把前兩條 row 轉成：

```text
row01[Q]   = [ row0.Q.s0..s7     | row1.Q.s0..s7 ]
row01[Q+1] = [ row0.(Q+1).s0..s7 | row1.(Q+1).s0..s7 ]
```

`R2` 則拆成兩個 XMM，先存成 `row2[Q]`、`row2[Q+1]`。所以「packed row2」
不是宣稱 row2 有不同的數學性質；它只是 `row0/row1` 成對後留下的 singleton。

## NTT32 stage 1+2：stripe producer

CT stage 1 的 distance 是 16，stage 2 是 8。對每個 `q=0..7`，一個 row01
stripe 只載入四個 YMM：

```text
Q=q, q+8, q+16, q+24.
```

先完成 distance-16 butterfly，再完成 distance-8 butterfly，立即把四個 stage-2
結果寫回 canonical Q slot。Stage 1 的 twiddle是 Montgomery `R=-147`。它在
模 q 意義下是單位元，但這個 Montgomery multiplication 仍負責把 lazy high
operand 降回一個 modulus，所以不能直接刪除。Stage 2 的兩組 twiddle 分別是
`R` 與 `omega32^8=366`，其中 `R` 同樣保留 reduction 作用。

singleton row2 在這裡第一次裝滿 YMM。Stage 1 將 `Q`、`Q+16` 的兩個 XMM
結果合成：

```text
P[q] = [ row2.stage1.Q.s0..s7 | row2.stage1.(Q+16).s0..s7 ].
```

接著 stage 2 對 `P[q]`、`P[q+8]` 做 YMM butterfly。低 128-bit half 使用
原始 `Q` 的 twiddle，高 half 使用原始 `Q+16` 的 twiddle；因此 singleton 的
twiddle 本身也是 `[twiddle_low x8 | twiddle_high x8]`。

具體 toy example：stage1+2 的 stripe `q=5` 讀 `Q={5,13,21,29}`。完成後
`row2_packed[5]` 的低 half 是 stage-2 `Q=5`，高 half 是 stage-2 `Q=21`；
`row2_packed[13]` 則是 `Q=13 | Q=29`。

## NTT32 stage 3+4+5：8-vector block consumer

Stage 3、4、5 的 distance 是 4、2、1，因此 stage 2 之後可以一次只保留一個
八向量 block：

```text
row01 blocks:       base = 0, 8, 16, 24
row2 packed blocks: base = 0, 8
```

每個 block 明確展開成八個 YMM local，依序做 4、4、4 個 butterfly，再存回。
row01 的兩個 128-bit half 是不同 row、相同 Q，所以 twiddle 相同；row2 packed
的兩個 half 是相差 16 的 Q，所以每個 butterfly 要載入兩個不同 twiddle。

這個 stage boundary 同時是資料相依方向的轉折：stage1+2 的 producer 是
`q,q+8,q+16,q+24` stripe，stage3+4+5 的 consumer 是連續八個 Q。用 1.5 KiB
stage2 scratch 做明確 transpose，比讓 register allocator 猜跨 boundary 的 live
range 更容易驗證，也更適合之後切成 scheduler region。

Hybrid ASM 對每一 stage 的四個 Montgomery butterfly 依下列順序交錯排程：

```text
4 x vpmullw
4 x vpmulhw(product high)
4 x vpmulhw(correction)
4 x vpsubw(Montgomery result)
4 x butterfly subtract
4 x butterfly add
```

八個資料向量固定佔 YMM0..YMM7，四個暫存佔 YMM8..YMM11；high operand 在兩個
product half 都發出後才 destructive overwrite。整個 ASM symbol 不使用 stack，
也沒有 spill/reload。

## 16-block SoA output

每個 terminal block 有四個係數 `c0..c3`。令 `k3=0..2` 是 DFT3 row、
`Q=0..31` 是 NTT32 slot、`branch=0..1`，則 ASM output 的精確 mapping 是：

```text
batch       = 4*k3 + floor(Q/8)       // 12 batches
lane        = 8*branch + (Q mod 8)    // 16 blocks per batch
output word = 64*batch + 16*c + lane
```

所以每個 batch 的 64 words 正好是四個 YMM：

```text
YMM0 = c0 of [branch0 Q0..Q7 | branch1 Q0..Q7]
YMM1 = c1 of [branch0 Q0..Q7 | branch1 Q0..Q7]
YMM2 = c2 of [branch0 Q0..Q7 | branch1 Q0..Q7]
YMM3 = c3 of [branch0 Q0..Q7 | branch1 Q0..Q7]
```

這裡的 `Q0..Q7` 是該 batch 的八個 Q；下一個 batch 是 Q8..Q15。和既有 GT
row-bitrev layout 的關係是：

```text
j = (32*k3 + 3*Q) mod 96
soa[64*batch + 16*c + lane] = rowbitrev[384*branch + 4*j + c]
```

最後一個 block 內先做 lane-local 8x8 int16 transpose。兩個 128-bit half 各自
transpose，因此不需在 transpose 中跨 half；之後用八個 `vperm2i128` 把 stream
`c` 與 `c+4` 的 half 配成四個 SoA YMM，直接 store，不另做 768-coefficient
transpose pass。

## Montgomery 與 Barrett 的 AVX2 指令

固定因子 `b` 的 16-bit Montgomery multiplication 使用 `B=b*qinv mod 2^16`：

```text
hi         = signed_mulhi(a, b)
correction = signed_mulhi(mullo(a, B), q)
result     = hi - correction
```

對應主要是 `vpmullw`、`vpmulhw`、`vpsubw`。Frontend 的 top-split、twist 與
DFT3 omega 已走 fixed-factor 版本；一般 NTT32 butterfly baseline 仍在 intrinsic
內算 `B`，之後組語版應把 `(b,B)` 一起預先排進 twiddle table。

Intrinsic row-bitrev path 最後把 lazy NTT 值 sign-extend 成 int32，使用
`vpmulld`、加 rounding、`vpsrad` 做 reference-compatible Barrett，再以
`vpackssdw` 壓回 int16；其 range 是 `[-1729,1729]`。

ASM SoA path 使用 packed int16 checkpoint：

```text
t = (vpmulhw(a, 19412)) >> 10
r = a - t*3457
```

對完整 lazy interval `[-27648,27648]` exhaustive 驗證後，`r` 與輸入 modulo q
相同且落在 `[0,3457]`。因此兩條 path 的 exact representative 不一定相同，測試
以 modulo q 比較。

其他關鍵指令/動作：

- XMM 的八條 stream 由 `vpunpcklqdq` 組成。
- 兩個 slot 以 `vinserti128` 填滿 YMM。
- DFT3 後 `vperm2i128` 建立 `row01`。
- Intrinsic path 因 AVX2 沒有 int16 scatter，最後把八條 stream 拆成兩組四 lane，
  依公開的 `physical=(32*k3+3*k32) mod 96` 做固定位置 store。
- ASM path 則以 lane-local unpack 和 `vperm2i128` 直接形成連續 SoA store。

## Range 與 constant-time

目前明確 precondition 是 `|a[i]| <= q-1`。Twist 後回到一個 modulus 的 bound；
DFT3 是 `3(q-1)`，五個 lazy NTT32 stage 每層最多再增加 `q-1`，最終
`8(q-1)=27648 < 32768`。完整推導在 `range-proof.md`。

所有 branch、table index 和 memory address 都只依賴公開 loop index；沒有
secret-dependent branch 或 lookup。Prototype wrapper 在 stack 上配置兩個 1.5 KiB
scratch，共 3 KiB。正式版本要再決定 caller-provided scratch、覆寫時機與是否清除
secret stack data。

## Register pressure 現況

設計上的目標 budget 是：

```text
8 long-lived data YMM
2 q / Montgomery constants
2 twiddle constants
4 transient temporaries
= 16 architectural vector registers.
```

Clang 產生的 stage1+2 目前沒有觀察到 vector spill/reload；手寫 ASM
stage3+4+5 正好把八個 data vector 保持在 register，而且 linked symbol 已確認
沒有 stack access。Frontend 則仍會因為六次
CRT-indexed load、twist construction 和 inlining 產生 stack spill/reload。這不是
數學 layout 必然要求的 spill，而是下一輪應優先處理的 code-generation 問題：

1. 預先打包 `(twist, twist*qinv)`，避免 runtime `setr` 與 factor 建構。
2. 預先打包 GT input mapping，減少 `%96` address arithmetic。
3. 把「一個 slot-pair frontend」抽成固定 symbolic region，再排 live range。
4. 比較 `row01 + packed row2` 和改配對 `row12 + packed row0`，但不改數學輸出。

## Slothy handoff

本機 Slothy checkout 的 core 雖然 architecture-agnostic，目前只有 Arm
architecture/target model，沒有 x86/AVX2 model。因此現在不能誠實地宣稱這份
AVX2 已經是 Slothy candidate，也不能直接拿 AArch64 Neon model 來排。

這個目錄依 `new_kernel_baseline_then_iterate` 的 gate 方式準備：

- `kernel-contract.yml`：ring、I/O、layout、range、constant-time 與 scratch。
- `baseline-contract.yml`：reference、驗證 gate、production replacement scope。
- `instruction-dag.yml`：frontend pair、stage12 stripe、stage345 block、scatter DAG。
- `gt_ntt_avx2.c`：可執行的 intrinsic semantics baseline。
- `gt_ntt_stage345_soa.s`：依 DAG 手排的 stage3+4+5 與 fused SoA store。
- `asm-soa-contract.yml`：hybrid ASM boundary、ABI、layout 與 output range。

之後要走 Slothy，合理順序是先補 x86 architecture model（instruction semantics、
latency/throughput、port model、register class），再把下列 region 各自抽成 symbolic
assembly，而不是一次排完整 768-point function：

1. one frontend slot-pair；
2. row01 stage1+2 stripe；
3. singleton stage1+2 stripe；
4. row01 stage3+4+5 block；
5. singleton stage3+4+5 block。

每個 region 都要保留既有 boundary test，檢查 ABI、stack alignment、callee-saved
register、spill、constant table address 和 modulo-q differential correctness；排程成功
不等於可以跳過語意驗證。

## 驗證與執行

在這個目錄執行：

```sh
make test
make check
make sanitize
make asm
```

macOS arm64 會用 `clang -arch x86_64` cross-compile intrinsic path，並透過 Rosetta
執行；GNU ELF ASM path 目前只在 Linux x86-64 build 啟用。
測試包含：

- 1000 組、16 lanes 的 scalar/AVX2 Montgomery exact comparison；
- 對完整 lazy range `[-27648,27648]` 的 exhaustive Barrett comparison；
- 對同一完整 lazy range 的 packed ASM Barrett modulo/range exhaustive test；
- frontend `row01/row2` packing differential；
- stage2 `row01/row2_packed` differential；
- impulse、boundary 與 200 組完整 random polynomial 對 AArch64 portable GT
  reference 的 modulo-q differential；
- 768-word SoA mapping 的 forward/inverse exact round trip；
- hybrid ASM SoA 對 mapping oracle 的 modulo-q differential 與 `[0,q]` range；
- intrinsic 與 ASM 的 in-place `out==in`；
- ASan/UBSan 可另外套在同一個 test binary。

Ryzen 7 9700X 的 preliminary run（CPU 2 pinned、boost on、SMT sibling 未隔離）中，
hybrid ASM SoA 的 serialized-TSC median 是 983，intrinsic GT 是 1476，約降低
33.4%。Production forward NTT 是 444，所以目前主要剩餘成本仍在 intrinsic
frontend/stage1+2，而不是把 prototype 直接升格成 production kernel。
