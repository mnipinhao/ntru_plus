# M5O results

- Full actual-assembly differential: pass, 1,254 complete Forward cases and
  1,083,456 output comparisons modulo q against Official Neon.
- Coverage: zero, five constant boundary/representative inputs, all 864 natural
  coefficient basis vectors, 256 centered-random inputs, and 128
  canonical-random inputs.
- ABI proof: all 864 FR-0 and Official physical offsets form a bijection;
  Official `zetas_mul` exactly matches scalar `zetas[288]` leaf order.
- ABI mapping SHA-256:
  `11bcb9351c470ca466347cd69f50b40aa23b56f1456556dc5da41a5417fa3c82`.
- Composition: one top-split call, one M5N call, fixed 1,792-byte aligned stack
  scratch, and all required symbols resolved in the linked test.
- Memory accounting: 1,728 meaningful coefficient loads and 1,728 meaningful
  coefficient stores total, i.e. two loads and two stores per coefficient.
  The only additional traffic is 32 zero padding halfword stores, never read.
- Local object text sizes: 276-byte top split, 4,928-byte M5N pass 2, and
  64-byte wrapper; 5,268 bytes combined on the local arm64 toolchain.
- Direct prerequisite regressions: top split 106 differential plus 5,185
  fixed-multiply checks passed; M5N 1,122 exact representative cases passed.
- Wrapper SHA-256:
  `9f6537d049dd81ef5a20b328e7ff20afd3c6afecf84624c1d0b1ce83a969f4af`.

This is correctness and composition evidence only.  It is not a cycle,
SUPERCOP, KEM/KAT, or Production-promotion result.
