# D1-P3B6 input-once ToBytes hypothesis

Observation: composing the FR0-to-Official map with the AArch64 `shuffle2`
byte order yields two identical top-local 54-by-54 degree-eight q-vector
graphs.  Direct output-major C1 pays 864 lane loads and address calculations;
P3B4 R9-A pays full intermediate coefficient passes.

Primary bottleneck category: memory and layout boundary.

Hypothesis: the machine-proved input order with at most sixteen partial output
vectors can load each contiguous FR0 q-vector once, distribute its eight lanes
with register moves, and normalize/pack every output as soon as it completes.

Exact proposed change: generate a straight-line, top-local Neon core for the
exact composed map.  It performs 54 `ldr q` inputs, 432 compile-time lane
moves, and 54 final norm/pack stores; the same core is called for both tops.

Expected static effect: replace C1's 432 lane loads per top with 54 q-loads,
remove address/shift tables and all coefficient scratch, and preserve the
final 1296-byte AArch64 ABI exactly.

Expected performance effect: beat P3B4 `r9_to=1849.450` cycles and target less
than 1250 Pi 5 cycles.

Expected register-pressure effect: at most sixteen partial outputs plus one
source and normalization/packing temporaries.  Any vector spill falsifies the
candidate before timing.

Correctness or range impact: none.  The composed map is a tagged bijection;
the full signed-int16 reduction and exact 12-bit byte encoding are unchanged.
All routing and addresses are public compile-time constants.

Falsifying measurement: any byte mismatch against P3B4 `r9_to`, any guarded
edge failure, any vector spill, or a Pi 5 median at or above 1250 cycles.
