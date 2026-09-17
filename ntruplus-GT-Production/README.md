# NTRU+ AArch64 production implementations

The release is split into two views:

```text
Additional_Implementation/aarch64/
  NTRU+768/
  NTRU+864/
SUPERCOP/
  crypto_kem/ntruplus864/aarch64/
```

`Additional_Implementation` contains self-contained source, tests, KATs, and
implementation contracts. On this branch, `SUPERCOP` contains the materialized
NTRU+864 algorithm leaf; the 768 production branch uses the same separation.
Development campaigns, scheduling inputs, rejected
candidates, and benchmark logs remain outside this release tree.

Build and validate a parameter set on AArch64 with `make check` from its
`Additional_Implementation` directory.
