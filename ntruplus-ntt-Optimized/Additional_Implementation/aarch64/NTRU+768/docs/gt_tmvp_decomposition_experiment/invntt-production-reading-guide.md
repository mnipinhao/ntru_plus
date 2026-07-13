# InvNTT Production Reading Guide

這份文件是給目前 `gt_production_opt` / `gt_production_opt_rminus1`
inverse NTT 用的讀碼索引。production wrapper 現在 include 的主檔是：

```text
asm/gt/invntt/poly_invntt.n1.opt.inc
```

舊的 legacy / rowstage45-post prototype assembly 已從 active `asm/` tree
移除；需要追歷史時請看 git history 與
`docs/gt_tmvp_decomposition_experiment/invntt-prototype-archive.md` 的背景紀錄。

## Production wrappers

| wrapper | 產生的 symbol | 用途 |
| --- | --- | --- |
| `asm/gt/invntt/poly_invntt.S` | `poly_invntt`, `gt_block_major_poly_invntt`, `gt_tuple_poly_invntt` | normal GT production inverse path |
| `asm/gt/invntt/poly_invntt_rminus1.S` | `poly_invntt_from_rminus1`, `gt_block_major_poly_invntt_from_rminus1`, `gt_tuple_poly_invntt_from_rminus1` | paired with `poly_basemul_rminus1`; branchfold table 改成 rminus1 版本 |

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
| `INVNTT_USE_LAZY_TWIDDLE1_STAGE123` | rminus1 production 專用；刪除 inverse NTT32 `len=2,4,8` 中 multiplier=1 的 modular multiply，直接做 butterfly 並延後 reduction |
| `INVNTT_USE_LAZY_TWIDDLE1_LEN16` | rminus1 production 專用；同樣刪除 `len=16` 的兩個 multiplier=1 modular multiply；`len=32` 仍保留 reduction，避免 bound 從 29376 上升到不安全的 55296 |
| `INVNTT_PRESERVE_CALLEE_SAVED_SIMD` | rminus1 production 在既有 stack frame 內保存/恢復 AAPCS64 規定的 `d8-d15` low halves |
| `INVNTT_EXPOSE_STAGE123_SCRATCH_ABI` | benchmark-only `asm/gt/bench/poly_invntt_rminus1_stage123scratch.S` exports the split stage123scratch symbols；standard `gt_production_opt_rminus1` KEM 不走這個 ABI |
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

目前 `GT_PRODUCTION_USE_INVNTT_LAZY_TWIDDLE1_LEN16` 預設為 `1`，因此上述
lazy Stage123/len16 與 ABI preservation 是 production rminus1 path。要重現
promotion 前的歷史版本，可在 make command 顯式設定：

```sh
GT_PRODUCTION_USE_INVNTT_LAZY_TWIDDLE1_LEN16=0
```

range proof 的核心界線是：Stage123 後 bound 13824、`len=16` 後 27648、
保留 `len=32` multiply/reduction 後 29376。若連 `len=32` multiplier=1 也刪除，
DC path 可達 55296，所以 production 不採用該延伸。

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
| `13` | `BARRETT_REDUCE` | q=3457 的 16-bit lane Barrett reduction |
| `19` | `FQMUL_LANE` | `sqrdmulh + mul + mls` 的 signed modular multiply |
| `39` | `INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH` | stage45 + row-end reduce fused Slothy schedule；input 從 `x14 + 64*j` stripe scratch load |
| `90` | `DIRECT_STAGE123_VEC` | 從 branch0/branch1 各 load `d`，合成一個 `q` vector |
| `96` | `STORE_STAGE123_STRIPE_SCRATCH` | stage123 output 寫成 `[j, j+8, j+16, j+24]` contiguous scratch |
| `118` | `DIRECT_STAGE123_BLOCK_TO_SCRATCH` | 8-vector block 的 stage1/2/3 butterflies；lazy flag 控制 multiplier=1 path |
| `174` | `DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY` | block-major row0 physical offset map |
| `192` | `DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY` | block-major row1 physical offset map |
| `206` | `DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY` | block-major row2 physical offset map |
| `220` | `TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY` | tuple input path；row 內 offset 是 `0,8,16,...,248` |
| `666` | `POST_STORE_PTR_BRANCHFOLD` | branchfold final merge + final output reductions + two `d` stores |
| `710` | `FUSED_POST_STRIPE` | inverse DFT3 + branchfold store 的 one-stripe body |
| `790` | `INVNTT_STACK_SIZE` / ABI macros | production rminus1 frame 擴充至 2144 bytes，保存 `d8-d15` |
| `839` | `gt_block_major_poly_invntt` | block-major public entry與三個 row 的 stage123/stage45 path |
| `905` | `gt_tuple_poly_invntt` | tuple input public entry |
| `963` | `L_invntt_post_tail` | common branchfold post loop、ABI restore 與 return |
| `1034` | `poly_invntt_stage45scratch` | exposed ABI prototype tail：input 已經是 stage123 stripe scratch |
| `1075` | `inv_consts` | q、Barrett precompute、DFT3 constants |
| `1080` | `invntt32_stage123_consts` | stage123 twiddles/precompute |
| `1085` | `invntt32_stage45_consts` | stage45 twiddles/precompute |
| `1114` | `inv_branchfold_vecs` | normal vs rminus1 branchfold table switch |

## What is intentionally not in production

`asm/gt/invntt/poly_invntt.n1.opt.inc` 不保留：

- `INVNTT_USE_OLD_GATHER`
- `INVNTT_USE_POST_FASTSCALE`
- `INVNTT_BENCH_STAGES`
- rowstage45/post fused prototype flags:
  `INVNTT_USE_ROWSTAGE45_POST_*`
- old standalone post Slothy selectors:
  `INVNTT_USE_POST_FUSED_*`, `INVNTT_USE_POST_BRANCHFOLD_A72_SLOTHY`

如果要看那些實驗，先看 archive doc，不要從 production 主檔開始讀。
