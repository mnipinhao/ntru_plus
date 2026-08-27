# GT9X16-FORWARD-OPT-V2 Lazy Reduction ASM

The unique range-proof mask 79 is now a complete namespaced Forward ASM
prototype.  It retains the frozen persistent-AoS, Natural-Q, T0-beta, paper-R2,
scale-4, and MA2 contracts.  Only the four proved-redundant inter-layer Barrett
calls per branch/q-block are omitted.

## Correctness and linked object

- zero, alternating, all-positive/all-negative, 2304 signed impulses, and 1003
  random-small inputs pass canonical differential against frozen T0-beta;
- unaligned caller storage, input immutability, output canaries, and the proved
  `[-21333,21333]` bound pass;
- linked Barrett vectors are exactly `72 -> 40`;
- linked instructions are `2787 -> 2691` (`-96`);
- constant-memory operands are `578 -> 546` (`-32`);
- `.text` is `15297 -> 14753` bytes (`-544`), `.rodata` is unchanged;
- routing remains 432, data loads/stores remain 144/144, and Montgomery chains
  are unchanged;
- the candidate remains a 32-byte-aligned straight-line leaf with no stack,
  spill, call, branch, or `vzeroupper`.

## Short diagnostic

A repository-local same-ELF three-launch diagnostic produced median deltas of
`-70 cycles` for one Forward and `-133 cycles` for two Forwards.  Individual
launches were placement/frequency-sensitive, including one reversed launch, so
this is only a signal to run a fresh-launch SUPERCOP-derived serious campaign;
it is not promotion evidence and is not added to the native debt ledger.

The Forward side track remains subordinate to `ENCAP-TAIL-ATTRIBUTION-V1`.
