# d4AoS prefixed-backend API coverage ledger

Frozen API source: Official-main `0c249d5828b90e8dd5de2c8405323d5ee2a0ce41`,
`Additional_Implementation/avx2/NTRU+768/poly.h`.  The planned prefix is
`gt_d4aos_`; it is a ledger namespace only in this phase, not a symbol remap.
“Unavailable” means exactly that: no d4AoS path falls back to an Official
NTT-domain kernel.

| Official prototype | Proposed prefixed backend API | Input → output domain | Status / native implementation | Explicit bridge | Required caller / KEM phase | Production blocker |
| --- | --- | --- | --- | --- | --- | --- |
| `void poly_ntt(poly *r)` | `gt_d4aos_poly_ntt` | COEFF → D4AOS-NTT | **native-d4aos-reference**, `d4aos_ref_forward` typed core | none | keygen, enc, dec | ABI wrapper and production CT/range proof absent |
| `void poly_invntt_scale(poly *r)` | `gt_d4aos_poly_invntt_scale` | scaled D4AOS-NTT → COEFF | **native-d4aos-reference** inverse only, `d4aos_ref_inverse` | none | keygen, enc, dec | Official scale compatibility absent |
| `void poly_basemul(poly *r,const poly *a,const poly *b)` | `gt_d4aos_poly_basemul` | D4AOS-NTT² → D4AOS-NTT | **native-d4aos-reference**, `d4aos_ref_basemul` | none | keygen, enc, dec | ABI wrapper and CT implementation absent |
| `void poly_basemul_scale(poly *r,const poly *a,const poly *b)` | `gt_d4aos_poly_basemul_scale` | D4AOS-NTT² → scaled D4AOS-NTT | unavailable | none | dec | factor/scale contract unproved |
| `void poly_baseinv_1(poly *r,__m256i den[12],const poly *a)` | `gt_d4aos_poly_baseinv_1` | D4AOS-NTT → adjugate/denominators | unavailable | none | keygen | terminal determinant representation unproved |
| `int poly_baseinv(poly *r,const poly *a)` | `gt_d4aos_poly_baseinv` | D4AOS-NTT → D4AOS-NTT | unavailable | none | keygen | success/failure and zeroization contract unimplemented |
| `void poly_tobytes(uint8_t r[1152],const poly *a)` | `gt_d4aos_poly_tobytes` | D4AOS-NTT → WIRE12 | unavailable | none | keygen, enc | Official WIRE12 mapping deliberately untouched |
| `int poly_frombytes(poly *r,const uint8_t a[1152])` | `gt_d4aos_poly_frombytes` | WIRE12 → D4AOS-NTT | unavailable | none | dec | checked malformed-wire behavior deliberately untouched |
| `void poly_add(poly *r,const poly *a,const poly *b)` | `gt_d4aos_poly_add` | D4AOS same-domain → D4AOS | unavailable | none | enc, dec | typed operation not implemented |
| `void poly_sub(poly *r,const poly *a,const poly *b)` | `gt_d4aos_poly_sub` | D4AOS same-domain → D4AOS | unavailable | none | enc, dec | typed operation not implemented |
| `void poly_cbd1(poly *r,const uint8_t buf[192])` | no d4 API | bytes → COEFF | unavailable by design | none | keygen, enc, dec | frozen coefficient helper; no shadow KEM |
| `void poly_sotp_encode(poly *r,const uint8_t msg[96],const uint8_t buf[192])` | no d4 API | bytes → COEFF | unavailable by design | none | enc | frozen coefficient helper; no shadow KEM |
| `int poly_sotp_decode(uint8_t msg[96],const poly *a,const uint8_t buf[192])` | no d4 API | COEFF → bytes | unavailable by design | none | dec | frozen coefficient helper; no shadow KEM |
| `void poly_triple(poly *r)` | no d4 API | COEFF → COEFF | unavailable by design | none | keygen | frozen coefficient helper; no shadow KEM |
| `void poly_crepmod3(poly *r)` | no d4 API | COEFF → COEFF | unavailable by design | none | dec | frozen coefficient helper; no shadow KEM |
| coefficient multiplication (no Official single symbol) | `ntruplus_poly_mul_coeff_d4aos_ref` | COEFF² → canonical COEFF | **native-d4aos-reference** full island | n/a | reference test only | no KEM integration requested or present |

There is no full `d4-aos-shadow-kem` target, no `kem.c` object in the reference
binary, no fake success stub, and no Official-domain conversion.  Any future
bridge must be named, range-proved, malformed-input-proved where applicable,
and tested before its row can change from `unavailable`.
