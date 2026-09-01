# Decision

Keep the fused bank-at-a-time schedule as the forward assembly contract. It
closes the previous tail uncertainty without a scratch boundary: tail NTT16
uses two registers, then its two column-block vectors stay live beside the
sixteen main states.

The three new identity reductions are mandatory parts of the Barrett range
contract. Do not copy M5A's skipped `s=0` identity or remove the `b0/c0`
boundaries unless a replacement machine proof is supplied.

This gate promotes only algebraic, memory, range, and register feasibility.
Handwritten assembly, disassembly audit, actual Slothy output, target timing,
full KEM, and SUPERCOP remain separate.
