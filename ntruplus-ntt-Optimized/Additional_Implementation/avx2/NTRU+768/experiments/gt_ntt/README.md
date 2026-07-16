# NTRU+768 AVX2 Good–Thomas NTT and pointwise prototype

這個目錄包含 opt-in、可差分驗證的 AVX2 GT intrinsic baseline，以及 Linux ELF
上的手寫組語 prototype。`gt_ntt_frontend_stage12_soa.S` 以 generated mapping/twist
table 手排 frontend 與 NTT32 stage 1+2，除 canonical single-entry producer 外，也
保留 zero/half-handoff benchmark candidates。`gt_ntt_stage345_soa.s` 提供 canonical
stage 3+4+5、packed Barrett、transpose、16-block SoA store，以及四個同語意 schedule
candidates。它們都沒有取代上層 `asm/ntt.s`。`gt_basemul_soa.c` 提供
AVX2 intrinsic pointwise baseline；`gt_invntt_soa.c` 已能直接消費相同 SoA、完成
inverse 與 full polynomial multiplication。`gt_invntt_ntt32_soa.s` 已手排 inverse
NTT32 region，`gt_invntt_dft3_soa.s` 已手排 inverse DFT3/checkpoint region；最後的
`gt_invntt_postprocess_soa.s` 已手排 untwist/merge/store region。三段目前仍由 C
wrapper 分開呼叫；`gt_invntt_fused_soa.S` 另外提供單一 ASM entry 做融合比較。
它仍是 opt-in prototype，沒有取代 production ASM。

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

### Hand-scheduled frontend

`generate_gt_frontend_tables.py` 把每個 slot-pair 所需的資料預先排成：

```text
input byte offsets:       16 pairs x 6 uint16 = 192 bytes
twist/qinv/factor table:  16 pairs x 3 rows x 32 int16 = 3072 bytes
```

同一個 generator 另產生等大小的 stripe-order tables：

```text
A(q)=(q,q+16), B(q)=(q+8,q+24), q=0..7
gt_frontend_stripe_input_byte_offset[16][6]     = 192 bytes
gt_frontend_stripe_twist_qinv_factor[16][3][32] = 3072 bytes
```

Canonical table 的六個 offset 依序是三個 `n3` 的 `(Q,Q+1)`；stripe table 則是
同樣三組 `(Q_a,Q_b)`，但 pair 由上述 A/B order 決定。每個 offset 都已包含
`8*((64*n3+33*Q) mod 96)`，所以 hot loop 不做除法、乘 33 或 `%96`。對任一
table-selected pair，每個 64-byte twist entry 是：

```text
[twist*qinv for Qa,Qb] | [twist for Qa,Qb]
```

其中每個 128-bit half 又是 `[branch0 x4 | branch1 x4]`。因此兩個 slot 能從
一開始就以一個 YMM 做完全相同的運算，不需要 runtime `setr` 或 scalar
`factor*qinv`。

一輪同時載入三組 low/high YMM，接著交錯發出三條 top-split Montgomery chain：

```text
3 x vpmullw(high, zeta*qinv)
3 x vpmulhw(high, zeta)
3 x vpmulhw(correction, q)
3 x Montgomery subtract
```

之後立即形成 branch0/branch1、做三條 twist chain，再利用 DFT3 Montgomery
latency 同時算 `x0+x1+x2`、`x0-x2`、`x0-x1`。輸出立即 transpose/store，不跨
slot-pair 保留 live value。Standalone frontend 使用全部 16 個 architectural
vector register，但 linked symbol 沒有 stack access 或 call。

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

手排 stage1+2 一次只保留上述一個 stripe。Stage 1 的兩條 identity-Montgomery
chain 一起發出；stage 2 的 identity 與 `omega32^8` chain 也交錯發出。row01
寫回後立即重用相同 data/temporary registers 處理 row2，七個常數固定留在
YMM9..YMM15，不再由 GCC 放到 stack/red-zone。這個 standalone linked symbol
同樣沒有 stack access 或 call。

`gt_ntt_avx2_frontend_stage12_asm` 把兩個 region inline 在同一個 ASM entry，擁有
一個 1536-byte、32-byte aligned frontend scratch，沒有 internal call、push、pop，
且只有尾端一個 `vzeroupper`。這個 scratch 是 row01/row2 的數學 boundary，不是
register spill。完整 input 在 stage1+2 寫回前已進 scratch，所以 `out==in` 安全。

另外實作兩個 benchmark-only handoff candidate。`direct` 將 table 改成每個
`q=0..7` 依序產生 stripe pair A=`(q,q+16)`、B=`(q+8,q+24)`；A 的三條
stage-1 結果保留在 YMM13..YMM15，B 算完後立即完成三條 stage 2，直接寫入
stage2 scratch，因此 frontend semantic handoff 是 0 bytes。`half` 使用相同
stripe-first schedule，但先把 A 的三個 YMM 暫存在它們最後會佔用的 stage2
slot，等 B 完成後 reload；它的 semantic handoff 是 768-byte store 加 768-byte
reload，而不是原本 1536-byte store 加 1536-byte reload。

兩個 low-level entry 都不碰 stack、沒有 call，並要求 1536-byte stage2 output 與
768-coefficient input 完全不重疊。Public wrapper 仍用私有 stage2 scratch，所以
對 caller 保留 `out==in`。算術 checkpoint 不變：DFT3、stage 1、stage 2 仍分別
界在 `3(q-1)`、`4(q-1)`、`5(q-1)`，沒有多插 Barrett reduction。最後以 Ryzen
7 9700X、每個 perf process 1,000,000 perf-loop iterations、forward/reverse
sequential order 各十回確認：
canonical 的 amortized cycles/iteration 是 425.40/425.71，`direct` 是
497.41/497.49，`half` 是 499.46/499.48；
也就是 direct 慢 16.86%--16.93%，half 慢 17.33%--17.41%。原因是 stripe-first
packing、跨 128-bit half 組合及更緊的 live range 成本大於 1.5 KiB hot scratch
流量，因此兩者保留作負結果，不取代 baseline。

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

Canonical serial schedule 的八個資料向量固定佔 YMM0..YMM7，四個暫存佔
YMM8..YMM11；high operand 在兩個 product half 都發出後才 destructive overwrite。
其他 candidate 允許 physical mapping 延續到後段。所有 ASM symbol 都不使用 stack，
也沒有 spill/reload。

同一個 source body 也產生四個 exact-output schedule candidate：

- `interleaved`：把八條 Barrett chain 與 transpose 成對交錯，實測中性；
- `remapped`：讓 butterfly 的 physical register mapping 直接流入 Barrett／transpose，
  每 stage 消掉四個 register copy，六個 block 共消掉 72 個 `vmovdqa`；
- `resident`：在 `remapped` 上把 q 與 Barrett reciprocal 整個 block 留在
  YMM14/YMM15，雖減少 memory-source operands，但實測中性到稍慢；
- `queued-store`：沿用 `remapped` 算術，先發出全部八個 `vperm2i128` 到
  YMM0..YMM7，再連續發出八個 `vmovdqu` store。

`queued-store` 是目前最佳候選。兩輪十回、forward/reverse sequential order 的
`perf stat -e cycles` 的 amortized values 中，isolated stage3+4+5 從
327.00/328.27 降到
323.30/323.34（快 1.13%--1.50%），完整 forward 從 756.25/756.75 降到
754.63/754.19（快 0.21%--0.34%）。Full polynomial multiplication 名目上在
兩個順序都約慢 0.10%，但落在 perf variation 內，視為 neutral/no reliable win；
所以此路徑仍是 default-off prototype，production 與
canonical regression symbol 都不變。

兩個方向也有實際合併：`direct+queued-store` 的完整 forward 是
846.89/846.92，雖比 direct+serial 的 850.26/850.71 快 0.40%--0.45%，
仍比 canonical 慢約 12%。Full polymul 在一個順序快 0.35%、反向順序慢 0.04%，
同樣沒有穩定的 composition win。

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

## 16-block SoA quartic basemul

每個 batch 直接載入 `a0..a3`、`b0..b3` 四組 SoA YMM，16 lanes 同時計算
16 個 `Zq[X]/(X^4-lambda)` 乘法：

```text
c0 = a0*b0 + lambda*(a1*b3 + a2*b2 + a3*b1)
c1 = a0*b1 + a1*b0 + lambda*(a2*b3 + a3*b2)
c2 = a0*b2 + a1*b1 + a2*b0 + lambda*a3*b3
c3 = a0*b3 + a1*b2 + a2*b1 + a3*b0
```

`gt_basemul_soa_avx2()` 對每個 runtime product 先做 packed Montgomery
reduction，讓 product 留在 `R^-1` domain；三個 wrapped accumulator 再乘
Montgomery-form lambda，最後四個 coefficient 乘 `R^2` 回到 normal domain。
輸出仍是相同四-YMM SoA layout，不需要 input/output transpose。

lambda table 的精確關係是：

```text
logical = (32*k3 + 3*bitreverse5(Q)) mod 96
lambda  = omega96^logical / F_branch * R mod q
F_0=2, F_1=22
```

`generate_gt_soa_tables.py` 產生 12×16 的 `lambda` 和 `lambda*qinv`；Makefile
每次 test 都用 `--check` 拒絕 stale table。測試另將 192 lanes 全部對照既有
`gt_rowbitrev_lambda[branch][physical_block]`，避免混用 input CRT `(64,33)` 與
正確的 output CRT `(32,3)`。

## SoA direct-consumer inverse NTT

Forward 的 `row01 / row2_packed` 是配合 CT distance `16,8,4,2,1` 的 producer
packing，不適合直接反過來使用。Inverse DIT 的順序是 `len=2,4,8,16,32`；SoA
每個 YMM 已經是：

```text
[ branch0 Qbase+0..7 | branch1 Qbase+0..7 ]
```

所以 `len=2,4,8` 以 `vpshufb` 在兩個 128-bit half 內各自形成 low/high operand，
不跨 half。每個 `(k3,c)` 只保留四個 Q-group YMM；`len=16` 配
`group0/1, group2/3`，`len=32` 配 `group0/2, group1/3`。這就是 inverse 的
first-load mapping；不先建立 row-bitrev buffer，也沒有獨立 768-word transpose。

五層採 lazy schedule。若 API input 滿足 `|a|<=q`：

```text
input -> len2 -> len4 -> len8 -> len16 -> len32
  q       2q      3q      4q       5q       6q
```

Montgomery high operand 每層都回到一個 modulus，最大 `6q=20742` 仍可安全留在
signed int16。只有 NTT32→DFT3 boundary 使用一次 packed Barrett，將 row 收回
`[0,q]`；inverse DFT3 三個輸出再各做一次 packed checkpoint。這取代最初每層
widen-to-int32 Barrett 的語意版。

第一個 inverse ASM region 在 `gt_invntt_ntt32_soa.s`。它以 `ymm0..ymm3` 保存四個
Q-group，`ymm4..ymm11` 作 shuffle/Montgomery temporary，`ymm12..ymm13` 先保存
兩個 `vpshufb` mask、mask 死後再重用為 qinv/factor，`ymm14` 保存 q，`ymm15`
保存 packed Barrett reciprocal。Linked symbol 是 955 bytes，沒有 stack access、
call、ZMM 或 opmask。ASM scratch output 對 intrinsic boundary 做 768-word exact
comparison，不只比較 modulo q。

第二個 inverse ASM region 在 `gt_invntt_dft3_soa.s`。每次 iteration 直接載入相距
512 bytes 的 `y0/y1/y2`，不改 scratch layout；`y2-y1` 的固定因子 Montgomery chain
啟動後，先排獨立的三條 DFT3 sum/difference，再完成 correction。三個結果各自需要
packed Barrett，因此以 `ymm8..ymm10` 交錯三條 quotient chain。四個常數常駐
`ymm11..ymm14`，`ymm15` 保持空閒。GCC linked symbol 是 230 bytes，沒有 stack
access、call、ZMM 或 opmask；16 次 in-place iteration 對 intrinsic scratch boundary
做 768-word exact comparison。

Inverse DFT3 之後的 natural `n3,n32` 以

```text
n = (64*n3 + 33*n32) mod 96
```

回到 96-point coefficient block。Untwist table 已照
`[branch0 n32=Q..Q+7 | branch1 n32=Q..Q+7]` 打包；接著同一 YMM 內完成兩個
branch 的 merge 與 `1/192,1/96` normalization。四個 `c` 的結果再做 lane-local
4×8 transpose，將逐 coefficient vectors 變成完整 quartic blocks。每兩個 Q block
共用一個 YMM，低/高 128-bit half 分別對應 output 的前/後 384 coefficients，最後
用四次 64-bit store 寫出，不再用 768 次 `vpextrw`。

第三個 inverse ASM region 在 `gt_invntt_postprocess_soa.s`。每個 loop iteration
同時保留四個 coefficient vector：先平行完成四條 untwist Montgomery chain，再把
branch0/branch1 拆成 XMM，交錯四條 `(z-z^5)^-1` correction，以及低 branch 的
`1/192`、高 branch 的 `1/96` normalization。`ymm12..ymm13` 依生命期重用為
untwist、correction 與 normalization factor pair，`ymm15` 常駐 q，`ymm14` 空閒。
最後的 4×8 transpose 留在 register 中；八個 output block index 由 generated public
table 讀入 GPR，直接形成 16 個 64-bit stores。Linked symbol 是 781 bytes，沒有
stack access、call、ZMM 或 opmask。

`generate_gt_invntt_tables.py` 產生 inverse twiddle、`twiddle*qinv`、packed
untwist、`untwist*qinv` 與 96-entry public CRT output-block map。Generator check、
row-bitrev inverse differential、in-place、round-trip、boundary/full polynomial product
都屬於 mandatory test gate。

## Montgomery 與 Barrett 的 AVX2 指令

固定因子 `b` 的 16-bit Montgomery multiplication 使用 `B=b*qinv mod 2^16`：

```text
hi         = signed_mulhi(a, b)
correction = signed_mulhi(mullo(a, B), q)
result     = hi - correction
```

對應主要是 `vpmullw`、`vpmulhw`、`vpsubw`。手排 forward 的 top-split、twist、
DFT3 omega 與五層 NTT32 butterfly 都使用預先打包的 `(b,B)`；intrinsic path 只作
語意與 range oracle，不是目前的 scheduled forward path。

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
secret-dependent branch 或 lookup。Canonical public wrapper 的 peak 是 frontend
與 stage2 各 1.5 KiB，共 3 KiB；direct/half wrapper 只保留 canonical stage2
scratch，peak 是 1.5 KiB。三者都需要 1536-byte stage2 scratch，zero-handoff 並不
代表 zero-scratch。正式版本要再決定 caller-provided scratch、覆寫時機與是否清除
secret stack data。

SoA basemul 與 inverse 允許 NTT-domain operand 落在 `[-q,q]`。每個 Montgomery
product 回到 `[-(q-1),q-1]`；最大的 quartic accumulator 是 `4(q-1)=13824`，
所以所有 packed `vpaddw` 都不會 wrap。乘 `R^2` finalizer 後回到
`[-(q-1),q-1]` normal-domain representative。完整逐步推導同樣記錄在
`range-proof.md`。Inverse 使用 1536-byte aligned row scratch；舊的 GCC 16
intrinsic linked symbol 另以 SysV red zone 保存兩個 vector constants，three-region
ASM wrapper 已沒有這兩個 spill。所有 input 都先進 scratch，因此 `out==in` 安全。

## Register pressure 與 spill audit

設計上的目標 budget 是：

```text
8 long-lived data YMM
2 q / Montgomery constants
2 twiddle constants
4 transient temporaries
= 16 architectural vector registers.
```

實際 GCC 16 linked-object audit 修正了早期推測：1484-byte intrinsic frontend
本身沒有 stack spill；其主要成本是 runtime CRT arithmetic 與 scalar twist/qinv
construction。573-byte intrinsic stage1+2 才有 40-byte frame 加 red-zone window，
共五個 YMM constant spill/reload。

手排 standalone frontend 與 stage1+2 linked symbols 分別是 518 與 423 bytes；
兩者都不讀寫 `%rsp`、不 call，並維持同一個 scratch/layout/range contract。融合
producer 是 970 linked bytes，唯一 stack allocation 是精確 1536-byte semantic
frontend scratch。Direct/half candidates 證實能把這個 handoff 降成 0/768 bytes，
但實測退步，因此 canonical path 仍保留它。Stage3+4+5 把八個 data vector 保持在
register，所有 schedule candidate 都沒有 spill/reload。也就是說目前完整 forward
prototype 的 compiler-generated vector spill 已消除；保留的 frontend 與 stage2
scratch 是經測量後選擇的資料相依 boundary，而不是 allocator 失敗。

SoA basemul intrinsic 也刻意保留為 semantics baseline：Ryzen 的 GCC 16 linked
symbol 是 773 bytes，會建立 72-byte frame 並使用 SysV red zone 做 YMM spill。
儘管如此，實測 TSC median 與 production basemul 同為 318，retired instructions
則少約 9.6%。下一個 pointwise optimization gate 是手排成 zero-spill ASM，再比較
是否真的降低 hardware cycles；不能只根據 intrinsic source 的運算數決定。

Inverse intrinsic 的 GCC 16 linked symbol 是 2681 bytes。Explicit stack adjustment
為 1480 bytes，另使用 120-byte red-zone window；其中 1536 bytes 是 row scratch，
兩個 YMM constant spill 是 compiler live-range artifact。最值得抽成 ASM 的三個
region 是：四-group lazy inverse NTT32、in-place inverse DFT3/checkpoint，以及
untwist/merge/4×8 final block store。三個 region 都已成為 zero-stack ASM；目前
保留配置 1536-byte row scratch 並做三次 call 的 regression wrapper，並另有下述
單一入口融合版可測量函式邊界成本。

融合版透過同一組 region macro 建立 standalone regression symbols 和
`gt_invntt_soa_avx2_fused_asm`，不是複製第二份數學 schedule。Fused entry 在 stack
配置一個 1536-byte、32-byte aligned scratch，以 `r10` 保留 output、`r11` 保留
原始 stack pointer；內部沒有 call、push、pop，只有函式尾端一個 `vzeroupper`。
Linked fused symbol 是 1968 bytes，full inverse exact output 與 `out==in` 都和
three-call/intrinsic path 相同。

## Slothy handoff

本機 Slothy checkout 的 core 雖然 architecture-agnostic，目前只有 Arm
architecture/target model，沒有 x86/AVX2 model。因此現在不能誠實地宣稱這份
AVX2 已經是 Slothy candidate，也不能直接拿 AArch64 Neon model 來排。

這個目錄依 `new_kernel_baseline_then_iterate` 的 gate 方式準備：

- `kernel-contract.yml`：ring、I/O、layout、range、constant-time 與 scratch。
- `baseline-contract.yml`：reference、驗證 gate、production replacement scope。
- `instruction-dag.yml`：frontend pair、stage12 stripe、stage345 block、scatter DAG。
- `gt_ntt_avx2.c`：可執行的 intrinsic semantics baseline。
- `generate_gt_frontend_tables.py`：CRT byte-offset 與 packed twist/qinv generator。
- `gt_ntt_frontend_stage12_soa.S`：手排 frontend、stage1+2 與 single-entry producer。
- `gt_ntt_stage345_soa.s`：依 DAG 手排的 stage3+4+5 與 fused SoA store。
- `asm-soa-contract.yml`：hybrid ASM boundary、ABI、layout 與 output range。
- `gt_basemul_soa.c`：16-block SoA quartic intrinsic semantics baseline。
- `basemul-soa-contract.yml`：pointwise representation、range 與 alias contract。
- `generate_gt_soa_tables.py`：lambda／lambda-qinv table generator/checker。
- `gt_invntt_soa.c`：直接消費 SoA 的 lazy inverse/full-pipeline prototype。
- `gt_invntt_ntt32_soa.s`：手排的 direct-SoA inverse NTT32 與 packed checkpoint。
- `gt_invntt_dft3_soa.s`：手排的 in-place inverse DFT3 與三路 packed checkpoint。
- `gt_invntt_postprocess_soa.s`：手排的 untwist/merge/normalization/final-store。
- `gt_invntt_fused_soa.S`：共用上述 macro 的 single-entry inverse benchmark。
- `invntt-soa-contract.yml`：inverse scaling、scratch、range 與 final-store contract。
- `generate_gt_invntt_tables.py`：inverse fixed-factor/CRT table generator/checker。

之後要走 Slothy，合理順序是先補 x86 architecture model（instruction semantics、
latency/throughput、port model、register class），再把下列 region 各自抽成 symbolic
assembly，而不是一次排完整 768-point function：

1. one frontend slot-pair；
2. row01 stage1+2 stripe；
3. singleton stage1+2 stripe；
4. row01 stage3+4+5 block；
6. one 16-block SoA quartic basemul batch。
7. one `(k3,c)` four-group lazy inverse NTT32；
8. one inverse DFT3 group；
9. one `n3,Qgroup` untwist/merge/4×8 final-store group。

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
- direct/half handoff 對 stage2 boundary 的 full-range、random exact differential；
- canonical 與四個 stage3+4+5 candidate 對獨立 `±5(q-1)` scratch 的
  modulo-q differential、`[0,q]` range 與 exact reachable-state regression；
- impulse、boundary 與 200 組完整 random polynomial 對 AArch64 portable GT
  reference 的 modulo-q differential；
- 768-word SoA mapping 的 forward/inverse exact round trip；
- hybrid ASM SoA 對 mapping oracle 的 modulo-q differential 與 `[0,q]` range；
- 192-entry lambda mapping 與 generated table exact comparison；
- SoA quartic basemul 的 boundary、200 random、output-range differential；
- 16 組 forward NTT → SoA basemul composition differential；
- SoA inverse 對 row-bitrev inverse 的 boundary 與 100 random differential；
- inverse NTT32 ASM scratch 對 intrinsic 的 boundary 與 100 random exact differential；
- inverse DFT3 ASM scratch 對 intrinsic 的 boundary 與 100 random exact differential；
- inverse postprocess ASM output 對 intrinsic 的 boundary 與 100 random exact differential；
- forward → inverse 的 impulse、full-range boundary 與 200 random round trip；
- forward → basemul → inverse 對 schoolbook 的 full-range boundary 與 16 random
  ternary polynomial products；
- intrinsic 與 ASM 的 in-place `out==in`；
- ASan/UBSan 可另外套在同一個 test binary。

Ryzen 7 9700X 的 preliminary run（CPU 2 pinned、boost on、SMT sibling 未隔離）中，
hybrid ASM SoA 的 serialized-TSC median 是 983，intrinsic GT 是 1476，約降低
33.4%。Production forward NTT 是 444，所以目前主要剩餘成本仍在 intrinsic
frontend/stage1+2，而不是把 prototype 直接升格成 production kernel。

同一主機 2026-07-16 的 pointwise run 中，production 與 SoA intrinsic basemul
median 都是 318 TSC ticks；hardware cycles/call 分別為 480.43 與 478.83，
instructions/call 分別為 1839.52 與 1662.35。這只證明 SoA 沒有因 layout 付出
transpose 成本。

同一主機先前的 direct-consumer inverse intrinsic run 是 1013 TSC ticks、1494.44
hardware cycles 和 4621.31 instructions；production inverse 是 432、651.01 和
2600.29。完整 GT SoA polynomial multiplication是 3323 TSC，production 是 1652。

加入第一個 inverse ASM region 後，同 run 的 inverse NTT32 boundary 從 537 降到
422 TSC、hardware cycles 從 801.49 降到 633.95，分別降低 21.4% 與 20.9%。完整
hybrid inverse 從 998 降到 886 TSC，完整 GT polymul 從 3301 降到 3179。Hybrid
full path 仍是 production 的 1.93×，所以 promotion gate 尚未通過。

加入第二個 inverse ASM region 後，之後的結論統一採 `perf stat -e cycles`。同主機
同一次五回重複測量中，isolated inverse DFT3/checkpoint 從 131.62 降到 125.09
cycles/call（4.96%）；完整 hybrid inverse 從 1315.90 降到 1306.74（0.70%）；完整
GT polymul 從 4671.29 降到 4640.95（0.65%）。兩-region full path 仍是 production
polymul 2414.32 cycles 的 1.92×；下一步是手排 untwist/merge/4×8 final-store
postprocess，再處理 pointwise 與 frontend spill。

加入第三個 inverse ASM region 後，isolated postprocess 從 580.83 降到 521.51
hardware cycles/call（10.21%）；完整 three-region inverse 從 1307.52 降到
1254.70（4.04%）；full GT polymul 從 4645.01 降到 4584.06（1.31%）。Production
polymul 同 run 是 2426.09 cycles，因此 GT 仍是 1.89×。下一步先融合三個 inverse
ASM region，移除中間的 call／`vzeroupper`，再決定 pointwise 或 frontend。

融合比較的三輪 `perf cycles` 顯示 inverse 只降低 0.07%–0.16%；full polymul 的
差異則介於 fused 慢 0.05% 到快 0.48%，反向順序確認是快 0.19%。因此單純移除
region boundary 對完整 pipeline 視為效能中性，不再繼續壓 call overhead。

KPQC Final 的 AVX2 NTRU+768 arithmetic sources 與這裡的 production baseline
逐檔相同。相同 Ryzen run 中，KPQC Final／production forward NTT 是 667.04
cycles，GT hybrid forward 是 1454.02（2.18×）；basemul 是 480.64 對 479.75，
實質相同；inverse 是 651.61 對 fused GT 1252.94（1.92×）；full polymul 是
2420.73 對 4585.62（1.89×）。這組結果把下一個里程碑鎖定為 forward
frontend/stage1+2，而不是 pointwise layout 或 inverse call fusion。

完成 prepacked table 與手排 frontend/stage1+2 後，十回、反向 operation 順序的
`perf stat -e cycles` 確認結果是：frontend `993.73 -> 334.82`（-66.3%）、
stage1+2 `161.56 -> 133.40`（-17.4%）、完整 GT forward `1452.44 -> 774.76`
（-46.7%），完整 GT polymul `4584.88 -> 3233.41`（-29.5%）。同 run 的
KPQC Final／production 是 forward 668.996、polymul 2422.08，因此差距縮成
1.16× 與 1.33×。

接著實作的 zero-handoff 與 half-handoff producer 在最後 1M-call 雙順序確認中
分別慢 16.86%--16.93% 與 17.33%--17.41%，所以 semantic frontend scratch 不是
目前 bottleneck。Stage3+4+5 的 `queued-store` 則把 isolated region 降低
1.13%--1.50%，完整 forward 降低 0.21%--0.34%，但 full polymul 沒有可靠改善。
兩個實驗都保留作 regression／schedule evidence，沒有改 production 或 prototype
default。下一個較高價值目標是 inverse/postprocess 或 stage2-to-stage345 boundary
的結構性改寫，而不是再做相同的 scratch-copy elimination。
