# D1-P1 — production-shaped GT864 integration

This default-off experiment compiles the unchanged stock NTRU+864
`common/kem.c` three times in one executable:

1. stock AArch64 Official poly API;
2. M5R-D Forward + old FR0 BaseMul + M5E Inverse;
3. M5R-D Forward + D1 direct-R0 BaseMul + M5E Inverse.

The GT poly wrapper makes every transform-domain boundary explicit. Forward
produces FR0, BaseMul consumes and produces FR0, Inverse consumes FR0, and the
generated bijection converts only at stock BaseInv and byte serialization
boundaries. Natural-domain CBD, triple, SOTP and `crepmod3` remain unchanged.

The hard gate requires deterministic byte equality for Keypair and Encaps,
successful Decaps, identical tampered-ciphertext failure behavior, and paired
Pi 5 PMU for BaseMul, BaseMulAdd, Keypair, Encaps and Decaps. This experiment
does not alter the NTRU+864 Production Makefile.
