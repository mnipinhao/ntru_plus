# Results

`make check` passes:

- 55 full composition cases and zero coefficientwise mod-q mismatches against
  M5B NTT16 followed by M4 FR-0;
- 18,087,936 exhaustive signed-halfword products for 276 distinct constants,
  with maximum fixed-product magnitude 3436;
- maximum observed final magnitude 12245 after selecting zero-reduction R0;
- all 864 meaningful P8 indices covered exactly once, all 32 padding indices
  untouched, and all 864 FR-0 output indices covered exactly once;
- constant-specific NTT16 maximum 9342 and whole-Forward maximum 25569;
- zero identity reductions and 36 NTT9 fixed multiplications per block;
- maximum planned caller-saved vector use 24 of 24;
- zero intermediate NTT16 memory loads or stores in the declared schedule.

The C schedule uses local arrays for readability and is not a code-shape or
performance result. The one-load/one-store pass-2 result is the proved
assembly schedule contract, not a claim about compiler-generated C. R0 also
passes the same 55-case replay under AddressSanitizer and
UndefinedBehaviorSanitizer.
