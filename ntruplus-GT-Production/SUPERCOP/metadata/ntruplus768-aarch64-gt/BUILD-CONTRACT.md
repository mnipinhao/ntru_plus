# Build contract

- Target: Linux AArch64, NTRU+768.
- Compile every top-level `.c` and `.s` in the leaf; SUPERCOP supplies
  `crypto_kem.h`, `randombytes.h`, randombytes and cryptoint support.
- Required public symbols: `crypto_kem_keypair`, `crypto_kem_enc`,
  `crypto_kem_dec`.
- `kem_api.s` preserves d8-d15 once at each public KEM boundary.
- No namespace adapter is present: this leaf is one standalone implementation.
- Recreate assembly with Linux `gcc -E -P -x assembler-with-cpp`.
