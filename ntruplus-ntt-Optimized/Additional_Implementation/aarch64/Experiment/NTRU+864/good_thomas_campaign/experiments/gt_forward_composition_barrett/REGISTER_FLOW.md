# Planned fused register flow

Only `v0-v7,v16-v31` are caller-saved, giving 24 usable registers without an
ABI save frame.

1. Tail NTT16: two data registers hold the sixteen `s=8` values for one bank;
   one q register, two vector constants, and two scratch registers suffice.
2. Main NTT16: sixteen state registers plus the two saved tail outputs are
   live. A four-butterfly group adds q, one packed scalar-constant vector, and
   four quotient registers: exactly 24 registers.
3. NTT9 block: nine registers are the current block and nine preserve the
   other block and its tail. R0 has no identity-reduction quotient. One exact
   two-product B3 needs the current three data registers plus roots, q,
   `saved_a`, and one reusable quotient. Counting the other fifteen data
   vectors gives 22 live vector registers. The 8x8 transpose remains
   destructive/in-place with two temporaries.
4. After the first nine FR-0 rows are stored, its registers become scratch for
   the second block. No coefficient spill or intermediate NTT16 store is
   required by the register contract.

This is a feasibility allocation, not evidence that an assembler or Slothy
has accepted the final kernel. That becomes the next realization gate.
