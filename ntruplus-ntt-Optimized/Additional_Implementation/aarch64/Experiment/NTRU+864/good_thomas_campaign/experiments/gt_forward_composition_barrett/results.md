# Results

`make check` passes:

- 55 full composition cases and zero coefficientwise mod-q mismatches against
  M5B NTT16 followed by M4 FR-0;
- 18,087,936 exhaustive signed-halfword products for 276 distinct constants,
  with maximum fixed-product magnitude 3436;
- maximum observed final magnitude 13886 with the two-product B3 DAG;
- all 864 meaningful P8 indices covered exactly once, all 32 padding indices
  untouched, and all 864 FR-0 output indices covered exactly once;
- constant-specific NTT16 maximum 9342 and correlation-aware exact-DAG
  whole-Forward maximum 28568, with zero unsafe signed-halfword nodes;
- zero identity reductions and 24 NTT9 fixed multiplications per block: eight
  twists, twelve products across six B3 calls, and four eta corrections;
- maximum planned caller-saved vector use 24 of 24;
- zero intermediate NTT16 memory loads or stores in the declared schedule.

The C schedule uses local arrays for readability and is not a code-shape or
performance result. The one-load/one-store pass-2 result is the proved
assembly schedule contract, not a claim about compiler-generated C. R0 also
passes the same 55-case replay under AddressSanitizer and
UndefinedBehaviorSanitizer.
