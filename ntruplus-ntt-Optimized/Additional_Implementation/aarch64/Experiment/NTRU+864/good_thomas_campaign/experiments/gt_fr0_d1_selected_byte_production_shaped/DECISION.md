# Decision

- Accept R9-A plus stock ToBytes and direct C1 FromBytes as the new
  experimental GT-D1 production-shaped byte boundary.
- Reject falling back to the previous scalar GT-D1 byte wrappers: the selected
  pair saves 1141.5/2666.9/6288.45 cycles in Keypair/Encaps/Decaps and wins all
  repetitions.
- Keep Production unchanged. This gate is byte-exact full-caller evidence, not
  KAT, SUPERCOP, constant-time final audit, or Production promotion.
- Close P3B4. The next hard gate should target the largest remaining linked
  component, not revisit byte routing immediately. Existing P2 attribution
  identifies the stock-BaseInv bridge and Inverse path as the next candidates;
  measure them again with the selected bytes fixed before choosing one.
