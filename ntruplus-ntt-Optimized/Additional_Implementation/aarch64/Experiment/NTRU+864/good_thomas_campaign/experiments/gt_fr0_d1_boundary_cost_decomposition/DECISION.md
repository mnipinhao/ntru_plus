# Decision

- Accept D1-P2 as an exact production cost decomposition. Retired instruction
  and branch ledgers close with zero residual for all three KEM APIs.
- Do not optimize M5R-D Forward next: it is already 197.835 cycles faster than
  Official at the production API boundary.
- Keep D1 BaseMul/BaseMulAdd; they are 701.993/694.741 cycles faster than
  Official and are not the complete-GT bottleneck.
- Prioritize the coordinate/byte ABI. FromBytes costs +2222.827 cycles and is
  called three times in Decaps; ToBytes costs +1318.990 and is called two or
  three times; the BaseInv bridge costs +3952.375 twice in Keypair.
- Keep Inverse as the second independent campaign: its raw arithmetic gap is
  +2088.975 cycles and centered normalization raises the API gap to +2854.900.
- The next hard gate is `D1-P3 GT byte-boundary architecture`: derive the
  exact structured 24-coefficient tile map and compare direct FR0 pack/unpack,
  vectorized map+normalization, and the current scalar bridge before writing
  production assembly or invoking Slothy.
- Production, KAT and SUPERCOP remain unchanged.
