# D1-P3B7 faithful-lowering hypothesis

Observation: P3B6 is correct and input-once but GCC emits 108 three-instruction
sign corrections and 108 zero-then-first-lane initialization pairs per full
ToBytes call.

Primary bottleneck category: instruction selection and register initialization.

Hypothesis: an equivalent `sshr+mls` sign correction and first-lane `dup` can
remove 216 retired instructions without changing the composed map, memory
boundary, arbitrary signed-int16 contract, or register frontier.

Exact proposed change: generate L1 with only the sign correction changed, then
L12 with the first insertion of every output changed from zero-plus-insert to
one lane duplicate.  P3B6 remains a separate control symbol.

Expected static effect: L1 removes 108 instructions per full call; L12 removes
another 108.  Expected performance effect: a material reduction from 1502.463
cycles, but not necessarily enough to cross 1250 cycles.

Expected register-pressure effect: unchanged or lower.  Any coefficient spill
fails the target-object gate.

Correctness or range impact: none.  L1 was exhaustively proved over all 65536
signed-int16 values.  In L2 every duplicated non-target lane is overwritten
before the output is consumed.

Falsifying measurement: any byte mismatch, edge-guard failure, vector spill,
failure to remove the expected static instructions, or no reproducible Pi 5
cycle reduction.
