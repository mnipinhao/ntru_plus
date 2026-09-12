# NTRU+864 GT optimization roadmap

This is the persistent work ledger for the production NTRU+864 GT path. Update
it after every optimization gate. A task may be removed only with a recorded
reason; failed experiments move to `Dropped`, rather than disappearing.

Comparison baseline: `/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`.
That captured source is the selected Official baseline; its independent status
as the latest upstream revision is not yet verified.

Status meanings:

- `Active`: current gate.
- `Next`: ordered work after the active gate.
- `Deferred`: retained, but not on the immediate critical path.
- `Done`: promoted and passed all required gates.
- `Dropped`: rejected, with evidence and a reopen condition.

## Ordered work

| ID | Status | Work | Completion gate |
|---|---|---|---|
| P0 | Done | Promote BaseInv 84-instruction fused-wide numerator and 37-instruction no-centering finish; promote scheduled ToBytes pair+merge | Passed exact linked-object sizes, Mac/Linux assembly, 100-case KAT, 808-case BaseInv failure/alias/wipe, malformed transcript and Pi 5 paired PMU |
| P1 | Done | Replace BaseInv bitwise exponentiation with a scale-correct shortest addition chain for exponent 3455 | Promoted 157-instruction, 21-MM zero-spill core; exact scale/range, KAT, failure/alias/wipe and Pi 5 BaseInv/Keygen gates passed |
| P2 | Done | BaseInv two-tile kernel with q/qinv/R constants resident and 18 numerator calls; SIMD chain-end failure aggregation | Promoted combined candidate: exact output/cleanup, constant-time scan, zero spill, KAT and Pi 5 BaseInv/Keygen gates passed |
| P3 | Done | Stage-fused Decaps inverse; retain promoted P3-A constant-resident `center864` | P3-A passed; P3-B producer-side centering was correct but failed Pi 5 performance and is recorded below |
| P3-B | Dropped | Pair half-filled I16 terminal vectors, center in producer registers, then use the existing scatter addresses | Correct and spill-free, but Inverse regressed 634.266 cycles (+9.05%) and Decaps 643.425 cycles (+1.46%); reopen only with a naturally full-vector terminal ABI |
| P4 | Done | Fuse FromBytes legality accumulation into decode/routing | Promoted after removing the second 1,728-byte scan, exact four-input rejection proof, no vector spill, unchanged KAT and Pi 5 full-KEM improvement |
| P5 | Done | Reuse KEM temporaries following proven lifetimes | Promoted one-`h` Keygen, `ct`-backed Encaps serialized `r`, and four-poly Decaps after stack/object, cleanup, KAT, rejection, malformed-transcript and Pi 5 gates |
| P6-A | Dropped | Retain both saved pairs in registers but keep the current third-pair row-copy plus TBL repair | Exact 33-vector frontier is Slothy-infeasible; both one-fewer-vector and no-index controls allocate, so storage-only rewriting is rejected |
| P6-B | Done | Compress pair-2 A to an exact seven-Q 12-bit state before constructing pair-2 B | All nine production route maps and 4,100 pack cases passed; 31-vector route and exact 32-vector full-normalization frontiers allocate without spill |
| P6 | Dropped | Consumer-oriented zero-scratch ToBytes route + normalization + packing | Correct architecture reached P6-D3, but exact Pi 5 boundaries regressed full by 28.40% and small by 66.37%; reopen only after removing the measured route/table instruction and read deficit |
| P6-C | Done | Joint packed-A producer + restore-A/B pack + three-pair merge symbolic DAG | Exact model and physical assembly oracle passed; peaks are 26/32; both Slothy allocations are optimal without spill; all physical TBL2/TBL3 groups are consecutive |
| P6-D | Done | Complete all-nine-row full/small zero-scratch ToBytes kernels | 12 Slothy regions optimal/no-spill; exact 1,296 bytes; 108 coefficient Q loads; zero coefficient scratch; 80 Q + 2 D stores; complete full/small oracle passed |
| P6-E | Done—Rejected | Same-boundary Pi 5 timing of P6-D3 versus frozen 432-byte-scratch ToBytes | 74 paired samples/mode: full 1766.734→2268.457 cycles; small 1363.399→2268.223; production unchanged |
| P6-F | Done | Fresh selected-Official full-KEM and call-site profiler checkpoint | 252 clean observations per operation/implementation, 6× exact/tampered compatibility and 12 instrumentation-equivalence gates passed; Inverse, BaseInv and aggregate ToBytes gaps isolated |
| P7 | Done—Local benefit only | Inverse CT feasibility | GT NTT16 is genuine CT DIT; 10,000-vector ordering proof, complete coordinate/scale/range/memory ledger and source audit pass. CT absorbs bit reversal and avoids a GS range cut, but no new CT/GS DAG attacks the measured +2,895.9-cycle whole-Inverse gap; production unchanged |
| P7-B0 | Done | Same-boundary Inverse core decomposition | Pi 5 PMU isolated inverse9 as the largest stage (2,958.406 cycles, IPC 1.292); main+tail scatter ideal-removal ceiling was only 164.890 cycles, so B1 selected inverse9 constant liveness rather than a new scatter ABI |
| P7-B1 | Done—Promoted | Keep the repeated `(722,6844)` Barrett-Shoup pair in `v0/v5`, then reschedule the fixed allocation | Removed 20 instructions/call and 80 object bytes; exact/KAT/alias/no-spill gates passed. Raw order regressed, but Slothy timing recovered it; final paired Pi 5 delta was -18.782 Inverse cycles and -17.875 Decaps cycles with exactly -240 instructions |
| P7-C0 | Done—Algebra/range pass | Re-close current physical Inverse arithmetic and one-product B3 alternatives | 266 constant pairs exhausted; current bounds tighten to I9 2311 / I16 19545 / raw 4485. One-product B3 gives 37→19 mulmods per I9 and -576 arithmetic instructions/Inverse, with safe 2617 / 21397 / 4577 bounds. Last I16 identity reset has a 33792 overflow witness and stays |
| P7-C1 | Done—Promoted | One-product inverse NTT9, preserving terminal tables and P8 stores | No-spill RA + local timing, exact range/centered-output/alias/wipe/KAT pass. Pi 5 Inverse 6995.484→5728.891; Decaps 43386.675→42104.900 cycles; -1200 instructions in both |
| P8 | Done—Promoted | Raw-Inverse-to-ternary Decaps consumer | Exact9155-value proof, native alias/AAPCS/wipe/KAT/malformed pass. One pass instead of center864+crepmod3; Pi5 Decaps42085.125→41333.675 cycles (-664 instructions). Old centered Inverse API retained |
| P9 | Done—Promoted | Input-once ToBytes full/small composed-map routing | Both modes passed static deficit, no-spill, exact-byte, KAT, malformed and Pi 5 gates; combined full-KEM saves 619.875/415.800/435.925 Keygen/Encaps/Decaps cycles |
| P10-A | Done—Promoted | Direct-FR0 BaseInv numerator/finish with one global inverse-scale correction | Approved 1972→2550 bound; all production gates pass. P9→P10 BaseInv success 5197.422→4139.985 and Keygen 45795.250→43670.500; selected Official two-call BaseInv 8366.875 vs P10 8188.250 |
| P10-B | Dropped—Unneeded | Contract-preserving normalized finish fallback | Reopen only if a future consumer cannot accept the approved 2550 bound; current K1→BaseInv→D1 chain is fully closed |
| P11 | Dropped | Joint terminal Inverse-to-ternary DAG after P7-C1/P8 | A0–A4 all correct/no-spill and removed up to 1,292 instructions, but every exact component candidate was slower. Best A2: +17.485 paired cycles, IQR [+15.961,+18.422]; production unchanged |
| P12 | Done—Profile/selection | Reconcile remaining instruction/branch gap after P11 | Fresh selected-Official clean/profile/event campaign reproduces +9439 instructions/+152.5 branches and localizes the meaningful deficits without changing production |
| P13-A | Done—Promoted | Widen exact Inverse tail initialization and 1792-byte scratch wipe from 16-byte scalar pairs to full-vector stores | Exact wipe/AAPCS/KAT/malformed gates pass; -291 instructions/-114 branches, paired -23.555 Inverse and -20.050 Decaps cycles |
| P13-B | Done—Promoted | Fuse terminal scale and top-CRT linear forms in the six-call `lazy_i16` interior | Exact algebra/range/oracle, zero-spill Slothy, native KAT/rejection/alias/AAPCS/wipe and paired Pi 5 gates passed; Decaps improves by 434.350 paired-median cycles with exactly 396 fewer instructions |
| P13-C | Done—Promoted | Tail-specific composite terminal map for the separately shaped six-useful-lane I16 kernel | Exact row-8 range/oracle, zero-spill Slothy, native KAT/rejection/alias/AAPCS/wipe and paired Pi 5 gates passed; Decaps improves 73.075 paired-median cycles with exactly 66 fewer instructions |
| P14 | Done—Rejected | Replace P9 lane-edge routing with 15 retained-source TBL4 neighborhood classes | Exact/no-spill assembly removes 1120 full+small instructions, but Pi 5 regresses full/small by 198.993/104.583 cycles; production remains P9 |
| P15 | Done—Combined rejected, full retained | Preserve P9 input-once lane routing and jointly schedule output completion, normalization and pack | Exact fixed-allocation schedule improves full by 76.555 cycles but small regresses 1.586; strict two-mode gate fails and production remains P9 |
| P16 | Done—Promoted | Replace only full ToBytes with the retained P15 schedule; keep P9 small unchanged | KEM/KAT/malformed/object gates pass; paired Keygen/Encaps/Decaps improve 74.875/77.775/71.050 cycles with zero instruction or branch growth |
| P17 | Done—Profiler checkpoint | Re-measure production against the selected SUPERCOP 20260831 Official and refresh component/call-site attribution after P13/P16 | GT wins Keygen/Encaps/Decaps by 727.25/1148.45/434.55 cycles; remaining positive component gaps were ToBytes and inverse-to-ternary |
| P18 | Done—Promotion candidate | Replace per-coefficient lane routing with class-local pruned 8x8 transposes and immediate normalization/packing | Exact/no-spill/Slothy gates pass; Full/Small save 31.368/149.117 boundary cycles and isolated Keygen/Encaps/Decaps save 334.125/194.400/182.825 cycles |
| P19 | Done—Promoted | Link both exact P18 kernels and remove legacy P9 public wrappers from the active object set | Manifest, linked-symbol, exact bytes, disjoint-buffer canary/input immutability, AAPCS/cleanup, KAT/malformed and paired boundary/full-KEM gates pass |
| P20 | Done—Profiler checkpoint | Refresh GT versus selected SUPERCOP after P19 | Fresh correctness/clean/cycle/event campaign passes; GT wins all full-KEM operations and residual positive gaps are localized |
| P21 | Done—Inverse decomposition | Re-profile the current P13-B/P13-C/P8 Inverse-to-ternary interior | Fresh 258-observation stage PMU selects main I16 ×6 at 2117.531 cycles; no-store control remains 1960.406, so terminal scatter is rejected as the next target |
| P22 | Next—Main-I16 arithmetic | Reconstruct and reduce the fixed-ABI P13-B main-I16 arithmetic/dependency DAG | Delete arithmetic/reduction work or shorten the critical path; preserve exact range/layout/memory ABI, no spill, and beat the 2117.531-cycle six-call Pi 5 boundary |

## Fixed facts and non-tasks

- GT already uses three-chain hierarchical BaseInv batch inversion.
- GT already has the BaseMul R^-1 plus matching inverse scale ABI; current
  BaseMul R^-1 is essentially tied with Official.
- P9 ToBytes reads every FR0 Q vector once and writes final bytes without
  coefficient scratch. Small intentionally omits the 108 Barrett reductions
  only for producers proved in `(-q,q)`; full retains them.
- Secret/scratch clearing is a policy requirement and is not deleted merely to
  match Official timing.
- Forward is currently faster than the selected Official component and is not
  on this immediate critical path.
- P10-A makes GT BaseInv faster than selected Official at the exact two-call
  Keygen boundary.  The wider, fully consumer-closed raw representative bound
  is explicitly approved and production uses P10-A.

## Change log

### 2026-09-12

- Completed P21 without changing production.  The P20-byte-identical library
  passed a fresh manifest build, 64 valid/tampered KEM cases and the unchanged
  100-case KAT.  Across 258 Pi 5 observations per stage, current Inverse-to-
  ternary decomposes to inverse9 ×12 1682.047, main I16 ×6 2117.531, tail I16
  341.313, raw-to-ternary 430.164 and a diagnostic 322.172-cycle residual.
- Deleting every main/tail `UMOV+STRH` in diagnostic-only controls saves an
  optimistic 157.125+17.891 cycles, while no-store main I16 still costs
  1960.406 cycles at IPC 1.294.  P22 therefore targets the P13-B main-I16
  arithmetic/dependency DAG; a terminal-store-only rewrite is excluded.
  ToBytes remains second.  Evidence:
  `experiments/gt864-p21-inverse-decomposition/`.

- Completed P20 without changing production.  A fresh manifest-bound build of
  revision `126fb028fe9dfe640f37a391e9acb967896be234` beats the selected
  SUPERCOP 20260831 Official by 1044.875/1350.950/630.025 cycles for
  Keygen/Encaps/Decaps across 252 clean observations each.  Six exact/tampered
  cross-implementation processes, twelve instrumentation-equivalence processes,
  KEM and KAT pass; Pi 5 stayed unthrottled.
- P19 reduced the aggregate ToBytes positive gaps to 153.250/237.150/243.125
  cycles for Keygen/Encaps/Decaps.  The largest remaining matched positive gap
  is now Decaps Inverse-to-ternary at +284.200 cycles and +3740 instructions
  versus Official Inverse plus Crepmod3.  P21 therefore re-decomposes the
  current optimized inverse interior before selecting another DAG; ToBytes is
  retained second.  Evidence: `experiments/gt864-p20-official-profile/`.

- Completed P17: the refreshed selected-SUPERCOP comparison shows production
  GT ahead by 727.25/1148.45/434.55 cycles for Keygen/Encaps/Decaps.  P18 then
  replaced P9 lane-edge routing with fifteen class-local partial transposes.
  It preserves exact bytes and the no-scratch ABI, schedules without spill,
  and wins both Full/Small boundaries by 31.368/149.117 cycles.  The isolated
  full-KEM candidate wins all three operations, so P19 promotes both kernels
  and repeats production-package validation.  Evidence:
  `experiments/gt864-p17-official-profile/` and
  `experiments/gt864-p18-partial-transpose-tobytes/`.

- Completed and promoted P19.  Production links the exact P18 Full/Small
  artifacts and the C adapter calls them directly; legacy P9 public wrappers
  are absent from the linked library.  Manifest, exact byte, KAT, malformed,
  disjoint-buffer canary/input-immutability, AAPCS and SIMD-cleanup gates pass.
  Compared with pre-P19 production, Full/Small improve 31.321/144.039 cycles;
  Keygen/Encaps/Decaps improve 331.875/209.425/194.550 cycles with exactly
  1419/940/940 fewer instructions.  P20 is the next selected-Official profiler
  checkpoint.  Evidence: `experiments/gt864-p19-p18-production/`.

- Completed and promoted P16.  Production now links the exact retained P15
  schedule for Full ToBytes while Small remains the byte-identical P9 object.
  Full/Small retain 1378/1277 instructions per top, no coefficient-Q stack
  access, the same memory/range/ABI contracts, exact KAT and malformed
  transcript.  Across 252 paired Pi 5 observations per operation,
  Keygen/Encaps/Decaps improve by 74.875/77.775/71.050 cycles with exactly zero
  instruction and branch delta.  P17 refreshes the selected-Official profiler
  after the cumulative P13 and P16 promotions before choosing another DAG.
  Evidence: `experiments/gt864-p16-full-tobytes-integration/`.

- Completed P15 without combined production promotion.  Slothy timing-only
  scheduling preserves the exact P9 instruction multiset, fixed allocation,
  memory boundary and coefficient no-spill contract across 9 full and 8 small
  bounded windows.  Both target packages pass KEM/KAT and 513 edge/random
  differential cases per mode.  On Pi 5, full improves
  1518.188→1441.633 cycles with identical retired instructions, branches and
  reads, but small regresses 1174.282→1175.868 cycles.  The predeclared
  both-mode gate therefore rejects P15 and skips full-KEM integration.
  Because the modes are separate call boundaries, P16 retains the measured
  full schedule for an independent full-only KEM gate while leaving P9 small
  untouched.  Evidence: `experiments/gt864-p15-p9-scheduling/`.

- Completed P14 without production promotion.  The exact composed route has
  only 15 distinct eight-source neighborhoods.  A maximum-overlap class path
  needs 64 source Q loads/top, and a fixed `v0-v7` implementation replaces
  eight lane moves per output with two `TBL4` plus `ORR`.  It passes exact
  full/small bytes and guard edges, has no top-body stack reference, and cuts
  complete-path instructions 2809→2260 full and 2607→2036 small.  Pi 5 rejects
  it decisively: paired medians regress 1507.220→1706.213 and
  1172.662→1277.245 cycles.  The extra lookup/table-load throughput dominates
  despite 555/573 fewer retired instructions.  Slothy and full-KEM integration
  are skipped after the predeclared same-boundary falsifier.  P15 retains P9's
  cheaper lane-move DAG and tests bounded joint scheduling only.  Evidence:
  `experiments/gt864-p14-class-tbl-tobytes/`.

- Completed and promoted P13-C.  The single tail `lazy_itail` call now uses
  its actual `[top0 components0..2 | top1 components0..2 | zero x2]` layout,
  tail-specific composite constants, `EXT #6`, and the unchanged 96 scatter
  addresses.  The exact final-row bound closes at 5028 before selective resets
  and 4303 afterward, below P8's unchanged 4577 contract.  Static instructions
  fall 669→603; same-mode Slothy timing is 167→150 with OPTIMAL no-spill RA.
  Native KAT, malformed rejection, 4096 exact/alias/AAPCS/wipe cases and all
  full-KEM checks pass.  Pi 5 paired medians improve Inverse-to-ternary by
  71.586 cycles (IQR [-72.469,-70.004]) and Decaps by 73.075 (IQR
  [-84.600,-66.350]), with exactly -66 instructions and unchanged branches.
  Keygen/Encaps instructions are unchanged.  P14 ToBytes is next; the rejected
  P6 storage-only direction remains closed.  Evidence:
  `experiments/gt864-p13c-inverse-tail-arithmetic/`.

- Completed and promoted P13-B.  The six main `lazy_i16` calls now fuse their
  terminal scale and two-row CRT map into two composite Algorithm-10 products
  per column, then horizontally combine the packed top halves.  Selective
  `b=1` resets at low columns 0/12 and high columns 0/2/8/10 close the raw
  output at 4454, below the unchanged P8 contract 4577; the tail kernel and
  every memory boundary remain unchanged.  The physical main body shrinks
  733→667 instructions; across six calls this is exactly -396 retired
  instructions.  Slothy allocation is optimal/no-spill and bounded timing
  improves 184→166 expected A76 cycles.  Native KAT, malformed rejection,
  4096 exact/alias/AAPCS/wipe cases and all full-KEM checks pass.  Pi 5 paired
  medians improve Inverse-to-ternary by 428.938 cycles and Decaps by 434.350;
  Keygen/Encaps instruction counts are unchanged.  P13-C now isolates the
  differently shaped tail I16 arithmetic before P14 ToBytes.  Evidence:
  `experiments/gt864-p13b-inverse16-arithmetic/`.

- Completed and promoted P13-A.  The P8 Inverse wrapper still clears exactly
  256 tail-padding bytes before arithmetic and wipes exactly 1792 scratch bytes
  afterward, but uses full-vector stores and a 128-byte wipe iteration.  The
  changed regions remove exactly 291 retired instructions and 114 branches.
  All manifest/build/KAT/malformed and 4096 exact/alias/AAPCS/wipe gates pass.
  Pi 5 paired medians improve Inverse-to-ternary by 23.555 cycles (IQR
  [-24.891,-23.172]) and Decaps by 20.050 (IQR [-31.537,-3.200]); Keygen and
  Encaps instructions are unchanged.  P13-B now targets the six-call
  `lazy_i16` arithmetic interior.  Evidence:
  `experiments/gt864-p13-inverse-interior/`.

- Completed P12 without changing production.  A fresh manifest-closed build of
  production revision `dd8c3146` and the selected SUPERCOP source reproduces
  Decaps 40761.450→40918.950 cycles (+157.500, +0.39%), +9439 instructions and
  +152.5 branches.  Per-call-site event profiling assigns +4493 instructions/
  +171 branches to GT Inverse-to-ternary versus Official Inverse+Crepmod3 and
  +2886/-24 to aggregate ToBytes.  Their cycle deficits are +815.675 and
  +485.000 respectively.  BaseMul R^-1 is cycle-tied despite +770/+73;
  Forward and FromBytes are faster despite positive instruction gaps, so those
  are not reopened.  P13 targets non-terminal Inverse arithmetic; P14 retains
  ToBytes second.  Evidence: `experiments/gt864-p12-decaps-profile/`.

- Completed and rejected P11. A0 replaced 1,728 terminal UMOV/STRH
  instructions with D records plus a joint ternary route, but regressed the
  exact component by 339.843 cycles. k-major A1, full-D-tail A2, joint-scheduled
  A3 and pure-unfold A4 progressively tested load shape, lane-store cost and
  loop overhead. A2 was the best exact component and still lost by a paired
  median 17.485 cycles, IQR [+15.961,+18.422], while removing 1,260
  instructions. A4 removed 1,292 instructions and 11 branches but also lost.
  All KAT, malformed, exact alias, AAPCS and scratch-wipe gates passed; this is
  a microarchitectural rejection, not a correctness failure. Production stays
  P10/P8. Reopen only with a naturally full-vector terminal producer or a DAG
  with substantially larger same-boundary margin. P12 is active. Evidence:
  `experiments/gt864-p11-inverse-ternary/`.

- Promoted P10-A after explicit user approval of the consumer-closed raw FR0
  output bound 1972→2550.  The actual production source passed manifest,
  100-case KAT, malformed transcript, complete KEM and 808-case BaseInv
  failure/alias/AAPCS/scratch gates on Pi 5.  Final P9→production measurements
  are BaseInv success 5197.422→4139.985 cycles and complete Keygen
  45795.250→43670.500.  Production beats selected Official by 178.625 cycles
  at the two-BaseInv boundary and by 657.500 cycles for complete Keygen.
  P10-B is dropped as unnecessary; P11 is active.

- Completed P10-A as a promotion candidate while leaving production frozen.
  Direct R0 cofactors remove each tile's input conversion and finish scale
  correction; determinant/prefix/recovery scales close as R^-2→R1→R^-1→R2,
  with one global Algorithm-10 R^-2 correction.  Three local Slothy regions are
  final OPTIMAL/no-spill: pair numerator 132 instructions/123 expected cycles,
  finish 26/31 and inverse3 164/293.  Machine proof closes the K1 producer cube
  `|x|<=28765`, every int16/int32 narrowing, raw output `|x|<=2550`, and the
  complete D1 consumer back to `[-1861,1861]`.
- The initial Pi component failure was traced to an inherited generic-int16
  harness sample outside P10's production-KEM contract, not hidden assembly
  divergence.  The corrected full-contract harness passes 808 cases, all 288
  zero leaves, alias/AAPCS/canaries/scratch wipe; KAT and malformed transcripts
  are byte-identical.  Pi 5 BaseInv success improves 5209.750→4129.875 cycles
  and complete Keygen 45804.125→43656.375 versus P9.  P10 also beats selected
  Official at the two-call BaseInv boundary by 161.125 cycles and complete
  Keygen by 648.750.  Explicit approval of the successful-output bound
  1972→2550 is required before promotion; otherwise run conditional P10-B.
- Added P11 as the next post-P10 target.  At consistent boundaries selected
  Official `Inverse + Crepmod3` is 4619.3 cycles and GT fused
  `Inverse_to_ternary` is 5432.35, so the remaining measured Decaps target is
  about 813 cycles.  P12 retains only a post-P11 re-profile of the residual
  instruction/branch gap.  Evidence: `experiments/gt864-p10-baseinv/`.

- Completed and promoted P9.  The old P3B6 peak-16 input-once route was
  reconsidered against the current P5 boundary rather than its obsolete
  1250-cycle threshold.  A separate small core removes every Barrett operation
  under the closed `(-q,q)` producer contract.  GCC target paths are 2809/2607
  instructions including two top calls and cleanup, versus P6-D3's 4061;
  neither has vector spill.  Full/small public PMU changes are -248.508/-196.656
  cycles, -422/-389 instructions and -424 read events each versus P5.
- The combined P9 candidate passed Mac and Pi exact bytes, guard edges, four
  complete KEM builds, unchanged 100-case KAT and malformed transcript, and six
  balanced full-KEM processes.  Keygen/Encaps/Decaps improve by
  619.875/415.800/435.925 cycles and exactly 1200/811/811 instructions versus
  P8.  P10 BaseInv is now next.  Evidence:
  `experiments/gt864-p9-tobytes-routing/`.
- Completed P8: new Decaps-only inverse_ternary entry consumes raw abs4577
  through compare +/-1728, correction +/-1 and rounded divide by3. q=1 mod3
  permits removing the centered-q materialization. Kernel has32 instructions
  per32 coefficients; no spill/new coefficient scratch. Preserve old centered
  API and all wipe policy. Full Decaps paired delta -745.275 cycles; malformed
  transcript and KAT unchanged. Evidence: experiments/gt864-p8-raw-ternary/.
  P9 is next; P10 remains queued. This shortcut must not use the historical
  abs6912 contract: it fails at5186. No new Official measurements.
- Completed and promoted P7-C1. Six one-product B3s reduce each I9 body
  284→184 instructions (including constant/move savings), object 1140→740 B.
  Local Slothy RA then bounded timing windows pass without spill; physical
  arithmetic matches all 288 P7-C0 terminal maps/ranges. Mac/Linux KATs agree,
  native alias/AAPCS/wipe tests pass. Six balanced Pi 5 runs give paired median
  deltas -1266.281 Inverse and -1284.675 Decaps cycles, exactly -1200
  instructions and unchanged branches. No meaningful Keygen/Encaps change.
  Evidence: `experiments/gt864-native-asm/inverse-p7c1-one-product/RESULTS.md`.
  P8 is next; P9 ToBytes and P10 BaseInv stay queued. No new Official timing
  was taken this round; the old Official checkpoint must not be mixed into a
  new same-run speedup claim.
- Completed P7-C0 in `experiments/gt864-native-asm/inverse-p7c0-range/`.
  Corrected the earlier assumption about the old proof: it already established
  `<q` by exhaustive fixed-constant checks; no automatic reduction deletion
  follows from replacing a `3q/2` label. Per-constant, per-input-interval images
  instead tighten the actual P7-B1 source chain to 22473→2311→19545→4485→1728.
- Traced P7-B1 physical I9 arithmetic and full main/tail I16 arithmetic/stores;
  checked 288 leaf roots and 41472 inverse weights including the R correction.
  All 64 one-product B3 orientations pass the model. The simple all-722 variant
  has 19 rather than 37 mulmods per I9, saves 48 arithmetic instructions/block,
  and closes at 22473→2617→21397→4577→1728. Mixed orientation mask 8 tightens
  this slightly but needs both root constant pairs; its timing is unknown.
- Retained the final I16 `b=1` reset: independent inputs within the existing
  2497 box can produce sixteen I9 s=0 values of 2112, giving 33792 without
  that reset. This is an input-contract witness, not asserted joint KEM
  reachability. Added P7-C1 for physical implementation and timing before P8;
  P9/P10 remain queued. Production assembly and the selected Official baseline
  are unchanged. No new cycle or physical-candidate correctness claim.

### 2026-09-10

- Created the persistent ledger.
- Completed P0 production promotion from the validated isolated
  `baseinv-tobytes-next-model` candidate.  The linked numerator and finish
  regions are exactly 84 and 37 instructions.  The pair+merge cores are 767
  (small) and 805 (full) instructions, with 432-byte wiped scratch.
- Pi 5 production versus selected Official: Keygen 47226.875 versus 44330.875
  cycles (+6.53%); Encaps 46007.625 versus 46413.375 (-0.87%); Decaps
  44191.300 versus 40772.875 (+8.38%).
- Promoted production passed 100 KAT cases (SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`),
  808 linked BaseInv cases including alias/failure/wipe, and the 417216-byte
  malformed transcript (SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`).
- Activated P1: shortest BaseInv exponent-3455 addition chain.
- P1--P6 were carried forward from the SUPERCOP remaining-optimization audit.
- Completed P1.  The inverse region changed from 28 to 21 widening Montgomery
  multiplications and from 208 to 157 instructions.  Slothy produced a
  zero-spill 283-cycle schedule.  Pi 5 BaseInv success improved by 91.797 cycles
  (-1.65%), and complete Keygen improved by 177 cycles (-0.375%).  Keygen's
  instruction count fell by exactly 102, matching its two BaseInv calls.
- Activated P2: two-tile BaseInv organization and SIMD failure aggregation.
- Completed P2-A.  One 160-instruction Slothy region replaces two 84-instruction
  numerator leaves, sharing q, qinv, R mod q and its Barrett-Shoup constant.
  Slothy reports 163 expected A76 cycles and zero spills.  The wrapper now makes
  18 pair calls instead of 36 tile calls, without changing the denominator
  layout or adding memory traffic.  Pi 5 BaseInv success improved by 162.923
  cycles and complete Keygen by 351 cycles versus P1.
- Completed P2-B.  The fixed 24-halfword scalar zero scan is replaced by three
  vector loads, three `CMEQ`, two `ORR`, `UMAXV`, and `UMOV`; all lanes are
  aggregated before the same single failure branch.  It removes 137 dynamic
  instructions and 24 branches per BaseInv, improving BaseInv success by
  68.672 cycles and Keygen by 145.25 cycles versus P1.
- Promoted the combined P2 candidate.  It removes 533 instructions and 78
  branches per BaseInv and 1,066 instructions and 156 branches per Keygen.
  BaseInv success improved from 5450.860 to 5214.297 cycles (-4.34%); Keygen
  improved from 46998.875 to 46503.875 cycles (-1.05%).  KAT, valid/tampered
  KEM, BaseInv success and BaseInv failure tests passed.  Encaps and Decaps have
  zero instruction change because they do not call BaseInv.
- Activated P3: monolithic/stage-fused Decaps inverse.
- Completed and promoted P3-A.  A single `center864` loop replaces 27
  `center32` calls, keeping q, reciprocal9 and halfq resident.  Slothy schedules
  each 64-byte body at 37 modeled Cortex-A76 cycles with 40 instructions and no
  spill.  Exhaustive producer-range scalar coverage, 4,096 random vectors,
  canaries, exact aliasing, KAT and tampered KEM checks passed.  Pi 5 Inverse
  improved from 7230.391 to 7017.531 cycles (-2.94%); Decaps improved from
  44206.275 to 43994.000 cycles (-0.48%), with exactly 235 instructions and 52
  branches removed from both.  P3 remains active for producer-fused centering.
- Completed and rejected P3-B.  The candidate packed the two half-filled
  terminal vectors with `ZIP1`, centered each packed group, and retained every
  existing `UMOV`/`STRH` address.  Exhaustive `[-6912,6912]` reduction,
  lane/address, dead-register, fixed-allocation Slothy, KAT, tampered, exact
  Inverse and alias gates passed.  It removed 108 Q loads, 108 Q stores and 29
  branches, but added exactly 61 instructions and serialized centering into 112
  scatter groups.  Pi 5 Inverse regressed from 7005.531 to 7639.797 cycles
  (+9.05%); Decaps regressed from 44006.425 to 44649.850 (+1.46%).  Production
  remains P3-A and P4 is now active.
- Completed and promoted P4.  Legality is accumulated with unsigned vector
  maxima directly from all 108 existing `unpack8` results, before their
  temporaries enter the unchanged routing network.  This removes the second
  1,728-byte output scan without adding input loads, output stores, scratch or
  vector spills.  Local differential testing passed 5,828 boundary/random
  cases; Pi 5 passed 13,824 KEM rejection cases across Encaps `pk` and Decaps
  `ct`, `sk[0]`, `sk[1]`, every coefficient position, and invalid values 3457
  and 4095.  KAT SHA-256 remained
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
  Checked FromBytes improved from 870.856 to 715.062 cycles (-17.89%);
  Encaps improved by 126.100 cycles and Decaps by 443.750 cycles, with exact
  dynamic deltas of -322 instructions/-108 branches per decoder call.  P5 is
  now active.
- Completed and promoted P5.  The Keygen `h` and `hinv` live intervals now
  share one 1,728-byte polynomial; Encaps uses the not-yet-final `ct` buffer for
  serialized `r`; Decaps reuses the dead `f` work slot and retains four rather
  than seven polynomial objects.  GCC 14.2 stack frames changed from
  10,720/8,704/16,288 to 8,992/7,392/11,072 bytes for Keygen, the Encaps helper
  and Decaps.  Every surviving secret-bearing object remains explicitly wiped
  on its applicable normal and failure paths.
- P5 passed exact 100-case KAT, 64 valid/tampered iterations, 13,824 exhaustive
  non-canonical KEM rejection cases and the byte-identical malformed transcript.
  Six balanced Pi 5 runs measured Keygen `-95.500` cycles (`-149`
  instructions), Encaps `-48.950` (`-124`) and Decaps `-166.800` (`-455`)
  versus P4.  The improvement is from storage lifetime and cleanup traffic;
  arithmetic and transform ABIs are unchanged.  P6 is now active.
- Completed P6-A and rejected only the storage-only/current-route candidate.
  Two retained pairs require 13 vector and 28 GPR storage slots; together with
  the current third-pair route, row copy and independent TBL index, the exact
  frontier is 33 vectors. Local Cortex-A76 Slothy reports `INFEASIBLE` with
  spills disabled. Both controls allocate `OPTIMAL`: either remove one held
  vector or remove the independent index lifetime. A Pi 5 bridge proxy still
  improves from 58.999 to 42.000 cycles/top, so P6 remains active as a
  consumer-oriented route redesign rather than being dropped.
- Completed the P6-B packed-half feasibility gate.  The third pair is split so
  its canonical A half occupies the exact 108-byte 12-bit representation
  (seven Q slots) before its nine-vector B route is created.  All nine
  production `p3b1_a_fwd` permutations and 4,100 exact pack cases passed.
  Local Slothy from `/Users/chenpinhao/slothy` allocated both the 31-vector
  route-repair frontier and the exact 32-vector full-Barrett frontier with
  spills disabled; both physical regions assembled for arm64.  This proves
  capacity, not a complete kernel: P6-C must still close the joint packed-A
  producer, pair reconstruction, three-pair merge, TBL grouping and final
  full-vector store DAG before any benchmark or production change.
- Completed the P6-C joint-consumer feasibility gate.  A stale symbolic load
  name had created seven false live-ins and the earlier 33-vector result; after
  repairing the definition chain, reverse liveness is exactly 26 vectors for
  packed-A production and 32 for the worst first-row consumer.  Local
  Cortex-A76 Slothy allocation is `OPTIMAL` without spill at modeled 45 and 30
  cycles, respectively.  All ten TBL2 and five TBL3 source groups are
  physically consecutive, and both allocated regions assemble on arm64.
- The executable Mac oracle passed 12,288 packed-A cases and 4,096 joint-row
  cases with exact output bytes and future-state preservation.  This remains a
  partial kernel: production and its 432-byte wiped scratch are unchanged.
  P6-D is now next and must build the complete full/small nine-row kernels,
  close GPR reconstruction/cross-row carry and public ABI, then pass complete
  correctness before Pi 5 timing.
- P6-D1 now proves the saved-pair producer frontier.  Pair 0 and pair 1 allocate
  `OPTIMAL` without spill at 407 and 475 semantic instructions; physical TBL
  groups are consecutive and `x18` is unused.  An executable arm64 oracle
  passed 4,107 edge/random cases against production `byte_pair_block`, including
  the exact 13-Q plus 28-GPR dense state.
- P6-D2 proves the all-nine-row coordinate schedule over 4,096 cases.  Rows are
  consumed in logical order `0,3,6,1,4,7,2,5,8`; physical row 4 is the exact
  Q-to-GPR crossing, and the final top boundary remains 40 `STR Q` plus one
  `STR D`.
- Completed P6-D3.  The third pair is processed as A-route/normalize/pack,
  then B-route, then nine physical-row consumers; this avoids simultaneous
  nine-A plus nine-B liveness.  Cross-row eight-byte carry converts the first
  byte-correct `72 Q + 18 D` shape into exactly `80 Q + 2 D` final stores.
  All twelve local Cortex-A76 Slothy regions are `OPTIMAL` with spill disabled.
  After adding the production-equivalent 32 volatile SIMD clears, the
  16,880-byte arm64 text performs 108 coefficient Q loads, uses a 176-byte
  public save frame and zero coefficient scratch, keeps TBL groups consecutive,
  and uses neither lane ST3 nor x18.  The executable oracle passed 4,107 full
  signed-int16 cases and 4,096 small-range cases with output canaries.

### 2026-09-11

- P6-E rejected P6-D3 at the complete public boundary.  On Pi 5, full changed
  from 1766.734 to 2268.457 cycles (+501.723, +28.40%) and small from 1363.399
  to 2268.223 (+904.825, +66.37%).  Every one of 74 paired samples per mode
  regressed.  P6-D3 removes about 105 PMU write events and 56--63 branches, but
  adds 101 read events and 829--1064 retired instructions; IPC also falls.
- Production remains the P5 432-byte wiped-scratch implementation.  A
  small-only Barrett specialization is not the next step because the full
  route/table DAG already fails.  ToBytes reopens only after a smaller
  FR0-coordinate-to-wire network jointly consumes normalization, 12-bit
  packing and routing without nine complete routed rows, reduces TBL2/TBL3,
  uses separate full/small DAGs, and statically removes at least about 829
  instructions and 101 reads before Slothy.
- The fixed priority is now P7 Inverse CT feasibility, P8 raw-Inverse-to-ternary,
  then P9 ToBytes routing search.  This replaces the temporary proposal to run
  another general profiler before selecting the next gate.
- Completed P6-F, the requested fresh profiler checkpoint.  On 252 clean Pi 5
  observations per operation and implementation, GT measured 46,389.875 cycles
  for Keygen (+4.72%), 45,748.075 for Encaps (-1.45%), and 43,366.125 for
  Decaps (+6.41%) against 44,299.625, 46,423.100, and 40,753.325 selected-
  Official cycles.  Six independent exact/tampered cross-implementation gates,
  fresh GT test/KAT, and all instrumentation-equivalence checks passed.
- Call-site profiling isolates the Keygen deficit primarily to BaseInv
  (+2,105 cycles per Keygen) and the Decaps deficit primarily to Inverse
  (+2,895.9).  Aggregate GT ToBytes remains slower by +1,276.0/+966.6/+977.6
  cycles in Keygen/Encaps/Decaps.  GT Forward is already faster by about
  725--730 cycles per two calls, R0 BaseMul is faster, R-inverse BaseMul is tied,
  and FromBytes is slightly faster.  Therefore P7--P9 remain ordered as before;
  P10 records the Keygen-only BaseInv opportunity so it is not forgotten.
- Completed P7.  Dependency inspection classifies GT's four-layer NTT16 as
  CT DIT and selected Official as GS DIF.  The exact N=16 ordering relation
  passed 10,000 random vectors: GT absorbs bit reversal into P8 coordinates
  and adds no complete permutation pass.  At the closed I16 input bound 3456,
  CT stays int16-safe while an unreduced GS sum path reaches 55,296 and needs
  at least one range cut, so the local CT benefit is real.  It is not an
  end-to-end win: GT still measures 7,013.950 versus 4,118.050 Official cycles,
  with 12 inverse9 calls, P8 materialization, 864 `UMOV` plus 864 scalar stores,
  a 1,169-instruction center pass and scratch lifecycle outside the CT/GS
  choice.  P7 therefore retains production CT without a new assembly candidate.
- The post-P7 priority was corrected before starting raw-to-ternary: P7-B0 now
  decomposes the fixed-ABI Inverse itself on Pi 5, and P7-B1 must optimize its
  measured dominant NTT/routing region.  This prevents removal of the consumer
  center pass from being mistaken for an Inverse-NTT improvement.  P8
  raw-Inverse-to-ternary follows only after the core attempt; P9 ToBytes and
  P10 BaseInv remain queued.
- Completed P7-B0.  Same-boundary PMU decomposed the 7,021.336-cycle production
  Inverse into inverse9 aggregate 2,958.406, six main NTT16 calls 2,555.812,
  tail NTT16 409.297, center864 750.859 and wrapper/residual work.  Inverse9 is
  both the largest isolated stage and the lowest-IPC stage (1.292).  Diagnostic
  removal of all 864 main/tail halfword scatters saved only 164.890 cycles, so
  a full-vector terminal ABI was not selected for B1.
- Completed and promoted P7-B1.  Physical `v0` and `v5`, previously unused by
  `packed_i9`, now retain the repeated Algorithm-10 constant pair 722/6844.
  This removes six repeated MOV+DUP materializations of each constant: 20
  instructions per inverse9 call, 240 per complete Inverse, and 80 text bytes.
  A generator audit caught and fixed both Q/V register alias termination and a
  destructive destination's final source use before the candidate was accepted.
- Instruction deletion alone was not sufficient: the raw-order candidate
  regressed Inverse by 15.258 cycles and Decaps by 10.225.  Timing-only Slothy
  from `/Users/chenpinhao/slothy`, with renaming and spills disabled, preserved
  all 284 instructions and produced a 71-cycle A76 model.  Relative to raw it
  recovered 27.571 Inverse and 25.700 Decaps cycles.  The final candidate versus
  production improved paired medians by 18.782 Inverse cycles and 17.875 Decaps
  cycles while retiring exactly 240 fewer instructions at both boundaries.
- Six baseline-to-candidate paired runs passed 24 valid, 24 tampered, 256 exact
  Inverse and 256 exact-alias checks each.  Fresh 64-case KEM and 100-case KAT
  passed with unchanged digest
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
  The cleaned production source assembles to the byte-identical benchmarked
  object.  Keygen and Encaps retire exactly zero changed instructions, confirming
  the caller scope; P8 is now active, followed by P9 and P10.
