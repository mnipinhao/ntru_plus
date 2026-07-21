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
| `asm/gt/invntt/poly_invntt.S` | `poly_invntt`, `gt_block_major_poly_invntt`, `gt_tuple_poly_invntt` | normal-representation generic API、fallback 與 transform/polymul 測試；default KEM 不呼叫 |
| `asm/gt/invntt/poly_invntt_rminus1.S` | `poly_invntt_from_rminus1`, `gt_block_major_poly_invntt_from_rminus1` | paired with `poly_basemul_rminus1`; branchfold table 改成 rminus1 版本；production 只展開 KEM 使用的 block-major body |

舊的 A72 opt-in prototype wrapper 已移除；目前 production 只保留上表兩個
InvNTT wrapper 入口。

### Default KEM 到底走哪一個 inverse

目前 `GT_PRODUCTION_USE_RMINUS1_DECAP` 是 common production flag。實際 KEM
call graph 是：

| operation | inverse call | count |
| --- | --- | ---: |
| keygen | 無；只做 forward NTT、base inversion、base products 與 serialization | 0 |
| encapsulation | 無；`r`/`m` 做 forward NTT，接著 basemul-add 直接產生 ciphertext bytes | 0 |
| decapsulation | `poly_basemul_rminus1 -> poly_invntt_from_rminus1` | 1 |

因此 default full KEM 中 `poly_invntt()` 的動態呼叫次數是 **0**。Profiler 的
`inverse_ntt_generic` 是 standalone repository/API diagnostic，不是 default KEM
weighted path；production decap 應看 `dec_first_invntt_actual` 或 paired
`basemul_rminus1 + invntt_from_rminus1`。

仍保留 generic `poly_invntt()`，是因為它定義 normal-representation transform
contract：

```text
poly_ntt(a) -> poly_invntt(A)                    # roundtrip
poly_basemul(A, B) -> poly_invntt(product)       # generic polymul
```

它同時是關掉 `GT_PRODUCTION_USE_RMINUS1_DECAP` 時的 decap fallback，也是
differential、ABI、roundtrip 與 generic polynomial API 測試的 entry。這是
repository/API 保留需求，不是目前 full-KEM performance 需求。不能把
`poly_invntt_from_rminus1` 直接改名成 `poly_invntt`，因為前者的 adjusted final
constants 只接受帶額外 `R^-1` 的 input；normal input 送入後會得到錯誤的固定
Montgomery scaling。

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
| `INVNTT_BLOCK_MAJOR_ONLY` | rminus1 production 只 emit block-major entry；tuple/BPQ bodies 仍可由未開此 flag 的 experiment wrappers 產生，不進 selected KEM binary |
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

這個 `R^-1` 不是由 forward NTT 或 layout permutation 產生。Montgomery product
的 raw result 帶有 `R^-1`；normal `poly_basemul()` 在 finalizer 乘回 `R` 並做
center reduction，`poly_basemul_rminus1()` 則省略這段、直接 store raw result。
因為下一個 consumer 已知就是 inverse，rminus branchfold constants 可以把該
correction 與 `1/96` normalization、untwist 和 branch merge 一次完成。

KAT 結論必須帶上 pairing 條件：

| producer -> consumer | result / KAT |
| --- | --- |
| `poly_basemul -> poly_invntt` | normal contract，正確 |
| `poly_basemul_rminus1 -> poly_invntt_from_rminus1` | compensation 完整，與 normal pair byte-equivalent，KAT 正確 |
| `poly_basemul_rminus1 -> poly_invntt` | 少一個 factor correction，錯誤 |
| `poly_basemul -> poly_invntt_from_rminus1` | 多一個 fixed factor correction，錯誤 |

也就是「省掉 basemul final correction」單獨使用一定會改變結果；目前不影響
KAT，是因為 paired inverse 的 final constants 精確補回。Promotion gate 已包含
actual pipeline differential、full KEM、canonical `.rsp` hash 與 cross-vector
decapsulation，不只是 GT 自己 encapsulate/decapsulate 的 self-consistency。

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
| `50` | `INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH` | stage45 + row-end reduce fused Slothy schedule；input 從 `x14 + 64*j` stripe scratch load |
| `101` | `DIRECT_STAGE123_VEC` | 從 branch0/branch1 各 load `d`，合成一個 `q` vector |
| `107` | `STORE_STAGE123_STRIPE_SCRATCH` | stage123 output 寫成 `[j, j+8, j+16, j+24]` contiguous scratch |
| `129` | `DIRECT_STAGE123_BLOCK_TO_SCRATCH` | 8-vector block 的 stage1/2/3 butterflies；lazy flag 控制 multiplier=1 path |
| `185` | `DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY` | block-major row0 physical offset map |
| `203` | `DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY` | block-major row1 physical offset map |
| `217` | `DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY` | block-major row2 physical offset map |
| `231` | `TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY` | tuple input path；row 內 offset 是 `0,8,16,...,248` |
| `741` | `POST_STORE_PTR_BRANCHFOLD` | branchfold final merge + final output reductions + two `d` stores |
| `785` | `FUSED_POST_STRIPE` | inverse DFT3 + branchfold store 的 one-stripe body |
| `867` | `INVNTT_STACK_SIZE` / ABI macros | production rminus1 frame 擴充至 2144 bytes，保存 `d8-d15` |
| `920` | `gt_block_major_poly_invntt` | block-major public entry與三個 row 的 stage123/stage45 path |
| `999` | `gt_tuple_poly_invntt` | generic/experiment tuple input entry；rminus1 production 由 `INVNTT_BLOCK_MAJOR_ONLY` 排除 |
| `1090` | `L_invntt_post_tail` | common branchfold post loop、ABI restore 與 return |
| `1161` | `poly_invntt_stage45scratch` | exposed ABI prototype tail：input 已經是 stage123 stripe scratch |
| `1202` | `inv_consts` | q、Barrett precompute、DFT3 constants |
| `1207` | `invntt32_stage123_consts` | stage123 twiddles/precompute |
| `1212` | `invntt32_stage45_consts` | stage45 twiddles/precompute |
| `1241` | `inv_branchfold_vecs` | normal vs rminus1 branchfold table switch |

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
