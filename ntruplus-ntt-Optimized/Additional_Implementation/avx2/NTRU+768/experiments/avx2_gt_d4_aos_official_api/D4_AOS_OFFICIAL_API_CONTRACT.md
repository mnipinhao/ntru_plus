# AVX2-GT-D4-AOS-OFFICIAL-API — Stage 0 API contract

Status: **complete for the reference-island scope**.  This is a source-derived ledger for the frozen
Official-main source tree, not a claim that its undocumented internal ranges
have already been proved for a new backend.

## Frozen source and build closure

- Official root: `/home/nuc/src/ntru_plus/third_party/NTRUplus-official-main`
- revision: `0c249d5828b90e8dd5de2c8405323d5ee2a0ce41`
- implementation: `Additional_Implementation/avx2/NTRU+768`
- ring: `Z_3457[X]/(X^768 - X^384 + 1)`; `N=768`, `D=4`, wire size `1152`.
- normal build closure: `kem.c`, `poly.c`, `consts.c`, `symmetric.c`, FIPS202,
  and `asm/{add,baseinv,basemul,cbd,crepmod3,invntt,ntt,pack}.s`.
- ABI: SysV AMD64 on Linux.  `poly` is 32-byte aligned and contains 768 signed
  `int16_t` elements.  All AVX2 kernels use aligned `poly` vector accesses.

Frozen source hashes for the NTT-domain closure are: `poly.h`
`b846b092…511b812f3`, `kem.c` `95532676…19ff7d8`, `consts.c`
`52649ae4…dc6fb080`, `ntt.s` `992b6137…d852b70`, `basemul.s`
`60b614a0…bcf868c`, `invntt.s` `991f13a7…d852b70`, `baseinv.s`
`3c6fc99e…555687`, and `pack.s` `dd1d2b96…a1a3c6`.

The normal Official target remains untouched.  This campaign does not compile a
shadow target or `kem.c`; any future remap is outside this reference phase.

Baseline validation on the local AVX2 host passed with `make CC=gcc test &&
./build/test`.  Its printed cycle figures are the upstream test-program
diagnostic, not a controlled campaign measurement and are intentionally not
used as a performance baseline.

## Domain names

| Name | Storage | Meaning |
| --- | --- | --- |
| `COEFF` | `poly` | natural coefficients in the target quotient ring |
| `OFFICIAL-NTT` | untagged `poly` | Official in-place quartic transform layout and scale |
| `D4AOS-NTT` | distinct reference type until shadow KEM | proposed branch-paired quartic AoS layout |
| `WIRE12` | 1152 bytes | Official serialization; its order is not an AoS memory order |

`poly` has no layout tag.  A `poly` cannot be consumed by a different NTT
backend without a named mapper.  This rule includes `tobytes`, `frombytes`,
`baseinv`, `add`, and `sub`.

## Exact exported/internal poly API

| Function | Exact prototype | Caller domain → output domain | Alias/in-place and failure/clear contract |
| --- | --- | --- | --- |
| `poly_tobytes` | `void poly_tobytes(uint8_t r[1152], const poly *a)` | `OFFICIAL-NTT → WIRE12` | distinct buffers in KEM; canonicalizes the serialized representative; no return/failure and no clear in ASM |
| `poly_frombytes` | `int poly_frombytes(poly *r, const uint8_t a[1152])` | `WIRE12 → OFFICIAL-NTT` | writes decoded lanes before returning; returns 1 if any 12-bit coefficient is `>=3457`; does not clear `r` itself |
| `poly_cbd1` | `void poly_cbd1(poly *r, const uint8_t buf[192])` | random bytes → `COEFF` | caller-owned output; fixed trip count |
| `poly_sotp_encode` | `void poly_sotp_encode(poly *r, const uint8_t msg[96], const uint8_t buf[192])` | message/random bytes → `COEFF` | fixed-size, no NTT layout |
| `poly_sotp_decode` | `int poly_sotp_decode(uint8_t msg[96], const poly *a, const uint8_t buf[192])` | `COEFF` → message | returns verification/decode failure; preserve exactly |
| `poly_ntt` | `void poly_ntt(poly *r)` | `COEFF → OFFICIAL-NTT` | in place; no clear |
| `poly_basemul` | `void poly_basemul(poly *r, const poly *a, const poly *b)` | `OFFICIAL-NTT × OFFICIAL-NTT → OFFICIAL-NTT` | output must not be assumed alias-safe without dedicated proof; no clear |
| `poly_basemul_scale` | `void poly_basemul_scale(poly *r, const poly *a, const poly *b)` | `OFFICIAL-NTT × OFFICIAL-NTT → scaled OFFICIAL-NTT` | Dec-only product contract; no clear |
| `poly_invntt_scale` | `void poly_invntt_scale(poly *r)` | scaled `OFFICIAL-NTT → COEFF` | in place; final canonical/bounded representative required by `crepmod3`; no clear |
| `poly_baseinv_1` | `void poly_baseinv_1(poly *r, __m256i den[12], const poly *a)` | `OFFICIAL-NTT →` adjugate plus 12 denominators | implementation helper; uses aligned vectors |
| `poly_baseinv` | `int poly_baseinv(poly *r, const poly *a)` | `OFFICIAL-NTT → OFFICIAL-NTT` | on noninvertible input, zeroes `r`, clears `den`, returns 1; on success clears `den`, returns 0 |
| `poly_add` | `void poly_add(poly *r, const poly *a, const poly *b)` | same-domain addition | Enc uses `OFFICIAL-NTT`; d4 shadow must provide D4AOS equivalent |
| `poly_sub` | `void poly_sub(poly *r, const poly *a, const poly *b)` | same-domain subtraction | Dec uses `OFFICIAL-NTT`; d4 shadow must provide D4AOS equivalent |
| `poly_triple` | `void poly_triple(poly *r)` | `COEFF → COEFF` | keygen coefficient helper; keep frozen Official implementation |
| `poly_crepmod3` | `void poly_crepmod3(poly *r)` | `COEFF → COEFF` | Dec coefficient helper; keep frozen Official implementation |

## Range and scale ledger

`poly_frombytes` proves a strict wire input bound `[0,3456]`; its maximum-lane
comparison is public, fixed-work AVX2 code.  `poly_tobytes` performs its own
representative reduction before packing.  The source does **not** expose a
numeric public precondition for every intermediate `OFFICIAL-NTT` value.

Consequently the d4AoS implementation gate is deliberately still open:

1. derive each Forward layer bound from its concrete reduction sequence;
2. derive the separate `basemul` and `basemul_scale` factors;
3. derive the `invntt_scale` final range consumed by `poly_crepmod3`;
4. record each proof in a generated range ledger before asm exists.

No current GT SoA lazy bound may be copied as evidence for this new layout.

## Deferred remap scope

An eventual, separately authorized remapping header would have to map exactly these NTT-domain operations to
prefixed symbols: `poly_ntt`, `poly_basemul`, `poly_basemul_scale`,
`poly_invntt_scale`, `poly_baseinv`, `poly_tobytes`, `poly_frombytes`,
`poly_add`, and `poly_sub`.  `poly_triple`, `poly_cbd1`, SOTP, `poly_crepmod3`,
hashing, and KEM control flow stay Official coefficient-domain code.

No such remapping header exists here.  Every implemented d4 reference function
owns and clears its private scratch before returning.  The unchanged KEM clear
paths remain authoritative for caller-owned secret values.
