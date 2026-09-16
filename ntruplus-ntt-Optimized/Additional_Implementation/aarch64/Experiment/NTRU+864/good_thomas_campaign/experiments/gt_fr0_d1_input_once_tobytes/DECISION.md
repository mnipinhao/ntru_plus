# D1-P3B6 decision

Decision: **keep experimental; do not promote.**

The exact current AArch64 byte ABI, including `shuffle2`, is implemented
correctly.  Apple clang and Pi GCC both allocate the generated top-local core
without coefficient spills.  On Cortex-A76 it improves the actual P3B4
`r9_to` control from 1848.172 to 1502.463 cycles, but does not meet the
predeclared `<1250` cycle gate.

No full-KEM binding was run: doing so after failing the isolated break-even
gate would not change the ToBytes conclusion and would mix this boundary result
with unrelated KEM noise.  Reopen this direction only with a concrete way to
reduce the 9-to-8 lane-routing or normalization/packing critical path; simple
compiler rescheduling is not a sufficient new hypothesis.
