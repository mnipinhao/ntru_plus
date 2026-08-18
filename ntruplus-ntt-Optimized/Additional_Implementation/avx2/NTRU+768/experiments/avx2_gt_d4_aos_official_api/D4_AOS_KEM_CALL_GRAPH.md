# AVX2-GT-D4-AOS-OFFICIAL-API — frozen KEM call graph

This graph is derived from frozen Official-main `kem.c`; it is the boundary a
shadow backend must satisfy without copying or forking `kem.c`.

## Key generation

```text
shake256 → poly_cbd1 → poly_triple → poly_ntt → poly_baseinv
                                                │
g, finv ───────────────────────────────────────┼→ poly_basemul → poly_tobytes(pk)
f, ginv ───────────────────────────────────────└→ poly_basemul → poly_tobytes(sk tail)
f (already transformed) ─────────────────────────── poly_tobytes(sk head)
```

`poly_ntt`, `poly_baseinv`, `poly_basemul`, and `poly_tobytes` must therefore
be one backend family in a full shadow KEM.  An Official `baseinv` bridge is
allowed only as an explicit, timed, non-production mapper pair.

## Encapsulation

```text
checked poly_frombytes(pk) → h:D4AOS-NTT
poly_cbd1(r) → poly_ntt(r):D4AOS-NTT → poly_tobytes(r):WIRE12 → hash_g
poly_sotp_encode(m):COEFF → poly_ntt(m):D4AOS-NTT
(h, r) → poly_basemul → poly_add(m) → poly_tobytes(ct):WIRE12
```

The failed-public-key path zeros `ct` and clears `ss`; a d4 `frombytes` must
return the same status and not bypass this path.

## Decapsulation

```text
checked poly_frombytes(ct, sk[0], sk[1152])
  → poly_basemul_scale(c, f)
  → poly_invntt_scale
  → poly_crepmod3                              (COEFF)
  → poly_ntt
  → poly_sub(c, message-ntt)
  → poly_basemul(hinv)
  → poly_tobytes → hash_g → poly_sotp_decode
  → re-sample → poly_ntt → poly_tobytes → constant-time verify
```

The only initially allowed semantic integration endpoint is the closed pair
`poly_basemul_scale → poly_invntt_scale`, with an explicit Official-to-d4AoS
input mapper and canonical coefficient output.  It must be measured including
the mapper and must feed `poly_crepmod3` exactly.

## Failure and clearing obligations

- invalid `poly_frombytes` in Enc clears `ss`, zeroes `ct`, returns 1;
- invalid `poly_frombytes` in Dec clears `ss`, then clears all local buffers and
  polys at `cleanup`;
- Dec re-encryption mismatch uses the fixed-work `verify` accumulation path;
- key generation retries only after the BaseInv result is explicitly
  declassified by the frozen source; d4 BaseInv must retain this behavior;
- `secure_clear` uses `explicit_bzero` on glibc, with platform fallbacks.

No d4 private layout may escape a KEM-local `poly` except through a prefixed
wire codec that is byte-identical to Official WIRE12.
