# NTRU+864 GT KEM — production optimization package

Current work order and gate status are maintained in
[OPTIMIZATION-ROADMAP.md](docs/OPTIMIZATION-ROADMAP.md). Update that ledger after
every optimization gate so deferred and rejected work does not disappear.

Latest production promotion is P48: Encaps writes P46's canonical Full bytes
directly into the `0x01 || bytes` SHAKE256 input through `hash_g_fr0`, removing
the otherwise immediate 1296-byte `hash_g` copy. Generic P46 and generic
`hash_g` remain available unchanged.

P47 remains selected for Decaps: Decaps no longer materializes its final
Full serialization into a 1296-byte temporary before comparison.  A private
constant-time assembly consumer compares each canonical 12-byte record as soon
as P46 forms it; generic P46 remains selected by Keygen and Encaps.  Pi 5
Decaps improves by 143.650 paired-median cycles, with 19 fewer instructions,
97.5 fewer branches and a 1072-byte smaller frame.

P46 remains the generic Full ToBytes implementation: it uses P24's globally interned
rotation/transpose DAG with the exact two-instruction `USHR+MLA` residual
canonicalization; Small remains P24. The Full candidate removes 108 retired
instructions/call and improves the exact Pi 5 boundary by 8.364 cycles.
Keygen/Encaps/Decaps improve by 13.500/13.650/5.450 paired-median cycles. The
user explicitly approved this target-silicon promotion despite the preserved
Slothy proxy regression from 1495 to 1562 modeled cycles.

P24 established the underlying Full and Small ToBytes layout: both use P23's
globally interned rotation/transpose DAG and accepted three-output schedules.
The kernels keep the P18 FR0/wire-byte ABI and no-coefficient-scratch contract,
but retire 194 fewer instructions and six fewer reads per call.  Against P18,
Pi 5 Full/Small improve by 15.906/39.660 cycles and complete
Keygen/Encaps/Decaps by 147.000/67.325/62.625 paired-median cycles.  P24 passed
manifest, linked-symbol/object, exact-byte, KAT, malformed-input,
input-immutability, ABI/cleanup and PMU gates from exact commit archives.
P25 then re-profiled this exact production against the selected SUPERCOP
20260831 AArch64 source: GT leads Keygen/Encaps/Decaps by
1167.750/1440.450/694.525 cycles.  The largest remaining positive matched
boundary is Inverse-to-ternary (+280.675 cycles); aggregate ToBytes is second.
The comparison target remains a fixed selected snapshot, not an independently
verified latest-upstream claim.
P26 then reconciled that Inverse gap instruction-for-instruction.  GT already
uses 151 fewer modular-multiply instructions; fragmented lane extraction,
stores and repeated constant loads dominate.  P27 therefore searches an
inverse9→I16 lane basis that directly feeds full-vector raw-to-ternary output,
without replaying P11's post-store routing.
P27 has now passed that machine-only search.  Its unique best matching pairs
the six existing main P8 blocks into three 32-state I16 regions, compacts the
tail to twelve Q records, and maps exactly 108 dense scratch records to 108
natural output records with at most four live TBL sources.  The static budget
removes at least 1,314 instructions after conservative parking/routing charges.
Production remains unchanged until P28 proves physical allocation, complete
correctness and Pi 5 Inverse/Decaps improvement.
P13-C previously changed the separately shaped tail Inverse16 so it now
uses the same composite-terminal algebra with its own six-lane layout.  Together
P13-B/C save 462 retired Inverse instructions and about 507 paired-median Decaps
cycles on Pi 5 while preserving the P8 raw-output bound and memory ABI.
Production also includes P10-A's direct-FR0 BaseInv, SIMD failure aggregation,
scheduled pair+merge ToBytes, and P3-A's constant-resident `center864` path for
the retained centered Inverse API.
Mac and Pi 5 KEM/KAT, canonical rejection, malformed-input, BaseInv
failure/alias/AAPCS/scratch-wipe and paired PMU gates pass.  See
[NATIVE-INTEGRATION.md](docs/NATIVE-INTEGRATION.md),
[TOBYTES-INTEGRATION.md](docs/TOBYTES-INTEGRATION.md) and
[VALIDATION.md](docs/VALIDATION.md).

This self-contained Linux/AArch64 package fixes P3B41 K1 as the shared Forward
for Keygen, Encaps and Decaps. Stock NTRU+864 and GT768 are unchanged.
The only public supported API is `api.h` (`crypto_kem_keypair/enc/dec`).
Internal `poly_*` names are not a general polynomial multiplication API.

## Build and read

On Linux AArch64 with GCC: `make check`. This verifies release hygiene and the
source manifest, runs KEM/AAPCS64/canonical/zeroization tests, compares the
generated NIST-style KAT byte-for-byte with the checked-in response, and checks
deterministic SUPERCOP export. KAT generation alone is not a comparison; see
`docs/VALIDATION.md`.
The application supplies `randombytes`; tests supply local randombytes.c or
the KAT RNG. Hash policy is SHAKE256 with NO_CE/fips202.c.

Read in this order:

1. `kem.c` and the **kem-normal.o rule in Makefile**: explicit per-file aliases
   select GT consumers, while crypto_kem_* retains the public names.
2. `transform_api.c`, `gt864_native.h/.c` and `gt864_native_public.S`: K1
   Forward, D1 BaseMul, direct FR0 BaseInv and the paired first-Decaps
   R^-1 BaseMul/Inverse.
3. `gt864_forward_poly_ntt.S`: public ABI wrapper saves/restores d8–d15.
4. `gt864_top_split.s`, `tail_layout.S`, `gt864_forward_six_bank.S`:
   raw top, T1 bank-major tail, K1 Pass-2.
5. `gt864_fr0_basemul_d1.c`, inverse assembly and tables.
6. `gt864_tobytes.h`, `gt864_tobytes.c`, `gt864_p18_tobytes.h`, and
   `gt864_p18_tobytes_{full,small}.S`: active caller-selected full/small
   normalization, globally interned routing and byte packing. `byte_api.c` and
   `cluster_transpose_frombytes.c` implement the checked canonical decoder.

## Integration policy and range

The production closure is listed explicitly by `KEM_OBJECTS`; historical
candidates, differential oracles, raw profiler logs and campaign sources live
outside this package. `scripts/export_supercop.py` exports only that accepted
closure. No profiler or benchmark source participates in a release build.

K1 replaces stage1.node0's b=1 Algorithm-10 reduction with a register copy.
Its larger representatives are safe for the proven KEM producer/consumer
chains, not arbitrary two-Forward-output multiplication. Keygen f's proven
Forward bound is 28765; the Decaps subtraction interval is [-24794,28894].
Do not infer safety from modular equivalence alone. The archived caller proof
includes K1 and K2; this package selects **K1 only**, never their combination.

`SOURCE-MANIFEST.sha256` freezes the release source tree. Historical proofs and
PMU evidence remain in the repository experiment archive rather than in the
production/export package.
There is no build-time dependency on the campaign or Slothy.

Generic polynomial multiplication is outside this package's contract.
KEM decoding uses gt864_fr0_frombytes_checked: all 12-bit values must be < q.
Encaps rejects noncanonical pk; Decaps rejects noncanonical ct/sk components.
Legacy void FromBytes helpers are internal compatibility APIs, not validators.
gt864_support_abi.S preserves d8-d15 around the six legacy support helpers.
Keygen now clears its sampling workspace, coins, f/finv/g/ginv and h/hinv.
The shared sampling workspace is overwritten across retries and erased on exit.
See the parent repository experiments/gt864-native-asm/CLEANUP-BASEINV-RESULTS.md
for the 2026-09-09 baseline and BaseInv stage measurements.
K1 import history above predates the scheduled ToBytes integration; see its
separate range, scheduling and validation record. Security parameters are unchanged.
