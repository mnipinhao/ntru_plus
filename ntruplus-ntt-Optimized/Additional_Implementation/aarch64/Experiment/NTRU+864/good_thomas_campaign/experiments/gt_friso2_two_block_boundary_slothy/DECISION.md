# Decision

**Pass the two-block register boundary gate; keep candidate status
`investigate`.**

CF3 proves that block-specific columns 0–7 and 8–15 constants can be consumed
with all eighteen outputs resident, no preservation copies, and no spill or
new memory boundary.  It does not prove that the existing NTT16 producer can
deliver the eighteen inputs in the allocation required by each pair.

## Next hard gate

Open a producer-to-pair boundary experiment, not a larger monolithic solve:

1. freeze the existing M5R-D NTT16 producer arithmetic and coefficient memory
   schedule;
2. derive each CF3 allocation's exact eighteen physical input registers;
3. recolor the producer outputs or prove the minimum required register moves;
4. include packed-common constant loads, `x3` setup, and the existing eighteen
   output stores in the instruction ledger;
5. build one linked bank for each `(top, component)` scaled case and run exact
   arithmetic/layout/range/ABI tests;
6. reject any candidate that adds a coefficient boundary or loses the net
   instruction advantage before Pi 5 timing.

Only a passing linked one-bank result should proceed to full Forward PMU.
Production and SUPERCOP remain unchanged.
