# Decision

Keep the fused bank-at-a-time schedule as the forward assembly contract. It
closes the previous tail uncertainty without a scratch boundary: tail NTT16
uses two registers, then its two column-block vectors stay live beside the
sixteen main states.

M5F-r2 supplies the replacement proof and selects R0: no identity reductions.
The exact constant set bounds all NTT16 nodes by 9342 and all complete Forward
nodes by 25569. Do not reintroduce generic 5185 propagation or change the
constant/reduction set without rerunning the placement search.

This gate promotes only algebraic, memory, range, and register feasibility.
Handwritten assembly, disassembly audit, actual Slothy output, target timing,
full KEM, and SUPERCOP remain separate.
