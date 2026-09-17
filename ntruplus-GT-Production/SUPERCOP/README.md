# NTRU+ AArch64 SUPERCOP leaves

Copy the directory into the matching SUPERCOP algorithm:

```text
crypto_kem/ntruplus864/aarch64/
```

The checked-in leaf is a deterministic materialization of the production
sources. Assembly is preprocessed for Linux/AArch64 and stored with lowercase
`.s` suffixes so SUPERCOP discovers it without repository-specific build
rules. It uses SHAKE256 and remains safe on Cortex-A76 without
requiring the Armv8.4 SHA3 extension.

Regeneration scripts are in `../scripts/`.
