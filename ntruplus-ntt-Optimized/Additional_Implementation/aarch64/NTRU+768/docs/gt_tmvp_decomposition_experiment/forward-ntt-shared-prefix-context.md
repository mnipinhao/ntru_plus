# Forward NTT Shared-Prefix Context

Date: 2026-07-08

## 目前到底在做什麼

目前不是已經有一個可以取代 production 的 candidate。現在是在研究一條
forward NTT decomposition route：

```text
production:
  Phase123 一次產生完整 row scratch raw Q0..Q31
  _gt_ntt32_batch8_to_blockmajor stage12 讀 raw Q
  _gt_ntt32_batch8_to_blockmajor stage345 做完 NTT32

shared-prefix experiment:
  Phase123 拆成較小 producer
  producer 直接產生 stage12 想吃的 Q group
  stage12 早一點接上
  看能不能省掉 raw Q layout handoff 的成本
```

這條路的重點不是換數學，而是改資料流順序。

## Phase123 slot 和 NTT32 stripe 的關係

每個 Phase123 iteration 會產生 4 個 local slots：

```text
slot0, slot1, slot2, slot3
```

對 even iterations `0/2/4/6`：

```text
iter0 slots0/1/2/3 -> Q0,  Q1,  Q2,  Q3
iter2 slots0/1/2/3 -> Q8,  Q9,  Q10, Q11
iter4 slots0/1/2/3 -> Q16, Q17, Q18, Q19
iter6 slots0/1/2/3 -> Q24, Q25, Q26, Q27
```

NTT32 stage12 stripe 的規則是：

```text
stripe s reads Q[s], Q[s+8], Q[s+16], Q[s+24]
```

所以：

```text
stripe0 = Q0, Q8,  Q16, Q24
stripe1 = Q1, Q9,  Q17, Q25
stripe2 = Q2, Q10, Q18, Q26
stripe3 = Q3, Q11, Q19, Q27
```

## U01 是什麼

U01 是 Phase123 的 slots0+1 producer。

它使用 `P0/P2/P4`，產生：

```text
iter0 -> Q0/Q1
iter2 -> Q8/Q9
iter4 -> Q16/Q17
iter6 -> Q24/Q25
```

因此它可以接：

```text
stage12 stripe0/1
```

目前結果：

```text
U01 all-row scratch:
  source-order oracle pass
  quick N1 Slothy: 453 instructions, 113 expected cycles
  quick opt oracle pass
```

## U23 是什麼

U23 是 Phase123 的 slots2+3 producer。

它使用 `P1/P3/P5`，產生：

```text
iter0 -> Q2/Q3
iter2 -> Q10/Q11
iter4 -> Q18/Q19
iter6 -> Q26/Q27
```

因此它可以接：

```text
stage12 stripe2/3
```

目前結果：

```text
U23 all-row scratch:
  source-order oracle pass
  quick N1 Slothy: 453 instructions, 113 expected cycles
  quick opt oracle pass
```

## 現在可以怎麼比較

先前只能做 isolated even-half comparison。

Production even half：

```text
4 個 Phase123 full iterations = 4 * 40 = 160
3 rows * 4 stripes * 8 = 96
total = 256 N1 expected cycles
```

Shared-prefix U01+U23：

```text
U01 stripes0/1 = 113
U23 stripes2/3 = 113
total = 226 N1 expected cycles
```

所以在這個 isolated N1 model 下，看起來有：

```text
256 -> 226
省 30 cycles，約 11.7%
```

現在 odd half 也完成後，可以做完整 stage12 coverage 的 isolated
comparison。

Production Phase123 + stage12：

```text
8 個 Phase123 full iterations = 8 * 40 = 320
3 rows * 8 stripes * 8 = 192
total = 512 N1 expected cycles
```

Shared-prefix scratch prototypes：

```text
even U01 stripes0/1 = 113
even U23 stripes2/3 = 113
odd U01 stripes4/5 = 113
odd U23 stripes6/7 = 113
total = 452 N1 expected cycles
```

所以在這個 isolated N1 model 下，完整 stage12 coverage 看起來是：

```text
512 -> 452
省 60 cycles，約 11.7%
```

但這還不是 production win，原因是：

```text
- 用的是 N1 model，不是 A76 / Pi5 real cycle
- 用的是 quick split，不是完整 fine-grained Slothy
- 還沒有接 production wrapper
- 還沒算 x13 scratch setup / stack frame integration
- 還沒接 stage345 / 完整 NTT32
```

## 能不能直接做完完整 NTT32

理論上可以把這條路繼續推到完整 NTT32，但不建議做成一個完全
register-resident mega-kernel。

完整 NTT32 需要：

```text
stage12 stripes0..7
stage345 blocks0..3
final reduce/scatter
```

目前已完成 isolated symbolic prototypes：

```text
even half:
  U01 -> stripes0/1
  U23 -> stripes2/3
odd half:
  U01 -> stripes4/5
  U23 -> stripes6/7
```

而 stage345 的 consumption 是：

```text
block0 reads Q0..Q7
block1 reads Q8..Q15
block2 reads Q16..Q23
block3 reads Q24..Q31
```

所以要做完整 NTT32，合理方向是：

```text
1. even half 產生 post-stage12 Q0..Q3/Q8..Q11/Q16..Q19/Q24..Q27
2. odd half 產生 post-stage12 Q4..Q7/Q12..Q15/Q20..Q23/Q28..Q31
3. 把 stage12 output 存成 stage345 block 想讀的 layout
4. stage345 從這個 layout load，完成 block0..3
```

不合理方向是：

```text
把 Phase123 + stage12 + stage345 全部塞進一個沒有 scratch 的 Slothy region
```

原因是 live vector 數量太大。只做 all-row U01 direct no-scratch 就已經至少
要 24 個 raw Q vector；完整 NTT32 要面對 32 個 Q vector 加上 twist、
stage12、stage345 暫存，超過可控範圍。

## 下一步

目前 odd-half counterpart 已完成：

```text
iterations 1/3/5/7
slots0/1 -> stripes4/5
slots2/3 -> stripes6/7
```

所以現在已經有完整 stage12 coverage：

```text
stripes0..7
```

下一步是評估：

```text
是否讓 stage12 output 直接 store 成 stage345 block layout
```

也就是不要先存回原本 row-major Q0..Q31 layout，而是研究能不能直接存成：

```text
block0 wants Q0..Q7
block1 wants Q8..Q15
block2 wants Q16..Q23
block3 wants Q24..Q31
```

這樣 stage345 可能少掉 hidden layout/load cost。

## Stage12 -> Stage345 layout audit

實際檢查 `asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S` 後，這裡有一個重要修正：

```text
目前 production stage12 store 的 row scratch layout
已經等於 stage345 block 想讀的 layout。
```

具體來說，Stage12 每個 stripe 寫：

```text
stripe0 -> Q0, Q8,  Q16, Q24
stripe1 -> Q1, Q9,  Q17, Q25
stripe2 -> Q2, Q10, Q18, Q26
stripe3 -> Q3, Q11, Q19, Q27
stripe4 -> Q4, Q12, Q20, Q28
stripe5 -> Q5, Q13, Q21, Q29
stripe6 -> Q6, Q14, Q22, Q30
stripe7 -> Q7, Q15, Q23, Q31
```

全部 stripes 寫完後，memory 仍然是：

```text
row_base + 16*Q
```

所以 Stage345 四個 block 直接讀：

```text
block0 -> Q0..Q7
block1 -> Q8..Q15
block2 -> Q16..Q23
block3 -> Q24..Q31
```

Audit artifact：

```text
experiments/forward_ntt_phase123_u01/audit_stage12_stage345_layout.py
```

目前結論：

```text
stage12_to_stage345_layout_ok
```

所以這裡不是要發明一個新的 stage345 layout。真正下一步應該改成：

```text
研究能不能少掉或攤掉 stage12 store -> stage345 load 這個 memory boundary
```

也就是從「layout reorder」改成「boundary fusion / scheduling」問題。

最小可控方向是 block-centric prototype：

```text
1. 先產生 Stage345 block0 需要的 post-stage12 Q0..Q7
2. 立刻接 Stage345 block0
3. 再處理 block1/block2/block3
```

但 block0 的 Q0..Q7 不是來自單一 U slice：

```text
Q0/Q1 -> even U01
Q2/Q3 -> even U23
Q4/Q5 -> odd U01
Q6/Q7 -> odd U23
```

因此下一個 prototype 不能只是把目前四個 slice 原樣串起來，而是要改成
`block0-first` 的 emission order，才可能讓 stage345 早一點開始。

## Block-first 的精確意思

Stage12 每個 stripe 其實都產生四個 post-stage12 outputs：

```text
stripe s:
  out0 -> Q[s]
  out1 -> Q[s+8]
  out2 -> Q[s+16]
  out3 -> Q[s+24]
```

所以 Stage345 block 的需求不是「某幾個 stripe」，而是：

```text
block0 wants out0 from stripe0..7 -> Q0..Q7
block1 wants out1 from stripe0..7 -> Q8..Q15
block2 wants out2 from stripe0..7 -> Q16..Q23
block3 wants out3 from stripe0..7 -> Q24..Q31
```

因此 block0-first 的最低可行形狀是：

```text
1. 用 even U01 / even U23 / odd U01 / odd U23 產生 stripes0..7 的 raw inputs
2. 跑 stage12 stripes0..7
3. 每個 stripe 保留 out0，形成 Q0..Q7
4. 立刻把這 8 個 vector 餵給 stage345 block0
5. out1/out2/out3 仍要存起來，給後面的 block1/2/3
```

新的 derivation artifact：

```text
experiments/forward_ntt_phase123_u01/derive_stage12_stage345_block_first_plan.py
```

這個 script 的目的只是固定 contract，避免下一輪寫 asm 時把 block/stripe
關係看錯。

## 目前 block0-first scaffold 結果

已新增 source-order scaffold：

```text
experiments/forward_ntt_phase123_u01/phase123_stage12_block0_first_allrows.sym.s
```

它做的事是：

```text
1. even U01 / even U23 / odd U01 / odd U23 全部產生 raw Q0..Q31
2. raw Q 寫到 x13 row-major scratch
3. Stage12 stripes0..7 對 rows0/1/2 跑完
4. post-stage12 Q0..Q31 留在同一個 x13 row-major scratch
5. Q0..Q7 成為 Stage345 block0 可以吃的 contiguous block
```

通過的 gate：

```text
check-kernel-contract: pass
clang -target aarch64-linux-gnu: pass
phase123_stage12_block0_first_ok seeds=64 rows=3 outputs=96 block0_outputs=24 later_outputs=72
```

但這個 scaffold 還不是 Slothy-ready：

```text
physical-register leak gate: fail
```

原因是它仍然沿用 source-order `v1..v31/q*` registers。這是刻意保守的
oracle scaffold，先證明資料流正確；下一步才把可控區塊改成真正 symbolic
registers。

目前最合理的下一個縮小範圍是：

```text
Stage12 stripes0..7 的 out0/q22
  -> Stage345 block0 input Q0..Q7
```

而不是一次把 1978 行 source-order scaffold 全部丟給 Slothy。
