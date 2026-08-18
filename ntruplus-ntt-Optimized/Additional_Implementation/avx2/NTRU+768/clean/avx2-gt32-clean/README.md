# NTRU+768 AVX2 clean implementation

This directory is a standalone, production-shaped export of the fastest
qualified GT implementation.  It is intentionally separate from the
`experiments/` tree and follows SUPERcop's flat implementation layout.

The public API is unchanged:

```c
crypto_kem_keypair(pk, sk)
crypto_kem_enc(ct, ss, pk)
crypto_kem_dec(ss, ct, sk)
```

File names describe the primitive rather than the research history:

- `ntt.s`: shared frontend.
- `ntt_m.s`, `ntt_p.s`: M- and P-terminal forward transforms. They remain
  separate translation units so their assembly-local constant labels stay
  private, as in the qualified source.
- `basemul.s`: M-domain BaseMul and the F0-by-J1 key-generation product.
- `baseinv.c`, `batch_inverse.s`: P-domain J1 BaseInv and batch inversion.
- `invntt.s`: M-domain inverse core and coefficient-output tail.
- `pack.s`: Q24 GT-native unpack, pack, and native equality routines.
- `keygen.c`, `encap.c`, `decap.c`: resolved production call paths.
- `kem.c`: public KEM API wrappers.

There are no runtime layout selectors. Key generation uses the P/J1 path;
encapsulation and decapsulation use the persistent M path.  See
[`SYMBOLS.md`](SYMBOLS.md) for symbol notation and [`LAYOUTS.md`](LAYOUTS.md)
for the typed representation contracts.

This snapshot deliberately excludes default-off experiments such as F14,
TF1, B3-final-store-add, sidecar, streaming Q24-to-B3, and linker-padding
variants.  A candidate enters this directory only after it is selected as a
whole-operation component.

## Reproduction

Install into a fresh SUPERcop implementation directory:

```sh
./install-supercop.sh /home/nuc/supercop-20260627 avx2-gt32-clean
```

The installer refuses to overwrite an existing target.  Benchmark method and
the source baseline are documented in [`BENCHMARK.md`](BENCHMARK.md).
