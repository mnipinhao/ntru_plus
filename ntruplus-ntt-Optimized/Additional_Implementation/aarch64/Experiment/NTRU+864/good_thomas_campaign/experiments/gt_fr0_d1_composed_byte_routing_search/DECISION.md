# Decision

- Accept the exact composed maps and reject mechanical route9 as the natural
  post-composition Q-vector unit.
- Carry M0 `R9-A + stock API` as the attribution control in P3B3.
- Implement C1 direct eight-lane-load output gathers and C2 two-TBL4 output
  gathers as separate P3B3 candidates in both directions.
- Do not rank C1 over C2 from 972 versus 1512 static instructions: C1 has an
  eight-load dependency chain; C2 has much greater byte traffic but short,
  independent lookup chains.
- Require P3B3 to measure complete `FR0→bytes` and `bytes→FR0`, including
  normalization, pack/unpack, address generation and all stores. Coordinate-
  only or routing-only timing is insufficient.
- Keep the `Official[864]` intermediate forbidden for direct candidates.
- Do not run Slothy before P3B3 identifies a real bounded hotspot. BaseInv,
  M5E Inverse, KAT, SUPERCOP and Production remain unchanged.
