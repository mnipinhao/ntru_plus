# D1-P1 hypothesis

- Observation: D1 removes 755 instructions and 547.594 cycles at the complete
  `2F + BaseMul + Inverse` boundary, while D1-C2 proves its serialization
  representative and explicit FR0/official coordinate bridge.
- Hypothesis: the same saving survives the unmodified stock NTRU+864 KEM call
  graph when all transform-domain poly APIs are connected through a
  production-shaped, default-off GT wrapper.
- Exact change: compile the same `common/kem.c` three times and link Official,
  GT-old, and GT-D1 in one binary. GT-old and GT-D1 differ only in BaseMul and
  BaseMulAdd final reduction.
- Static expectation: D1 removes about 755 retired instructions for each BaseMul
  or BaseMulAdd, without changing Forward, Inverse, serialization,
  BaseInv, randomness, hashing, or memory boundaries.
- Performance expectation: D1 improves GT-old Keypair (two BaseMul), Encaps
  (one BaseMulAdd), and Decaps (two BaseMul) in paired Pi 5 PMU measurements.
- Register pressure: unchanged outside the already audited D1 kernels; no new
  assembly is introduced.
- Correctness/range impact: none beyond the closed `[-2911,2911]` D1 output
  contract. Byte-identical deterministic KEM outputs and success/failure
  behavior are required.
- Falsification: any byte mismatch, cross-variant return-code mismatch,
  throttle event, or non-negative D1-minus-GT-old median cycle delta fails the
  production-shaped gate.
