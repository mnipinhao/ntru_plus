# GT768 fused `hash_g` gate

Experiment ID: `gt768-fused-shake-hashg-20260911-e41`

This experiment is based on `aarch64-production` revision
`a64e7035cb13410554af1c67870d4132a30037b4`.  Production source is unchanged.

## Gate 0: exact data flow

The complete byte/lane contract is in `HASH_G_MAPPING.md`.  Its executable
oracle passed 259 messages: all-zero, all-one, byte-ramp, and 256 deterministic
random messages.  For each message it compared every lane of all eight full
blocks and the padded tail against the contiguous `0x01 || msg` construction.

Verified permutation count:

```text
8 full-block permutations
+ 1 padded-tail / first-output permutation
+ 1 continuation-squeeze permutation
= 10
```

The mapping exposes a one-byte seam.  Apart from the first lane, a word-wise
direct absorber reads message words beginning at offsets congruent to seven
modulo eight.  This is legal on AArch64, but input-load/extract cost must be
included in the candidate rather than assuming aligned 64-bit blocks.

## Gate 1: live-state feasibility

Static inspection of `keccakf1600.S` establishes the canonical boundary map
shown in `HASH_G_MAPPING.md`: 25 state lanes occupy 25 GPRs after the final
normalization.  Five architectural GPRs remain outside that map.  The caller
link register is already saved by the existing 128-byte frame.

The current scalar permutation performs, per call:

- 12 `ldp` plus one `ldr` to load the 25 state lanes;
- 12 `stp` plus one `str` to store them;
- six callee-save `stp` and six restore `ldp`, plus stack and return control;
- one bounded temporary state spill/reload inside the round schedule.

Ten calls therefore execute 260 state load/store instructions.  A fused path
does not need a memory-backed state and can store the 17+7 output lanes
directly.  It still needs one function prologue/epilogue and small stack slots
for the message pointer, output pointer, round-constant pointer, inner-round
counter, outer-permutation counter, and the existing bounded round temporary.

The existing body has a usable live-state re-entry point in principle: after
the 23 final normalization rotates, the next input block can be XORed into the
canonical register map and execution can re-enter the first-round arithmetic
after the standalone state loads.  The round-constant pointer is already
recoverable from the stack and the first-round code reinitializes the inner
round counter.

This proves architectural feasibility, not performance.  The next static gate
must account for:

- direct construction of the one-byte-shifted input lanes;
- the boundary branch and outer-loop control;
- whether the 23 normalization rotates remain at every boundary or can be
  absorbed into the next block representation;
- output stores and cleanup-policy equivalence;
- exact stack-frame growth and absence of additional state spills.

## Current decision

Gate 0 passes.  Gate 1 does not find a register-capacity blocker, so the fused
candidate remains open.  No performance claim is made yet.  The next controlled
change is B: remove `data[1153]` while retaining the current ten standalone
permutation calls.  C then fixes the complete 1152-byte-input/192-byte-output
loop shape.  Only their measured residual justifies implementing D.
