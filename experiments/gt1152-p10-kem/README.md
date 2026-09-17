# GT1152-P10 — the KEM, and the KAT

**Milestone 1's correctness gate. A complete, runnable NTRU+1152 Good-Thomas
KEM that reproduces the checked-in KAT byte for byte.**

```sh
make check      # KAT comparison + 64 KEM round trips with tampered rejection
```

## Result

```
cmp PQCkemKAT_3488.rsp  ntruplus-ntt-Optimized/KAT/NTRU+1152/PQCkemKAT_3488.rsp
sha256 2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3
PASS: 64 KEM round trips and tampered ciphertext rejection
```

That sha256 is exactly the checked-in value recorded in G1's `ring-profile.yml`.

## What is in it

| source | from |
| --- | --- |
| `kem.c`, `poly.h`, `api.h`, `fips202.c`, `randombytes.c`, `secure_clear.h` | NTRU+864 package, **verbatim** — `kem.c` is parameter-neutral, 27 `NTRUPLUS_*` macros and no bare size literals |
| `params.h` | `Reference_Implementation/NTRU+1152`, verbatim |
| `ntt*.S` | G3b, eight-bank forward |
| `base.c` | G4, degree-4 basemul |
| `inverse.c` | G5, degree-4 baseinv and the R⁻¹ boundary |
| `inverse_ntt.S`, `inverse9.S`, `inverse16.S`, `crepmod3_raw.S`, `inverse16_tail.c` | G6b |
| `pack.c` | G7, the codec |
| `symmetric.c`, `support.c`, `api_glue.c` | **new here** |

`symmetric.c` uses the **generic** sponge, not NTRU+864's fixed-size
specialization. That specialization is the single largest lever in the 864
campaign (≈4358 and ≈4103 cycles), but it is an optimization and 864 itself
reached it at gate 53 of 58. Recorded as M2-1.

`support.c` holds the elementwise and natural-order leaves — `poly_cbd1`,
`poly_sotp_*`, `poly_sub`, `poly_triple` — transcribed from the 1152 reference.
They are order-agnostic or sit either side of the transform, so the
Good-Thomas layout never reaches them.

Headers were split the way 864 splits them: `pack_asm.h` / `inverse_asm.h`
carry the raw-array kernels, `pack.h` / `inverse.h` the `poly *` API that
`kem.c` compiles against.

## Scope: what this gate does and does not prove

**Does:** the arithmetic is right, end to end, against the authoritative KAT
vectors — forward, basemul, basemul_add, baseinv, the R⁻¹ boundary, the fused
inverse-to-ternary, the codec, and the KEM flow around them.

**Does not:** this ran on macOS/arm64. It is *not* the NTRU+864 release gate.
Still owed, on Linux/AArch64:

- `make check`'s other arms: source manifest, ABI sentinels, canonical decode
  sweep at package level, zeroization, deterministic SUPERCOP export
- **the per-leaf non-invertibility suite owed since G5** — 864 gates this with
  808 failure/alias/wipe cases; this package has not earned that claim
- a `-D__STDC_WANT_LIB_EXT1__=1` flag was needed for `secure_clear` on this
  host; the Linux build path should be confirmed rather than assumed

No Pi 5 measurement and no performance claim of any kind.

## Not yet promoted

This lives in `experiments/`, not in
`ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+1152/`.
Promotion is a separate, deliberate step once the release gates above pass on
the right host.
