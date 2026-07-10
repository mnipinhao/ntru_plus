# U01v3 Stage12 -> Stage345 Contract

Date: 2026-07-09

## Stage Contract

The only fused boundary in U01v3 is:

```text
Stage12 out0 Q0..Q7 -> Stage345 block0 Q0..Q7 input
```

All other boundaries remain scratch based:

```text
Phase123 raw Q0..Q31 -> row-major scratch
Stage12 out1 Q8..Q15 -> scratch
Stage12 out2 Q16..Q23 -> scratch
Stage12 out3 Q24..Q31 -> scratch
```

The Stage345 block0 instruction stream is copied from the current production
block0 region.  Only its row loads are replaced by register handoff.

## Register Context

Wrapper live-ins:

```text
x19 = final scatter output base
x20 = input base
x21 = row-major scratch base
x22 = Phase123 twist table base
x23 = ntt32 twiddle table base
v0  = q/constants
```

Stage345 setup per row:

```text
x10 = out + row scatter offset
x14 = out + 768 byte wrap bound
x12 = ntt32 stage3 twiddle base = x23 + 64
```

Stage12 handoff registers:

```text
Q0 -> q29 -> Stage345 q29
Q1 -> q1  -> mov to Stage345 q6
Q2 -> q28 -> Stage345 q28
Q3 -> q17 -> Stage345 q17
Q4 -> q26 -> Stage345 q26
Q5 -> q5  -> Stage345 q5
Q6 -> q18 -> Stage345 q18
Q7 -> q8  -> Stage345 q8
```

Q1 uses `q1` because Stage345 block0 first uses `q6` as a twiddle register:

```asm
ldr q6, [x12], #16
...
mov v6.16b, v1.16b
```

The `mov` is placed exactly where the old `ldr q6, [x4,#16]` lived.

## Store/Load Replacement

For each row and each Q0..Q7:

```text
old:
  Stage12 stores out0 Qk to [scratch + row_base + 16*k]
  Stage345 later loads Qk from [x4 + 16*k]

new:
  Stage12 writes Qk directly into a handoff vector register
  Stage345 consumes that register
```

Deleted stores:

```text
row0 Q0..Q7 offsets    0..112
row1 Q0..Q7 offsets  512..624
row2 Q0..Q7 offsets 1024..1136
```

Deleted loads:

```text
Stage345 block0 offsets 0,16,32,48,64,80,96,112 for each row
```

The exact per-row map is machine-readable in:

```text
u01v3_layout_map.json
```

## Expected-vs-Actual Check

The correctness target compares final scatter output:

```text
P oracle:
  production source-order Phase123/Stage12 scratch
  -> Stage345 block0 from scratch

V baseline:
  U01v2 shared-prefix Phase123/Stage12 scratch
  -> Stage345 block0 from scratch

F candidate:
  shared-prefix raw Phase123 scratch
  -> Stage12 out0 Q0..Q7 in registers
  -> Stage345 block0 register handoff
```

The test initializes output buffers with the same sentinel and compares all 768
coefficients.  Only block0 scatter positions should change; all untouched
positions remain sentinel in both outputs.

ABI sentinel checks:

```text
x19-x28 unchanged
d8-d15 low 64-bit unchanged
```

## Cost Categories

Expected static changes inside the fused boundary:

```text
minus 24 q stores from Stage12 out0
minus 24 q loads from Stage345 block0
plus  3 vector moves for Q1 q1 -> q6
same Stage345 arithmetic
same final reduction
same scatter and scalar wrap chain
same high-half ext+str sequence
```

Because this is not Slothy-rescheduled, any win comes from removing the
boundary memory operations directly.  If PMU is flat, the next explanation is
store/load latency not being on the critical path or the added live ranges
hurting local scheduling.
