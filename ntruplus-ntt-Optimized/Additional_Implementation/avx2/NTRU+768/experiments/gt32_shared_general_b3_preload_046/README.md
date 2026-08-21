# GT32-SHARED-GENERAL-B3-PRELOAD-046

Test the 044/045-qualified qinv preload by replacing the existing shared
General-B3 body in place.  No private clone or new production symbol is added.

Profiles:

- `A`: GT Clean shared General-B3.
- `G`: the same shared symbol with one qinv preload per T16 block and four
  register-source multiplies.  Four NOP bytes keep the symbol and image size
  identical to `A`.

Both Encap and Decap therefore consume the candidate.  Keypair is the unrelated
control.  Promotion requires identical geometry, canonical KAT, neutral
Keypair/Encap, and a negative Decap confidence interval.

## Decision

The shared-body experiment removes the 045 clone-footprint failure: both images
have identical `.text`, `.rodata`, selected symbol addresses, and call graph.
Both images also pass the canonical 100-vector KAT.

Two independent 256-block paired runs did not provide the required stable
promotion result.  Encap improved in both runs, but Decap was significant only
in the first, while the pooled 512-block result also showed an unrelated
Keypair regression.  The candidate is therefore retained as a conditional
reference, not promoted to GT Clean production.  See `RESULTS.md`.
