# Forward NTT Phase123 U01 Shared-Prefix 結果

Date: 2026-07-08

## 這一步在測什麼

前一版 row0 direct fuse 是：

```text
U01(iter0/2/4/6) 只算 row0 slots0+1
  -> 直接接 NTT32 stage12 stripes0+1
```

它的好處是 row0 raw Q 不用 store/load，但缺點是沒有利用 Good-Thomas
三個 row 共用同一個 U01 prefix。這一輪改測：

```text
U01(iter0/2/4/6) 一次算 row0/row1/row2 slots0+1
  -> raw Q 先存到 stage12-order scratch
  -> stage12 stripes0+1 從 scratch load
```

這回答的是：

```text
共同 prefix 攤到三個 row 後，算術成本是否看起來有機會贏？
```

它不是 production patch，也不是 direct no-scratch patch。

## 為什麼不是 all-row direct no-scratch

如果完全不落 scratch，stage12 stripes0+1 要等到：

```text
iter0 -> Q0/Q1
iter2 -> Q8/Q9
iter4 -> Q16/Q17
iter6 -> Q24/Q25
```

而且三個 row 都要保留：

```text
3 rows * 4 iterations * 2 slots = 24 個 raw Q vector
```

這還沒算第 4 個 U01 iter 的 twist/zip 暫存，也還沒算 stage12 的暫存。
在只有 32 個 Neon register 的條件下，直接 all-row no-scratch 太緊。

所以這一輪採用比較務實的 gate：

```text
shared-prefix 算 row0/1/2
  -> x13 compact scratch
  -> stage12 從 x13 讀
```

## Scratch layout

`x13` 是 temporary scratch base，offset 都是 public/fixed：

```text
x13 +   0: row0 Q0,Q1,Q8,Q9,Q16,Q17,Q24,Q25
x13 + 128: row1 Q0,Q1,Q8,Q9,Q16,Q17,Q24,Q25
x13 + 256: row2 Q0,Q1,Q8,Q9,Q16,Q17,Q24,Q25
```

Stage12 stripe0 讀：

```text
Q0, Q8, Q16, Q24
```

Stage12 stripe1 讀：

```text
Q1, Q9, Q17, Q25
```

## 新增 artifacts

```text
experiments/forward_ntt_phase123_u01/generate_stage12_allrows_scratch.py
experiments/forward_ntt_phase123_u01/phase123_u01_stage12_allrows_scratch_stripe01.sym.s
experiments/forward_ntt_phase123_u01/verify_stage12_allrows_scratch_symbolic.py
experiments/forward_ntt_phase123_u01/optimize_stage12_allrows_scratch.py
experiments/forward_ntt_phase123_u01/slothy_stage12_allrows_scratch_n1.log
experiments/forward_ntt_phase123_u01/slothy_stage12_allrows_scratch_n1_quick.log
experiments/forward_ntt_phase123_u01/phase123_u01_stage12_allrows_scratch_stripe01.quick.opt.s
```

`verify_u01_symbolic.py` 也被擴充，現在可以模擬 writable scratch memory。

## Correctness 結果

Source-order asm：

```text
clang -target aarch64-linux-gnu: pass
phase123_u01_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
```

Slothy quick N1 output：

```text
clang -target aarch64-linux-gnu: pass
phase123_u01_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
```

這代表：

```text
generated .quick.opt.s 的 row / Q index / scratch load-store layout 都對到 production oracle
```

## Slothy 結果

完整 fine-grained split run 超過三分鐘，已中止並保留 log：

```text
slothy_stage12_allrows_scratch_n1.log
```

它不是 parser error，而是 453-instruction region 對完整 overlapping split
heuristic 太重。

改用 quick split：

```text
optimize_stage12_allrows_scratch.py --target n1 --split-stepsize 0.25
```

結果：

```text
Instructions:    453
Expected cycles: 113
Expected IPC:    4.01
split_heuristic_full: OK
```

注意：這是 `neoverse_n1_experimental`，不是 A76。

## 跟 production 怎麼比

只看 U01 slice，也就是 rows0/1/2 的 stage12 stripes0+1：

```text
production:
  4 Phase123 full iterations * 40 cycles = 160
  3 rows * 2 stage12 stripes * 8 cycles = 48
  total = 208 N1 expected cycles

all-row U01 scratch:
  U01 rows0/1/2 slots0+1 + stage12 stripes0+1 = 113 N1 expected cycles
```

所以這個 slice 看起來有機會。

但不能直接說完整 forward NTT 贏，因為 production 的 4 個 Phase123
iterations 同時也算了 slots2+3；本 prototype 只算 slots0+1。

比較公平的下一步是：

```text
再做 U23 counterpart
  -> stage12 stripes2+3
  -> 比 production even-iteration stripes0..3
```

如果 U01 + U23 合計還接近或低於 production 的：

```text
4 Phase123 iters + 3 rows * 4 stage12 stripes
```

這條路才值得繼續往 production integration 推。
