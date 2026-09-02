# Results

Status: **explicit static fallback rejected; cycle viability open; Production
unchanged.**

- All 288 FR-ISO2 factorizations and the 18-/32-modulus comparison families
  pass exact finite-field identities.
- For components 1 and 2,
  `F9^-1 diag((theta^32)^(j*r)) F9` has 81/81 nonzero entries and is not
  monomial.  The row factor is therefore not a free NTT9 orientation or row
  rotation.
- The exact no-new-boundary absorption DAG costs 72 Algorithm-10 mulmods per
  Forward and 64 per Inverse.  Two Forwards plus one Inverse cost 208 mulmods,
  or 624 arithmetic instructions, before public constant loads.
- The two-constant BaseMul DAG is range- and scale-safe.  It deletes two
  five-instruction widening Montgomery reductions per tile: 360 arithmetic
  instructions over 36 tiles.  Including 36 removed zeta loads and two public
  constant materializations, its optimistic saving is 394 instructions.
- Net full-product delta is therefore **+230 instructions**, even while all
  absorption-table loads are optimistically free.
- The less aggressive 18-modulus column-only family is also +30 instructions
  in its optimistic ledger; the 32-modulus row-only family is +544.

The representation remains a valid C oracle, but the explicit fallback does not
pass the whole-path instruction-reduction gate.  M5U-B1 later showed that the
BaseMul portion saves 334 actual A76 cycles, so this ledger must not be read as
a cycle-level rejection.  No transform assembly or Slothy run was started.
