# Forward NTT Stage345 Block0 Live-In Contract

Date: 2026-07-09

Status:

```text
investigate
boundary contract plus symbolic pressure-test candidate
no production asm changed
Slothy N1 no-split reached OPTIMAL 100 cycles but failed to emit opt file
```

## Goal

The current production boundary is:

```text
Stage12 stripes0..7 produce post-stage12 Q0..Q7
Stage12 stores Q0..Q7 to row scratch
Stage345 block0 loads Q0..Q7 from row scratch
```

The experiment asks whether we can replace that with:

```text
Stage12 stripes0..7 produce post-stage12 Q0..Q7
Stage345 block0 consumes Q0..Q7 as live inputs
```

This is only for block0 first.  Blocks1/2/3 still need their values from
`out1/out2/out3`.

## Production Load Contract

Audit script:

```text
experiments/forward_ntt_phase123_u01/derive_stage345_block0_livein_contract.py
```

Result:

```text
stage345_block0_livein_contract_ok
```

Production Stage345 block0 currently loads these row-base inputs:

| Stage345 input | memory source | logical Q | producer |
|---|---:|---:|---|
| `q29` | `[x4,#0]` | Q0 | Stage12 stripe0 out0 |
| `q6` | `[x4,#16]` | Q1 | Stage12 stripe1 out0 |
| `q28` | `[x4,#32]` | Q2 | Stage12 stripe2 out0 |
| `q17` | `[x4,#48]` | Q3 | Stage12 stripe3 out0 |
| `q26` | `[x4,#64]` | Q4 | Stage12 stripe4 out0 |
| `q5` | `[x4,#80]` | Q5 | Stage12 stripe5 out0 |
| `q18` | `[x4,#96]` | Q6 | Stage12 stripe6 out0 |
| `q8` | `[x4,#112]` | Q7 | Stage12 stripe7 out0 |

The load order is not Q order because Slothy scheduled it for latency:

```text
Q7, Q5, Q3, Q6, Q4, Q2, Q1, Q0
```

But the set is exactly:

```text
Q0..Q7
```

## Meaning Of `out0/q22 -> block0 input`

In the source-order Stage12 scaffold, every stripe has four outputs:

```text
out0 = q22 -> Q[s]
out1 = q23 -> Q[s+8]
out2 = q26 -> Q[s+16]
out3 = q27 -> Q[s+24]
```

Therefore:

```text
stripe0 out0 -> Q0
stripe1 out0 -> Q1
stripe2 out0 -> Q2
stripe3 out0 -> Q3
stripe4 out0 -> Q4
stripe5 out0 -> Q5
stripe6 out0 -> Q6
stripe7 out0 -> Q7
```

Those eight `out0` values are exactly Stage345 block0 inputs.

## Proposed Replacement

The direct replacement contract is:

| logical Q | current Stage345 register | current load | proposed producer |
|---:|---|---|---|
| Q0 | `q29` | `ldr q29, [x4,#0]` | Stage12 stripe0 out0 |
| Q1 | `q6` | `ldr q6, [x4,#16]` | Stage12 stripe1 out0 |
| Q2 | `q28` | `ldr q28, [x4,#32]` | Stage12 stripe2 out0 |
| Q3 | `q17` | `ldr q17, [x4,#48]` | Stage12 stripe3 out0 |
| Q4 | `q26` | `ldr q26, [x4,#64]` | Stage12 stripe4 out0 |
| Q5 | `q5` | `ldr q5, [x4,#80]` | Stage12 stripe5 out0 |
| Q6 | `q18` | `ldr q18, [x4,#96]` | Stage12 stripe6 out0 |
| Q7 | `q8` | `ldr q8, [x4,#112]` | Stage12 stripe7 out0 |

In a symbolic version, these should not be physical registers.  They should be
symbolic live-ins such as:

```text
Q<b0_q0> ... Q<b0_q7>
```

Then Stage345 block0 should be rewritten to consume those symbolic values
instead of performing the eight row-base loads.

## Cost Hypothesis

Potential saving for one row/block0:

```text
remove 8 Q stores from Stage12 out0 hot path
remove 8 Q loads from Stage345 block0 input
```

But this is not free:

```text
Q0..Q7 must stay live across the boundary
Stage345 block0 already has high vector pressure
the current production block0 has Slothy spills/restores
```

So this is a pressure tradeoff:

```text
less memory traffic
more live vectors
possibly harder scheduling
```

## Symbolic Pressure-Test Candidate

The next cut has now been generated under:

```text
experiments/forward_ntt_phase123_u01/stage345_block0_livein/
```

Files:

```text
baseline-stage345-block0.s
baseline-contract.yml
kernel-contract.yml
instruction-dag.yml
candidate-contract.yml
generate_stage345_block0_livein.py
candidate-stage345-block0-livein.sym.S
optimize_stage345_block0_livein.py
```

The baseline is the exact production Slothy region:

```text
_gt_ntt32_batch8_ct_stage345_block0_slothy_start
_gt_ntt32_batch8_ct_stage345_block0_slothy_end
```

Baseline static shape:

```text
instructions = 167
loads        = 19
stores       = 23
Slothy annotation expected cycles = 55
```

The candidate removes only the eight row scratch loads:

```text
ldr q29, [x4,#0]
ldr q6,  [x4,#16]
ldr q28, [x4,#32]
ldr q17, [x4,#48]
ldr q26, [x4,#64]
ldr q5,  [x4,#80]
ldr q18, [x4,#96]
ldr q8,  [x4,#112]
```

and replaces them with symbolic live-ins:

```text
V<b0_q0>..V<b0_q7>
```

Candidate static shape:

```text
instructions = 159
loads        = 11
stores       = 23
symbolic values = 77
```

Local gates:

```text
baseline contract: pass
kernel contract: pass
candidate contract: pass
physical register leak: pass
symbolic asm: 0 errors, 8 srshr classifier warnings
```

The `srshr` warnings are from the local checker not classifying `srshr` as a
destination-defining instruction.  The candidate preamble explicitly lists the
`srshr` outputs so the use-before-def check stays clean.  This is a checker
limitation, not an arithmetic or layout change.

## Slothy Results On Remote Host

Remote host:

```text
ssh -p 51208 pinhao@172.25.166.141
```

Remote Slothy path:

```text
/home/pinhao/slothy
```

Target availability:

```text
n1: available as slothy.targets.aarch64.neoverse_n1_experimental
a76: not available; cortex_a76 and cortex_a76_frontend modules are missing
```

Run summary:

| log | mode | result |
|---|---|---|
| `slothy_stage345_block0_livein_n1.log` | split heuristic | failed before scheduling; chunk live-out `b0_q*` virtual output type ambiguous |
| `slothy_stage345_block0_livein_n1_nosplit.log` | no split | OPTIMAL, expected 100 cycles, then result extraction `AssertionError`; no `.opt.s` |
| `slothy_stage345_block0_livein_n1_nosplit_keep_tw0.log` | no split, keep `tw0` output | OPTIMAL, expected 100 cycles, then same extraction `AssertionError`; no `.opt.s` |
| `slothy_stage345_block0_livein_n1_nosplit_keep_outputs.log` | no split, conservative outputs | OPTIMAL, expected 100 cycles, then same extraction `AssertionError`; no `.opt.s` |
| `slothy_stage345_block0_livein_a76_nosplit.log` | no split, A76 target | failed at import; A76 target module not present |

Important interpretation:

```text
production Stage345 block0 annotation = 55 expected cycles
live-in block0 no-split N1 estimate  = 100 expected cycles
```

This is not a promotable Slothy artifact because no `.opt.s` was emitted.
However, the scheduler still found an optimal 100-cycle solution before result
extraction failed.  That is already much worse than the production 55-cycle
block0 schedule, even though the live-in candidate removes 8 row scratch loads.

Current conclusion:

```text
The Stage12->Stage345 block0 live-in route is not promising in this shape.
The saved memory traffic is outweighed by the Stage345 live-vector pressure and
the scheduling constraints.
```

Contract comparison is intentionally not preserved:

```text
production baseline consumes Q0..Q7 from x4 row scratch memory
candidate consumes Q0..Q7 from live symbolic vectors
```

Therefore this candidate is not a drop-in production splice.  It is only a
pressure test for a later fused producer.

## Slothy Handoff

Remote Slothy host requested by the user:

```text
ssh -p 51208 pinhao@172.25.166.141
```

Attempt on 2026-07-09:

```text
ssh -p 51208 -o BatchMode=yes -o ConnectTimeout=10 pinhao@172.25.166.141 pwd
ssh: connect to host 172.25.166.141 port 51208: Operation timed out
```

When the host is reachable, run from the candidate directory after syncing the
files:

```text
cd ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/forward_ntt_phase123_u01/stage345_block0_livein
python3 optimize_stage345_block0_livein.py \
  --input candidate-stage345-block0-livein.sym.S \
  --output candidate-stage345-block0-livein.n1.opt.s \
  --target n1
```

If Slothy cannot allocate without spills, or if the expected cycles are worse
than the production 55-cycle block despite removing 8 loads, then full
Stage12->Stage345 fusion is likely not worth pushing.

## Original Next Cut

Do not feed the full 1978-line block0-first scaffold to Slothy.

The next useful cut is:

```text
1. Extract Stage345 block0 as a symbolic region.
2. Replace only its eight `[x4,#0..112]` data loads with symbolic live-ins.
3. Keep twiddle loads and scalar scatter logic unchanged.
4. Compare static shape and Slothy pressure before trying to fuse Stage12.
```

If that symbolic block0 cannot schedule cleanly even with live-ins, then the
full Stage12->Stage345 fusion is unlikely to win.
