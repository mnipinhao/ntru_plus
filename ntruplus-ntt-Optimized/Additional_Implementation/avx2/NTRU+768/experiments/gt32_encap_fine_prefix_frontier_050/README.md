# GT32-ENCAP-FINE-PREFIX-FRONTIER-050

One final exact-production split of the three coarse divergence frontiers found
by 049. The frozen 043 Official and GT Clean measurement ELFs are patched in
place; no compile or relink occurs.

- A1: public-key Decode and valid-result branch complete.
- A2: hash_f and hash_h complete.
- A3: CBD(r) complete.
- B1: frontend plus Forward(r) complete.
- B2: r-hat serialization complete.
- B3: hash_g complete.
- D: BaseMul and add(m) complete, then production cleanup.
- T0: same semantic point as D, then minimal common return.
- T1: final ciphertext serialization complete, then minimal common return.
- E: complete byte-exact production Encap.

A1 requires an exit-only shim to initialize the pointer slots consumed by the
original cleanup. Official and GT execute the same classes and count of shim
instructions. A2-B3 redundantly save the cleanup pointer in both images so the
artificial exit work remains symmetric.

T0/T1 are the matched pair used to locate the final serializer frontier without
cleanup. D/T0 and E/T1 separately show whether the production cleanup/tail can
change the cumulative delivery gap. No adjacent difference is a standalone
component cost.
