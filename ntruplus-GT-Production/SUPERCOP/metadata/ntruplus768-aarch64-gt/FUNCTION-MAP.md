# Function map

The public SUPERCOP ABI is unchanged. `kem_api.s` preserves the public-call
ABI and dispatches to the operation-specific GT orchestration in `kem.c`.

| KEM path | Serialization / support | Transform and base arithmetic |
|---|---|---|
| `crypto_kem_keypair` | Official `poly_cbd1`; GT `poly_tobytes_keygen_cq` | `poly_ntt_keygen_cq`, `poly_baseinv_keygen_cq_scaled_r`, `poly_basemul_keygen_cq_scaled_r` |
| `crypto_kem_enc` | Official `poly_cbd1`; GT checked `poly_frombytes_encap` and loose/canonical pack | `poly_ntt_encap_small_lazy`, `poly_ntt_loose`, `poly_basemul_add_encap` |
| `crypto_kem_dec` | Official SOTP and centered `crepmod3`; GT ciphertext unpack/pack | `poly_ntt_decap`, `poly_frombytes_basemul_decap_scale`, `poly_basemul_decap`, `poly_invntt_decap_scale` |

Assembly ownership:

- `ntt.s`: operation-specific forward and inverse GT transforms and tables.
- `base.s`: Keygen inversion helpers and Encap/Decap base multiplication.
- `pack.s`: checked public-key decode and operation-specific serialization.
- `add.s`: polynomial subtraction and tripling used by the GT call sites.
- `cbd.s`: byte-for-byte Official CBD/SOTP source.
- `crepmod3.s`: Official centered mod-3 body with an internal symbol rename;
  `crepmod3_adapter.c` supplies the GT two-pointer contract.

There is deliberately no generic `poly_ntt`/generic basemul compatibility
layer in this leaf. The public boundary is the three SUPERCOP KEM functions.
