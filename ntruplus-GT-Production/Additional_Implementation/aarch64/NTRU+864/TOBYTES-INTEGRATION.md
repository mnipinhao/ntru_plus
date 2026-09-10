# Scheduled pair+merge dual-entry ToBytes — promoted 2026-09-10

The original dual-entry integration is retained below as history.  Production
now additionally promotes the scheduled pair+merge candidate: the first two
pairs write 432 bytes of scratch and the third pair is consumed directly by
the row merge.  Mac and Pi 5 validation and the selected Official comparison
are complete.

## Exact scope

This document's scope is ToBytes.  The package also contains separately
validated Forward K1, D1 BaseMul/BaseMulAdd, native BaseInv and paired R^-1
BaseMul/Inverse; their contracts are documented elsewhere.

`kem.c` directly selects `gt864_fr0_tobytes_small` for h, hinv, c and r2.
It selects `gt864_fr0_tobytes_full` for f, r and r1. `poly_tobytes` and the old
P3B12 adapters remain as legacy internal helpers, not the active KEM path.
The small entry is not a generic signed-int16 serializer.

Sources: `gt864_tobytes.c/.h`, `gt864_tobytes_public.S`, full/small/merge
`_core.S`, `gt864_pair_merge_{full,small}.S` and `byte_merge_tables.h`. These
are self-contained, with no experiment-tree build dependency.  The promoted
pair+merge instruction order is copied from the tested scheduled `.opt.S`;
only production comments and Apple symbol aliases are added.

## Range and security review

- D1 ends each output component with signed32 SQRDMULH by 621199, MLS by 3457,
  and narrowing. Exact quotient-interval enumeration over all 2^32 inputs proves
  [-3023,3023]. Both BaseMul and BaseMulAdd use this tail, including malformed
  ciphertext paths. This is an output range proof, not a substitute for product
  correctness. Re-run `experiments/gt864-native-asm/tobytes-producer-audit/proof.py`.
- Exhaustive scalar check over [-3456,3456] proves sign-add canonicalization
  equals full normalization. Forward-domain counterexamples prohibit using the
  small entry on f/r/r1; their Barrett reductions remain.
- Entry selection is static by caller. Wrapper branches depend only on the
  entry flag and fixed loop/pair counters, never coefficients. The three cores
  have no conditional branches. Loads/stores use public pointers and constant
  offsets. TBL indices come from fixed public tables; coefficient bytes are
  table operands, not memory addresses or secret-dependent indices.
- Coefficients remain in SIMD registers. No coefficient-to-GPR branch/address
  path was introduced. Arithmetic instruction choice is input-independent.
- Input/output must be disjoint; all seven KEM sites satisfy this. Input is 1728
  bytes and output is exactly 1296 bytes. Public wrapper preserves AAPCS GPRs
  and d8-d15, allocates and wipes 432 scratch bytes. SIMD
  temporaries are cleared before restoring caller-owned registers.
- Native tests cover byte equality, input immutability, output canaries, ABI
  and wipe. Canary tests are not inaccessible-page overread tests. Review is
  limited to this delta; it is not a formal microarchitectural side-channel
  proof or a new whole-scheme security certification.

## Validation

`verify-production-mac.py` derives the exact source/object selection and flags
from `make -Bn libgt864.so`, compiles it natively with Clang, then links the
objects directly into the existing test and KAT executables. This avoids Linux
shared-library linker flags on Mac; it does not validate the Linux .so link.

- Old package: 27 objects; integrated package: 32 objects.
- Both pass 64 KEM round trips and tampered-ciphertext checks.
- Both generate 100 KAT cases; complete `.rsp` files compare byte-identically.
- SHA256: `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Complete D1 and Forward six-bank objects compare byte-identically.
- Prior scheduled standalone Mac/Pi tests and experimental full-KEM tests remain
  recorded in `experiments/gt864-native-asm/TOBYTES-TIMING-RESULTS.md`.

Scratch validation artifacts:
`/tmp/gt864-tobytes-production.4JUuZs/{baseline,old-build,new-build}`.
They are disposable; the KAT digest and source manifest are persistent evidence.

## Current Pi 5 result

The promoted production package passes 100 KAT cases and the complete
valid/tampered/malformed transcript. Relative to the selected SUPERCOP 20260831
Official, complete Encaps is 46007.625 versus 46413.375 cycles (-0.87%).  The
complete KEM values and environment are recorded in
`experiments/gt864-native-asm/baseinv-tobytes-next-model/production-promotion-results.json`.

## Benchmark policy

The next Official comparison must use
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64/` on Pi5, not the
archived 20260627 tree. The path and SHAKE256 hash_f were checked read-only.
See `bench/aarch64/gt-production/OFFICIAL-BASELINE.json`. Do not claim this
snapshot is upstream latest without an independent provenance check.

The full/small isolated boundary improvements remain diagnostic; complete KEM
numbers above are the production result.  Future comparisons use the same
selected Official directory and record whether upstream provenance was checked.
