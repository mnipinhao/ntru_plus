# Decision

Reject `top split -> NTT9 -> NTT16` for the current GT864 campaign and retain
`top split -> NTT16 -> NTT9`.

This is not a register-capacity rejection: the row-major physical layout fits
with a conservative 26-vector peak and produces an ideal NTT16 pair layout.
It is an algebra/cost rejection.  The column-dependent phase cannot cross
NTT9 as a free row permutation, and canonical CRT packing violates the memory
contract or exceeds the static budget.

Do not implement Gate 2 assembly.  The next hard gate is the code-size-faithful
NTT16-first CF5-B Forward.

Reopen only if an exact two-dimensional DAG absorbs `theta^(6*c*s)`, preserves
two coefficient loads and two stores, needs no spill/full-buffer permutation,
and proves a static full-Forward count below 4726 before assembly.
