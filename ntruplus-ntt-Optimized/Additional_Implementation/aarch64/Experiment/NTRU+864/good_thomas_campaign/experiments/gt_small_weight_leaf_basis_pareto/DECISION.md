# Decision

**Accept FR-SIGN4 algebra; reject all three candidates on the current Forward
topology.**

- `H={176,464,752}` exactly produces the signed small weights `+/-9,+/-3`.
- Signed BaseMul retains the existing direct-wide int32 proof with no extra
  mulmod or reduction.
- Every slope retains 64 direct-Inverse row-correction mulmods.
- The exact minimum add-scale cut is eight mulmods.
- Twelve bounded `<=21` searches found no qualifying witness, but did not prove
  total infeasibility.
- Verified Forward upper bounds are all-26 for H176, 26/26/26/27 for H464, and
  26/27/26/27 for H752.
- H176 is the preferred sign4 algebra target, but its optimistic complete
  arithmetic ledger is still +215 instructions versus M5R-D.

Do not schedule or benchmark these witnesses.  Reopen H176 only after changing
the NTT9 arithmetic topology or obtaining a stronger identity/cut construction
that reaches at most 21 mulmods per block.
