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

## On the Pi 5 — the real target

Everything above also passes on `pi@100.99.191.9`, Cortex-A76, Linux
6.18.33, GCC 14.2.0, `throttled=0x0`, host idle. Evidence: `pi-results.json`.

| gate | result |
| --- | --- |
| KAT | **byte-identical**, sha256 `2ddfc810c4…64c3` |
| `test_kem` | 64 round trips and tampered-ciphertext rejection |
| `test_baseinv_fail` | **288/288 leaves** reject with 1 and clear, aliased and not |
| `test_canonical` | **13,824 cases**, 0 failures |
| `test_zeroization` | 26 clear calls, 37,526 bytes, 0 nonzero after |
| `test_abi` | **8/8 sentinels `mask=0x00000`** |

Three of these are worth calling out.

**The Linux build caught a real defect.** `-D_DEFAULT_SOURCE` was missing, so
`explicit_bzero` and `syscall` were implicitly declared. macOS took a different
branch of `secure_clear.h` and never noticed. NTRU+864's Makefile has the flag;
this one had dropped it.

**The per-leaf non-invertibility debt from G5 is paid.** `test_baseinv_fail`
walks every one of the 288 leaves, zeroes it inside an otherwise invertible
polynomial, and requires rejection with a fully cleared output — then repeats
through an exact `out == in` alias. Until now the coverage was incidental: a
few naturally non-invertible inputs and an all-zero transform.

**The ABI sentinels validate the riskiest structural choice.** All eight public
entry points preserve every callee-saved register. That is what makes the asm
driver's `SAVE_PUBLIC` correct around leaves that clobber v8–v15, and what makes
calling the C tail from assembly safe.

## Still owed

- Source manifest and deterministic SUPERCOP export — the latter belongs to G9.
- No performance measurement of any kind. Nothing here was timed.

## Not yet promoted

This lives in `experiments/`, not in
`ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+1152/`.
Promotion is a separate, deliberate step.

## Not yet promoted

This lives in `experiments/`, not in
`ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+1152/`.
Promotion is a separate, deliberate step once the release gates above pass on
the right host.
