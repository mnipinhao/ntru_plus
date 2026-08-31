# Decision

Pass and freeze the NTT16 producer range gate. The exact existing top split,
branch twist, and four radix-2 layers fit int16 for every input in
`[-3456,3456]`; the final bound 8874 satisfies M5A with margin 6878. No
separate reduction boundary is required between NTT16 and FR-0.

This does not pass the final assembly memory-schedule gate. Current compiler
codegen spills the 16-vector array, so handwritten composition must preserve
the proved arithmetic while allocating registers explicitly. It also does not
prove BaseMul arithmetic, inverse arithmetic, full KEM, or SUPERCOP behavior.

The next bounded hard gate is to consume the generated FR-0 leaf zetas in an
actual BaseMul/BaseMulAdd implementation and differential-test its arithmetic.
