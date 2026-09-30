# NTRU+ for AArch64 (Armv8-A Neon)

NTRU+768, NTRU+864 and NTRU+1152 with a Good-Thomas (GT) NTT, for Linux/AArch64
(ELF) and macOS/AArch64 (Mach-O):

```text
aarch64/
  NTRU+768/    implementation, tests, canonical KAT, docs
  NTRU+864/    implementation, tests, canonical KAT, docs
  NTRU+1152/   implementation, tests, canonical KAT, docs
```

Each set builds and validates on its own with `make check`. The three share the
same Keccak-f[1600] permutations, mlkem-native's scalar and FEAT_SHA3 routines.
Start with each package's README: build, validation, and performance against
the official implementation (`github.com/ntruplus/ntruplus` main 3991b2a, in
SUPERCOP 20260831's leaf form).

The performance figures come from an Apple M2 Pro (macOS, Apple Clang,
FEAT_SHA3) and a Raspberry Pi 5 (Cortex-A76, Linux, GCC, no FEAT_SHA3),
including SUPERCOP 20260831 on the Pi 5. The tools that produce them are in
[`bench/`](../../../bench/README.md).

## SUPERCOP

No SUPERCOP leaf is checked in. Export one into a fresh directory, for example:

```sh
cd NTRU+864
python3 scripts/export_supercop.py /path/to/supercop/crypto_kem/ntruplus864/aarch64-opt
```

NTRU+864 and NTRU+1152 export the same leaf on any host; NTRU+768's exporter
runs on Linux/AArch64 with GCC. Each leaf is generated from the sources that
`make check` validates, declares `goal-constbranch` and `goal-constindex`, and
passes SUPERCOP's TIMECOP. `../supercop_archive.py` collects these three leaves
and the AVX2 ones in one archive.

## Source manifests and release archive

```sh
for s in NTRU+768 NTRU+864 NTRU+1152; do make -C $s manifest-check; done
git archive --format=zip --prefix=ntruplus-aarch64/ \
  --output=/tmp/ntruplus-aarch64.zip HEAD:production/Additional_Implementation/aarch64
```

## License

Each package's `README.md` (section License) lists the licenses of its files:
MIT for the Official code and the GT changes (`LICENSE`), Apache-2.0 OR ISC OR
MIT for the Keccak files from mlkem-native (`LICENSE.mlkem-native`), and the
upstream notices of `fips202.c` and the KAT harness.
