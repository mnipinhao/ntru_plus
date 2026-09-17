# NTRU+768 SUPERCOP leaves

Materialized implementation directories for a SUPERCOP tree. Each leaf is
generated from the corresponding release package and is byte-reproducible:

```text
crypto_kem/ntruplus768/aarch64            AArch64 Neon
crypto_kem/ntruplus768/avx2-gt32-clean    x86-64 AVX2
```

Regenerate or verify a leaf with the matching script under `../scripts/`.
`check` rebuilds the leaf into a temporary directory and compares it byte for
byte, failing on any missing, extra, or changed file:

```sh
python3 ../scripts/generate_supercop_ntruplus768_avx2.py check \
  --gt-root ../Additional_Implementation/avx2/NTRU+768 \
  --leaf-root crypto_kem/ntruplus768/avx2-gt32-clean
```

## What a SUPERCOP measurement of these leaves establishes

SUPERCOP builds each leaf with its own compiler records and its own link step.
It copies an implementation directory recursively but compiles only the
top-level `.c`/`.s`/`.S` files, and it never passes `-T`. A leaf therefore
cannot carry a linker script, a section-placement contract, or any other
layout control.

This matters for the AVX2 package, whose qualification is stated as an
executable-layout contract: a 611-byte Encap caller reservation, page-aligned
RX `.e0v_tail` / `.ql2_tail` / `.rhash_tail` sections, and address- and
byte-identical pre-existing hot symbols. None of that is reproduced by a
SUPERCOP build. The promoted Encap steps are worth roughly 57-92 core cycles
against a ~46,000-cycle Encap, which is below what an uncontrolled link can
resolve.

Read the two numbers as separate claims:

- A SUPERCOP result is the whole-KEM cost **as SUPERCOP builds it**, against
  the other implementations in the same tree and the same harness.
- The promoted-step A/B is the layout-controlled, fixed-ELF paired result from
  `make qualified-supercop` in the AVX2 package, audited by
  `qualified/audit-layout.py`.

Neither substitutes for the other, and a SUPERCOP delta must not be reported
as the promoted-step gain.

## `crypto_kem/ntruplus768/avx2-gt32-clean` — x86-64 AVX2 GT

Drop `crypto_kem/ntruplus768/avx2-gt32-clean` into a SUPERCOP tree. The leaf
name keeps the Official `avx2` implementation in place so both are measured in
the same run.

The leaf is the flat compilable closure of the AVX2 GT release package: the GT
frontend and M/P terminal transforms, BaseMul and BaseInv, the Q24 codec, the
promoted QL2 Encap path, the direct r pack-to-hash helper, and the AVX2 Keccak
backend, together with `api.h`, `params.h`, `architectures`, and the
constant-time goal files. `invntt.s` carries its generated inverse-tail
constant stream inlined, so the leaf has no subdirectory and does not depend on
the assembler's working directory.

Four things in the package are deliberately absent from the leaf:

- `e0v-tail.ld`, because SUPERCOP never applies a linker script.
- `encap-slot-pad.s`, whose only purpose is to hold the caller-slot
  reservation open under that script.
- `qualified/`, the frozen E0V and QL2 controls used by the layout-controlled
  A/B. SUPERCOP would copy them without compiling them.
- `randombytes.c` and the package test and KAT harness, which SUPERCOP
  supplies itself.

Built with SUPERCOP-style flags and no linker script, the leaf reproduces the
qualified KAT response byte for byte
(SHA-256 `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`).

## `crypto_kem/ntruplus768/aarch64` — AArch64 Official-shell / GT-polynomial

Drop `crypto_kem/ntruplus768/aarch64` into a SUPERCOP tree. Official CBD/SOTP,
centered mod-3, NO_CE hash, utility clearing and public headers are retained.
The NTT, inverse NTT, base arithmetic, pack/unpack and their operation-specific
KEM call sites use the GT Production backend. The public SHAKE and symmetric
hash APIs remain unchanged. Hash-f/hash-h retain their existing construction;
hash-g uses the fixed-size register-resident AArch64 sponge. Generic SHAKE uses
the standalone AArch64 x1 Keccak-f[1600] backend. The lowercase scalar
assembly is always available. The uppercase feature-gated assembly and
`fips202.c` select the Arm SHA3 backend only when the SUPERCOP compiler flags
define `__ARM_FEATURE_SHA3`; otherwise the leaf remains safe on Cortex-A76.
