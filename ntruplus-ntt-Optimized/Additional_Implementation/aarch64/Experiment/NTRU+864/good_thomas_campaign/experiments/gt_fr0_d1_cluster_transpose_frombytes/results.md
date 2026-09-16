# D1-P3B23 evidence

Status: **accepted as the isolated experimental FromBytes champion.**

The exact map exposes eight aligned four-source clusters and four aligned
two-source clusters.  Four-source clusters use eight `TRN` instructions plus
eight 64-bit inserts; two-source clusters use two `ZIP` instructions plus
eight 32-bit inserts.  Two unaligned four-source clusters and the six-source
cluster retain scalar lane moves.

Local correctness passes 256 arbitrary-byte cases and both guarded edges. Pi 5
passes 128 differential cases.  Every serialized input group is still loaded
once, there is no coefficient scratch, and `transpose_top` has zero stack
reference or spill.

Paired Cortex-A76 PMU (core 3, three repetitions):

| variant | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| P3B11 | 938.935 | 1715.045 | 6.010 |
| P3B23 local TRN/ZIP | **657.225** | **1383.045** | 6.010 |
| candidate - P3B11 | **-281.710** | **-332** | 0 |

All three candidate medians are 657.217--657.228 cycles.  The requested
145-cycle recovery gate passes by 136.710 cycles of additional margin.

The target object contains 32 `TRN1`, 32 `TRN2`, four `ZIP1`, four `ZIP2`, and
zero stack references.  This is isolated-boundary evidence, not yet a linked
Encaps/Decaps or SUPERCOP claim.
