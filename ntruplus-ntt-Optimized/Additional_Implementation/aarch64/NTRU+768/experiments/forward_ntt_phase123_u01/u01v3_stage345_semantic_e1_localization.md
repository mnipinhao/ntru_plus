# U01v3 Track E E1 Differential Localization

Status: harness generated and run on Pi5. Production default is unchanged.

The localization harness compares `E0 semantic reproduction` with `E1 preserve-liveins` and records four source-order Stage345 block0 checkpoints per row: Stage3 exit, Stage4 exit, Stage5 exit, and block0 exit. Each checkpoint dumps `q0..q31` plus block1 scratch slots `Q8..Q15`.

Important caveat: E1 intentionally renames physical registers, so the first raw q-register difference is not automatically the semantic bug. It is a locator. The decisive correctness signal remains the final block0/block1 output mismatch; the contract JSON maps which registers are live-ins, temps, live-outs, or parked values.

Observed Pi5 localization run:

```text
first_debug_diff row0 stage3_exit q1 lane0: e0=0 e1=911
u01v3_stage345_semantic_e1_localize_debug_diff=1
u01v3_stage345_semantic_e1_localize_final_mismatches=144
```
