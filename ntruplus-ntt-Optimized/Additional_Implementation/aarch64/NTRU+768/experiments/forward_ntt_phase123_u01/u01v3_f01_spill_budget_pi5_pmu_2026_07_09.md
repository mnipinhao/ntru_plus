# U01v3 F01 Spill-Budget Pi5 Result

Date: 2026-07-09

Status: experiment-only.  Production defaults were not changed.

## Variants

Budget definition: number of block1 handoff vectors per row preserved across
unchanged Stage345 block0.

| variant | status | budget/row | q spills | q restores | extra raw q reloads | duplicate Stage12 |
|---|---:|---:|---:|---:|---:|---:|
| Bmin | feasible, same as minimum | 8 | 24 | 24 | 0 | no |
| B2 | infeasible | 2 | n/a | n/a | n/a | n/a |
| B4 | infeasible | 4 | n/a | n/a | n/a | n/a |
| B8 | feasible | 8 | 24 | 24 | 0 | no |

B2 and B4 are not emitted as performance candidates because Stage345 block0
clobbers all eight block1 live-ins: `q10 q20 q30 q24 q9 q6 q31 q23`.

## Pi5 Correctness

Standalone correctness/ABI test:

```text
u01v3_f01_spill_budget_abi_mask=0x0
u01v3_f01_spill_budget_mismatches=0
mismatches = 0
```

PMU harness correctness, `NVALID_ORACLE=4096`:

```text
Bmin total_mismatches=0
B8   total_mismatches=0
```

## Pi5 PMU

Settings:

```text
taskset -c 3
NTESTS=61
NITERATIONS=20000
NWARMUP=300
NINPUTS=64
NVALID_ORACLE=4096
```

| variant | cycles | instructions | CPI | vs P | vs V | vs F0 | vs F1 | addr mod32/mod64 | text |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P | 2047 | 2850 | 0.718246 | 0 | -26 | -10 | -15 | 16 / 16 | 11288 |
| V | 2073 | 2890 | 0.717301 | +26 | 0 | +16 | +11 | 0 / 32 | 11448 |
| F0 | 2057 | 2842 | 0.723786 | +10 | -16 | 0 | -5 | 16 / 16 | 11256 |
| F1 | 2062 | 2842 | 0.725545 | +15 | -11 | +5 | 0 | 0 / 0 | 11256 |
| Bmin | 2057 | 2842 | 0.723786 | +10 | -16 | 0 | -5 | 16 / 48 | 11256 |
| B8 | 2057 | 2842 | 0.723786 | +10 | -16 | 0 | -5 | 0 / 32 | 11256 |

Interpretation: Bmin/B8 are correct one-pass F01 spill-budget candidates, but
with unchanged Stage345 block0 they do not beat the F0 envelope. The block1
scratch boundary is replaced by stack spill/restore traffic one-for-one, so the
instruction count and measured cycles match F0 within this run.
