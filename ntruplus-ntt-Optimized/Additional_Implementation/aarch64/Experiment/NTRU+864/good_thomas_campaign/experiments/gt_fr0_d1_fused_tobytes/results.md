# D1-P3B5 evidence

Status: **REJECTED at the Pi 5 cross-oracle gate; PMU was not run.**

The original local oracle serialized `canonical(FR0[M[i]])`, where `M` is the
FR0-to-Official transform-leaf map.  That is not the byte ABI implemented by
the current AArch64 Official path: its `poly_shuffle2` is part of the serialized
ordering, not merely an internal pack accommodation.  On Pi 5 the fused body
continued to match that scalar-M oracle, but the actual selected P3B4 `r9_to`
control first differed at byte 1 (`scalar-M=64`, `r9_to=128`) on index tags.

The correct direct target is the already-proved composed map
`F[post_index] = M[shuffle2[post_index]]`, SHA-256
`087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270`.
After composition, each top is a connected 54-input/54-output q-vector graph
of degree eight; the twelve independent route9 components no longer exist.
Therefore a completed R9-A Official q-vector cannot be packed independently.

- The generated FR0-to-Official map has SHA-256
  `11bcb9351c470ca466347cd69f50b40aa23b56f1456556dc5da41a5417fa3c82`,
  matching the existing root-derived ABI witness.
- 256 full-polynomial cases passed all 1296 byte comparisons against the
  independent scalar `canonical(FR0[M[i]])` oracle.  Cases include index tags,
  `INT16_MIN`, `INT16_MAX`, `+/-3457`, and random signed-int16 inputs.
- An additional sweep covers every one of the 65536 signed-int16 values and
  confirms the exact Neon reduction before packing.
- Guard pages at both buffer starts and ends pass for the exact 1728-byte input
  and 1296-byte output contracts.
- Apple clang 21 emits a 32-byte wrapper GPR call frame.  The noinline fused
  route/normalize/pack core has no stack reference and uses vector registers
  `v0-v7` and `v16-v22`: no coefficient or vector spill.
- The core loads exactly nine FR0 q-vectors and writes nine final 12-byte byte
  groups.  Twelve calls cover all 108 input q-vectors exactly once.
- The emitted Apple-clang core is 948 bytes / 237 instructions.  This is a
  static shape observation, not a Pi 5 cycle claim; GCC allocation and the
  eleven public literal-vector loads per call still require target audit.
- AArch64 feature and secret-independent static checks report no warning.
  Pattern inventory warnings are the expected public `TBL`, transpose/lane
  operations, and the already-proved signed reciprocal reduction.

No timing result is claimed.  The successor is D1-P3B6: generate the proven
input-once, peak-16 partial-output schedule for the composed map, load every
FR0 q-vector exactly once, and consume each completed post-shuffle output
directly with normalization and packing.
