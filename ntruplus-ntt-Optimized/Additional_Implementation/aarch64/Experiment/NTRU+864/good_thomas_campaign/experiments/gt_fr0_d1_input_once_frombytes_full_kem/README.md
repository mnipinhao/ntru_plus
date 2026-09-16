# D1-P3B12 — input-once FromBytes full-KEM closure

This gate links P3B11 into the frozen P3B4 production-shaped harness.  The
only baseline/candidate difference is `c1_from` versus input-once FromBytes;
R9 ToBytes and every transform/arithmetic object are identical.

Official, P3B4 and P3B11 are built in one binary with portable SHAKE256.  Eight
deterministic valid/tampered KEM cases precede paired Keypair, Encaps and Decaps
PMU.  The gate passed: Encaps saves 242.063 cycles and Decaps saves 817.050
cycles, with exact one-call/three-call retired-instruction closure.  Production
and SUPERCOP remain unchanged.
