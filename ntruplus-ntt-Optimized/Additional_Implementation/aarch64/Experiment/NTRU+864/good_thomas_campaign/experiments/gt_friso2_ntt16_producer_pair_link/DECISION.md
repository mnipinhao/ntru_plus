# Decision

**Pass M5U-CF5-A as a register/layout/correctness hard gate; retain candidate
status `investigate`.**

The actual M5R-D NTT16 producer coloring can feed every CF3 scaled pair with
zero boundary instructions and no coefficient memory boundary.  The linked
Forward produces the exact FR-ISO2 representation on Cortex-A76, including
in-place aliasing, while preserving the constants required by subsequent
banks.

Do not benchmark the current generated assembly as the candidate against
Official.  It duplicates the producer four times to isolate correctness and
therefore has a nonrepresentative instruction-cache footprint.

## Next hard gate

Build the code-size-faithful CF5-B integration:

1. emit one shared 345-instruction NTT16 producer;
2. for each scaled bank, call that producer and fall through into its one
   case-specific consumer at the call return site;
3. retain the existing M5R-D helper for the two unscaled component-0 banks;
4. prove 4726 dynamic instructions with PMU, zero reloads, and unchanged
   coefficient load/store counts;
5. rerun the 1126-case Forward oracle and ABI test;
6. only then run paired Pi 5 PMU against M5R-D, CF0, and Official.

CF5-B must be rejected if code sharing introduces boundary moves, constant
reloads, an extra coefficient pass, or if measured cycles fail to improve on
CF0.  SUPERCOP remains deferred until a full Forward + BaseMul + Inverse path
passes its own performance gate.
