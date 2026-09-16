# P3B35 — liveness audit and consumer-range investigation

## Decision and scope

Two separate gates completed against P3B34. P3B33 remains the fixed comparison
baseline. No assembly, production, scheduling or benchmark change in this gate.
This is a read-only kernel audit plus an isolated mathematical exploration,
using the SIMD understanding workflow and lattice range-proof workflow.

- **A:** 9 of 12 moves are individually eligible for local read substitution;
  3 of 53 constant loads have no live vector consumers.
- **B:** exact marginal reachable sets close one more deletion,
  `main.twist0`, under the existing [-3,4] coefficient contract.
  The other two deletions still fail; exact row-0 extrema demonstrate that
  the signed-int32 BaseMul risk is not merely an interval artifact under this
  contract/model.

## A — MOV liveness

The audit follows physical vector-register definitions and reads in the actual
straight-line one-bank helper. MLS reads its previous destination as well as
its explicit sources. Lane-specific constant reads are distinguished from
full-vector reads. The helper's 12 P3B33/P3B34 copy instructions are examined
until their destination version is overwritten.

| Parent source line | Copy | Individual local substitution |
|---:|---|---|
| 192 | v22 ← v28 | eligible |
| 293 | v2 ← v27 | eligible |
| 298 | v2 ← v24 | blocked: v24 overwritten before last read |
| 303 | v29 ← v22 | eligible |
| 306 | v0 ← v7 | eligible |
| 311 | v25 ← v9 | eligible |
| 316 | v10 ← v12 | eligible |
| 323 | v26 ← v21 | blocked: v21 overwritten before last read |
| 328 | v26 ← v11 | blocked: v11 overwritten before last read |
| 342 | v28 ← v29 | eligible |
| 354 | v27 ← v3 | eligible |
| 362 | v6 ← v8 | eligible |

Eligible means explicit read operands can use the original source while its
value is still available. It does **not** mean deleting the MOV line alone is
correct. Nor does nine individually safe substitutions establish that all nine
can be applied simultaneously without rerunning liveness: one rewrite can
change another copy's use set. Preserve the source as a baseline and prove
the combined transformed SSA graph before compiling.

If all nine can ultimately be combined without compensation, the arithmetic-
independent opportunity is 54 instructions per complete Forward. No cycle
prediction or demonstrated instruction saving is claimed here.

## A — constant liveness

The 53 x2/x3 table loads contain exactly three dead vector definitions:

| Parent line | Instruction | Explanation |
|---:|---|---|
| 187 | ldr q22, [x2], #16 | deleted tail stage-0 b vector |
| 188 | ldr q30, [x2], #16 | deleted tail stage-0 reciprocal vector |
| 291 | ldr q8, [x2], #16 | deleted main stage-0 identity constant pair |

These are 18 redundant q-vector reads / 288 table bytes per complete Forward
at the instruction-address level, not a claim about cache misses or DRAM traffic.
The remaining 50 loads have at least one read; unused individual lanes do not
make the entire load dead.

**Post-increment remains live.** Deleting these lines would shift subsequent
table reads. One conservative lowering is to replace lines 187/188 together
with `add x2,x2,#32`, and line 291 with `add x2,x2,#16`: three table loads gone
but only one net instruction saved per helper. Folding increments into a
nearby retained load or compacting tables is a separate address-equivalence
proof. Do not combine claimed load savings with MOV savings before lowering.

## B — initial M5C diagnostics

Retain all 13 P3B34 identity bypasses, then try each requested deletion alone.
The old affine-with-reset model reaches all 288 leaves but reports:

| Additional deletion | Violating leaves before refinement |
|---|---:|
| main.twist0 | 3 |
| main.stage1.node0 | 11 |
| main.stage2.node0 | 18 |

Every first violation is the third cubic accumulator:

    accum2 = a0*b2 + a1*b1 + a2*b0

It has no zeta term and is accumulated before D1's final reduction. A stronger
D1 output theorem alone cannot fix an overflowing producer.

## B — exact reachable-set refinement

Input contract: each natural coefficient is independently in [-3,4]. For each
top coefficient, enumerate all 64 low/high pairs exactly:

    top0 = low - 722*high
    top1 = low + 723*high

Do not replace these sparse sets by their convex intervals. Apply exact fixed
products and exact set sums/differences throughout each scalar NTT16 marginal.
The DIT tree operands at every butterfly derive from disjoint natural input
supports; the script asserts this structural property. This makes Minkowski
sum/difference exact for each output marginal. It does not assert different
NTT16 outputs are mutually independent. Integer-bitset convolution is checked
against brute-force sums/differences for 450 small-set cases.

For other NTT9 rows we retain the conservative affine-with-reset proof. For
row 0, the actual one-product DAG simplifies to `sum(f0,...,f8)` with no
reduction on that sum. The nine s producers have disjoint input coefficients,
so exact marginal extrema can be added. Every intervening NTT16 value is
checked as signed int16; existing NTT9 intermediate gates remain active.

### main.twist0: range gate passes

This is the t=0 input b=1 multiplication, not a nonidentity twist.

| Chain quantity | Refined bound |
|---|---:|
| Forward maximum intermediate | 26731 |
| M5C maximum absolute accumulator | 2143639083 |
| D1 BaseMul/BaseMulAdd domain | [-2095389628,2143665212] |
| D1 output | [-3023,3023] |
| M5E maximum halfword intermediate | 17220 |

The upper D1 input has only 3818435 of signed-int32 headroom; this is not a
license to delete another reduction. Existing P3B34 full-int16 serialization
and full-int32 D1 premises are reused. The next gate must lower this one
deletion independently and run object/differential/full-product tests. It has
not been added to the assembly or benchmarked.

### Other two: reachable extreme explains the accumulator problem

After exact marginal refinement, length-4 node 0 still has two violating
row-0 leaves; length-8 node 0 has eight. Examples:

| Deletion | (top,row,column) | Exact reachable leaf extrema | Attainable positive accum2 |
|---|---|---|---:|
| main.stage1.node0 | (0,0,8) | [-26952,26954] | 3 × 26954² = 2179554348 |
| main.stage2.node0 | (0,0,0) | [-29726,29589] | 3 × 29726² = 2650905228 |

Both exceed 2147483647. The three components are independently supplied by
disjoint input coefficients, and the two input polynomials can be equal.
Thus the same attainable extreme can populate all three components of both
operands, yielding these positive accumulators. This is a mathematical
attainability argument, not a recorded assembly overflow run or a materialized
864-coefficient witness file.

Therefore neither deletion is valid as a direct drop-in under the full [-3,4]
contract with this unchanged BaseMul DAG. This does not establish failure for
every narrower KEM-specific producer distribution. Narrowing that contract,
relocating a reduction, changing the leaf representation or widening BaseMul
would be separate experiments. More correlation analysis alone cannot remove
the reachable extremes shown here.

## Files and reproduction

```sh
python3 audit.py
python3 consumers.py
python3 reachable.py
```

- `audit.py`: instruction-definition/read ledger, scalar-lane usage, MOV and
  dead-load decisions, source SHA256.
- `consumers.py`: captures every leaf before the original M5C assertion and
  reports specific offending products/accumulators without disabling a gate.
- `reachable.py`: sparse-set NTT16 and exact row-0 extrema, then reruns the
  unchanged downstream gates.
- `build/liveness.json`: all 12 moves and all 53 constant loads with uses.
- `build/consumers.json`: old-model failure leaves.
- `build/reachable.json`: marginal cardinalities/ranges, exact row-0 extrema,
  remaining failures and source hashes.
- `build/reachable-main.twist0.json`: passing chain, affine edge records,
  atom domains and leaf intervals.

All generated files are gitignored; no remote sync, Slothy, cycle benchmark,
production edit or commit was performed. Keep the next copy/load cleanup and
the twist0 deletion as separate candidates so their benefits remain attributable.
