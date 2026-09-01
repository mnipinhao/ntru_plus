# Decision

Keep the fused bank-at-a-time schedule as the forward assembly contract. It
closes the previous tail uncertainty without a scratch boundary: tail NTT16
uses two registers, then its two column-block vectors stay live beside the
sixteen main states.

M5F-r2 selected R0 for the historical four-product B3. M5G supersedes only
that B3 arithmetic DAG with the correlation-safe two-product form. The exact
proof bounds NTT16 by 9342 and all nodes in the changed Forward DAG by 28568,
with zero unsafe signed-halfword nodes. Do not reintroduce the rejected `2a`,
`3a` path or change constants/arithmetic order without rerunning the exact DAG
proof.

This gate promotes only algebraic, memory, range, and register feasibility.
Handwritten assembly, disassembly audit, actual Slothy output, target timing,
full KEM, and SUPERCOP remain separate.
