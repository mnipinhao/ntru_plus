# GT32-DECAP-PRIVATE-GENERAL-B3-PRELOAD-045

Promotion gate for the single 044-qualified component: qinv preload in the
general-B3 invocation used by Decap.

Both fixed-geometry images contain an additional Decap-private general-B3 slot:

- `C`: the private slot contains a clean-equivalent general-B3 body;
- `P`: the same slot contains the qinv-preload body and equal-length padding.

Only Decap calls the private symbol.  Encap continues to call
`ntruplus768_basemul_general_m_avx2`; Keypair is unchanged.  Public B3, Decode,
Scale-B3, inverse, and Q24 symbols are identical between C and P.

The first gate compares C and P with all selected addresses and section sizes
fixed.  A later exact-image gate may compare a clean export against P, but may
not attribute any relocation effect to the private-B3 mechanism.

## Decision

The fixed-geometry causal gate passed.  Across 256 paired blocks, the private
qinv-preload body changed Decap by `-16.1875` cycles with a 95% bootstrap CI of
`[-19.3333, -10.25]`.  Keypair and Encap remained neutral.  This qualifies the
callsite-local mechanism.

The first clean export did **not** pass the exact-image gate.  Adding the 704-byte
private clone moved later hot code.  Relative to GT Clean, the resulting image
changed Keypair by `-18.1354`, Encap by `+220.5`, and Decap by `+125.9167`
paired-median cycles.  Keypair and Encap do not call the private symbol, so
their large changes are direct evidence of whole-image delivery effects.  The
Decap regression is likewise much larger than the fixed-geometry improvement.

Therefore:

- the qinv-preload General-B3 mechanism is qualified;
- the current standalone SUPERcop export is rejected;
- GT Clean production is unchanged;
- a future retry must place the private body after all existing hot symbols, or
  consume an equal-size reserved slot, and must preserve Keypair/Encap delivery.

See `RESULTS.md` for the complete benchmark summary.
