# GT inverse NTT 目前實作中文說明

> 歷史封存文件。下列路徑描述 2026 年 6 月重整前的實作，不能當成目前
> production source map；現況請以 `docs/README.md` 指向的 production summary
> 為準。

本文說明目前 production `poly_invntt` 的實際路徑。重點是幫助讀懂
assembly，不討論 Slothy 產生流程。

## 入口檔案

目前 production wrapper 是：

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/inv_my_ntt.s
```

它只設定 gate，真正實作在：

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/invntt_opt.s
```

production gate 是：

```asm
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
```

所以本文只解釋這條路徑：

```text
GT row-bitrev input
  -> direct physical load
  -> inverse NTT32 stage123
  -> stripe-major scratch
  -> inverse NTT32 stage45 + row-end reduce
  -> three row buffers
  -> inverse DFT3 across rows
  -> branchfold untwist/final merge
  -> reduced output representatives
```

## 高層資料布局

NTRU+768 的 GT layout 可以看成 `3 x 32 x 8 halfword lanes`。

每個 NEON `q` register 是 8 個 `int16`：

```text
q = h[0..7]
  = lower d half: branch0 的 4 個係數
  = upper d half: branch1 的 4 個係數
```

direct load 會從 input 的兩個 768-byte branch 各拿一個 `d`：

```asm
ldr dX,  [x3, #off]      // branch0, 4 x int16
ldr d12, [x4, #off]      // branch1, 4 x int16
mov vX.d[1], v12.d[0]    // 組成一個 q-vector
```

因此 row kernel 和 post kernel 都是在一個 `q` 裡同時處理兩個 branch。
最後輸出時才用 `str d...` 分別把 lower half 和 upper half 寫回不同
offset。

## Stack layout

entry ABI：

```text
x0 = output poly pointer
x1 = input poly pointer
```

prologue：

```asm
stp x30, x0, [sp, #-16]!
sub sp, sp, #2080
```

active path 的 frame：

```text
sp + 0       .. sp + 31      padding / unused
sp + 32      .. sp + 543     row0 buffer, 32 q-vectors = 512 bytes
sp + 544     .. sp + 1055    row1 buffer, 32 q-vectors = 512 bytes
sp + 1056    .. sp + 1567    row2 buffer, 32 q-vectors = 512 bytes
sp + 1568    .. sp + 2079    stripe-major scratch, 32 q-vectors = 512 bytes
sp + 2080                       saved x30
sp + 2088                       saved x0
```

`INVNTT_STACK_SIZE = 2080`，`INVNTT_SAVED_X0_OFFSET = 2088`。

row buffers 存 stage45 之後、post 之前的 natural `k32` row output。
scratch 只服務 stage123 到 stage45 的暫存轉置。

## 全域 GPR 用法

| register | active path 用途 |
| --- | --- |
| `x0` | entry 時是 output pointer。prologue 存到 stack，post 前從 `[sp + 2088]` 載回。 |
| `x1` | input pointer，全程視為不變。 |
| `x2` | row kernel 的 current row output base。依序是 `sp+32`、`sp+544`、`sp+1056`。 |
| `x3` | 多用途。direct load 時是 branch0 input base；stage/post 時是 constants pointer。 |
| `x4` | direct load 時是 branch1 input base，也就是 `x1 + 768`。 |
| `x5` | post loop counter。 |
| `x7` | stage123 constants pointer。 |
| `x8` | post 讀 row0 buffer 的 pointer。 |
| `x9` | post 讀 row1 buffer 的 pointer。 |
| `x10` | post 讀 row2 buffer 的 pointer。 |
| `x11` | output A pointer，初始化 `x0 + 0`，每個 3-stripe group 加 24。 |
| `x12` | output B pointer，初始化 `x0 + 512`，每個 3-stripe group 加 24。 |
| `x13` | output C pointer，初始化 `x0 + 256`，每個 3-stripe group 加 24。 |
| `x14` | stripe-major scratch base，active row path 固定設成 `sp + 1568`。 |
| `x30` | link register，存在 stack frame 尾端。 |

`x3` 是最容易混淆的，因為它在不同階段代表不同東西：

```text
row direct load:       x3 = x1
stage123 const load:   x7 = invntt32_stage123_consts, x3 仍可當 input base
stage45:              x3 = invntt32_stage45_consts，macro 內每 stripe 加 32
post:                 x3 = inv_branchfold_vecs，macro 內每 output 加 64
```

## 全域 NEON constants

`v0` 在函式開始從 `inv_consts` 載入：

```asm
adr x3, inv_consts
ldr q0, [x3]
```

`v0` lane 用法：

| lane | 值 | 用途 |
| --- | ---: | --- |
| `v0.h[0]` | `3457` | modulus `q`，給 `mls ..., v0.h[0]` 用。 |
| `v0.h[1]` | `19412` | Barrett reduce reciprocal。 |
| `v0.h[2]` | `-723` | inverse DFT3 裡 `(row2-row1)` 的 multiplier。 |
| `v0.h[3]` | `-6853` | 上一個 multiplier 的 `sqrdmulh` precompute。 |
| `v0.h[4..7]` | final merge 舊路徑常數 | active branchfold path 基本不用這幾個 lane。 |

`v15` 也會從 `inv_consts + 16` 載入，但 production branchfold merge
把 untwist 和 final scale 折進 `inv_branchfold_vecs`，所以 active path
不依賴 `v15`。

## 基本算術 macro

### `FQMUL_LANE`

```asm
sqrdmulh tmp, in, pre
mul      out, in, tw
mls      out, tmp, q
```

這是 centered multiplier。`tw` 是 normal multiplier，`pre` 是給
`sqrdmulh` 的 precompute。它不是 Montgomery table。

語意近似：

```text
out = in * tw mod q
```

### `INV_BUTTERFLY_LANE`

```text
prod = fqmul(hi, tw)
old_lo = lo
lo = old_lo + prod
hi = old_lo - prod
```

這是 inverse NTT butterfly。production row path 採 lazy row arithmetic：
stage123 不在每個 butterfly 後 reduce，stage45 結尾才 reduce。

### `BARRETT_REDUCE`

```asm
sqdmulh tmp, reg, v0.h[1]
srshr   tmp, tmp, #11
mls     reg, tmp, v0.h[0]
```

把 `reg` 拉回 centered representative。production row path 的 row-end
reduce 已經 fuse 到 stage45；production post path 的 final outputs 也會
在 branchfold store 前 reduce。

## Row path overview

三個 rows 依序處理：

```asm
add x3, x1, #0
add x4, x1, #768
add x2, sp, #32
DIRECT_STAGE123_STRIPE_SCRATCH_ROW0
RUN_INVNTT32_STAGE45_SCRATCH_ROW

add x3, x1, #0
add x4, x1, #768
add x2, sp, #544
DIRECT_STAGE123_STRIPE_SCRATCH_ROW1
RUN_INVNTT32_STAGE45_SCRATCH_ROW

add x3, x1, #0
add x4, x1, #768
add x2, sp, #1056
DIRECT_STAGE123_STRIPE_SCRATCH_ROW2
RUN_INVNTT32_STAGE45_SCRATCH_ROW
```

每個 row 做兩段：

```text
stage123: direct physical load -> 8-vector blocks -> stripe-major scratch
stage45:  scratch stripe -> stage45 butterfly -> Barrett reduce -> row buffer
```

## Direct physical load

row `k3` 的 physical input offset 是：

```text
physical_j(k3, k32_br) = (32*k3 + 3*k32_br) mod 96
byte offset            = 8 * physical_j
```

所以三個 row 的 source offsets 是：

```text
row0: 0, 24, 48, ..., 744
row1: 256, 280, ..., 760, 16, 40, ..., 232
row2: 512, 536, ..., 752, 8, 32, ..., 488
```

每個 offset 載入一個 `q`：

```text
lower d = input branch0 at x1 + offset
upper d = input branch1 at x1 + 768 + offset
```

## Stage123

stage123 每次處理 8 個 `q`，暫存在 `v3..v10`：

```text
v3  = input[j + 0]
v4  = input[j + 1]
v5  = input[j + 2]
v6  = input[j + 3]
v7  = input[j + 4]
v8  = input[j + 5]
v9  = input[j + 6]
v10 = input[j + 7]
```

constants：

```asm
adr x7, invntt32_stage123_consts
ldr q1, [x7]       // normal twiddles
ldr q2, [x7, #16]  // sqrdmulh precompute
```

stage123 register roles：

| register | 用途 |
| --- | --- |
| `v1` | stage123 normal twiddle lanes。 |
| `v2` | stage123 precompute lanes。 |
| `v3..v10` | 8-vector working block。 |
| `v11` | `INV_BUTTERFLY_LANE` 的 product。 |
| `v12` | direct load branch1 temporary，之後也當 butterfly temporary。 |

stage123 做三層：

```text
len=2:
  (v3,v4), (v5,v6), (v7,v8), (v9,v10)

len=4:
  (v3,v5), (v4,v6), (v7,v9), (v8,v10)

len=8:
  (v3,v7), (v4,v8), (v5,v9), (v6,v10)
```

這三層結束後，`v3..v10` 是 8 個 stage123 outputs。

## Stripe-major scratch

production path 不把 stage123 output 直接寫成 row-major：

```text
row-major:
  out[0], out[1], ..., out[31]
```

而是寫成 stage45 需要的 stripe-major：

```text
scratch[64*j + 16*group] = stage123_output[j + 8*group]
```

其中：

```text
j     = 0..7    stage45 stripe index
group = 0..3    stage123 8-vector block index
```

一個 `DIRECT_STAGE123_BLOCK_TO_SCRATCH group` 會把 `v3..v10` 存成：

```text
v3  -> scratch[64*0 + 16*group]
v4  -> scratch[64*1 + 16*group]
v5  -> scratch[64*2 + 16*group]
v6  -> scratch[64*3 + 16*group]
v7  -> scratch[64*4 + 16*group]
v8  -> scratch[64*5 + 16*group]
v9  -> scratch[64*6 + 16*group]
v10 -> scratch[64*7 + 16*group]
```

這個 layout 的目的：stage45 每個 stripe 可以用四個連續 load：

```text
scratch[64*j + 0]   = stage123_output[j]
scratch[64*j + 16]  = stage123_output[j+8]
scratch[64*j + 32]  = stage123_output[j+16]
scratch[64*j + 48]  = stage123_output[j+24]
```

不能把 scratch overlay 到 final row buffer，因為 stage45 的 natural-order
store 會覆蓋還沒被其他 stripe 讀走的 scratch value。

## Stage45 from scratch

`RUN_INVNTT32_STAGE45_SCRATCH_ROW` 會 call：

```asm
_invntt32_8way_stage45_from_scratch
```

它設定：

```asm
adr x3, invntt32_stage45_consts
```

然後對 `j=0..7` 跑 `INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH j`。
雖然 macro 名字保留歷史命名，這裡只看它的語意。

每個 stripe 的 input：

```text
x14 = scratch base
x2  = current row buffer base
x3  = stage45 constants pointer

load:
  in0  = scratch[64*j + 0]   = stage123_output[j]
  in8  = scratch[64*j + 16]  = stage123_output[j+8]
  in16 = scratch[64*j + 32]  = stage123_output[j+16]
  in24 = scratch[64*j + 48]  = stage123_output[j+24]
```

scheduled code 裡的主要 semantic mapping：

| semantic value | register at load |
| --- | --- |
| `in0` | `v17` |
| `in8` | `v26` |
| `in16` | `v30` |
| `in24` | `v11` |
| stage45 normal constants | `v5` |
| stage45 precompute constants | `v7` |

stage45 做兩層：

```text
len=16:
  (in0,  in8)
  (in16, in24)

len=32:
  (out0, out16)
  (out8, out24)
```

然後立刻做 row-end Barrett reduction。

store mapping：

```text
v17 -> row[j]
v10 -> row[j+8]
v29 -> row[j+16]
v23 -> row[j+24]
```

對應 assembly stores：

```asm
str q17, [x2, #(16 * j)]
str q23, [x2, #(16 * (j + 24))]
str q29, [x2, #(16 * (j + 16))]
str q10, [x2, #(16 * (j + 8))]
```

store order 是排程結果，不代表 natural order 的概念順序。真正的 row
buffer layout 仍然是：

```text
row[0], row[1], ..., row[31]
```

stage45 scheduled code 的其他 vector registers 是 temporaries：

```text
v3, v6, v8, v9, v13, v14, v18, v19, v20, v21, v22,
v25, v27, v28, v29
```

其中 `v29` 最後變成 output16；其他多數是 multiply/reduce temporary。

## Post-row setup

三個 row 都完成後，post phase 設定：

```asm
adr x3, inv_consts
ldr q15, [x3, #16]
ldr x0, [sp, #INVNTT_SAVED_X0_OFFSET]
add x8,  sp, #32
add x9,  sp, #544
add x10, sp, #1056
adr x3, inv_branchfold_vecs

add x11, x0, #0
add x12, x0, #512
add x13, x0, #256
```

post pointer roles：

```text
x8  = row0 read pointer
x9  = row1 read pointer
x10 = row2 read pointer

x11 = output A base = x0 + 0
x12 = output B base = x0 + 512
x13 = output C base = x0 + 256

x3 = branchfold constants stream
```

注意 output base 順序是 A, B, C，但 C 在記憶體位置是 `x0+256`，
B 是 `x0+512`。這是 GT natural output store pattern 決定的。

## Post loop shape

production 使用 3-stripe loop：

```text
repeat 10 times:
  stripe k32 = 3*g + 0
  stripe k32 = 3*g + 1
  stripe k32 = 3*g + 2
  A/B/C pointers += 24

tail:
  stripe k32 = 30
  stripe k32 = 31
```

總共 32 stripes。每個 stripe 讀三個 rows 的同一個 `k32` vector：

```asm
ldr q1, [x8], #16    // row0[k32]
ldr q2, [x9], #16    // row1[k32]
ldr q3, [x10], #16   // row2[k32]
```

## Inverse DFT3 across rows

`FUSED_POST_STRIPE` 裡先做 inverse DFT3：

```asm
sub      v4.8h, v3.8h, v2.8h
sqrdmulh v5.8h, v4.8h, v0.h[3]
mul      v6.8h, v4.8h, v0.h[2]
mls      v6.8h, v5.8h, v0.h[0]

add      v7.8h, v1.8h, v2.8h
add      v7.8h, v7.8h, v3.8h

sub      v8.8h, v1.8h, v2.8h
add      v8.8h, v8.8h, v6.8h

sub      v9.8h, v1.8h, v3.8h
sub      v9.8h, v9.8h, v6.8h
```

semantic mapping：

| register | meaning |
| --- | --- |
| `v1` | row0 input |
| `v2` | row1 input |
| `v3` | row2 input |
| `v4` | `row2 - row1` |
| `v5` | fqmul precompute temporary |
| `v6` | `fqmul(row2-row1, inv_dft3_twiddle)` |
| `v7` | DFT3 output 0 |
| `v8` | DFT3 output 1 |
| `v9` | DFT3 output 2 |

因為 `INVNTT_POST_DFT3_NO_REDUCE=1`，這三個 DFT3 outputs 不在這裡
Barrett reduce。它們會直接進入 branchfold final merge。production path
後面會 reduce final outputs，所以最終代表值仍通過現有 representative tests。

## Branchfold final merge

一般概念上，post phase 需要：

```text
inverse DFT3
  -> untwist by F_b^k
  -> branch merge
  -> final scale
  -> store low/high branch halves
```

production 的 `POST_STORE_PTR_BRANCHFOLD` 把後三件事折到常數表
`inv_branchfold_vecs` 裡。對每個 DFT3 output vector，它載入四個 q-vector
constants：

```asm
ldr q10, [x3], #16    // low normal constants
ldr q11, [x3], #16    // low sqrdmulh precompute
ldr q12, [x3], #16    // high normal constants
ldr q13, [x3], #16    // high sqrdmulh precompute
```

接著做兩條 fqmul path：

```text
low path:
  v18 = fqmul(xvec, v10/v11)
  v21 = v18 + ext(v18, #8)
  reduce v21
  store d21 -> output low offset

high path:
  v23 = fqmul(xvec, v12/v13)
  v23 = v23 + ext(v23, #8)
  reduce v23
  store d23 -> output high offset
```

為什麼要 `ext #8` 再 add？

一個 `q` 裡有兩個 branch half：

```text
lanes 0..3 = branch0
lanes 4..7 = branch1
```

branchfold constants 讓 branch0 和 branch1 先各自乘上已折好的常數。
`ext #8` 交換 lower/upper half，`add` 後 lower half 就是兩個 branch
合併後的 4 lanes。最後只存 `d21` 或 `d23` 的 lower half。

active branchfold store register roles：

| register | 用途 |
| --- | --- |
| input `xvec` | `v7`、`v8`、或 `v9`，也就是 DFT3 output。 |
| `v10` | low normal constants。 |
| `v11` | low precompute constants。 |
| `v12` | high normal constants。 |
| `v13` | high precompute constants。 |
| `v17` | low path `sqrdmulh` temporary。 |
| `v18` | low path fqmul result before half-combine。 |
| `v19` | `ext(v18,#8)` temporary。 |
| `v21` | low output vector before `str d21`。 |
| `v20` | high path `sqrdmulh` temporary，也被 final Barrett reduce 當 tmp。 |
| `v23` | high output vector before `str d23`。 |
| `v24` | `ext(v23,#8)` temporary。 |

## Output store pattern

post 每個 `k32` stripe 會產生三個 DFT3 outputs：`v7`、`v8`、`v9`。
它們依 `k32 mod 3` 寫到 A/B/C 的不同 offset。

程式註解給的 mapping：

```text
k32 mod 3 == 0:
  v7 -> A
  v8 -> B
  v9 -> C

k32 mod 3 == 1:
  v7 -> C + 8
  v8 -> A + 8
  v9 -> B + 8

k32 mod 3 == 2:
  v7 -> B + 16
  v8 -> C + 16
  v9 -> A + 16
```

其中：

```text
A = x11 = x0 + k32_group*24
B = x12 = x0 + 512 + k32_group*24
C = x13 = x0 + 256 + k32_group*24
```

branch1 half 會存在 `+768` 對應位置：

```text
low branch store:  off_lo = 0, 8, 16
high branch store: off_hi = 768, 776, 784
```

所以一個 3-stripe group 剛好填滿每個 A/B/C pointer 的 24 bytes：

```text
offset 0   = k32 mod 3 == 0 的 4 halfwords
offset 8   = k32 mod 3 == 1 的 4 halfwords
offset 16  = k32 mod 3 == 2 的 4 halfwords
```

然後：

```asm
add x11, x11, #24
add x12, x12, #24
add x13, x13, #24
```

## 一個完整 row 的 register lifetime

以 row0 的一個 stage123 block 為例：

```text
x3 = x1
x4 = x1 + 768
x2 = sp + 32
x14 = sp + 1568

v1/v2      = stage123 constants
v3..v10    = 8 loaded q-vectors
v11/v12    = butterfly temporaries

after stage123:
  v3..v10 = final stage123 outputs for this 8-vector block

store:
  v3..v10 go to stripe-major scratch positions for group 0/1/2/3
```

接著 stage45：

```text
x3 = invntt32_stage45_consts
x14 = sp + 1568
x2 = sp + 32

for j in 0..7:
  load scratch[j, j+8, j+16, j+24]
  run len16 and len32 inverse butterflies
  Barrett reduce four outputs
  store to row0[j], row0[j+8], row0[j+16], row0[j+24]
```

row1、row2 完全同型，只是 `x2` 指到不同 row buffer，而且 direct physical
load offsets 不同。

## 現在寫法為什麼難讀

有三個原因：

1. `x3` 和多個 vector registers 在不同 phase 會換身份。
2. stage45 的 store order 是排程導向，不是 semantic order。
3. branchfold 把 untwist、branch merge、final scale 合在 constants table，
   所以 post 裡看不到傳統「先 untwist，再 merge」的明確分段。

讀 code 時建議固定用 phase 來看：

```text
phase 1: direct load + stage123
phase 2: scratch -> stage45 -> row buffer
phase 3: row0/1/2 -> DFT3
phase 4: branchfold constants -> final d stores
```

不要跨 phase 追同一個 register 名稱，因為它們多半已經被重用。

## Rewrite 時最重要的不變條件

如果要重寫 `invntt32`，先保持以下 contract 不變：

1. input q-vector lane layout 必須仍是 lower d branch0、upper d branch1。
2. row0/row1/row2 的 physical offset sequence 不能改錯。
3. stage123 output 若仍接 current stage45，scratch layout 必須維持：

   ```text
   scratch[64*j + 16*group] = stage123_output[j + 8*group]
   ```

4. stage45 output row buffer 必須是 natural row order `row[0..31]`。
5. post phase 讀 row buffers 時假設 `x8/x9/x10` 每次 `#16` 線性前進。
6. branchfold constants stream 的消耗順序必須和 output store pattern 完全一致。
7. final branchfold path 必須保留 output Barrett reduction，否則 raw representatives
   可能對 `poly_crepmod3` 不安全。
