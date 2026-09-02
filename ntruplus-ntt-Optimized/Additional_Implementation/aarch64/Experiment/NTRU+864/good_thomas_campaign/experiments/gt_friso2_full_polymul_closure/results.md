# Results

Status: **complete-operation correctness passed; CF0 composition performance
rejected.**

- Direct FR-ISO2 Inverse: 43 zero/impulse/random cases versus explicit
  denormalization plus the frozen FR-0 Inverse; zero modulo-q mismatches.
- Complete `2F + BaseMul + I`: 117 cases, including 100 impulse pairs and 16
  random-small products, versus schoolbook modulo `x^864-x^432+1`; zero
  modulo-q mismatches.
- Representation boundary: zero 864-halfword conversion passes.  The candidate
  directly connects CF0 Forward output to direct-wide BaseMul and then to the
  fused FR-ISO2 Inverse consumer.
- Algebra/scale: every generated row and inverse-twist factor decodes to the
  exact finite-field formula; input and output of the correction remain R0.
- Range: for inverse input `[-2168,2168]`, nontrivial corrected rows are at
  most 1825, P8 maximum is 2136, complete lazy
  halfword maximum is 19512, final output maximum is 3696, and the largest
  known widened product is 27088320.  All signed lane widths pass.
- Inverse correction: 64 Algorithm-10 multiplications, or 192 arithmetic
  instructions, with all column factors merged into existing inverse-twist
  table loads.
- Whole-product lower bound relative to the retained FR0 route: two CF0
  Forwards add 584 instructions, direct-wide BaseMul removes 361, and the
  Inverse adds at least 192.  Net is at least **+415 instructions**, excluding
  inverse public-constant loads.
- Existing Pi 5 component evidence is already decisive for CF0: two Forward
  penalties total 797.356 cycles and BaseMul saves 334.194, leaving **+463.162
  cycles before Inverse correction**.

No new Pi 5 or SUPERCOP run was performed because the composed candidate fails
the pre-timing cost gate.  This result proves that the complete operation has
now been researched and made executable; it does not make it competitive with
Official.
