# D1-P3B21 peak-26 pair-wait ToBytes hypothesis

Exact `2^15` minimax DP over indistinguishable routing classes finds a
pair-aware input order with peak 26 output vectors, versus P3B15's 28.  Keep
the same input-once, no-scratch, normalization, pack16 and byte ABI.

The two released registers should remove non-ABI spills and allow paired pack
to beat P3B6.  Falsifiers are any byte/guard mismatch, any non-ABI vector
spill, or Pi5 cycles at or above 1502.432.
