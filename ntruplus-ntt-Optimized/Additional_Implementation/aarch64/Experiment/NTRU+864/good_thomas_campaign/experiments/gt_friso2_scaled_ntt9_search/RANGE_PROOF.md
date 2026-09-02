# Range proof

The verifier does not use Algorithm 10's coarse universal `5185` output bound
at every multiplication.  Doing so loses the concrete constant and correlation
information and gives a false `34799` bound at `t0c1:g2_y1_base`.

Instead, it imports the frozen M5F constant-specific NTT16 producer intervals:

- top 0 maximum: 9342;
- top 1 maximum: 9323.

For every witness and every one of the 16 columns, the verifier then executes
the precise implementation selected by the MILP:

- equal input labels: add/sub first, then one composite multiplication if the
  output label differs;
- unequal input labels: multiply each differing operand into the output label,
  then add/sub;
- existing twist/rho/eta edge: replace it with its exact composite constant.

For each nonidentity multiplication it enumerates the complete incoming
integer interval through the accepted signed-halfword Algorithm-10 formula.
All add/sub nodes are checked before their values may be consumed by another
instruction.

The worst magnitudes are 19121, 19427, 11894, and 13606 for `(t0,c1)`,
`(t0,c2)`, `(t1,c1)`, and `(t1,c2)`.  All are below 32768.  This proves the four
specific witnesses safe; it is not a range claim for arbitrary MILP solutions.
