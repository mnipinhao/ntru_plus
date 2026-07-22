# InvNTT Stage123 pair-pipeline experiment

Status: experiment-only, default-off.

This experiment schedules two adjacent inverse-NTT32 Stage123 groups as one
window. It keeps the production rminus1 arithmetic, lazy-twiddle proof scope,
stripe-scratch layout, Stage45 body, post path, and ABI unchanged. The only
intended change is to overlap group N+1's fixed public-offset input loads with
group N's butterfly and modular-multiply chain.

The first candidate does not remove any of the 96 Stage123 stores or 96
Stage45 reloads. That boundary remains visible so this experiment can answer a
narrow question: does cross-group scheduling alone reduce Pi 5 cycles?

The symbolic source spells full-vector copies as
`orr vD.16b, vS.16b, vS.16b`. This is the architectural canonical form of the
`mov vD.16b, vS.16b` alias used by production and has the same encoding and
dataflow. The spelling avoids a Slothy generic-MOV datatype parser failure; it
is not an arithmetic or instruction-count change.

Each pair is scheduled in two explicit solver windows. The 83-instruction
`xover` window contains group N arithmetic/stores and group N+1 load assembly;
this is the only range that can hide the next group's loads. The 59-instruction
`tail` window schedules group N+1 arithmetic/stores without forcing Slothy to
repeatedly prove a 166-instruction whole-pair optimum.

Artifacts follow the existing-region Slothy workflow:

```text
baseline-row0-pair01.S
baseline-contract.yml
kernel-contract.yml
instruction-dag.yml
stage123_pair_pipeline.sym.S
optimize_stage123_pair_pipeline.py
stage123_pair_pipeline.opt.S
stage123_pair_pipeline.opt.inc
candidate-contract.yml
```

No candidate may be selected from N1 expected cycles alone. Required gates are
the rminus1 differential test, ABI sentinel, direct InvNTT PMU, decap-context
PMU, and full decapsulation non-regression.

## Pi 5 result (2026-07-20)

The candidate passed 516-case differential testing, in-place testing, and the
AAPCS64 sentinel (`mismatches=0`, `abi_mask=0x0`). Core-pinned paired PMU did
not show a performance win:

| Variant | Cycles | Instructions | Paired delta vs production |
|---|---:|---:|---:|
| promoted production | 3558.52 | 4814 | 0.00 |
| Stage123 pair pipeline | 3559.23 | 4814 | +0.71 |

Decision: reject for production. Distinct registers remove the artificial
cross-group dependency, but the existing Cortex-A76 out-of-order schedule
already hides enough of this boundary that full InvNTT cycles remain flat.
