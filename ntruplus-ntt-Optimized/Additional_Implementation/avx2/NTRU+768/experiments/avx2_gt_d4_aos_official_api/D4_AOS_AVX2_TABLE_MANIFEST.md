# AVX2 consumption-order table view

The existing deterministic `generated/` manifest remains the source of truth. The prototype derives only d4 AoS vectors from its field identities, never from Official or GT SoA tables. For vector `v=16*k3+pair`, every root vector has lane order `[z00×4,z01×4,z10×4,z11×4]`, where `zbu=(beta_b*omega^(32*k3+3*(2*pair+u)))^(+/-i)*R`. Zeta uses the same order without exponent `i`; alpha, inverse-96, and CRT delta are broadcast. A final ASM candidate must replace this deterministic runtime view with checked-in factorized stage-order tables.
