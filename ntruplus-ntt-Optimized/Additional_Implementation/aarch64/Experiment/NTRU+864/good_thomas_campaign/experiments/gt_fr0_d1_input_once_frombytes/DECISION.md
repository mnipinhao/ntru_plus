# D1-P3B11 decision

Decision: **accept as the isolated experimental FromBytes champion; do not
promote to Production yet.**

The exact arbitrary-byte contract, guard pages and Pi 5 correctness pass.  The
GCC top-local core has no stack reference or coefficient spill.  Input-once
improves the paired P3B4 C1 control from 1181.090 to 935.717 cycles, removes
1458 retired instructions and 24 branches, and wins in all three repetitions.

The next gate must replace only C1 FromBytes in the frozen P3B4 full-KEM
candidate and measure Encaps/Decaps.  Do not combine P3B6 ToBytes in that gate:
otherwise caller savings cannot be attributed independently.  Once FromBytes
caller closure passes, ToBytes structured routing may use the same composed-map
and completion-order evidence as a separate experiment.
