# A76 base_gt layout experiments

這份文件只整理目前 A76/Cortex-A76 方向下，`base_gt` / `poly_basemul_add`
和跨 kernel layout 的實驗切法。重點是避免把三件不同的事混在一起：

```text
input load form:     ld4  vs  ldp/ldr + uzp/trn
output store form:   st4 AoS ABI  vs  SoA private ABI
cross-kernel layout: NTT -> base_gt -> InvNTT 是否全線改成同一個 SoA
```

## 1. base_gt_ld4_vs_ldrtrn

目前新增的 guarded experiment 是：

```text
GT_BASEMUL_USE_LDPTRN_LOAD4
asm/base_gt_opt_ldrtrn_noadd_wrapper.S
make test_gt_basemul_opt_ldrtrn_load4
```

它只替換 `base_gt.opt.s` 的 block-major input load，不改 arithmetic、不改
`st4` output，也不改 ABI。這樣可以單獨回答：

```text
在 A76 上，ld4 的結構化 load 成本是否比 ldp q,q + software deinterleave 更糟？
```

原本每個 operand 的 input：

```asm
ld4 {a0.8h, a1.8h, a2.8h, a3.8h}, [src], #64
```

實驗版每個 operand 的 input：

```asm
ldp qraw0, qraw1, [src]
ldp qraw2, qraw3, [src, #32]
add src, src, #64

uzp1 tmp0.8h, raw0.8h, raw1.8h   // a/c for blocks 0..3
uzp2 tmp1.8h, raw0.8h, raw1.8h   // b/d for blocks 0..3
uzp1 tmp2.8h, raw2.8h, raw3.8h   // a/c for blocks 4..7
uzp2 tmp3.8h, raw2.8h, raw3.8h   // b/d for blocks 4..7

uzp1 a0.8h, tmp0.8h, tmp2.8h     // a0..a7
uzp1 a1.8h, tmp1.8h, tmp3.8h     // b0..b7
uzp2 a2.8h, tmp0.8h, tmp2.8h     // c0..c7
uzp2 a3.8h, tmp1.8h, tmp3.8h     // d0..d7
```

A76 cost intuition:

| form | pressure |
| --- | --- |
| `ld4` | slow structured-load uop, but no extra NEON permutes |
| `ldp + uzp` | normal load pipes, but adds 8 vector permutes per operand |

Pi5 sample result so far:

```text
baseline test_gt_basemul_opt
  correctness: ok
  final clean make-run sample: 62 ticks
  poly_basemul: 63 ticks in make-run sample
  direct rerun samples: 83, 100 ticks

ldp+uzp test_gt_basemul_opt_ldrtrn_load4
  correctness: ok
  final clean make-run sample: 64 ticks
  poly_basemul: 63 ticks in make-run sample
  direct rerun samples: 85, 101 ticks
```

Interpretation:

```text
No clear win.  The software deinterleave removes ld4, but spends enough uzp
work that the full basemul loop is essentially tied or slightly slower.
```

所以這條可以保留為 A76 experiment，但目前不像是會帶來大幅收益。

## 2. base_gt_store_soa

`base_gt` arithmetic 的自然 result register 其實已經是 SoA：

```text
r0 = coefficient 0 for 8 physical blocks
r1 = coefficient 1 for 8 physical blocks
r2 = coefficient 2 for 8 physical blocks
r3 = coefficient 3 for 8 physical blocks
```

目前用 `st4` 是為了寫回 public `poly` ABI：

```text
physical_j: r0 r1 r2 r3
physical_j+1: r0 r1 r2 r3
...
```

如果下一個 kernel 可以吃 SoA，那 store 可以變成：

```asm
stp qR0, qR1, [dst]
stp qR2, qR3, [dst, #32]
```

這會避開 A76 上較慢的 `st4`。但這不是 drop-in，因為 consumer 也要改。

目前不能直接改的地方：

```text
encap: poly_basemul_add(c, h, r, m) -> poly_tobytes(ct, c)
```

`poly_tobytes()` 吃的是 public `poly` ABI，所以 encap 的 output 若改 SoA，
就必須一起做 `poly_tobytes_soa()` 或 `basemul_add_to_bytes()`。

比較合理的 first target 是 private path：

```text
decap: poly_basemul(m1, c, f) -> poly_invntt(m1, m1)
```

但是之前的 tuple/stage123scratch prototype 已經顯示：只做 layout-only store
不夠，因為會把成本搬到下一個 gather/copy。真正有機會的是讓 consumer
直接吃這個 SoA，或把 `basemul -> InvNTT stage123` fuse 起來。

## 3. poly_basemul_add c input early load

這點要分 production 版本看。

`asm/gt/base_gt.opt.s` 裡的 old `poly_basemul_add` schedule 的確把 `c` input
load 放得很晚，接近 final add：

```text
ld4 c at about cycle 82 in the annotated old add path
```

但目前 production `poly_basemul_add` 走的是：

```text
GT_BASE_ADD32_ASM = asm/gt/poly_basemul_add_gt_production.s
asm/slothy/production/base_gt_add32_full_pipeline.n1.opt.S
```

在這個 full-pipeline Slothy path 中：

```text
ld4 a at cycle 0
ld4 b at cycle 0
ld4 c at cycle 12
```

所以「把 c load 提早」在目前 production add32 path 已經大致做過。接下來
還可以試的是：

```text
1. 將 c layout 改成 SoA，讓 c 用 ldp/ldr 而不是 ld4。
2. 讓 Slothy 在 A76 model 下重排 full-pipeline，檢查 c load 是否能更早或更穩。
3. 若 encap output 要保留 public ABI，最後仍要面對 output st4 或 tobytes fusion。
```

## 4. Ideal end-to-end SoA

理想資料流是：

```text
forward NTT store SoA
  -> base_gt uses ldr/ldp, no ld4 deinterleave
  -> base_gt stores SoA
  -> InvNTT accepts SoA directly
```

這會避開：

```text
store AoS -> ld4 deinterleave -> st4 interleave
```

但它不是一個小改動，因為現在有三個 ABI 邊界：

```text
forward NTT output ABI
base_gt input/output ABI
InvNTT input ABI
```

如果只改其中一段，很容易變成：

```text
省掉一個 ld4/st4，但新增 copy/reorder/gather
```

這正是 tuple-decap 和 stage123scratch split prototype 目前沒有贏的原因。

## Current recommendation

短期排序：

1. 保留 `base_gt_ld4_vs_ldrtrn` target，但目前結果是 neutral，不 promote。
2. 下一個可做的是 `base_gt_store_soa` micro ABI，不接 KEM，先只測 store-side
   cost 和 correctness mapping。
3. 若 store-side 明顯贏，再選一個 private consumer 接起來；優先 decap
   `poly_basemul -> poly_invntt`，不要先動 encap public ciphertext path。
4. `poly_basemul_add` 的下一步不是再把現有 `c` load 往前搬，而是研究
   `c` 是否能以 SoA 進來，或直接做 `basemul_add_to_bytes()` 避免最後再回
   public `poly` ABI。
