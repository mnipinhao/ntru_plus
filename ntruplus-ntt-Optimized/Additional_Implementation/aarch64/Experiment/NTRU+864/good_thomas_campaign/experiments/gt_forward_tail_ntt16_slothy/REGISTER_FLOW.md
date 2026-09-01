# M5L register-flow view

## Exact gather

Entry: `x1=&p8[768+bank]`, `x4=16`, and the two symbolic data vectors do not
yet exist.  `movi` defines each vector before partial lane writes.  Sixteen
`ld1 {V.h}[lane],[x1],x4` instructions produce:

`tail_lo.h = [P8(t0,s8),...,P8(t7,s8)]`

`tail_hi.h = [P8(t8,s8),...,P8(t15,s8)]`

Exit: `x1` advanced by 256 bytes.  Layout changes from strided scalar tail to
two natural-t vectors; scale and bounds do not change.

## Branch twist and length 2

Four public vectors contain `(b,bprime)` for the two t halves.  Two
`mul/sqrdmulh/mls` triples create twisted R0 representatives.  A further
Algorithm-10 triple multiplies the high half by the length-2 constant one;
this is a required representative reduction.  `add/sub` then compute the
eight `(t,t+8)` butterflies.

## Length 4

`trn1/trn2 .2d` create lane pairs whose canonical state indices differ by 2.
The right-vector exponents are `[0,0,0,0,4,4,4,4]`.  One vector
Algorithm-10 product and `add/sub` complete the layer.

## Length 8

`trn1/trn2 .4s` create canonical distance-4 pairs.  Exponents are
`[0,0,4,4,2,2,6,6]`; Algorithm 10 plus `add/sub` completes the layer.

## Length 16 and consumer handoff

`trn1/trn2 .8h` create distance-8 pairs.  Exponents are
`[0,4,2,6,1,5,3,7]`.  The final `add/sub` leaves both vectors in bit-reverse-3
lane order.  A shared public byte-index vector and two `tbl` instructions
produce `tail0.h[lane]=NTT16[column=lane]` and
`tail1.h[lane]=NTT16[column=8+lane]`, exactly the M5K consumer contract.
