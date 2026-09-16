# NTRU+768 AVX2 GT Clean implementation

This directory is the production-shaped source root of the fastest qualified
GT implementation.  It follows SUPERcop's flat implementation layout.  The
`experiments/` subdirectory is archival research material and is not part of
the production source list.

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
- `pack.s`: Q24 GT-native unpack, pack, virtual-sum pack, and native equality
  routines.
- `keygen.c`, `encap.c`, `decap.c`: resolved production call paths.
- `kem.c`: public KEM API wrappers.

There are no runtime layout selectors. Key generation uses the P/J1 path;
encapsulation and decapsulation use the persistent M path.  See
[`SYMBOLS.md`](SYMBOLS.md) for symbol notation and [`LAYOUTS.md`](LAYOUTS.md)
for the typed representation contracts.

Encapsulation uses QL2 at the message/product convergence point. Message
Forward and an Encap-private general BaseMul emit QL2 directly; the two-source
serializer adds them and completes the last Q24 routing layer. The semantic
sum is not materialized. `encap-slot-pad.s` preserves the qualified 611-byte
caller slot and `e0v-tail.ld` retains the old E0V helper plus the deterministic
page-aligned QL2 RX cluster without moving pre-existing hot code or rodata.

The selected Encap scratch map has four polynomial slots. The `m` slot first
holds the coefficient producer and is overwritten by `ntt_m` only after the
frontend has consumed it. This reduces the frame from 8128 to 6592 bytes; it
is a resource-shape improvement, not a claimed cycle speedup.

The production root deliberately excludes default-off experiments such as F14,
TF1, B3-final-store-add, sidecar, streaming Q24-to-B3, and arbitrary
linker-padding variants. A candidate enters this directory only after it is
selected as a whole-operation component.

The numbered research archive and its current architecture-closure summary are
documented in [`experiments/README.md`](experiments/README.md).

The frozen Official implementation is not duplicated here.  Local tests and
KAT harnesses are taken from:

```text
../../../../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
```

`make check` builds and runs the GT Clean functional test and KAT generator
using that frozen third-party harness.  Production source files remain the
flat files in this directory.

## Link-time constant-table closure

Assembly-local constant tables are emitted in independently collectable
`.rodata.gtclean.*` input sections.  The local build enables
`-ffunction-sections -fdata-sections` and `--gc-sections`, so a selected
production symbol retains only the table groups it references.  Adjacent
labels without an independent alignment boundary remain in one section; this
preserves intentional base-plus-offset table contracts.

This is an executable-image hygiene rule, not an arithmetic optimization.
It removes dormant experiment tables and makes selected-symbol placement less
dependent on uncalled variants.  It does not imply that every removed byte
would otherwise cause a dynamic load.

For the bundled functional-test ELF on the qualification host, the closure
changed:

| Section / file | Before | After |
|---|---:|---:|
| `.text` | 47,608 B | 47,096 B |
| `.rodata` | 59,664 B | 20,640 B |
| ELF file | 130,888 B | 89,080 B |

The comparison is build-harness-specific.  Qualification additionally checks
that normalized instruction sequences of common production symbols are
unchanged and that the generated KAT response is byte-exact.

## Reproduction

Install the production file set into a fresh SUPERcop implementation directory:

```sh
./install-supercop.sh /home/nuc/supercop-20260627 avx2-gt32-clean
```

The installer refuses to overwrite an existing target.  Benchmark method and
the source baseline are documented in [`BENCHMARK.md`](BENCHMARK.md).

The qualified SUPERcop link must use the same executable-layout recipe as the
production build. From either this directory or the installed export, run:

```sh
make qualified-supercop SUPERCOP_ROOT=/home/nuc/supercop-20260627
```

This builds matched pre-E0V/E0V measure ELFs and fails unless at least 80
pre-existing hot symbols, `.rodata`, the caller reservation, tail alignment,
and RX/RWX security properties satisfy the layout contract. The generated
`qualified/build/layout-audit.json` is the machine-readable qualification map.
