# NTRU+864 GT KEM — K1 integration

This self-contained Linux/AArch64 package fixes P3B41 K1 as the shared Forward
for Keygen, Encaps and Decaps. Stock NTRU+864 and GT768 are unchanged.
The only public supported API is `api.h` (`crypto_kem_keypair/enc/dec`).
Internal `poly_*` names are not a general polynomial multiplication API.

## Build and read

On Linux AArch64 with GCC: `make check`. This verifies the source manifest,
builds `libgt864.so`, runs 64 valid/tampered KEM tests and generates NIST-style
KAT files. KAT generation alone is not a comparison; see VALIDATION.md.
The application supplies `randombytes`; tests supply local randombytes.c or
the KAT RNG. Hash policy is SHAKE256 with NO_CE/fips202.c.

Read in this order:

1. `kem.c` and the **kem-normal.o rule in Makefile**: explicit per-file aliases
   select GT consumers, while crypto_kem_* retains the public names.
2. `gt864_poly_api.c`: K1 Forward, GT inverse, centered BaseInv adapter, D1.
3. `gt864_forward_poly_ntt.S`: public ABI wrapper saves/restores d8–d15.
4. `gt864_top_split.s`, `tail_variants.S`, `gt864_forward_six_bank.S`:
   raw top, T1 bank-major tail, K1 Pass-2.
5. `gt864_fr0_basemul_d1.c`, inverse assembly and tables.
6. `byte_api.c`: candidate ToBytes → r9_to; candidate FromBytes → cluster transpose.
   `byte_boundary.c`, `route9.c`, `cluster_transpose_frombytes.c` implement them.

## Integration policy and range

The source snapshot is copied from P3B41 K1/build/sync/raw, not linked to it.
Internal experiment symbol names and compatibility helpers deliberately remain
in this first integration. Stock support files and old helper functions are
NOT evidence that the KEM uses stock Forward: inspect the object relocations.
No profiler or benchmark source participates in the library build.

K1 replaces stage1.node0's b=1 Algorithm-10 reduction with a register copy.
Its larger representatives are safe for the proven KEM producer/consumer
chains, not arbitrary two-Forward-output multiplication. Keygen f's proven
Forward bound is 28765; the Decaps subtraction interval is [-24794,28894].
Do not infer safety from modular equivalence alone. The archived caller proof
includes K1 and K2; this package selects **K1 only**, never their combination.

`SOURCE-MANIFEST.sha256` freezes imported sources (kem_stock.c renamed kem.c).
`evidence/caller-range-proof.json` preserves the original range proof and
original source hashes. This is inherited evidence, not a new independent
proof run: imported K1 sources and core objects are checked unchanged.
There is no build-time dependency on the campaign or Slothy.

Generic polynomial multiplication is outside this package's contract.
No new scheduling, arithmetic, layout or security-parameter change was made.
