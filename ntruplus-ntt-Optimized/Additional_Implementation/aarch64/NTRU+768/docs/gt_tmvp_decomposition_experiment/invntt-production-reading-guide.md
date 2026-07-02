# InvNTT Production Reading Guide

這份文件是給目前 `gt_production_opt` / `gt_production_opt_rminus1`
inverse NTT 用的讀碼索引。production wrapper 現在 include 的主檔是：

```text
asm/slothy/production/invntt_opt.production.s
```

原本的 `asm/slothy/legacy/invntt_opt.s` 保留成 legacy / experiment superset；
rowstage45/post prototypes 和 bench-only fragments 另外集中到：

```text
asm/slothy/archive/invntt_rowstage45_post_prototypes.s
docs/gt_tmvp_decomposition_experiment/invntt-prototype-archive.md
```

## Production wrappers

| wrapper | 產生的 symbol | 用途 |
| --- | --- | --- |
| `asm/gt/poly_invntt_gt_production.s` | `poly_invntt`, `gt_block_major_poly_invntt`, `gt_tuple_poly_invntt` | normal GT production inverse path |
| `asm/gt/poly_invntt_from_rminus1_gt_production.S` | `poly_invntt_from_rminus1`, `gt_block_major_poly_invntt_from_rminus1`, `gt_tuple_poly_invntt_from_rminus1` | paired with `poly_basemul_rminus1`; branchfold table 改成 rminus1 版本 |

舊的 A72 opt-in prototype wrapper 已移除；目前 production 只保留上表兩個
InvNTT wrapper 入口。

## Active flags

| flag | 現在意思 |
| --- | --- |
| `INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH` | input 不先 gather 成完整 row buffer；直接 load physical block-major 或 tuple input，做完 stage123 後寫成 stage45 想吃的 stripe scratch |
| `INVNTT_USE_STAGE45_REDUCE_FUSION` | row-end Barrett reduction fuse 進 stage45 store 前 |
| `INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY` | stage45 + reduction 使用 Slothy schedule |
| `INVNTT_POST_DFT3_NO_REDUCE` | post DFT3 三個 output 不在中間 reduce；靠 branchfold final output reductions 保住 KEM 所需 representative |
| `INVNTT_USE_POST_BRANCHFOLD` | untwist、branch merge、final scaling 由 branchfold constants table 合併 |
| `INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS` | final store 前做 output Barrett reductions，這是 `poly_crepmod3` representative contract 的關鍵 |
| `INVNTT_INPUT_RMINUS1` | rminus1 wrapper 專用；改 include `invntt_branchfold_vecs_rminus1.inc` |
| `INVNTT_EXPOSE_STAGE123_SCRATCH_ABI` | rminus1 wrapper 目前也 export stage123scratch split prototype symbols；standard `gt_production_opt_rminus1` KEM 不走這個 ABI |
| `INVNTT_NO_POLY_ALIAS` | legacy/prototype wrapper 專用；不要 export `poly_invntt` |

## rminus1 decap data flow

目前 production rminus1 decap path 在 `kem.c` 是：

```text
poly_frombytes(&c, ct)
poly_frombytes(&f, sk)
poly_basemul_rminus1(&m1, &c, &f)
poly_invntt_from_rminus1(&m1, &m1)
poly_crepmod3(&m1, &m1)
```

`poly_basemul_rminus1()` 的 output 還是 GT block-major layout，但多留一個
`R^-1` factor。`poly_invntt_from_rminus1()` 使用同一份 row/post pipeline，
差別只在 final branchfold constants table，讓最後輸出回到 normal `R^0`
representative。

這幾輪做的 split prototype 是另一條實驗 path：

```text
poly_basemul_rminus1_to_stage123scratch(m1.coeffs, &c, &f)
poly_invntt_from_rminus1_stage45scratch(&m1, m1.coeffs)
```

它可以驗證「basemul 直接產生 InvNTT stage45 scratch layout」這個方向，但目前
KEM benchmark 沒有比 standard rminus1 path 快，所以不視為 production default。

## Production file line map

| line | 段落 | 要看什麼 |
| --- | --- | --- |
| `18` | `BARRETT_REDUCE` | q=3457 的 16-bit lane Barrett reduction |
| `24` | `FQMUL_LANE` | `sqrdmulh + mul + mls` 的 signed modular multiply |
| `37` | `INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH` | stage45 + row-end reduce fused Slothy schedule；input 從 `x14 + 64*j` stripe scratch load |
| `89` | `DIRECT_STAGE123_VEC` | 從 branch0/branch1 各 load `d`，合成一個 `q` vector |
| `95` | `STORE_STAGE123_STRIPE_SCRATCH` | stage123 output 寫成 `[j, j+8, j+16, j+24]` contiguous scratch |
| `117` | `DIRECT_STAGE123_BLOCK_TO_SCRATCH` | 8-vector block 的 stage1/2/3 butterflies，最後寫 stripe scratch |
| `154` | `DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY` | block-major row0 physical offset map |
| `172` | `DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY` | block-major row1 physical offset map |
| `186` | `DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY` | block-major row2 physical offset map |
| `200` | `TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY` | tuple input path；row 內 offset 是 `0,8,16,...,248` |
| `232` | `POST_STORE_PTR_BRANCHFOLD` | branchfold final merge + final output reductions + two `d` stores |
| `272` | `FUSED_POST_STRIPE` | inverse DFT3 + branchfold store 的 one-stripe body |
| `363` | `gt_block_major_poly_invntt` | block-major public entry，`w15=0` |
| `367` | `gt_tuple_poly_invntt` | tuple public entry，`w15=1` |
| `372` | `L_invntt_entry_common` | common prologue、三個 row 的 stage123/stage45、post loop、return |
| `498` | `poly_invntt_stage45scratch` | exposed ABI prototype tail：input 已經是 stage123 stripe scratch |
| `538` | `_invntt32_8way_stage45_from_scratch` | stage45 scratch consumer loop |
| `553` | `inv_consts` | q、Barrett precompute、DFT3 constants |
| `558` | `invntt32_stage123_consts` | stage123 twiddles/precompute |
| `563` | `invntt32_stage45_consts` | stage45 twiddles/precompute |
| `592` | `inv_branchfold_vecs` | normal vs rminus1 branchfold table switch |

## What is intentionally not in production

`asm/slothy/production/invntt_opt.production.s` 不保留：

- `INVNTT_USE_OLD_GATHER`
- `INVNTT_USE_POST_FASTSCALE`
- `INVNTT_BENCH_STAGES`
- rowstage45/post fused prototype flags:
  `INVNTT_USE_ROWSTAGE45_POST_*`
- old standalone post Slothy selectors:
  `INVNTT_USE_POST_FUSED_*`, `INVNTT_USE_POST_BRANCHFOLD_A72_SLOTHY`

如果要看那些實驗，先看 archive doc，不要從 production 主檔開始讀。
