# Forward NTT Production Reading Guide

這份文件是目前 `gt_production_opt`、`gt_production_opt_rminus1`
forward NTT 的讀碼索引。production 主檔是：

```text
asm/gt/my_ntt.s
```

`asm/gt/my_ntt.s` 現在只保留 production path。舊的 GAS `PHASE123_ITER`
fallback、`NTT32_FUSED_SCATTER=0` row-buffer scatter fallback、Phase123 A/B/C
experiment selector 都已經不在主檔裡。

## Production wrappers

| wrapper | 產生的 symbol | 用途 |
| --- | --- | --- |
| `asm/gt/my_ntt_phase123_n1.s` | `poly_ntt`, `gt_block_major_poly_ntt` | normal GT production forward NTT |

## Active selectors

| selector | 現在意思 |
| --- | --- |
| `MY_NTT_DARWIN_NO_WEAK` | Apple assembler path；用 `.global` 取代 weak alias |

不再使用：

| old selector/path | 狀態 |
| --- | --- |
| `MY_NTT_USE_PHASE123_N1` | 移除；`asm/gt/my_ntt.s` 固定 include production Phase123 N1 schedule |
| `MY_NTT_PHASE123_EXPERIMENT_A/B/C` | 移除；A/B/C benchmark 沒有優於 baseline |
| `NTT32_FUSED_SCATTER` | 移除；production 固定 fused-scatter row kernel |
| `_scatter_ntt32_row` | 移除；舊 row-buffer fallback，不是目前 KEM 路徑 |
| `MY_NTT_DIRECT_TUPLE` / direct-tuple wrapper | 移除；direct-tuple / TMVP experiment path 已退場 |

## Forward data flow

Normal GT production：

```text
poly input
  -> asm/gt/my_ntt.s prologue
  -> asm/slothy/my_ntt_phase123.n1.opt.s
       natural input -> GT split/twist/DFT3 -> three row scratch buffers
  -> asm/slothy/my_32ntt.opt.s::_ntt32_8way, called once per row
       NTT32 stage1..5 -> block-major final store
  -> GT block-major NTT-domain polynomial
```

## Production file line map

| line | 段落 | 要看什麼 |
| --- | --- | --- |
| `1` | file header | production path 與移除的舊路徑 |
| `14` | `CALL_NTT32_8WAY` | normal `_ntt32_8way` call |
| `25` | frame constants | 3 row scratch buffers + saved destination slot |
| `28` | symbol alias block | `poly_ntt` / `gt_block_major_poly_ntt` |
| `54` | register aliases | public ABI: `x0=dst`, `x1=src` |
| `62` | prologue | constants load、callee-saved SIMD 保存、stack frame |
| `74` | scratch setup | `row0=sp+32`, `row1=sp+544`, `row2=sp+1056` |
| `79` | Phase123 include | `asm/slothy/my_ntt_phase123.n1.opt.s` |
| `81` | NTT32 row calls | 三個 row 依序呼叫 row kernel，output offset 是 `0/256/512` |
| `100` | epilogue | restore stack/GPR/SIMD |
| `108` | `zetas` | q、Barrett/Montgomery/DFT3 constants packed in `q0` |
| `112` | `twist_table` | Phase123 scheduled region 消耗的 twist/precompute table |

Generated files：

| file | line | 用途 |
| --- | ---: | --- |
| `asm/slothy/my_ntt_phase123.n1.opt.s` | `4`..`2682` | Phase123 N1 scheduled body |
| `asm/slothy/my_32ntt.opt.s` | `81` | normal block-major `_ntt32_8way` entry |
| `asm/slothy/my_ntt_phase123_flat.sym.s` | full file | Phase123 Slothy symbolic/regeneration source |

## Phase123 A/B/C experiment status

2026-06-25 量測結果：

| variant | KEYGEN | ENCAP | DECAP | `poly_ntt` profiler | decision |
| --- | ---: | ---: | ---: | ---: | --- |
| baseline | 923 | 894 | 744 | 59 | keep |
| A: no-writeback twist load | 923 | 893 | 745 | 59 | neutral |
| B: zip/DFT3 triad streaming | 924 | 893 | 744 | 59-60 | neutral |
| C: full triad streaming | 926 | 895 | 745 | 60-61 | slower |

A/B/C 沒有比 baseline 好，所以不保留在 production 主檔，也不再保留未追蹤
的 generated experiment tree。之後若要重開 Phase123 排程，從
`asm/slothy/my_ntt_phase123_flat.sym.s` 和 `asm/slothy/optimize_phase123_split.py`
開始，而不是把 selector 加回 `asm/gt/my_ntt.s`。
