# GT32-ENCAP-CONTEXT-REENTRY-048

Measure whether the controlled-hot R2/R3 advantage survives the real Encap
entry history. The timed target is identical between HOT and REAL modes;
prefix work is never subtracted or included in the timed interval.

- R2: Forward(r) plus serialization of r-hat.
- R3: Forward(m), general BaseMul, add(m), and ciphertext serialization.
- HOT: execute the same target repeatedly immediately before measurement.
- REAL: execute the real Encap prefix immediately before measurement.

Official and GT use the same canonical KAT public key and deterministic coins.
The primary statistic is `(GT_real-GT_hot)-(Official_real-Official_hot)`.
Production is not modified.

## Decision

The real prefix measurably erodes the GT R3 advantage, but only by about ten
cycles. R2 changes by about two cycles. This is a real context effect, not the
missing 170–250-cycle explanation. See `RESULTS.md`.
