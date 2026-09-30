# NTRU+

Optimized implementations of the NTRU+ key encapsulation mechanism (NTRU+768,
NTRU+864 and NTRU+1152) for Armv8-A Neon and x86-64 AVX2, laid out as the
official submission's `Additional_Implementation/<architecture>/NTRU+<set>/`.

| Directory | Contents |
|---|---|
| [`production/Additional_Implementation/aarch64/`](production/Additional_Implementation/aarch64/README.md) | AArch64 Neon, with a Good-Thomas (GT) NTT |
| [`production/Additional_Implementation/avx2/`](production/Additional_Implementation/avx2/README.md) | x86-64 AVX2: the official AVX2 implementation with drop-in kernel replacements and mlkem-native's Keccak, byte-identical to it in pk, sk, ct and ss |
| [`bench/`](bench/README.md) | The tools behind the AArch64 packages' performance figures |

Each package is self-contained (source, tests, canonical KAT and SUPERCOP
export) and validates with `make check`. Its README reports its performance
against the official implementation: `github.com/ntruplus/ntruplus` main
3991b2a, in SUPERCOP 20260831's leaf form.

## Quick start

On an AArch64 host (Linux or macOS):

```sh
for s in NTRU+768 NTRU+864 NTRU+1152; do
  make -C production/Additional_Implementation/aarch64/$s check
done
```

On an x86-64 host with AVX2, BMI1 and BMI2:

```sh
for s in NTRU+768 NTRU+864 NTRU+1152; do
  make -C production/Additional_Implementation/avx2/$s check
done
```

## SUPERCOP

Each package exports its own SUPERCOP leaf. Once every package passes
`make check` (the AArch64 ones on AArch64, the AVX2 ones on x86-64), running

```sh
python3 production/Additional_Implementation/supercop_archive.py ntruplus-supercop.zip
```

on Linux/AArch64 writes all six into one archive (`.zip` or `.tar.gz`) that
unpacks over a SUPERCOP tree: `crypto_kem/ntruplusN/avx2-opt` and
`crypto_kem/ntruplusN/aarch64-opt` for N = 768, 864, 1152. Each leaf holds the
sources, `api.h`, `architectures`, `goal-constbranch`, `goal-constindex` and the
license files.

## License

Each package carries its licenses: MIT for the official NTRU+ code and the
changes to it (`LICENSE`), and the upstream license of any vendored code.
