# M5L: exact tail gather and packed NTT16 hard gate

M5L closes the tail half of the real pass-2 NTT16 producer for one
`(top,component)` bank.  In P8 the sixteen `s=8` values are not contiguous:
bank `b=3*top+component` is at `p8[768 + 8*t + b]`.  Starting `x1` at
`&p8[768+b]`, the kernel therefore performs sixteen exact halfword lane loads
with public `x4=16`.  It reads 32 meaningful bytes from a 256-byte public
address span, with no over-read.

Two vectors then hold natural `t=0..7` and `t=8..15`.  Branch twist uses two
lane-dependent Algorithm-10 products.  Four DIT layers operate on only two
data vectors.  The layer-boundary `trn1/trn2` sequence is `.2d`, `.4s`, `.8h`;
this maps the next canonical butterfly pair to the same lane.  The final raw
lane order is `[0,4,2,6,1,5,3,7]` in each eight-column half, so two `tbl`
instructions restore canonical columns for the frozen M5K consumer ABI.

The length-2 twiddle is mathematically one but its Algorithm-10 multiply must
remain.  At the proven producer bounds it also changes the integer
representative by multiples of 3457.  Removing it passed small basis tests but
failed exact-representative random tests; M5L deliberately preserves it.

Slothy 0.2.2 lacked a model for real `ld1 {v.h}[lane], [xbase], xstride`.
`optimize.py` adds that one real instruction class.  Its boundary ledger is:
`Xm` input, `Va` and `Xa` in/out; `Xa` is the writeback base.  The N1 proxy
uses the existing `ld2`-lane model's conservative V-unit/throughput-2/latency-7
cost.  This is not a pseudo macro and no unfolding is involved.

On `pinhao@172.25.166.141:51208`, RA is OPTIMAL in 0.916156 seconds and the
real 65-instruction split-window schedule completes with
`split_heuristic_full:OK!` at 16 N1-proxy cycles.  Both outputs assemble; the
scheduled artifact uses only caller-saved `v0-v7,v16-v31`, `x1/x2/x4`, no
`v8-v15`, stack, store, branch, or spill.

This gate does not yet include the sixteen main P8 vector loads, lane-wise
main NTT16, or M5K.  M5M must preserve these two tail outputs while producing
the sixteen main columns and entering the already-proved two-block consumer.
