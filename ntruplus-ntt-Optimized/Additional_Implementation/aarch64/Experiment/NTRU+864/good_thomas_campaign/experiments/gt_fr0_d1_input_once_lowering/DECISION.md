# D1-P3B7 decision

Decision: **reject L1/L12 as inline-assembly C candidates.**

Both candidates are byte-correct for the full signed-int16 contract and have
no coefficient spills, but both regress Cortex-A76 cycles despite retiring
fewer instructions.  Their opaque two-instruction inline-assembly blocks lower
available instruction-level parallelism; the measured IPC collapse is larger
than the static saving.

Keep the mathematical `sshr+mls` identity and first-lane `dup` operation in the
research ledger.  They may be reconsidered only inside a larger symbolic or
handwritten assembly region that permits cross-output scheduling.  Do not
promote either generated object and do not run full KEM for this experiment.
