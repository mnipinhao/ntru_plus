# M5M: exact one-bank Forward producer-consumer hard gate

M5M is the first bounded region that contains every coefficient read for one
`(top,component)` bank, both complete NTT16 paths, and both complete oriented
NTT9 column blocks.  It composes the frozen M5L tail producer and M5K consumer
with a new sixteen-vector main producer.  There is no coefficient scratch
boundary between them.

The input bank consists of 128 main halfwords in sixteen sequential vectors
plus sixteen strided `s=8` halfwords.  The region therefore reads exactly 144
meaningful coefficients: sixteen `ldr q,[x0],#16` and sixteen legal
`ld1 {v.h}[lane],[x1],x4` with public `x4=16`.  It performs no coefficient
store.  Public traffic is 56 vectors: 22 from the NTT16 chain, 32 NTT9 table
vectors, and two shared modulus/root vectors.

The main path names natural input `t` into bit-reversed symbolic states
`[0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15]`.  This is a zero-instruction
layout choice, not a runtime permutation.  Four packed branch vectors and
five packed stage vectors each hold four adjacent `(b,bprime)` pairs.  Lane
forms of `mul/sqrdmulh`, followed by `mls`, realize four independent
Algorithm-10 products per loaded constant vector.

The fixed tail outputs are `v17` for columns 0--7 and `v16` for columns
8--15.  They are reserved from allocation.  The roots vector is deliberately
loaded only after the main NTT16 finishes, so the producer peak is the sixteen
main states, two tails, modulus, one current constant vector, and arithmetic
temporaries.  M5K then consumes both tails without a spill.

On `pinhao@172.25.166.141:51208`, Slothy 0.2.2 finds an OPTIMAL functional
allocation for all 633 real instructions in 143.014540 seconds with selfcheck
OK and spills forbidden.  Scheduling the allocated code in approximately
20-instruction windows completes with `split_heuristic_full:OK!`; the emitted
N1 proxy is 158 cycles.  Both returned artifacts assemble and use exactly
`v0-v7,v16-v31` plus `x0-x5`, with no `v8-v15`, stack, store, or branch.

The 158-cycle number is a scheduling proxy, not a Raspberry Pi 5 measurement
and not SUPERCOP evidence.  M5M also has no repeated-bank control or final FR-0
stores.  The candidate remains Experiment/investigate until those full-path
gates are closed.
