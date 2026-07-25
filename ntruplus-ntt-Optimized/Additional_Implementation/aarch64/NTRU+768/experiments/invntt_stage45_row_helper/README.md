# InvNTT Stage45 Row Helper

Status: promoted as a production code-size tradeoff, not a cycle optimization.

The preceding production InvNTT expanded the same 331-instruction Stage45 row
body three times. This implementation emits that body once as a local helper
and replaces the three expansions with `bl` calls. It does not change
Stage123, Stage45 arithmetic, modular reduction, scratch layout, final
branchfold processing, or the public polynomial contract.

## Files

- `asm/gt/invntt/poly_invntt.n1.opt.inc`
  contains the default-off `INVNTT_USE_STAGE45_ROW_HELPER` switch.
- `asm/gt/experiment/invntt/poly_invntt_rminus1_stage45_row_helper.S`
  exposes the namespaced test candidate.
- `asm/gt/experiment/invntt/poly_invntt_rminus1_stage45_row_helper_dropin.S`
  is used only for isolated full-KEM measurement.
- `gt_test/test_invntt_stage45_row_helper.c`
  checks differential, in-place, and ABI behavior.
- `gt_bench/bench_invntt_stage45_row_helper_pmu.c`
  measures direct InvNTT with paired PMU cycles and instructions.

## Static result

| Artifact | Production | Helper | Delta |
|---|---:|---:|---:|
| InvNTT object `.text` | 16,352 B | 13,712 B | -2,640 B |
| Isolated full-KEM binary `.text` | 74,857 B | 72,233 B | -2,624 B |

The helper adds exactly three dynamic `bl` instructions and three `ret`
instructions per InvNTT. The production object built with the switch disabled
is byte-identical to the clean release:

```text
SHA-256 .text:
25710098310acdf2bd080733500ba47afff8a44dd1447b9db934487bbb8c70de
```

## Correctness and ABI

Pi 5:

```text
invntt_stage45_row_helper_mismatches=0
invntt_stage45_row_helper_abi_mask=0x0
```

The test covers 1024 reachable NTT-domain products, out-of-place and in-place
calls, and canaries for `x19-x28` plus the ABI-preserved low halves `d8-d15`.
The same-binary KEM harness also passed valid/invalid decapsulation checks:

```text
correctness,phase=paired,checks=366,mismatches=0
```

## Production decision

See
`../../../../../aarch64-bench/results/invntt_stage45_row_helper_2026-07-24/result.md`
for the raw comparison.

Direct InvNTT was 1.52 cycles faster in the paired median, despite retiring the
expected six extra instructions. Full decapsulation was consistently slower:

- same-binary paired median: `+11.75 cycles`, candidate wins `0/61`;
- isolated binaries with equal `poly_invntt` address: paired median
  approximately `+10.5 cycles`, candidate wins `2/8`.

The code-size reduction is real, while the current Pi 5 decapsulation path is
about 10-12 cycles slower. Production accepts this roughly 0.03% cycle cost to
remove about 2.6 KB of duplicated hot-kernel text. The result must therefore be
described as a code-size tradeoff, not as an InvNTT speedup.
