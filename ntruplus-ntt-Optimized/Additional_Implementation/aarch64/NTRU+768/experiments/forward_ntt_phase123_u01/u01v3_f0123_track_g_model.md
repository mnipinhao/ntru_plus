# U01v3 F0123 Track G Model

Status: model generated after E4 live-all failure. Production default unchanged.

Summary:

```text
E3 current best: F012 semantic-regalloc
q0 reserved: True
data regs with q0 reserved: 31
Stage345 block0 max-live: 15
G2 future regs reserved for block0: 23
G2 available block0 colors: 8
```

G1 delayed block3 scratch-consume:

```text
status: model_promising
extra_arithmetic_vs_E3: 0
extra_q_loads_vs_E3: 24
q_spills_restores: 0
expected_instruction_delta_vs_E3: 486
```

G2 one-vector spill live-all:

```text
status: infeasible
q_spills_restores: 1
block0_stage345_max_live: 15
available_block0_colors: 8
available_minus_required: -7
```

The important point is that one spill solves the global 32-output vs 31-data-register count, but it does not solve cross-block preservation. With block1+block2+block3 live-ins reserved, Stage345 block0 would have only 8 available q colors while its SSA max-live is 15.

G3 partial shared-prefix / controlled recompute:

```text
status: model_only
feasible_under_q0_reserved: likely, if it avoids keeping block3 live across block0
```

Decision:

```text
Do not build G2_spill1 live-all ASM under current rules.
Build G1_delayed_block3 scratch-consume as the bounded Track G prototype.
Keep G3 model-only until G1 PMU says scratch-consume is not enough.
```
