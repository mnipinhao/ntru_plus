# U01v3 Track H2 Consumer-Driven Producer-Order Model

Status: model-only. No ASM emitted, no Slothy run, and production defaults are unchanged.

## Derived producer contract

The existing U01v2 symbolic body executes Phase123 iterations in `0,2,4,6,1,3,5,7` order. Each iteration computes one shared prefix and four DFT3 raw slots. Mechanically extracted per iteration:

```text
shared prefix instructions: 104
four raw-slot groups: 52 instructions (40 arithmetic + 12 stores)
fixed-base wrapper setup: 5 instructions
tail pointer instructions: 4
total per iteration in U01v2/G1 shape: 165
```

One Stage12 stripe always needs four raw values produced by four different Phase123 iterations:

```text
stripe0: A/B/C/D=Q0/Q8/Q16/Q24 from iter [0, 2, 4, 6] slot 0
stripe1: A/B/C/D=Q1/Q9/Q17/Q25 from iter [0, 2, 4, 6] slot 1
stripe2: A/B/C/D=Q2/Q10/Q18/Q26 from iter [0, 2, 4, 6] slot 2
stripe3: A/B/C/D=Q3/Q11/Q19/Q27 from iter [0, 2, 4, 6] slot 3
stripe4: A/B/C/D=Q4/Q12/Q20/Q28 from iter [1, 3, 5, 7] slot 0
stripe5: A/B/C/D=Q5/Q13/Q21/Q29 from iter [1, 3, 5, 7] slot 1
stripe6: A/B/C/D=Q6/Q14/Q22/Q30 from iter [1, 3, 5, 7] slot 2
stripe7: A/B/C/D=Q7/Q15/Q23/Q31 from iter [1, 3, 5, 7] slot 3
```

The Stage12 semantic split is:

```text
t0 = reduce(B + D)       out0 = t2 + t0
t1 = twist_reduce(B-D)   out1 = t2 - t0
t2 = A + C               out2 = t3 + t1
t3 = A - C               out3 = t3 - t1
```

This is why pair-major is the natural split: blocks0/1 share `t0,t2`, and blocks2/3 share `t1,t3`. Strict block-major throws away that sharing.

## Candidate comparison

All counts cover three rows and eight stripes. Removed loads/stores are the 24 G1 block3 Stage345 loads and 24 Stage12 out3 stores.

| Candidate | Extra arithmetic | Removed q load/store | Raw q reloads | Max live q | Instr delta vs G1 | Gate |
|---|---:|---:|---:|---:|---:|---|
| H2a | 216 | 24 / 24 | 288 | 16 | +483 | fail |
| H2b | 0 | 24 / 24 | 96 | 29 | +57 | fail |
| H2c | 144 | 24 / 24 | 96 | 31 | +201 | fail |

### H2a strict block-major

Four branch-specific Stage12 passes cost 22 arithmetic instructions per stripe instead of 13. It reloads A/B/C/D three extra times, so the result is `+483` instructions versus G1 even after removing the block3 store/load boundary. Regenerating Phase123 instead would be worse: three extra full passes cost about 3960 instructions.

### H2b pair-major 01 then 23

This preserves all Stage12 arithmetic sharing: `6 + 7 = 13` instructions per stripe. Its blocker is memory lifetime. After Stage345 blocks0/1 consume the first pair, the second pair needs the same A/B/C/D again, adding exactly 96 raw-q reloads and 9 twiddle loads. Net estimate is `+57` instructions versus G1. Register count looks plausible, but the candidate fails Track H's explicit no-96-reload gate.

### H2c hybrid E3/F012 plus reordered out3

Under the existing lifetime this is the already-modelled G3a shape. E3 leaves raw A/B/C in scratch but overwrites D with out3. Delaying out3 preserves D, then later reloads all A/B/C/D and rebuilds the out3 cone: 96 raw reloads, 144 arithmetic instructions, and `+201` instructions versus G1. Keeping an eight-vector basis in registers instead reserves 24 future values at Stage345 block0, leaving 7 colors for a block whose SSA needs 15.

## Decision

```text
hard-gate passing H2 candidates: none
emit H2 ASM: no
least-bad model: H2b pair-major, +57 instructions vs G1
reason: H2b still reintroduces the rejected 96-vector raw-q reload pass
```

Consumer order by itself does not solve the source lifetime. A viable Track H candidate must either delay the destructive source overwrite without extending 24 future live values (H1), or identify a smaller register-resident reconstruction basis (H3).
