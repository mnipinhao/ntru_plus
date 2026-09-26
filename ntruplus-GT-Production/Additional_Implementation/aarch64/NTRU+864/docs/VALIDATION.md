# K1 production integration evidence

`experiments/...` paths below refer to the development branch `gt864-1152-cleanup`,
preserved at tag `evidence/aarch64-20260925`, where the evidence and scripts live; this release
tree does not carry them.

## Two-state Keccak for key generation's seeds (P140, 2026-09-25)

The f and g seeds (SHAKE256 of 32 coins each) are the only two independent
hashes in the KEM; `shake256_x2` permutes both states at once, with FEAT_SHA3
through `keccakf1600_x2_v84a.S` (mlkem-native's x2 routine, instructions
unchanged; about the cost of one single-state call on Apple M2) and elsewhere
as two single-state calls.  The key pair draws the next 32 coins before trying
f -- that draw is certain to be used, by an f retry or by g -- so randombytes
sees the same calls in the same order.

- KAT byte-identical with the two-state path (macOS) and the fallback (Linux);
  `make check` passes on both.
- M2 key generation 4,127 -> 3,800 ns (-7.9%); encapsulation and decapsulation
  unchanged; Cortex-A76 unchanged (the fallback path).
- SUPERCOP TIMECOP (`TIMECOP=256`) passes at `-O`, `-O2`, `-O3` and `-Os`.

## Canonical reduction in the full serializer (P134, 2026-09-24)

`reduce_canon` keeps its Barrett step (rounding multiply-high and
multiply-subtract, landing in (-q, q)) and then picks the canonical
representative with an add and an unsigned minimum instead of a sign mask and
a second multiply-subtract: four instructions either way, one multiply fewer.
Identical for all 65,536 int16 inputs (exhaustive check).  M2 keygen / decaps -7 / -8 ns; A76 keygen / encaps / decaps -0.39 / -0.41 / -0.45%.

## P133 run-based frombytes — 2026-09-24

`frombytes` is now the exact inverse of the run-based serializer: one 16-byte
load per nine-byte run at its own offset, one `tbl` expanding it to six
halfwords, an 8x8 halfword transpose, and one `and` or `ushr` per vector.  It
replaces the generated decoder, whose 388 lane inserts built each output
vector 64 bits at a time (~520 lines -> ~110).  The idea is the NEON form of
an AVX2 decoder for Official's layout; GT's runs are scattered, so each run is
loaded on its own and the transpose does what AVX2's in-lane interleave does.

Checked against the previous decoder on 200,000 inputs (half canonical, half
random bytes) and on one out-of-range coefficient at each of the 864
positions: identical output and return value, with the input ending at a guard
page.  `frombytes` M2 73.8 -> 55.4 ns, A76 640 -> 498 cycles a call.

| | M2 keygen / encaps / decaps | A76 keygen / encaps / decaps |
|---|---|---|
| before | 4,131 / 4,654 / 3,818 ns | 15,090 / 14,687 / 14,022 ns |
| after | 4,132 / 4,637 / **3,760** ns | 15,080 / 14,637 / **13,841** ns |
| | +-0 / -0.36% / **-1.5%** | +-0 / -0.34% / **-1.3%** |

## P130 codec and first-product overheads — 2026-09-23

Three M2-driven fixes to overheads around unchanged arithmetic:
- `frombytes` loads each 12-byte group with one 16-byte load instead of an
  8-byte load, a scalar load and a lane insert; the group at byte 636 of a
  half loads the 16 bytes ending at its last byte (AddressSanitizer on
  exact-size buffers: clean; with the plain load it reports the overflow).
- the decapsulation first product runs its 36 tiles in one call: constants
  set once, no per-tile `bl` and pointer shuffling.
- `tobytes` writes 113 of its 144 nine-byte runs with one 16-byte store whose
  seven extra bytes land in a neighbouring run written later (group, lane and
  store order generated and byte-simulated by
  `experiments/gt864-p130-decaps-m2/gen_store_order.py`): 288 stores become
  175.

| | M2 keygen / encaps / decaps | A76 keygen / encaps / decaps |
|---|---|---|
| before | 4,169 / 4,752 / 3,874 ns | 36,770 / 35,802 / 34,091 cyc |
| after | 4,146 / 4,731 / **3,824.5** ns | 36,449 / 35,505 / **33,652** cyc |
| | -0.55% / -0.45% / **-1.28%** | -0.87% / -0.83% / **-1.29%** |

## P124-P125 constant time, scratch ownership, range proof — 2026-09-23

- **SUPERCOP TIMECOP passes** (20260831, valgrind 3.24.0 with `libc6-dbg`,
  Pi 5, `TIMECOP=256`) at `-O`, `-O2`, `-O3` and `-Os`, with SUPERCOP's own
  checksum `b0cdac76...`.  Before this change the leaf failed on two branches:
  the secret-key decode status in Decaps and BaseInv's failure branch.
  Official's 864 leaf fails too, on `poly_fqinv_batch`.
- BaseInv is branch-free: a non-invertible input zeroes the 24 running
  inverses after the inversion, so the output is cleared on the same path.
  Keygen and the Decaps key decode declassify their status bits as Official
  does.  `test_baseinv_fail` now gates all 288 leaves (rejects and clears,
  aliased and not); removing the masking makes it fail.
- The inverse's 1,792-byte scratch is part of `kem.c`'s `io` union, overlaid on
  `buf1`/`buf3` and cleared with them on exit, at no extra cost.
- Timing, min of blocks: keygen +0.1% A76 / +0.2% M2, Decaps unchanged.
- **Range proof of the linked inverse** (interval interpreter over the
  executable's disassembly, exact error of every constant pair,
  `experiments/gt-p125-864-1152-range-proof`): for every input with
  |x| <= 2497 no intermediate leaves int16 (peak 22,473 in `packed_i9`), the
  output is in {-1,0,1}, and every q-centering input is at most 4,482, inside
  the 5,185 up to which the single correction is exact.  The proof holds up to
  |x| <= 3,640.  The 32 never-written scratch halfwords the transform reads
  (scratch + 0x60c..0x6fe, the old tail padding) never reach an output, so the
  padding needs no initialisation.

## P48 Encaps Full-ToBytes-to-SHAKE promotion — 2026-09-16

Encaps now calls `hash_g_fr0`, which places the exact P46 canonical Full
serialization directly after SHAKE256's `0x01` domain byte. This removes the
complete 1296-byte `ct -> data+1` copy while preserving the exact 1297-byte
transcript and 216-byte output.

The Python oracle passed 1,000 arbitrary signed-int16 inputs; the Pi 5 native
differential passed 1,024 arbitrary inputs plus input/output canaries. KAT,
malformed ciphertext and 64 KEM cases pass for both packages. Across 252 paired
Pi 5 observations, Encaps improves 44996.375 -> 44877.825 cycles (paired
-121.225), with -175 retired instructions and -24 branches. Keygen and Decaps
have zero instruction/branch deltas and remain controls. P46 assembly is reused
unchanged, so no new Slothy allocation or schedule is involved. Evidence is in
`experiments/gt864-p48-encaps-shake/`.

## P47 Decaps Full-ToBytes-to-compare promotion — 2026-09-16

The final Decaps re-encryption path now consumes P46's canonical 12-byte
records directly in a constant-time comparison with `buf1`; it does not write
or reread a 1296-byte candidate buffer.  Generic P46 remains unchanged for
Keygen and Encaps.  The earlier `hash_g` output keeps a 216-byte `buf2`, reducing
the compiled Decaps frame from 11088 to 10016 bytes.

Python and native tests cover arbitrary signed-int16 inputs, exact equality and
every one of the 1296 expected-byte positions independently corrupted.  KAT,
malformed transcript, 64 KEM round trips/tampered rejection, no-spill object
audit and 18/18 optimal Slothy windows pass.  Across 252 paired Pi 5
observations, Decaps changes 39907.300 to 39763.225 cycles, with -19 retired
instructions and -97.5 branches.  Complete evidence is in
`experiments/gt864-p47-decaps-compare/`.

## P46 Full normalization promotion — 2026-09-16

Only Full ToBytes changes.  Each post-Algorithm-10 residual correction changes
from `SSHR+AND+ADD` to the exhaustive signed-int16 identity `USHR #15; MLA q`;
Small remains exact P24.  The promoted source is the exact scheduled assembly
used by the Pi 5 candidate package, renamed only to the existing public symbol.

Exhaustive arithmetic, exact wire bytes, 18/18 no-spill Slothy windows, object
audit, KAT and malformed-ciphertext gates pass.  Full changes 1395.125 to
1386.762 cycles and retires exactly 108 fewer instructions/call.  Across 252
observations, Keygen/Encaps/Decaps improve by 13.500/13.650/5.450 paired-median
cycles.  The A76 Slothy proxy regresses 1495 to 1562 modeled cycles; the user
explicitly approved promotion on the broader target-silicon evidence without
altering that recorded result.  Complete evidence is in
`experiments/gt864-p46-full-normalization/`.

## P27 consumer-oriented I16 lane-basis gate — 2026-09-14

P27 changes no production source.  Its checker exhausts all 15 perfect
matchings of the six current main P8 records and selects one unique minimum-
arity basis.  The selected three paired regions overwrite only their consumed
P8 blocks; dense tail output occupies twelve Q records.  All 864 tagged
coordinates form a bijection over 108 dense source Q records and 108 natural
output Q records.  The generated consumer plan loads each source once, has a
four-Q live maximum and uses consecutive `v0-v3` TBL sources.

Machine checks retain the exact inverse roots, table scale, R0 output and the
closed 2497/2617/21397/4577 range chain.  No extra coefficient pass, larger
scratch, lane ST3, terminal UMOV/STRH or P11 D-record route is introduced.
The 32-vector/eight-GPR budget and conservative -1314-instruction ledger are
not physical allocation or timing claims.  P28 must still pass Slothy/no-spill,
complete Inverse/KEM correctness, ABI/cleanup and paired Pi 5 gates.  Complete
route masks and source identities are recorded in
`experiments/gt864-p27-consumer-i16-lane-basis/audit-results.json`.

## P26 matched Inverse deficit audit — 2026-09-14

P26 changes no production source.  Exact source-loop and helper-call expansion
reconciles selected Official Inverse+Crepmod3 at 4583 source plus 22 profiler
instructions and GT fused Inverse-to-ternary at 8324 source plus 21 profiler
instructions.  This exactly reproduces P25's 4605/8345 counts and +3740 gap.

GT has 151 fewer combined `mul/sqrdmulh/mls` instructions, so reduction is not
the deficit.  The dominant deltas are +864 lane extracts, +788 loads, +1159
stores and +438 scalar setup/address/control.  Exact source hashes, per-stage
and per-mnemonic counts, load provenance and historical P11/P21/P22 exclusions
are recorded in `experiments/gt864-p26-inverse-deficit-audit/`.

## P25 selected-Official profiler checkpoint — 2026-09-13

Exact P24 production revision
`d76a8289a8652e156665aff78bee6946183b2923`, extracted by `git archive`, passed
a fresh manifest build, KEM test, KAT, six-process exact/tampered
cross-implementation comparison and all instrumentation-equivalence gates.
The Pi 5 remained unthrottled from 57.6 to 60.4 C.

Across 252 clean observations, GT versus selected SUPERCOP 20260831 Official
was 43137.875 versus 44305.625 Keygen cycles, 44982.175 versus 46422.625
Encaps cycles, and 40067.250 versus 40761.775 Decaps cycles.  The Official tree
SHA-256 remains
`40a284439eb5fe8dfef77f1a995ebc8dd16182835048d64e959fbcb6e3df0b59`;
its independent upstream-latest status is unverified.

The largest remaining positive matched boundary is GT fused
Inverse-to-ternary versus Official Inverse+Crepmod3 at +280.675 cycles and
+3740 instructions.  Aggregate ToBytes is +47.000/+174.350/+178.000 cycles in
Keygen/Encaps/Decaps.  Complete distributions, event data and linked-object
provenance are in `experiments/gt864-p25-official-profile/`.

## P24 ToBytes production promotion — 2026-09-13

Production now links the exact P23 globally interned, three-output scheduled
Full and Small ToBytes artifacts under the unchanged P18 public symbol names.
The committed comparison used `git archive`: P18 baseline
`32481d08aae9135803379499c68c12b20a3856d4` and P24 candidate
`4b7a3b83085045694f8861cea61660d3345816ac`.  It therefore does not depend on
the benchmark-time working tree or an older target file.

Manifest, active-symbol/object, 513 Full + 513 Small exact-byte, guarded edge,
input immutability, output canary, AAPCS/SIMD cleanup, KEM, KAT and malformed
rejection gates pass on Pi 5.  Both target objects have zero Q-register stack
access.  Full/Small improve 1409.773→1393.867 and 1024.633→984.973 cycles,
with exactly 194 fewer instructions and six fewer reads per call.  Across 252
observations, complete Keygen/Encaps/Decaps improve by paired medians
147.000/67.325/62.625 cycles and 582/388/388 instructions.  The Pi remained
unthrottled.  Complete evidence is in
`experiments/gt864-p24-p23-production/`.

## P19 production promotion — 2026-09-12

Full and Small ToBytes link the exact P18 partial-transpose assembly artifacts,
SHA-256 `634fe9ee2e982405e86d87980703080dae0c51821d7b79e16905676eb128d83e`
and `f32af0ec4e173481018856d62a24999fb59818f4d2d1b26a9b4fa541443c1254`.
The C adapter calls the complete P18 public functions directly; legacy P9
wrapper objects are not linked.  Final production-package validation and Pi 5
results are recorded in `experiments/gt864-p19-p18-production/`.

The memory contract remains disjoint input/output.  Promotion checks exact
1,296-byte output extent, immutable input, canaries, `d8-d15` preservation and
SIMD cleanup; it does not claim unsupported in-place aliasing.

The production package manifest, linked-symbol audit, 513-case Full and Small
oracles, guarded edges, 64-case KEM test, KAT and malformed transcript pass on
Pi 5.  Against pre-P19 revision `34d62285`, Full/Small improve by
31.321/144.039 cycles.  Across 252 paired observations per operation,
Keygen/Encaps/Decaps improve by 331.875/209.425/194.550 cycles and retire
1,419/940/940 fewer instructions.  The Pi remained unthrottled.  Complete raw
results are in `experiments/gt864-p19-p18-production/pi-results.json`.

## P16 production promotion — 2026-09-12

Only Full ToBytes changes: production links the exact P15 scheduled assembly;
Small remains the byte-identical P9 object.  Full and Small retain 1378/1277
instructions per top and have no coefficient-Q stack access.  Two package KEM
tests, exact KAT, malformed transcript and six-process exact/tampered KEM
compatibility pass.  On Pi 5, 252 paired observations per operation improve
Keygen/Encaps/Decaps by 74.875/77.775/71.050 cycles with zero instruction or
branch delta.  See `experiments/gt864-p16-full-tobytes-integration/`.

## P13-C production promotion — 2026-09-12

The single tail Inverse16 call now uses its six-useful-lane composite terminal
map.  Its actual lane ABI is top0's three degree-3 components, top1's three
components, then two zero padding lanes; it therefore uses `EXT #6`, not the
main kernel's `EXT #8`.  All 96 natural store addresses, public wrapper and
scratch behavior are unchanged.  Tail-specific closure gives `|raw| <= 4303`,
below P8's existing 4577 limit.

Slothy reports OPTIMAL/no-spill allocation and 167→150 same-mode expected A76
cycles.  Pi 5 passed identical KAT and malformed transcripts, 4,096
exact/alias/AAPCS/wipe cases, and full-KEM checks.  Paired medians improve
Inverse-to-ternary by 71.586 cycles and Decaps by 73.075 cycles, with exactly
66 fewer instructions and no branch change.  See
`experiments/gt864-p13c-inverse-tail-arithmetic/`.

## P13-B production promotion — 2026-09-12

The six main Inverse16 calls now use a fused terminal-scale/top-CRT DAG.  Two
composite Algorithm-10 products replace the previous scale plus two CRT
products per column; selective `b=1` resets retain the existing P8 raw-output
contract (`|x| <= 4454`, contract limit 4577).  The tail, natural scatter,
scratch boundary and public wrapper are unchanged.

Exact algebra/range proof covers all 144 row/column contexts and all 8,909 P8
consumer inputs.  The symbolic oracle passes 544 main/tail cases.  Slothy gives
an optimal no-spill allocation and improves the bounded A76 estimate 184→166
cycles.  Pi 5 passes KAT, malformed rejection, 4,096 exact/alias/AAPCS/wipe
cases and full-KEM checks.  Paired medians improve Inverse-to-ternary by
428.938 cycles and Decaps by 434.350 cycles, with exactly 396 fewer retired
instructions; Keygen and Encaps instruction counts are unchanged.  Full
evidence is in `experiments/gt864-p13b-inverse16-arithmetic/`.

## P10-A production promotion — 2026-09-12

The approved P10-A direct-FR0 BaseInv is production.  Machine proof closes the
K1 input bound 28765, direct numerator, R^-2 determinant, twelve-step prefix,
one global inverse correction, R2 recovery, raw R0 output bound 2550 and the
complete D1 consumer to `[-1861,1861]`.  Three local Cortex-A76 Slothy regions
are final OPTIMAL with zero spill.

The actual production source passed manifest/build, 64 KEM round trips and
tampered rejection, identical 100-case KAT, identical 417216-byte malformed
transcript, and 808 BaseInv cases including all 288 zero leaves, exact alias,
canaries, AAPCS and 1200-byte scratch wipe.  Six balanced Pi 5 runs measured
BaseInv success 5197.422 to 4139.985 cycles and complete Keygen 45795.250 to
43670.500 versus P9.  Selected Official versus production was 8366.875 versus
8188.250 cycles for Keygen's two BaseInv calls and 44309.125 versus 43651.625
for complete Keygen.  See `experiments/gt864-p10-baseinv/RESULTS.md`.

## P8 promotion — 2026-09-12

Decaps now uses `poly_invntt_ternary`; original centered API remains.
Raw abs4577 proof, 9155-value native exhaustive consumer test,1024 exact full
inverse+conversion/alias/AAPCS/wipe cases, Mac/Pi KAT and Pi malformed transcript
all pass. Six paired Pi5 runs: Decaps42085.125→41333.675 cycles, -664 instructions;
Inverse+conversion6182.235→5417.047 (baseline adapter overhead documented).
No fresh Official comparison. Details: experiments/gt864-p8-raw-ternary/RESULTS.md.

## P7-C1 promotion — 2026-09-12

Only `inverse9.S` changes. Six one-product B3 nodes, no-spill
local Slothy allocation/timing, and unchanged terminal tables/store ABI.
Physical 288-map/range checks, 100-case Mac/Linux KAT (digest below), 64 KEM
round trips/tamper rejection, 256 native inverse inputs plus 256 BaseMul chains,
alias/canaries/AAPCS/1792-byte wipe, and 808 BaseInv regression cases pass.
Mac testing uses a test-only alias for the pre-existing `binv_num_pair` Mach-O
symbol omission; Linux benchmark source has no such shim.

Six balanced paired Pi 5 runs: Inverse 6995.484→5728.891 cycles; Decaps
43386.675→42104.900. Both retire exactly 1200 fewer instructions; branches
unchanged. See `experiments/gt864-native-asm/inverse-p7c1-one-product/RESULTS.md`
for frozen identities, raw samples and limitations. Official was not remeasured.

## Current promotion gate — 2026-09-10

The production-linked 84/37 BaseInv and pair+merge ToBytes promotion passed:

- local Apple arm64: 47 exact Makefile-selected objects, 64 KEM
  round-trips/tampered rejections and 100 KAT cases;
- Pi 5 Linux/GCC 14.2: manifest, assembly/link, the same KEM/KAT gate, and 808
  BaseInv success/failure/alias/canary/AAPCS/scratch-wipe cases;
- malformed transcript: 417216 bytes, SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`;
- KAT `.rsp`: SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.

Six-process AB/BA paired PMU on Pi 5, core 3, ondemand governor, 62 C:

| Operation | SUPERCOP 20260831 Official | GT production | Delta |
|---|---:|---:|---:|
| Keygen | 44330.875 | 47226.875 | +6.53% |
| Encaps | 46413.375 | 46007.625 | -0.87% |
| Decaps | 40772.875 | 44191.300 | +8.38% |

The comparison source is
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`; independent latest
upstream provenance remains unverified.  Raw evidence is retained under
`experiments/gt864-native-asm/baseinv-tobytes-next-model/production-promotion-results/`.

The remainder of this document records historical K1 integration evidence.

Historical K1 evidence below. Latest sequential native integration and unchanged
ToBytes validation: [NATIVE-INTEGRATION.md](NATIVE-INTEGRATION.md). Linux testing
now passes. The 2026-09-08 checked-decoder gate closes the previously observed
Official noncanonical-input rejection gap: 10368 boundary differential cases
and all 79 x+q counterexamples pass. See experiments/gt864-native-asm/
CHECKED-PROFILE-RESULTS.md in the parent repository for fresh PMU and profiler.
Do not reuse historical numbers below as current performance.
The 2026-09-09 gate additionally aligns Keygen-owned secret cleanup; all above
correctness gates pass again. CLEANUP-BASEINV-RESULTS.md supersedes the earlier
checked-decoder report's missing-Keygen-cleanup limitation and performance baseline.

Host: pi@100.99.191.9, Linux AArch64, GCC Debian 14.2.0-19.
Remote directory: /home/pi/ntruplus-experiments/gt864-production-k1-validation/NTRU+864.
Reference: /home/pi/ntruplus-experiments/gt864-p3b41-k1/raw.so.

## P20 selected-Official profiler checkpoint — 2026-09-12

Production revision `126fb028fe9dfe640f37a391e9acb967896be234` passed a
fresh build, KEM test, 100-case KAT, six cross-implementation processes with
100 exact and 100 tampered cases each, and twelve instrumentation-equivalence
processes. The KAT digest remains
`0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
The Pi 5 remained unthrottled from 58.7 to 63.1 C.

Across 252 clean observations per operation, GT versus selected Official was
43276.875 versus 44321.750 Keygen cycles, 45084.175 versus 46435.125 Encaps
cycles, and 40134.675 versus 40764.700 Decaps cycles. The comparison target is
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`, tree SHA-256
`40a284439eb5fe8dfef77f1a995ebc8dd16182835048d64e959fbcb6e3df0b59`;
its independent latest-upstream status remains unverified. Full profiler
evidence is in `experiments/gt864-p20-official-profile/`.

## P21 Inverse-to-ternary decomposition — 2026-09-12

The P20-byte-identical production library passed a fresh manifest check, 64 KEM
round trips/tampered rejections and the unchanged 100-case KAT before timing.
Six balanced Pi 5 processes produced 258 observations per boundary on CPU 3;
the host remained unthrottled from 57.1 to 62.0 C.

Net medians were 1682.047 cycles for inverse9 ×12, 2117.531 for main I16 ×6,
341.313 for tail I16, 430.164 for raw-to-ternary and 4893.227 for complete
Inverse-to-ternary. Diagnostic no-store copies removed exactly the existing
terminal lane scatters without touching production and established only an
optimistic 175.016-cycle aggregate ceiling. Full evidence and interpretation
are in `experiments/gt864-p21-inverse-decomposition/`.

## P22 main-I16 two-output SSA experiment — 2026-09-12

P22 changes only the six-call P13-B main-I16 interior.  It replaces 32
held-value `ORR` copies per call with explicit two-output SSA butterflies,
reducing 667 to 635 region instructions while preserving all roots, scales,
ranges, table loads and exact halfword stores.  A 544-case exact symbolic
oracle, no-spill Cortex-A76 Slothy allocation, 4096-case native exact/alias/
AAPCS/wipe test, KEM test, unchanged 100-case KAT and malformed transcript pass.

The scheduled candidate improves the isolated six-call boundary from 2129.531
to 2092.344 cycles with exactly 192 fewer instructions.  It nevertheless
regresses complete Inverse-to-ternary by a 5.610-cycle paired median and Decaps
by 21.775 cycles.  The RA-only control regresses those boundaries by 186.407
and 199.300 cycles.  The full-path gate therefore rejects P22; no production
kernel or linked object was changed.  Complete evidence is in
`experiments/gt864-p22-main-i16-ssa/`.

## P23 global ToBytes routing candidate — 2026-09-13

P23 leaves production unchanged and compares against the exact linked P18
Full/Small serializers.  Structural interning plus a constructive 26-register
cache reduces each complete call by 194 instructions and six coefficient Q
loads, with no coefficient scratch and no vector stack accesses.  The exact
coordinate-map SHA-256 remains
`087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270`.

Python passed 516 exact lane/byte cases.  Apple arm64 passed 513 Full, 513
Small and two guard-page cases before and after Slothy.  Pi 5 packages passed
KEM, exact boundary canaries, KAT SHA-256
`0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`
and malformed transcript SHA-256
`2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.

The accepted three-output fixed-allocation Slothy schedule improves P18
Full/Small boundaries by 16.375/46.586 cycles.  Frozen full-KEM integration
improves Keygen/Encaps/Decaps by 131.375/81.125/64.500 paired-median cycles and
exactly 582/388/388 retired instructions.  The Pi remained unthrottled.  A
one-output-window control is explicitly rejected because it regressed despite
the same smaller instruction multiset.  P24 subsequently copied these exact
artifacts into production and repeated all production-package gates.  Evidence:
`experiments/gt864-p23-tobytes-global-dag/RESULTS.md`.

## Correctness and selection

- `make -j4 check`: imported manifest passed, assembler/linker passed,
  64 valid KEM round trips and tampered ciphertext tests passed, KAT generated.
- `test/paired.c`: 32 deterministic valid/tampered cases, byte-identical
  pk/sk/ct and shared secrets; 32 malformed ciphertext cases returned equal
  status and output against original K1. Repeated in all six PMU processes.
  The inherited instrumentation-equivalence label is not a profiler test here:
  both handles deliberately point to the uninstrumented implementation.
- KAT generator linked separately against original K1: entire .rsp matched.
  SHA256 PQCkemKAT_2624.rsp:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Full object byte comparisons passed for ntt9.o,
  ntt.o, ntt_api.o, base.o,
  inverse9.o, unpack.o.
  This compares complete objects, including function sections, not empty .text.
- kem-normal.o relocations select poly_ntt at all KEM Forward calls,
  production BaseMul/Inverse/BaseInv and production byte adapters.
- Library SHA256:
  `b295d006eee1f6e496dcdaea7a31bf659e3ca13ce9cf559c814eeae036b3f302`.

## Paired PMU integration check

Core 3; six processes, alternating order, 41 samples/process; 4 Keygen or
20 Encaps/Decaps calls per sample. Numbers below are median of six process
medians. Raw cycles/instructions/branches are in evidence/paired0..5.log.

| Operation | Original K1 cycles | Package cycles |
|---|---:|---:|
| Keygen | 54274.250 | 54154.000 |
| Encaps | 46085.150 | 46095.425 |
| Decaps | 44430.875 | 44424.675 |

No new speedup is claimed. Small sub-percent variation, especially the
order-dependent Keygen split, does not establish an arithmetic improvement.
Encaps differs by +0.022%; Decaps by -0.014%. The identical core objects and
these results support integration parity, not a new optimization result.

This comparison is against original K1, NOT a fresh Official comparison.
The existing Official reference remains SUPERCOP 20260627 SHAKE256 and has
not been verified to be upstream's latest version.

## Scope and limitations

KEM-only producer/consumer range evidence is inherited from P3B40 and the
tested P3B41 K1 lowering; it is archived, not independently re-solved here.
The imported source hash manifest binds the unchanged implementation.
The wrapper object is unchanged (including d8–d15 preservation); a new
standalone ABI-sentinel test was not run. No generic polynomial multiply gate.
Linux/GCC is the validated build; Darwin and CE hash builds are not claimed.
Internal compatibility/helper symbols are retained for faithful integration;
only crypto_kem_* is a supported public API. Name/dead-helper cleanup remains
a separate mechanical gate, not part of this arithmetic promotion.
## P1 BaseInv addition-chain promotion — 2026-09-10

The production `binv_inverse3` uses 21 widening Montgomery multiplications and
157 instructions, versus P0's 28 and 208.  Local Cortex-A76 Slothy scheduling
completed with no spill and an expected 283 cycles.

Mac and Pi 5 passed the 100-case KAT, 64 KEM round trips, tampered rejection,
and the linked 808-case BaseInv test including every zero-leaf position, exact
aliasing, canaries, AAPCS preservation, and scratch wipe.  The Pi 5 malformed
transcript remained exactly 417,216 bytes with SHA-256
`2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
Six paired Pi 5 repetitions measured BaseInv success at 5469.860 cycles versus
5561.656 and Keygen at 46995.250 versus 47172.250.

## P3-A complete inverse centering — 2026-09-10

The production Inverse now calls one constant-resident `center864` kernel in
place of 27 `center32` calls.  The closed input bound remains `abs <= 6912` and
the exact output remains natural-order centered R0 with `abs <= 1728`.
Exhaustive scalar coverage of the producer range, 4,096 random vectors and
memory canaries passed locally.  On Pi 5, both isolated P2/P3-A packages passed
manifest validation, `test_kem`, 100-case KAT, 256 exact Inverse comparisons,
256 exact-alias comparisons, and six repetitions of valid/tampered KEM tests.
Paired PMU measured -235 instructions, -52 branches, and -212.859 cycles per
Inverse; complete Decaps inherited the same exact static-event reduction and
-212.275 cycles.

## Cleanup policy

This package follows the same Official-aligned policy NTRU+768 adopted, rather
than the former P0-B full-frame policy.

- Secret **data** with a lifetime is still cleared in C: keys, inverses, coins,
  messages, hash buffers and the polynomials derived from them, through
  `secure_clear`, which is a plain clear plus a compiler barrier on every
  non-Windows platform.
- Assembly **working frames are not wiped.** The leaves take their scratch from
  the caller rather than allocating it, so nothing they touch is unreachable
  from C, but the buffer itself is not erased.  The one exception costs
  nothing: decapsulation's inverse takes its scratch from `kem.c`'s `io` union,
  which overlays `buf1` and `buf3` (first written after the inverse) and is
  cleared with them on exit.
- **Volatile SIMD registers are still erased** at the inverse boundary. That is
  a deliberate exception: it costs one cycle, and unlike a stack frame, register
  state is not overwritten by whatever runs next.

The frame wipes were measured before being retired. At the wipe's own boundary
the scratch does survive the call -- probing the stack immediately after
`poly_invntt_ternary` finds the full 1,152-halfword scratch intact without it,
and 31 halfwords with it. But by the time decapsulation returns, the transform,
basemul, two hashes and the serializer that follow have overwritten the same
region either way: 64 halfwords of recognisable residue, with the wipe and
without. The window in which the wipe changes anything is the few thousand
cycles between the inverse returning and the next write to that stack.

Removing them costs nothing in coverage that survives the call and returns
about 540 cycles on NTRU+864 and 320 on NTRU+1152 decapsulation.

There is no promise to erase handwritten spill frames. This is not a proof
about compiler copies, caches, swap, or microarchitectural remanence.
