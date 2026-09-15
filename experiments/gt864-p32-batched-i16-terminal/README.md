# P32 — split I16 producer and batched composite terminal

P32 tests one precise hypothesis: the six production main-I16 calls all use
the same 64-vector composite table, so materialize the preterminal I16 state
in the already-dead input scratch and consume all six banks column-major.

The public transform ABI, roots, scale, output order, range and tail path are
unchanged.  Production is not modified by this directory.

Declared gate:

1. exact contract and static ledger;
2. spill-free local Slothy allocation and Cortex-A76 timing scheduling;
3. exact complete inverse/KEM/alias/wipe validation;
4. paired Pi 5 main-I16, complete Inverse and Decaps timing;
5. promotion only if complete Inverse and Decaps both improve with negative
   cycle-delta IQR.
