# InvNTT Prototype Archive

2026-06-25 cleanup 後，production wrapper 改 include：

```text
asm/gt/invntt/poly_invntt.n1.opt.inc
```

rowstage45/post fused prototypes、bench-only symbols、old gather / fastscale
相關 fragments 集中備份在：

```text
asm/slothy/archive/invntt_rowstage45_post_prototypes.s
```

這個 archive 不是 production include target；它只是保留實驗歷史，避免 production
主檔再混進不會用到的 flags。

## Archived fragments

| original range | archived content |
| --- | --- |
| `asm/slothy/legacy/invntt_opt.s:659-705` | fastscale final-store prototype |
| `asm/slothy/legacy/invntt_opt.s:828-1203` | post Slothy prototype helpers，包括 N1/A72 post stripe schedules |
| `asm/slothy/legacy/invntt_opt.s:1204-2399` | rowstage45/post fused prototype macros |
| `asm/slothy/legacy/invntt_opt.s:2459-2908` | prototype-specific stack size/prologue/entry blocks |
| `asm/slothy/legacy/invntt_opt.s:2924-2946` | old gather input materialization fallback |
| `asm/slothy/legacy/invntt_opt.s:3251-3503` | `INVNTT_BENCH_STAGES` bench-only symbols |
| `asm/slothy/legacy/invntt_opt.s:3511-3524` | old gather offset table |

## How to use it

如果之後要重新研究 rowstage45/post fusion，從 archive 找 dataflow 和 macro 名稱，
再另外建立新的 wrapper 或新的 production candidate。不要直接把 flags 加回
`poly_invntt.n1.opt.inc`；那個檔案應該維持「目前 KEM 真的會走」的路徑。
