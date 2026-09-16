# D1-P3B8 direct-address hypothesis

Observation: P3B6 makes GCC emit one integer `add` before nearly every FR0
`ldr q`, although every public aligned input offset fits the AArch64 scaled
unsigned immediate form.

Primary bottleneck category: address generation.

Hypothesis: encoding each load as `ldr q,[input,#imm]` removes 54 integer
instructions per top without changing vector dependencies or introducing the
opaque arithmetic scheduling regression observed in P3B7.

Exact proposed change: mechanically derive a distinct candidate from P3B6 and
change only its 54 top-local input-load address forms.

Expected static effect: 54 fewer `add` instructions/top.  Expected cycle effect
is positive but smaller than the instruction reduction because integer address
work may overlap Neon execution.

Expected register-pressure effect: one fewer temporary GPR; vector allocation
is unchanged.  Correctness/range impact: none.

Falsifying measurement: any byte mismatch, coefficient spill, failure to emit
direct immediate loads, or no reproducible Cortex-A76 cycle improvement.
