# P3B6 ToBytes optimization audit

## Fixed contract

The input is the 864 signed-int16 coefficients in the current GT FR0 physical
layout.  The output is exactly the 1296-byte AArch64 serialization ABI,
including the effect of `poly_shuffle2_asm`.  The composed-map digest is
`087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270`.

Do not specialize the serializer to the Forward NTT16 bound of 9342.  ToBytes
has several real KEM producers (`h`, `f`, `hinv`, `r`, `c`, `r1`, and `r2`),
so the local boundary continues to accept every signed-int16 value.

## Measured baseline

P3B6 takes 1502.463 cycles and retires 2769.060 instructions on the Pi 5
Cortex-A76, versus 1848.172 cycles and 4360.060 instructions for P3B4 `r9_to`.
Its measured IPC is approximately 1.843.  The generated core is called once
per 432-coefficient top.

GCC's exact per-top opcode histogram is:

| opcode | count |
| --- | ---: |
| `mov` | 501 |
| `add` | 160 |
| `ldr` | 56 |
| each of `uzp1/uzp2/ushr/shl/orr/tbl` | 54 |
| each of `sqrdmulh/mls/cmlt/and` | 54 |
| `st1` | 54 |
| `str` / `stur` | 27 / 27 |
| ABI `stp` / `ldp` | 4 / 4 |

This identifies three large local costs:

1. 432 lane insertions per top, plus vector initialization/copies;
2. one normalization and one six-operation packing sequence per output q-vector;
3. address materialization and two stores per twelve-byte output.

## P3B7: faithful-lowering shootout

This is the next implementation gate.  It must retain the exact map, arbitrary
signed-int16 correctness, input-once memory contract, output bytes, and no-spill
contract.  Emit cumulative variants so each saving is attributable.

### L1: two-instruction sign correction

After `sqrdmulh` and `mls`, the residual over all 65536 signed-int16 inputs is
in `[-3291,3291]`.  Replace:

```text
cmlt mask, residual, #0
and  mask, mask, q
add  residual, residual, mask
```

with:

```text
sshr mask, residual, #15
mls  residual, mask, q
```

For a negative residual, `mask=-1`, so `mls` computes
`residual - (-1)*q = residual+q`.  For a nonnegative residual, `mask=0`.
Exhaustive machine checking proves identical canonical outputs `[0,3456]` for
all 65536 inputs.  Static target: remove 108 instructions per complete call.

### L2: initialize an output with its first real lane

The current generated C clears every new partial output and then inserts its
first coefficient.  Use one `dup` of that first source lane instead.  The seven
irrelevant duplicated lanes are overwritten by the remaining seven inputs.
Static target: remove another 108 instructions per complete call.

### L3: direct input addressing and one outer ABI frame

Current inline assembly makes GCC materialize `in+offset` with an `add` before
almost every `ldr q`.  Every input offset is a public aligned immediate that is
directly encodable by AArch64 `ldr q, [base,#imm]`.  Generate that addressing
form directly.  Also place both tops under one outer function so `d8-d15` are
saved and restored once rather than once per top.

Static target: remove about 108 input-address `add` instructions and eight
duplicated ABI save/restore instructions per complete call.  Output-address
changes are a separate gate because `ST1 lane` has no immediate-offset form.

Combined L1-L3 should reduce roughly 324 arithmetic/address instructions plus
the duplicated frame from the measured 2769-instruction body.  Cycles cannot
be inferred directly because integer address work overlaps vector work.
Measure every cumulative variant on the same paired PMU harness.

P3B7 passes only if it remains spill-free and reaches below 1350 cycles.  The
global promotion threshold remains below 1250 cycles.

## Packing and routing findings

Blindly batching final packing is not register-feasible under the present
input-once schedule.  Waiting for consecutive output groups before freeing
registers gives greedy live-output peaks of 32, 52, 54, and 54 vectors for
batch widths 2, 4, 6, and 8.  Independently computing each eight-output batch
would require 336 input q-loads per top instead of 54.  These two naïve forms
are rejected before assembly.

The remaining high-upside directions are therefore:

1. **Structured route synthesis.** Replace a significant part of the 864
   full-call lane `mov` network with `TRN/ZIP/UZP/EXT/TBL` subnetworks while
   preserving input-once behavior.  This needs an exact graph search; the old
   route9 kernel cannot simply be pasted in because composing `shuffle2`
   changes the graph to two 54-by-54 degree-eight components.
2. **Single-vector pack lowering.** Search equivalent 8-coefficient-to-12-byte
   instruction sequences using `SLI/SRI`, and separately investigate paired
   output stores.  A candidate must reduce real instructions, not only source
   intrinsics, and must preserve the final guarded 12-byte tail.
3. **Cross-stage byte-friendly ABI.** Let Forward/BaseMul/FromBytes/Inverse use
   a physical leaf order closer to the post-`shuffle2` byte order.  This could
   remove most routing, but it is a separate transform-domain ABI campaign,
   not a local ToBytes experiment, and must be priced across the complete KEM.

Recommended order: P3B7 faithful lowering, then a structured-route synthesis
gate.  Only if their combined result remains above 1250 cycles should the much
larger cross-stage ABI campaign be opened.
