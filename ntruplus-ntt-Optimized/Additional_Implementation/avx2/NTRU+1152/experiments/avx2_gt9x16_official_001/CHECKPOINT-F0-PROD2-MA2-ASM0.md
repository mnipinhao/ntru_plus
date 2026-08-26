# Checkpoint F0-PROD2-MA2-ASM0

## Outcome

The selected materialized P2-B realization is implemented and correctness
qualified. It keeps the coefficient-domain input, top split, formation, paper
R2, D1 arithmetic/routing, physical P traversal, reductions, and scale exactly
as P1-H. Only the final D1 redeposit changes:

```text
F0-semantic transform
-> D1 final registers
-> 72 local vperm2i128 per forward
-> 72 aligned MA2 coefficient-plane stores
-> 2,304-byte materialized boundary
-> MA2-native loads
```

There is no live-register D1-to-MA2 fusion and no KEM integration in this
checkpoint.

## Physical ABI vocabulary

The checkpoint distinguishes three different objects:

- `F0-semantic transform`: the mathematical scale-four transform.
- `F0-generic physical ABI`: P1-H vectors containing two terminal-coefficient
  halves.
- `F0-MA2 physical ABI`: one `(branch,p,terminal-coefficient)` owner per YMM,
  with all sixteen physical-q leaves in inherited bit-reversed identity order.

P2-B produces the third object directly. Its P order remains the paper-R2
semantic order, its scale is four, its Montgomery exponent is zero, and its
exact signed-i16 envelope remains `[-20751,20753]`.

## Arithmetic identity

`tools/generate_f0_prod2_ma2_asm.py` derives the candidate assembly from the
frozen P1-H source and recognizes exactly two final-store patterns. It replaces
only those patterns with the P2-B epilogue and refuses generation if the P1-H
symbol set or store patterns change.

The linked opcode audit proves:

| helper region | P2-B versus P1-H |
| --- | --- |
| formation pair 0 | identical |
| formation pair 1 | identical |
| R2 second layer | identical |
| D1 | identical except 18 static `vperm2i128` epilogue instructions |
| reductions / scale conversions | no additions |

The helper remains a 32-byte-aligned AVX2 leaf with no frame, spill, call, or
`vzeroupper`. The wrapper retains the same one top-split call and four fixed
public-selector helper calls.

## Exact correctness gates

The producer oracle compares raw representatives, not canonicalized residues:

```text
P1-H generic F0 -> exact projection to MA2 planes
P2-B direct MA2 planes
```

The complete 2,304-byte buffers are bit-exact for zero, alternating bounds,
2,304 signed impulses, 1,003 random KEM-small cases, alias operation, input
immutability, range, and canaries.

The consumer oracle then compares:

```text
P1-H generic F0 -> existing MA2 input formation -> MA2 arithmetic/serializer
P2-B planes      -> native plane loads          -> same arithmetic/serializer
```

All 257 producer-real consumer cases produce identical 1,728 ciphertext bytes.
The native MA2 symbol is a test/candidate input-ABI realization: compared with
the existing complete MA2 symbol, its linked opcode ledger differs only by
`-144 vmovdqa` and `-144 vperm2i128`, exactly the two generic operand
projections. All arithmetic and serializer instructions are unchanged.

ASan/UBSan, strict warnings, alignment, input immutability, scratch canaries,
and ciphertext canaries pass.

## In-place backing proof

The static helper handles eighteen backing slots per `(branch,terminal-pair)`
execution. For every slot the linked D1 instruction stream records exactly one
source read and one destination write, and proves:

```text
first_write_instruction > last_read_instruction
```

All eighteen inequalities pass. Dynamically, the four helper invocations cover
all 72 planes. P2-B therefore reuses the existing 2,304-byte backing with zero
additional temporary bytes and without an alias cycle.

## Structural gate

```text
top split:                         unchanged
scalar adapters:                   0
generic F0 final stores:           0
generic F0 -> MA2 reloads:          0
D1 -> MA2 epilogue:                72 vperm2i128 + 72 aligned stores
MA2-native input loads:            72 per operand
extra temporary:                   0 bytes
backing array:                      existing 2,304 bytes
helper spill/frame/call:            0 / 0 / 0
new reduction / scale conversion:  0 / 0
```

## Decision

ASM0 is correctness and structure qualified. The next authorized checkpoint is
only a producer-boundary pricing island:

```text
control:   P1-H generic F0 -> existing MA2 projection
candidate: P2-B direct MA2 planes
```

Both measurements must stop at the exact MA2 input ABI and use the SUPERCOP
derived measurement policy. Native KEM, full encapsulation, resident-`h`, top
split fusion, live D1-to-MA2 handoff, P2-C traversal, and plane-formation
micro-superoptimization remain unauthorized until that pricing gate is
reviewed.
