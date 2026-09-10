# P6-B packed-half ToBytes gate

## Outcome

`PASS` for the packed-half representation and its two isolated allocation
frontiers.  This is not yet a complete ToBytes candidate and production is
unchanged.

P6-A showed that retaining two complete packed pairs while materializing both
coefficient streams of the third pair leaves only one vector register.  Merely
removing a `TBL` index does not solve full ToBytes because Barrett
normalization still needs `q`, reciprocal 9, and one quotient temporary.

P6-B changes the lifetime shape:

1. Route and canonicalize the 72 `A` coefficients of pair 2.
2. Retain them in their exact 12-bit representation:
   72 low bytes plus 36 packed high-nibble bytes = 108 bytes = seven Q slots.
3. Only then create the nine-vector `B` route.
4. Normalize and consume `B` while reconstructing the final 216 pair bytes.

The peak data state is therefore:

```
two saved pairs       13 Q + 28 X  (432 bytes)
packed pair-2 A        7 Q          (108 bytes)
pair-2 B route         9 Q          (144 bytes)
------------------------------------------------
data total            29 Q-equivalent vector slots
```

This leaves exactly three vector registers for full normalization.

## Exact mapping gate

`model.py` reads the production `p3b1_a_fwd` table rather than using an
invented route.  It checked all nine row-dependent lane permutations.  It then
checked four boundary/structured cases and 4,096 deterministic random cases.
For every one of the 4,100 cases:

```
packed A -> restored A -> pair(A,B)
```

was byte-identical to direct NTRU+ 12-bit packing:

```
byte0 = A & 255
byte1 = (A >> 8) | ((B & 15) << 4)
byte2 = B >> 4
```

The packed-A state is exactly 108 bytes; this is a representation change, not
lossy compression.

## Slothy gate

Slothy was loaded from `/Users/chenpinhao/slothy` and used the Cortex-A76
model with spilling disabled.

| Region | Exact peak | Solver | Spill/reload tokens | Model cycles |
|---|---:|---|---:|---:|
| One-stream route repair | 29 data + index + result = 31 | `OPTIMAL` | 0 | 15 for the 60-instruction synthetic slice |
| Full normalization | 29 data + q + reciprocal + quotient = 32 | `OPTIMAL` | 0 | 17 for the 67-instruction synthetic slice |

Both allocated regions assembled successfully as arm64 Mach-O objects.  The
reported cycle counts include synthetic frontier loads/stores and are not a
ToBytes performance prediction.

## What is and is not proved

Proved:

- the exact 12-bit packed-A representation and final pair-byte identity;
- the production route table used by the model;
- sufficient vector-register capacity for route repair;
- sufficient vector-register capacity for full Barrett normalization at the
  exact 32-register frontier;
- no spill in either isolated Slothy allocation.

Not yet proved:

- a complete seven-register SIMD producer for packed A;
- the joint restore-A / pack-B / three-pair merge DAG;
- consecutive-register constraints for any multi-register `TBL`;
- direct full-vector final stores;
- complete full/small ToBytes correctness or cycle improvement.

The next gate is P6-C: author those consumer operations as one exact symbolic
DAG, require peak `<= 32`, no coefficient scratch, no extra coefficient loads,
no lane `ST3`, and only then produce a complete assembly candidate.
