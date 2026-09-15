# NTRU+768 AArch64 Official-shell / GT-polynomial package

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
