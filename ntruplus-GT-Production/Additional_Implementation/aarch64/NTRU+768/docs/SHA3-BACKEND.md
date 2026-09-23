# Keccak-f[1600] backends

The SHAKE interface in `fips202.c` is portable C.  Only the Keccak-f[1600]
permutation has AArch64 backends, selected at compile time; there is no runtime
dispatch.

| Build | Permutation | Source |
| --- | --- | --- |
| `__ARM_FEATURE_SHA3` defined | `ntruplus_keccak_f1600_x1_v84a_aarch64` (EOR3/RAX1/XAR/BCAX) | `keccakf1600_v84a.S` |
| otherwise | `ntruplus_keccak_f1600_x1_aarch64` (scalar) | `keccakf1600.S` |

Cortex-A76 has no SHA3 extension, so the Raspberry Pi 5 and the SUPERCOP A76
builds use the scalar backend.  Apple M-series builds with SHA3 enabled use the
v8.4-A backend.  `keccakf1600_v84a.S` assembles to an empty object when the
feature is absent.

The v8.4-A round body comes from `pq-code-package/mlkem-native` revision
`438f0da19dc3d5299bb2e318d1067f9a298f1bcf`; the generated upstream source has
SHA-256 `8f7841f3c130549ccc64af236e8b8d6f811cba1cdafd83a8b12424476973d3da`.
Its NTRU+ integration is not itself formally verified.

Both backends take `(state, round constants)` and preserve AAPCS64 `d8-d15`.
The package KAT (`make kat-check`) is byte-identical with either backend; a
build with `-U__ARM_FEATURE_SHA3` on a SHA3-capable host checks the scalar path.
