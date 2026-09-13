# Input-once dual-entry ToBytes — P24 global DAG promoted 2026-09-13

Production uses P23's global common-subexpression DAG and accepted three-output
schedule, promoted by P24 for both Full and Small.  It interns repeated source
rotations and transpose nodes across consumers instead of rebuilding them per
output class.  Each top branch
loads its 54 FR0 Q vectors once, retires a routed eight-coefficient output as
soon as its last source lane arrives, normalizes it, packs it to twelve bytes,
and writes its final wire address.  The complete call has 108 coefficient
loads, no coefficient scratch, and no intermediate nine-row array.

The two entry points deliberately remain different:

- full accepts any signed `int16_t` and applies 108 Barrett-Shoup reductions
  followed by negative correction;
- small is restricted to the already-proved `(-3457,3457)` KEM producers and
  uses only negative correction.  Its target object contains no `SQRDMULH` or
  `MLS` normalization instruction.

The exact composed FR0-to-wire map hash is
`087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270`.
Both target cores have a peak of sixteen partial output vectors and no vector
spill.  Public wrappers clear `v0-v31` and restore caller-owned `d8-d15`.

On the Pi 5 public boundary, P9 changes full from 1766.672 to 1518.164 cycles
and small from 1370.425 to 1173.769 cycles.  The combined KEM candidate changes
Keygen/Encaps/Decaps by -619.875/-415.800/-435.925 cycles and by exactly
-1200/-811/-811 retired instructions.  Complete evidence is in
`experiments/gt864-p9-tobytes-routing/`.

P15 then preserved the exact Full instruction and memory multiset while
rescheduling bounded completion/normalization/pack windows.  Its public Full
boundary improved 1518.188→1441.633 cycles; its Small schedule was neutral and
was rejected.  P16 integrates only Full and keeps the P9 Small object
byte-identical.  Across 252 paired observations per operation, P16 improves
Keygen/Encaps/Decaps by 74.875/77.775/71.050 cycles with zero retired-instruction
or branch delta.  Evidence is in `experiments/gt864-p15-p9-scheduling/` and
`experiments/gt864-p16-full-tobytes-integration/`.

P18 replaced lane-edge routing with class-local partial transposes.  P23 then
globally interned the repeated rotation/transpose graph and jointly scheduled
three consumers; P24 promoted those exact artifacts.  Relative to P18,
Full/Small save 15.906/39.660 cycles, 194 instructions and six reads per call.
Complete Keygen/Encaps/Decaps save 147.000/67.325/62.625 paired-median cycles.
The public ABI and range contracts are unchanged.  Evidence is in
`experiments/gt864-p23-tobytes-global-dag/` and
`experiments/gt864-p24-p23-production/`.

## Previous implementation

The original dual-entry integration is retained below as history.  Production
previously used the scheduled pair+merge candidate: the first two
pairs write 432 bytes of scratch and the third pair is consumed directly by
the row merge.  Its source remains for audit and controlled comparisons, but
the public full/small entries no longer call it.

## Exact scope

This document's scope is ToBytes.  The package also contains separately
validated Forward K1, D1 BaseMul/BaseMulAdd, native BaseInv and paired R^-1
BaseMul/Inverse; their contracts are documented elsewhere.

`kem.c` directly selects `gt864_fr0_tobytes_small` for h, hinv, c and r2.
It selects `gt864_fr0_tobytes_full` for f, r and r1. `poly_tobytes` and the old
P3B12 adapters remain as legacy internal helpers, not the active KEM path.
The small entry is not a generic signed-int16 serializer.

Active sources are `gt864_tobytes.c/.h`, `gt864_p18_tobytes.h`, and
`gt864_p18_tobytes_{full,small}.S`.  They are self-contained, with no
experiment-tree build dependency.  P24 deliberately retains the existing P18
public symbol names and ABI while replacing both implementations with the
hash-checked P23 three-output schedules.

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
