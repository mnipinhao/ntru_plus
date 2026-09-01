# M5S: Forward-local fused-twist NTT9 search

This experiment is deliberately independent of the delayed-twist ABI work.
It preserves the complete FR-0 output and replaces only the two NTT9 blocks in
the M5R-B one-bank Forward DAG.

The algebra search covers cyclic first-level B3 orientations and
`lambda -> lambda*eta^a` row rotations.  It proves that the four non-identity
eta corrections cannot disappear under that family.  The selected local DAG
therefore keeps all Algorithm-10 multiplications but pairs each adjacent
`(b,bprime)` table read with one `ldp`.

Per block the fair M5R-B baseline is 136 instructions (the historical 142
includes six copies already removed by M5R).  The candidate is 128
instructions.  Across both blocks the one-bank region falls from 617 to 601
instructions without changing coefficient memory traffic, roots, R0 scale,
ranges, or output ordering.

The generated assembly remains experimental and is not linked by Production.
