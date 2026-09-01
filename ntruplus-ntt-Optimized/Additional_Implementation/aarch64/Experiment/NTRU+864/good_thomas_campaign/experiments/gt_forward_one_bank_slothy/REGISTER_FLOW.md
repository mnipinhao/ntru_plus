# M5M register-flow view

## Common state and tail producer

Entry has coefficient pointers `x0/x1`, table pointers `x2/x3/x5`, and public
stride `x4=16`.  The first `x5` load defines the modulus vector.  M5L gathers
the sixteen strided tail halfwords, applies branch twist and the complete
two-vector NTT16, and canonicalizes lanes with `tbl`.

Exit state is `v17.h = C[0..7][s=8]` and
`v16.h = C[8..15][s=8]`.  Both are normal signed R0 representatives bounded
by 9342.  `x1` has advanced by 256 bytes.  No coefficient was stored.

## Main load and branch twist

Sixteen `ldr q,[x0],#16` instructions read natural `t=0..15`; each vector's
lanes are `s=0..7`.  The symbolic destination names use the bit-reverse-4
map, so later radix-2 butterfly partners already have the required names.
Four public vectors contain four `(b,bprime)` pairs each.  For every state,
`mul` computes the low product, `sqrdmulh` estimates the quotient, and `mls`
subtracts that quotient times 3457.

Exit is sixteen twisted NTT16 leaf vectors plus the two fixed tails.  Scale
remains R0; only integer representatives and symbolic layout names changed.

## Four main NTT16 layers

Each layer loads packed fixed constants and executes independent
Algorithm-10 products before `add/sub` butterflies.  The table footprint is
one vector each for lengths 2, 4, and 8, then two vectors for length 16.  No
runtime transpose is needed: the earlier bit-reversed state naming makes the
final states `c0..c15` canonical column vectors.

Exit is sixteen `c` vectors bounded by the inherited exact 9342 proof, with
`v17/v16` still live and untouched.  Only now is the second `x5` vector loaded
to introduce NTT9 roots; delaying it removes one producer-live vector.

## First oriented NTT9 block

The frozen M5K handoff transposes `c0..c7` into eight row vectors and uses
`v17` as row `s=8`.  Eight lane-dependent twists and the complete paper-style
oriented radix-3 NTT9 produce `out0..out8`.  Fixed `v16`, containing the other
tail block, remains live across the whole block.

## Second oriented NTT9 block

The same flow consumes `c8..c15` plus `v16`.  All nine first-block outputs
remain live while `out9..out17` are produced.  The complete exit ABI is
eighteen vectors, eight columns per lane, with the proven output union
`[-28568,28565]`.  The next consumer must either store this exact FR-0 tile or
consume it directly; M5M performs neither operation.
