# Decision

- Accept D1-P1 as a production-shaped consumer closure and retain D1 as the
  experimental GT864 BaseMul/BaseMulAdd arithmetic baseline.
- Do not promote the complete GT path: although D1 saves 665--1069 cycles at
  each KEM API versus GT-old, GT-D1 remains 3776--10396 cycles behind Official.
- Preserve the newly explicit Forward-to-byte/BaseInv and
  Inverse-to-crepmod3 normalization contracts. They are correctness
  requirements, not optional benchmark scaffolding.
- Keep the stock NTRU+864 Makefile unchanged. KAT and SUPERCOP remain blocked
  on a faster production wrapper/full-chain candidate.
- The next hard gate is `D1-P2 boundary cost decomposition`: isolate the
  FR0/official permutation+normalization, stock-BaseInv bridge, Forward and
  Inverse contributions at the same KEM caller boundaries. Do not start
  Slothy until that decomposition identifies a changed arithmetic DAG or a
  bounded scheduling region.
