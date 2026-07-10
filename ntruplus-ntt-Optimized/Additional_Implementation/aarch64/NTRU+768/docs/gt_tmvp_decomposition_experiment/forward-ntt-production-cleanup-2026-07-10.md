# Forward NTT Production Cleanup

日期：2026-07-10

## Active production

- `asm/gt/poly_ntt_g1_r123_s2.S`
- `asm/gt/poly_ntt_g1_r123_s2_tables.inc`
- `asm/slothy/production/my_32ntt.opt.s`

`my_32ntt.opt.s` 仍需連結，因為 specialized keypair triple NTT 會呼叫
`_ntt32_8way`；promoted generic `poly_ntt` 本身沒有這個 call boundary。

Legacy regression path：

```text
GT_PRODUCTION_USE_LEGACY_NTT=1
```

## Retained provenance

- G1、G1+S2、G1R123、G1R123+S2 四個獨立 ASM variants。
- final differential/ABI tests：`test_u01v3_g1_fullpath`、
  `test_u01v3_g1_reduction_slothy`。
- R123 Slothy input/output/log/contract。
- same-binary paired KEM harness 與三方 full-KEM benchmark。
- `experiments/forward_ntt_phase123_u01` generator、semantic-regalloc、layout
  contract 與歷史結果；這是 production provenance，不是 active link path。

## Removed experiment artifacts

- rowspec direct-offset、D1-D5、S1-S4 generated ASM/Slothy outputs。
- st1 lane、twiddle1 lazy reduction、twiddle-offset experiments。
- rowspec correctness/ABI/PMU harness 與舊 S2/S4 result directories。
- U01 block0/block1/block01/F012/F0123/E-stage intermediate ASM、tests 與 PMU
  harness；生成器與 semantic contracts 保留。
- generated binaries、dependency files、Python `__pycache__`。

Active Makefiles 不再列出被刪除的 target。整理約移除 25 MB 的 generated
experiment artifacts，production/default、legacy regression、final hardening 與
reproducibility 路徑都保留。
