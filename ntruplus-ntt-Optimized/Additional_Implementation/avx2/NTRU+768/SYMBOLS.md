# Function-symbol notation

Production symbols use this pattern:

```text
ntruplus768_<operation>_<typed-contract>_avx2
```

The prefix is the algorithm namespace, the middle describes the operation and
its compile-time representation contract, and `_avx2` states the required ISA.
M, P, F0, and J1 are types, not runtime modes.

## Notation

| Token | Meaning |
|---|---|
| `m` | Persistent BaseMul-native coefficient-plane SoA used by Encap/Decap. |
| `p` | Key-generation coefficient-plane placement used by Forward, BaseInv, F0-by-J1 BaseMul, and Q24 pack. |
| `f0` | Forward-produced value with Montgomery exponent `e=0`. |
| `j1` | BaseInv-produced inverse with Montgomery exponent `e=1`. It is only consumed by the typed F0-by-J1 product. |
| `scale` | BaseMul result is scaled for the inverse path (`e=-1` contract). |
| `general` | BaseMul result remains in the general `e=0` NTT-domain contract. |
| `centered` | Input already satisfies the narrow centered representative contract. |
| `lazy10788` | Every signed input word satisfies `abs(x) <= 10788`, `e=0`. |
| `highrange12699` | Every signed input word satisfies `abs(x) <= 12699`, `e=0`. |
| `sum` | Two M/e0 inputs are added in registers; the semantic sum is not materialized. |
| `modq12699` | Difference is safe in signed 16-bit and compared after exact reduction modulo 3457. |
| `sp1` | Selected P-to-Q24 scheduling/orientation; it changes execution order, not the P semantic type. |
| `frontend` | Shared coefficient-order-to-GT landing state; it is not a persistent external ABI. |
| `tail` | Inverse terminal mapping from the M inverse core to coefficient order. |

## Production symbol index

| Symbol | File | Contract and caller |
|---|---|---|
| `ntruplus768_ntt_frontend_avx2` | `ntt.s` | Coefficient order to shared GT frontend scratch. All three KEM operations. |
| `ntruplus768_ntt_m_avx2` | `ntt_m.s` | Frontend to M/F0. Encap and Decap. |
| `ntruplus768_ntt_p_avx2` | `ntt_p.s` | Frontend to P/F0. Keygen. |
| `ntruplus768_baseinv_j1_avx2` | `baseinv.c` | P/F0 to P/J1; returns nonzero for a noninvertible input. Keygen only. |
| `ntruplus768_baseinv_batch_tree_avx2` | `batch_inverse.s` | Internal denominator batch inversion used by `ntruplus768_baseinv_j1_avx2`. |
| `ntruplus768_basemul_f0_j1_avx2` | `basemul.s` | P/F0 times P/J1 to P/e0. Keygen only. |
| `ntruplus768_basemul_scale_m_avx2` | `basemul.s` | M/e0 times M/e0 to inverse-input M/e-1. First Decap product. |
| `ntruplus768_basemul_general_m_avx2` | `basemul.s` | M/e0 times M/e0 to M/e0. Encap and recovered-r Decap product. |
| `ntruplus768_invntt_m_avx2` | `invntt.s` | M/e-1 to inverse terminal state. Decap. |
| `ntruplus768_invntt_tail_avx2` | `invntt.s` | Inverse terminal state to coefficient order. Decap. |
| `ntruplus768_unpack_m_avx2` | `pack.s` | One canonical 1152-byte polynomial to M/e0; returns canonicality failure. Encap. |
| `ntruplus768_unpack3_m_avx2` | `pack.s` | Three serialized polynomials to M/e0 with shared canonicality accumulation. Decap. |
| `ntruplus768_unpack_m_body_avx2` | `pack.s` | Internal Q24 unpack body shared by the public unpack entries. |
| `ntruplus768_pack_m_centered_avx2` | `pack.s` | Narrow centered M/e0 to canonical 1152-byte serialization. Recovered-r Decap boundary. |
| `ntruplus768_pack_m_lazy10788_avx2` | `pack.s` | M/e0, `abs(x)<=10788`, to canonical bytes. Encap `r-hat`. |
| `ntruplus768_pack_m_highrange12699_avx2` | `pack.s` | M/e0, `abs(x)<=12699`, to canonical bytes. Encap ciphertext. |
| `ntruplus768_pack_m_sum_highrange12699_avx2` | `pack.s` | Two M/e0 inputs whose sum satisfies `abs(x)<=12699`; add before Q24 transpose/canonicalization. Encap ciphertext. |
| `ntruplus768_pack_p_sp1_lazy10788_avx2` | `pack.s` | P/e0, `abs(x)<=10788`, to canonical bytes. Keygen public/secret polynomial fields. |
| `ntruplus768_equal_m_modq12699_avx2` | `pack.s` | Constant-time equality of two M/e0 values modulo 3457 under the 12699 difference contract. Final Decap check. |

The only externally visible KEM symbols are `crypto_kem_keypair`,
`crypto_kem_enc`, and `crypto_kem_dec`. Symbols ending in `_impl` are C-level
operation bodies behind those wrappers; they are not an alternate public API.
