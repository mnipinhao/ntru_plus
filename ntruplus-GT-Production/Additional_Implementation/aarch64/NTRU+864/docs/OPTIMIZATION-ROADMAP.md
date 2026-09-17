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
| P22 | Done—Rejected | Replace 32 held-value `ORR` copies/call with two-output SSA butterflies | Exact/no-spill/model and isolated main-I16 gates pass, but complete Inverse and Decaps regress; production unchanged |
| P23 | Done—Promotion candidate | Globally intern P18's repeated source rotations and transpose nodes, then jointly schedule three output consumers | Exact 26-register/no-scratch DAG removes 194 instructions and 6 reads per call; Full/Small and all three isolated full-KEM boundaries win on Pi 5 |
| P24 | Done—Promoted | Link the exact P23 three-output schedules as production Full/Small ToBytes | Commit-archive rebuild passed manifest/symbol/object, exact-byte/canary/input immutability, AAPCS/wipe, KAT/malformed and paired boundary/full-KEM gates; all three KEM operations win |
| P25 | Done—Profiler checkpoint | Refresh production versus selected SUPERCOP 20260831 Official after P24 | Exact/tampered and instrumentation-equivalence gates pass; GT wins Keygen/Encaps/Decaps by 1167.750/1440.450/694.525 cycles; Inverse-to-ternary is the largest positive matched gap |
| P26 | Done—Inverse deficit audit | Align Official Inverse+Crepmod3 with GT inverse9/main-I16/tail-I16/raw-ternary/wrapper work and classify the +3740 instructions | Exact dynamic source ledger reconciles to P25 PMU; GT has 151 fewer modular-multiply instructions, while lane extraction/load/store fragmentation dominates |
| P27 | Done—Machine candidate | Search an inverse9→I16 physical basis that directly feeds vector raw-to-ternary output | All 15 P8-record matchings exhausted; unique three-bank basis gives exact 108-Q dense scratch/108-Q natural route, max four live TBL sources, unchanged root/scale/range and conservative -1314 instructions; production unchanged |
| P28 | Done—Rejected | Realize P27 as paired main-I16, dense tail and standalone routed ternary consumer | Correct/no-spill and isolated replacement wins, but complete Inverse regresses 147.266 cycles; production unchanged |
| P28-S | Done—Rejected | Timing-schedule fixed P28 allocation with bounded local Slothy windows | Recovers 60.313 cycles versus P28 but remains 83.875 cycles slower than production complete Inverse |
| P29 | Done—Rejected | Replace standalone TBL route with equal-half pairs and direct full-vector ST3 | Removes masks and 1452 production instructions, but complete Inverse/Decaps regress 76.844/108.625 cycles |
| P30 | Done—Rejected | Schedule adjacent direct-ST3 records jointly | Slothy model predicts -240 route cycles, but Pi 5 regresses complete Inverse by 10.336 cycles versus P29; model mismatch recorded |
| P31 | Done—Rejected | Produce rows 0--3 early from pair2 and rows 4--7 from pair1 | Removes 1536 scratch bytes but adds 159 instructions versus P29 and regresses production Inverse/Decaps by 418.617/439.000 cycles |
| P32 | Done—Rejected | Split six I16 prefixes from one column-major six-bank composite terminal consumer | Exact/no-spill/KAT/alias/wipe pass and -173 complete-Inverse instructions, but IPC falls and Inverse/Decaps regress 106.664/111.300 cycles |
| P33 | Done—Rejected | Reusable two-bank hybrid: materialize one prefix, compute one live prefix, then share terminal constants across the pair | Retires 147 fewer complete-Inverse instructions, but main-I16/Inverse/Decaps regress 132.110/95.297/104.150 cycles as IPC falls |
| P34 | Done—Selected successor | Re-profile and select a non-materializing Inverse DAG that removes arithmetic or scatter/routing work rather than only table loads | Exact P8 domain and terminal range audit selects KEM-only reset pruning; P35 later finds one additional dead tail constant setup, making the exact delta -74 instructions |
| P35 | Done—Promoted | Distinct KEM-only main/tail I16 helpers retaining only main high-column-8 reset | Exact/no-spill/Slothy/arm64/alias/AAPCS/wipe/KAT/malformed gates pass; Inverse-to-ternary -139.485 cycles and Decaps -138.825 cycles with exactly -74 instructions |
| P36 | Done—Retained | Revisit the sole remaining main high-column-8 reset with a correlation-aware reachable-range or equivalent composite-representative search | Current constants are minimax; strict integer correlation proof did not close abs<=5185, so deletion gate fails and P35 production remains unchanged |
| P37 | Done—Profiler checkpoint | Refresh P35 production versus selected SUPERCOP 20260831 Official and update component/call-site attribution | All gates pass; GT wins Keygen/Encaps/Decaps by 1158.250/1432.075/849.325 cycles; Full ToBytes is +301--305 cycles/call while Small already wins |
| P38 | Done—Rejected statically | Co-design direct-Forward terminal representatives with Full route/normalization/packing; freeze Small and P35 Inverse | Every coordinate has a valid small/keygen input outside `(-q,q)`; post-pass/store canonicalization only relocates all 216 instructions and quotient reuse fails, so best net deletion is zero |
| P39 | Done—Rejected statically | Search the twelve inverse9 blocks for a new identity, composite constant or redundant reduction while freezing P35 I16 and memory ABI | All 64 B3 orientations and 36 terminal vectors checked; best exact in-contract rewrite saves only 1 instruction/block, below the required complete Algorithm-10 triple, so production remains unchanged |
| P40 | Done—Rejected on Pi 5 | Move the exact inverse9 geometric terminal phase into row-dependent twisted I16 tables and compose the remaining row/top scale into P13 terminal tables | Exact/no-spill/KAT/alias/wipe pass and -137 instructions, but Inverse/Decaps regress 221.508/219.525 cycles as multiply dependency and table pressure reduce IPC; P35 remains production |
| P41 | Done—Rejected at exact boundary | Pair adjacent 12-byte Full records as overlapping Q/S/D stores while preserving P24 normalization, packing and wire ABI | Exact/no-spill/KAT/KEM pass and -38 instructions, but A-before-B routing adds 30 reads and Full boundary regresses 2.253 cycles; production remains P24 |
| P42 | Done—Rejected on Pi 5 | Replace each ToBytes `SSHR+AND+ADD` sign correction with `CMLT+MLS` while freezing P24 routing, packing and memory ABI | Exact/no-spill/KAT/KEM pass and -108 instructions/call, but multiply-pipeline pressure lowers IPC; Full/Small regress 7.438/14.774 cycles |
| P43 | Done—Profiler checkpoint | Re-run exact current GT production versus selected SUPERCOP 20260831 Official with clean KEM and component/event profiling | All correctness/instrumentation gates pass; GT wins Keygen/Encaps/Decaps by 1170.500/1411.075/852.100 cycles; remaining positive gaps are Full ToBytes and fused Inverse-to-ternary |
| P44 | Done—Rejected statically | Retain P41's overlapping Q/S/D stores and borrow `v29` (then phase-local `v30-v31`) while routing; every consumer boundary returns to the exact P24 26-register route-cache contract | Best instruction/load Pareto points were 306/70 and 311/66 per top, missing the required 300/61 gate even in an optimistic no-relocation-cost model; no assembly or Slothy run was warranted |
| P45 | Done—Rejected statically | Replace P41's independently packed A/B records with one exact two-record packing DAG and Q/D-granularity stores | Exact nine-instruction joint packing saves 243 instructions/top, but simultaneous A/B routing needs 121 coefficient loads and 384 route instructions/top; it fails the 61-load/300-instruction gate before assembly |
| P46 | Done—Promoted | Replace each Full-only `SSHR+AND+ADD` correction with the exact `USHR+MLA` sign-bit identity; freeze Small | Exhaustive identity, exact bytes, no-spill allocation, KAT/malformed and Pi 5 pass; Full saves 8.364 cycles and every KEM caller wins with -108 instructions. User explicitly approved promotion despite the preserved Slothy 1495→1562 proxy regression |
| P47 | Done—Promoted | Let the Decaps re-encryption serializer feed the ciphertext comparison consumer directly without materializing an avoidable generic boundary | Exact/all-byte/KAT/malformed, constant-time, no-spill and Slothy gates pass; Decaps saves 143.650 cycles, 19 instructions, 97.5 branches and 1072 stack bytes; generic P46 remains unchanged |
| P48 | Done—Promoted | Let the Encaps Full serializer feed the exact `0x01 || bytes` SHAKE input directly, eliminating the immediate 1296-byte copy | Exact transcript/native/KAT/malformed/KEM and object gates pass; Encaps saves 121.225 cycles, 175 instructions and 24 branches; controls are unchanged |
| P49 | Done—Rejected statically | Specialize only the Keygen Full producer/serializer boundary using its proven K1 range | All 288 leaves exceed the Small contract and no exact uniform shifted/biased/scaled three-instruction reduction exists; no assembly, Slothy or Pi timing warranted |
| P50 | Done—Selected-Official profiler checkpoint | Re-run exact P48 production versus selected SUPERCOP 20260831 Official with explicit P47/P48 fused-boundary attribution | All correctness/instrumentation gates pass; GT wins Keygen/Encaps/Decaps by 1182.125/1586.900/995.875 cycles; largest isolated gaps are Decaps Full-compare +176.050 and fused Inverse +153.725 cycles |
| P51 | Done—Experimental, not promoted | Retain recovered FR0 `f`, regenerate into dead `c`, and compare congruence directly in identical FR0/R0 coordinates instead of routing 1296 canonical bytes | All gates pass and the experiment saves 988.525 Decaps cycles, but user policy keeps it outside production; P47 serializer/compare remains linked |
| P52 | Done—Profiler checkpoint | Profile exact P51 against selected SUPERCOP 20260831 and identify the next boundary | All gates pass; P51 GT wins Keygen/Encaps/Decaps by 1182.000/1525.950/1987.425 cycles; fixed-size NO_CE `hash_g` selected for P53 |
| P53 | Done—Promoted NO_CE | Parameterize the 768 production register-resident scalar sponge for SHAKE256(`0x01 || 1296 bytes`) → 216 bytes | All gates pass; hash_g -4358.235, Encaps -4252.225 and Decaps -4312.950 cycles with no SHA3-extension instruction; Keygen retires zero changed instructions |
| P54 | Done—Release hardened | Adopt 768's layered release gates and export contract without copying its transform implementation | Direct-link closure contains only selected P53/P47/P46/P35/P10/K1 sources; legacy candidates/evidence removed; KEM, ABI, canonical rejection, zeroization, exact-KAT and deterministic-export gates pass on Pi 5 |
| P55 | Done—Promoted NO_CE | Specialize fixed-size SHAKE256(`0x00 || 1296 bytes`) → 32-byte `hash_f` for Keygen and Encaps | Differential/alias, KEM/KAT/malformed, ABI/wipe/no-CE and hash_g-byte-identity gates pass; hash_f -4102.938, Keygen -4117.000 and Encaps -4095.400 paired cycles; Decaps retires zero changed instructions |
| P56 | Done—Selected-Official profiler checkpoint | Re-run exact P55 production against selected SUPERCOP 20260831 Official with full correctness, clean PMU and component attribution | GT wins Keygen/Encaps/Decaps by 5207.375/9734.450/5385.875 cycles (11.75%/20.99%/13.21%); remaining diagnostic deficits are Inverse-to-ternary about +155.75 cycles and serialization/compare about +58.4 |
| P57 | Done—Packaging | Align the NTRU+864 release with the `Additional_Implementation`/`SUPERCOP` structure and replace campaign-oriented source names with role-oriented names | Full Pi 5 release gate and independent SUPERCOP-leaf build pass; paired PMU has zero instruction/branch delta and no cycle regression |

## ToBytes priority policy

Keep two ordered tracks because a faster generic serializer and the fastest
complete KEM do not necessarily select the same boundary.

For improving the reusable production ToBytes entry point, use this order:

1. P44 route-cache borrowing plus overlapping stores — rejected statically.
2. P45 two-record joint packing plus Q/D-granularity stores — rejected statically.
3. P46 a new Full normalization DAG — promoted after explicit target-silicon
   override of the documented Slothy-proxy regression.

For improving complete KEM operations as quickly as possible, use this order:

1. P47 Decaps Full-ToBytes-to-compare — promoted.
2. P48 Encaps Full-ToBytes-to-SHAKE — promoted.
3. P44 generic serializer work.
4. P49 Keygen Full normalization — rejected statically.

P44 and P45 are closed at their static gates. P46 is the production generic
Full serializer; Small remains P24. P47 is now the production Decaps-private
compare consumer. P48 is now the production Encaps-private SHAKE consumer. P49
is closed at its static gate; P50 has refreshed the selected-Official
profile. P51 transform-domain equality remains an archived experiment rather
than production; P53 fixed-size NO_CE `hash_g` and P55 fixed-size NO_CE
`hash_f` are active. Caller-specific results
must not be mixed into a generic same-boundary result.

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

### 2026-09-17

- Started P57 packaging cleanup. Production filenames and internal symbols now
  use transform roles (`ntt`, `base`, `inverse`, `pack`, `unpack`, `hash`)
  instead of parameter/campaign prefixes. Research provenance comments were
  removed from executable sources while range, Montgomery-scale, ABI, alias,
  constant-time and zeroization contracts were retained. A deterministic
  `SUPERCOP/crypto_kem/ntruplus864/aarch64` leaf is now materialized alongside
  the additional implementation. Arithmetic and data-flow selection remain
  identical to P55. Pi 5 release and independent SUPERCOP-leaf builds pass.
  Paired PMU retires exactly the same instructions and branches; Keygen,
  Encaps and Decaps cycle deltas are -20.125, -7.975 and -0.225 cycles, all
  non-regressions. Evidence: `experiments/gt864-p57-production-layout/`.

- Completed P56 against the pinned selected SUPERCOP 20260831 SHAKE256
  AArch64 source. The three Official anchor hashes are unchanged; upstream-
  latest status remains unverified. Fresh GT KEM/KAT, six 100-case exact plus
  tampered cross-implementation processes, twelve instrumentation-equivalence
  processes and unthrottled Pi 5 PMU all pass.
- Across 252 clean observations per implementation and operation, P55 GT beats
  Official Keygen by 5207.375 cycles (11.75%), Encaps by 9734.450 (20.99%) and
  Decaps by 5385.875 (13.21%). P55 `hash_f` contributes about 4.1k cycles to
  both Keygen and Encaps, while P53 `hash_g` contributes about 4.46k to Decaps.
  Diagnostic matched boundaries leave only about +155.75 cycles in fused
  Inverse-to-ternary and +58.4 in Decaps serialization/compare. Evidence:
  `experiments/gt864-p56-official-profile/`.

### 2026-09-16

- Completed and promoted P55 for the NO_CE build. The exact transcript is
  SHAKE256(`0x00 || input[1296]`) to 32 bytes: nine full absorb blocks, a
  73-byte tail and four output lanes after the tenth permutation. The state
  stays in GPRs; the virtual prefix removes the 1297-byte temporary image.
  Differential and exact-alias checks passed 4,096 cases, and package KEM,
  ABI, canonical rejection, zeroization, KAT and malformed transcripts remain
  exact. The P53 `hash_g` object section is byte-identical and the new object
  contains no Armv8.4 SHA3 instruction.
- Across both execution orders, P55 improves `hash_f` by 4102.938 paired-
  median cycles and 16,056 instructions. Keygen improves by 4117.000 cycles
  and Encaps by 4095.400 cycles. Decaps retires exactly zero changed
  instructions or branches; its +2.575-cycle movement is noise. Evidence:
  `experiments/gt864-p55-noce-hash-f/`.

- Completed P54 release hardening without changing transform arithmetic. The
  direct source closure removes legacy stock transforms, T0/T2 tail variants,
  retired inverse/ToBytes candidates, compatibility adapters and raw evidence.
  Pi 5 passes 64 valid/tampered KEM iterations, zero AAPCS64 sentinel bits for
  eleven endpoints, all 10,368 noncanonical public/ciphertext/secret-key cases,
  runtime zeroization (`25` calls, `26,904` bytes, zero uncleared bytes), and
  exact KAT response SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
  The deterministic flat SUPERCOP export independently compiles and passes the
  same 64-case direct KEM test on Pi 5. P54 is packaging/release work, so it
  intentionally makes no cycle-performance claim.

- Completed P51 at the Decaps re-encryption equality boundary, then withdrew
  its production binding at the user's request. The kernel, proof and timing
  remain archived as an experimental candidate; production again uses P47.
  Both operands are the same FR0 coordinate permutation, logical root set and
  R0 Montgomery scale, so the injective wire permutation and canonical 12-bit
  packing are unnecessary for equality.  Exact producer closure gives K1
  regenerated leaves inside `[-24799,24794]`, recovered D1 leaves inside
  `[-3023,3023]`, and differences inside signed int16.  Exhaustive evaluation
  of every signed-int16 input proves the `SQRDMULH(9)+MLS(3457)` residue lies
  in `[-3291,3291]` and is zero exactly for multiples of q.
- The selected 86-instruction object reads each 1728-byte operand once, writes
  nothing, uses no stack or scratch, has one fixed nine-iteration branch, and
  wipes its secret SIMD temporaries.  Native differential, alias/immutability,
  KAT, malformed ciphertext and six-process exact/tampered gates all pass.
  Against exact P50 production on Pi 5, 252 paired observations retire 2014
  fewer instructions and improve Decaps by 988.525 cycles.  Keygen and Encaps
  retire exactly zero changed instructions.
- A separate all-29-register Slothy candidate preserved the exact 60-loop-
  instruction multiset without spill and reduced the Cortex-A76 model from
  128 to 62 cycles.  It did not improve the complete Pi 5 boundary after its
  larger wipe footprint (`-989.550` cycles versus baseline, statistically tied
  with the compact candidate), so production deliberately retains the smaller
  compact allocation in the experiment. P52 then refreshed the
  selected-Official profiler checkpoint.
  Evidence: `experiments/gt864-p51-transform-equality/`.

- Completed P52 against the selected SUPERCOP 20260831 SHAKE256 AArch64 tree.
  All correctness and instrumentation-equivalence gates passed. P51 GT won
  Keygen/Encaps/Decaps by 1182.000/1525.950/1987.425 cycles. `hash_g` remains
  an approximately 14.46k-cycle GT boundary, so P53 adapts only the 768
  production fixed-size, register-resident scalar sponge organization for
  864; no 768 NTT/layout/range fact is reused. Evidence:
  `experiments/gt864-p52-official-profile/`.

- Completed and promoted P53 for the NO_CE build. The fixed transcript is
  SHAKE256(`0x01 || input[1296]`) to 216 bytes: nine full absorb blocks, a
  73-byte tail, then 136+80 output bytes. State remains in GPRs over eleven
  scalar permutations. Differential/alias, KAT, malformed, object/wipe and
  paired PMU gates pass. `hash_g` improves by 4358.235 cycles and complete
  Encaps/Decaps by 4252.225/4312.950 cycles. Keygen retires exactly zero
  changed instructions. P54 now applies the 768 production package/release
  structure without importing its transform math. Evidence:
  `experiments/gt864-p53-noce-hash/`.

- Completed P50 without changing production. Exact commit `53ba4e27` and the
  selected SUPERCOP 20260831 AArch64 tree passed fresh manifest/build/KEM/KAT,
  six 100-case exact plus tampered cross-implementation processes, and all
  cycle/event instrumentation-equivalence gates. The Pi 5 remained
  unthrottled. Across 252 clean observations each, GT beats Official by
  1182.125 Keygen, 1586.900 Encaps and 995.875 Decaps cycles, with higher IPC
  in all three operations.
- P50 explicitly instruments P48 `Full_to_hash_g`, P47 `Full_compare`, and the
  selected Official's inline `verify`. Matched attribution leaves two leading
  positive Decaps boundaries: regenerated-f serializer+verify at +176.050
  cycles and fused Inverse-to-ternary at +153.725. Encaps's fused
  Full-to-hash sub-boundary is +80.775, but its second Small serializer wins by
  126.900, so its two serialization paths win in aggregate. P51 is selected:
  retain the recovered FR0 `f`, regenerate into an already-dead poly slot, and
  perform constant-time mod-q transform-domain equality without producing the
  second wire image. The algebra gate must prove coordinate/root/scale
  identity, transform injectivity, exact zero-test range, and rejection
  equivalence before assembly or timing. Evidence:
  `experiments/gt864-p50-official-profile/`.

- Completed P49 and rejected it before assembly. The exact K1 Keygen `f`
  producer has 288 leaf intervals with envelope `[-28765,28258]`; none fits the
  Small serializer contract. P46's reciprocal-9 residual narrows to
  `[-3107,3107]` but still has both signs. Exhaustive fixed-constant searches
  find no exact uniform shifted, biased or scaled three-instruction reduction;
  shifted/biased families have no solution even per leaf. Direct Small has a
  canonical-byte counterexample at 3457. Production remains P46 and Slothy/Pi
  timing were correctly skipped. Evidence: `experiments/gt864-p49-keygen-full/`.

- Completed and promoted P48 only at the Encaps `r -> hash_g` boundary. The
  exact P46 serializer now writes into `data+1`, with `data[0]=0x01`, before the
  unchanged SHAKE256 call. This removes the full 1296-byte `ct -> data` copy
  without changing the transcript or generic interfaces. Python/native
  differential, KAT, malformed rejection, 64 KEM cases and object binding pass.
  Across 252 Pi 5 observations, Encaps improves 44996.375->44877.825 cycles
  (paired -121.225), -175 instructions and -24 branches; Keygen/Decaps controls
  have zero instruction/branch deltas. Evidence:
  `experiments/gt864-p48-encaps-shake/`.

- Completed and promoted P47 only at the Decaps re-encryption boundary. The
  P46 route/normalize/pack DAG now compares each exact 12-byte record directly
  with `buf1`, returning one constant-time mismatch bit without candidate-byte
  stores or overreads. `buf2` retains only its earlier 216-byte `hash_g`
  lifetime, shrinking the compiled Decaps frame 11088→10016 bytes. Exact
  equality plus every byte position corrupted across 256 native inputs, KAT,
  malformed rejection, 64 KEM cases, no-spill object audit and 18/18 optimal
  Slothy windows pass. Across 252 Pi 5 observations, Decaps improves
  39907.300→39763.225 cycles (paired -143.650), -19 instructions and -97.5
  branches. Generic P46 remains selected for Keygen and Encaps. Evidence:
  `experiments/gt864-p47-decaps-compare/`.

- Completed P45 and rejected it before assembly. The joint A/B pack itself is
  exact and costs only nine instructions per adjacent two-record group, but
  requiring both records together destroys the P24 route-cache economics. The
  best 27-register search point needs 384 route instructions and 121
  coefficient Q loads/top, versus the declared 300/61 gate. Evidence:
  `experiments/gt864-p45-two-record-pack/`.

- Completed and promoted P46 for Full ToBytes only. The
  Full-only `USHR #15; MLA q` identity is exhaustive over signed int16 and
  removes 108 instructions/call while leaving Small, routing, packing and
  memory traffic unchanged. All 18 fixed-allocation Slothy windows are
  optimal/no-spill, exact bytes, KAT and malformed gates pass. Pi 5 Full
  improves 1395.125→1386.762 cycles and Keygen/Encaps/Decaps improve by
  13.500/13.650/5.450 cycles. The A76 Slothy proxy regresses 1495→1562; the
  user explicitly approved the broader full-path tradeoff on 2026-09-16 and
  both numbers remain recorded without manufactured parity. Evidence:
  `experiments/gt864-p46-full-normalization/`.

- Completed and statically rejected P44 without changing production. The exact
  P24 Full top region and contracts were frozen before search. A phase-aware
  model allowed 27--29 route registers during construction but forced every
  consumer boundary back into `v0-v25`, so `v29-v31` were genuinely available
  to unchanged normalization and packing. Across 300,000 precedence-preserving
  mutations, the best instruction-first point was 306 route instructions and
  70 coefficient loads/top; the best load-first point was 311/66. Both miss the
  predeclared 300/61 gate, and the model does not yet charge possible physical
  relocation, so symbolic assembly and Slothy were correctly skipped. P41's
  reloads require cross-consumer retention, not merely transient route space.
  Evidence: `experiments/gt864-p44-route-cache-borrowing/`. P45 is now the next
  generic serializer gate.

- Completed P43, a measurement-only exact-production profiler checkpoint.
  Commit `34d2c758` was archived and compared with selected SUPERCOP 20260831
  Official on Pi 5. Fresh manifest/build/KEM/KAT, 600 exact and 600 tampered
  cross-implementation cases, and all instrumentation-equivalence gates pass.
  Across 252 clean observations each, GT wins Keygen/Encaps/Decaps by
  1170.500/1411.075/852.100 cycles (-2.641/-3.040/-2.090%). GT IPC is higher
  in all three despite +4790/+2611/+7274 retired instructions.
- Component profiling confirms GT Forward saves 717--732 cycles per two calls;
  BaseMul R0/BaseMulAdd also win materially. Remaining positive matched gaps
  are Full ToBytes at 302--305 cycles/call and Decaps fused Inverse-to-ternary
  at +142 cycles. Small ToBytes is 123--125 cycles/call faster than Official.
  The prior P43 route-cache experiment moves to P44. Evidence:
  `experiments/gt864-p42-production-profile/`.

- Completed and rejected P42 without changing production. P15/P16 had used
  `CMLT+AND+ADD`; they had never tested the exact two-instruction `CMLT+MLS`
  lowering at the current P24 boundary. P42 froze all route, packing, memory
  and ABI work and exhaustively proved the two forms equal for every signed
  int16 input. It removes exactly 108 retired instructions per Full or Small
  call with no load/store/branch change.
- The user's multiply-pipeline concern is confirmed by both models and silicon.
  Fixed-allocation Cortex-A76 Slothy changes Full 1495 to 1562 and Small 1010
  to 1071 modeled cycles/top. Pi 5 changes Full 1393.617 to 1401.055 cycles
  (+7.438) and Small 985.117 to 999.891 (+14.774); IPC falls
  1.5558->1.4704 and 1.9776->1.8404. Keygen/Encaps/Decaps regress
  26.625/18.525/25.825 cycles despite fewer instructions. P24 remains
  production. The former P42 route-cache proposal is retained as P43.
  Evidence: `experiments/gt864-p42-cmlt-mls-canonicalization/`.

- Completed and rejected P41 without changing production.  The original
  two-live-record design explodes the 26-register route cache to 423 route
  instructions and 136 coefficient loads/top.  The implemented alternative
  stores even record A as a Q with four temporary high bytes, then lets odd
  record B overwrite those bytes with `STUR S` and finish with `EXT #4` plus
  `STUR D`.  It needs no cross-record register lifetime or scratch.
- The A-before-B precedence schedule costs 320 route instructions and 76
  coefficient loads/top versus P24's 285/61.  Overlapping stores still reduce
  the complete call by 38 instructions, 54 writes and 108 vector-to-GPR moves,
  at the cost of 30 reads.  A 1,028-case exact model, arm64 assembly, 513-case
  Pi boundary oracle, no-spill object audit, KAT, malformed and full KEM gates
  pass.  Local Slothy Full timing changes 1495 to 1489 modeled cycles/top.
- Exact Pi 5 Full ToBytes changes 1393.356 to 1395.609 cycles (+2.253), so the
  predeclared component gate rejects promotion.  Complete Keygen/Encaps/Decaps
  nevertheless improve by 45.125/16.775/31.450 paired-median cycles with
  exactly 38 fewer instructions; this caller-context signal is retained for
  P42.  P42 must first remove the 30 precedence-induced coefficient reloads,
  targeting at most 61 loads and 300 route instructions/top before Slothy.
  Evidence: `experiments/gt864-p41-paired-record-store/`.

- Completed and rejected P40 without changing production. The exact terminal
  factor is `k(top,c,s)=k(top,0,s)*2863^(cs) mod 3457`, with 2863 of order 144.
  P40 deletes nine terminal Algorithm-10 products from each of twelve inverse9
  calls, twists all I16 right-branch constants, and composes the residual
  row/top factor into P13. The exact audit checked 288 factor contexts and 336
  I16 basis vectors; signed-int16 and P8 radius closure require only tail
  column-6-low's final `b=1` reset. No coefficient pass or scratch was added.
- The first all-constants-live DAG exceeded the 32-vector frontier. Loading one
  `(b,bhat)` pair immediately before all consumers made inverse9/main/tail
  Slothy allocation `OPTIMAL` with no spills; fixed allocations then completed
  bounded Cortex-A76 timing and all scheduled sources assembled for arm64.
- Pi 5 passed identical 100-case KAT, 417216-byte malformed transcript, 9155
  raw conversion values and 1024 exact/alias/AAPCS/wipe cases. Despite retiring
  137 fewer instructions, Inverse-to-ternary regressed 4753.867 to 4975.375
  cycles (+4.66%) and Decaps regressed 39917.525 to 40137.050 (+0.55%). Inverse
  IPC fell from about 1.739 to 1.634: shifting work into every I16 butterfly
  increased multiply dependency and table pressure. P35 remains production.
- The old P6 reopen threshold was retired: P23/P24 already surpassed P6 and is
  the active production baseline.  Subsequent ToBytes gates compare directly
  against P24's 285 route instructions and 61 coefficient loads per top.

- Completed and statically rejected P39 without changing production. The exact
  184-instruction inverse9 body contains 19 Algorithm-10 products: six B3,
  four eta and nine terminal. All 288 physical terminal maps, all 64 known B3
  orientations and all 36 terminal constant vectors were machine-checked.
- The terminal table has the exact form
  `k(top,column,s) = -384 * lambda(top,column)^s (mod 3457)`. Only `s=0` is a
  column-independent full vector. Moving its `-384 = 9^-1` factor through I16
  exposes an input bound of 22473; the next legal pair can reach 44946 and
  therefore violates the frozen int16 I16 contract. A prior `b=1` reset makes
  the move safe but saves only one instruction/block (12/Inverse), below P39's
  required 36. Per the gate, no Slothy or Pi 5 run was performed. Evidence:
  `experiments/gt864-p39-inverse9-arithmetic-dag/`.
- P40 is the explicit inverse9-to-I16 phase-ABI gate. It may alter only this
  internal representation and tables/row ordering; it must first prove a net
  36-instruction saving with no extra memory pass before physical assembly.

### 2026-09-15

- Completed and statically rejected P38 without changing production. The
  current Full serializer executes 108 `SQRDMULH+MLS` normalization pairs per
  call. A local Apple-arm64 executable linked the exact production K1 Forward
  and ran 32,768 valid small plus 32,768 valid Keygen-f inputs. Every one of
  864 physical output coordinates has a constructive witness outside
  `(-3457,3457)`; observed unions were `[-16667,15974]` and
  `[-18539,18288]`. Therefore no coordinate can safely use Small under the
  unchanged representative contract.
- A normalization post-pass and normalization immediately before current
  Forward stores each remove 216 Full instructions but add the same 216
  instructions to Forward; the former also adds a memory pass and the latter
  changes the FR0 representation. Exact local B3 enumeration also shows the
  existing rho-product quotient cannot determine the three output quotients.
  P38's required 108 true deletions therefore fails with best net zero. Per the
  hard gate, no candidate assembly, Slothy or Pi 5 run was performed.
- P39 is now the inverse9 arithmetic-DAG search. It targets P37's remaining
  +147.075-cycle fused-Inverse gap without repeating rejected P27--P33 routing
  experiments. A candidate must delete at least one complete Algorithm-10
  multiplication from each of twelve inverse9 blocks before Slothy. Evidence:
  `experiments/gt864-p38-forward-full-tobytes-codag/`.

- Completed P37 without changing production. Exact committed P35 revision
  `88fb877e` and the selected SUPERCOP 20260831 AArch64 tree passed fresh
  manifest/KEM/KAT, six 100-case exact plus tampered cross-implementation
  processes, all instrumentation-equivalence gates and balanced cycle/event
  PMU. The Pi 5 remained unthrottled. GT beats Official by 1158.250 Keygen,
  1432.075 Encaps and 849.325 Decaps cycles despite retiring 4790/2607/7282
  more instructions.
- Component attribution now separates ToBytes modes. GT Small is about
  125--126.5 cycles faster than an Official call, but GT Full is 301--305
  cycles slower; each operation has exactly one Full call. Aggregate ToBytes
  gaps are therefore only +48/+180/+179 cycles. Decaps fused
  Inverse-to-ternary is the second positive boundary at +147.075 cycles.
  Forward, BaseInv, R0 BaseMul, BaseMulAdd, FromBytes and R-inverse BaseMul all
  meet or beat Official cycles at their matched boundaries.
- P38 is selected as a direct-Forward terminal-representative plus Full-ToBytes
  normalization co-DAG. All Full producers are direct Forward results. The
  static gate must eliminate at least 108 of the 216 Full-only
  `SQRDMULH+MLS` instructions rather than relocate them, preserve every other
  FR0 consumer contract, add no coefficient memory boundary/scratch/spill and
  target at least 150 cycles per Full call before Slothy or Pi 5. Evidence:
  `experiments/gt864-p37-official-profile/`.

- Completed P36 without changing production.  The remaining P35 reset protects
  main high column 8, whose old interval bound is 5278 versus P8's exact 5185
  limit.  Enumeration proves the current `(b,bhat)` pairs `(335,3175)` and
  `(120,1137)` are already minimax across signed-int16 congruent
  representatives, so a table-only correction cannot close the 93-value gap.
- Exact integer MILPs globally closed all 32 one-product NTT9 row-6 min/max
  bounds.  A 236-variable CT-NTT16 envelope was then audited.  A
  continuous-state trial reporting 5187 failed independent scalar replay and
  was rejected; restoring integer states left the 5186 feasibility query at a
  300-second timeout with neither primal nor infeasibility proof.  Because
  deletion requires a positive bound proof, P36 retains the reset and performs
  no Slothy/Pi run.  P37 is now the fresh profiler checkpoint.  Evidence:
  `experiments/gt864-p36-last-reset-decision/`.
- Completed and promoted P35.  Separate KEM-only main/tail helpers preserve the
  current P8 memory layout and stores, retain only the necessary main high
  column-8 reset, and leave the centered general Inverse on its original
  reset-complete helpers.  The tail's now-unused `mov`/`dup` constant setup is
  deleted too, correcting the P34 estimate from -72 to exactly -74 retired
  instructions per Decaps.  Local Cortex-A76 Slothy allocates without spills;
  fixed-allocation timing is main `667/166 -> 657/164` instructions/cycles and
  tail `603/150 -> 589/147`.
- The exact symbolic oracle passed 1,088 main/tail cases with identical store
  addresses, mod-3457 residues and P8 ternary outputs.  Physical arm64, 64-case
  KEM/tamper, identical 100-case KAT, identical 417216-byte malformed
  transcript, exhaustive 9,155-value raw conversion, and 1,024 complete
  inverse/alias/AAPCS/wipe cases pass.  Six balanced Pi 5 runs measure
  Inverse-to-ternary `4893.594 -> 4754.109` cycles (-139.485, -2.85%) and
  Decaps `40072.400 -> 39933.575` (-138.825, -0.346%); Keygen and Encaps retire
  zero changed instructions.  Evidence:
  `experiments/gt864-p35-kem-reset-pruning/`.  P36 is the next decision gate.
- Completed P34 without changing production.  A fresh six-process Pi 5 stage
  profile of the exact production library reproduces main I16 as the largest
  stage: inverse9/main-I16/tail/raw/complete are
  `1682.172/2117.821/341.453/430.156/4888.141` net cycles.  Exhaustive
  signed-int16 checking proves P8 raw-to-ternary's exact one-q-wrap domain is
  `[-5185,5185]`, with `±5186` as first failure witnesses.  Re-closing every
  P13 terminal interval shows only main high column 8 exceeds it (`5278`);
  all other main resets peak at 5143 and the tail peaks at 5028.  P35 is
  selected to retain that one reset while deleting five reset chains in each
  of six main calls and all six tail chains: -72 dependent vector arithmetic
  instructions per Decaps, with no new load, store, route, scratch boundary or
  register-pressure requirement.  The centered general Inverse remains on its
  reset-complete helpers.  Evidence:
  `experiments/gt864-p34-nonmaterializing-inverse-dag/`.
- Completed and rejected P33 without changing production.  The two-bank hybrid
  passes manifest, no-spill Slothy, arm64 object, 64-case KEM/tamper, identical
  100-case KAT, 4096 inverse/alias/AAPCS/wipe and identical 417216-byte
  malformed-transcript gates.  It reduces main static work `4002→3906`, and
  complete-Inverse PMU confirms -147 instructions/-6 branches.  Nevertheless,
  paired Pi 5 main-I16 regresses 132.110 cycles (0/546 wins, IQR
  `[+129.531,+133.062]`), complete Inverse regresses 95.297 cycles (0/366,
  `[+93.156,+102.328]`), and Decaps regresses 104.150 cycles (1/186,
  `[+89.687,+120.212]`).  Main-I16 IPC falls 1.9604→1.7978.  A fixed-register
  joint timing rescue emitted `t=0..2` but did not converge at `t=3`; unbounded
  scheduling is not justified.  P32/P33 therefore close the materialized
  terminal-sharing family.  Evidence:
  `experiments/gt864-p33-two-bank-terminal/`.
- Completed P32 without changing production.  Six exact 190-instruction I16
  prefixes overwrite their consumed P8 blocks; one column-major terminal loads
  each four-Q composite group once and consumes all six banks.  This removes
  320 repeated table loads, adds 96 Q stores plus 96 Q reloads, and reduces the
  complete-Inverse PMU count by exactly 173 instructions and one branch.  The
  root/scale/range/output ABI and 1792-byte scratch are unchanged; local Slothy
  allocation and four bounded terminal timing shapes are spill-free.
- Exact 64-case KEM/tamper, 100-case KAT, 256 direct Inverse, 4096
  alias/AAPCS/wipe and 417216-byte malformed-transcript gates pass.  On Pi 5,
  however, Inverse regresses 106.664 cycles with IQR
  `[+104.821,+107.996]`, and Decaps regresses 111.300 cycles with IQR
  `[+96.525,+124.237]`; both lose every paired sample.  IPC falls
  1.7044→1.6326 and the terminal text is 10932 bytes.  P32 is rejected;
  P33 may test a smaller reusable two-bank hybrid.  Evidence:
  `experiments/gt864-p32-batched-i16-terminal/`.
- Reconciled the persistent ledger for P28/P28-S/P29/P30/P31.  All remain
  rejected experimental evidence; none changed the frozen P13-C/P8 production
  inverse.

### 2026-09-14

- Completed P27 as a machine-only candidate without changing production.  All
  15 perfect matchings of the six current `(component,four-row-half)` P8
  records were exhausted.  The unique best basis pairs blocks `(0,2)`, `(1,4)`
  and `(3,5)`; each paired I16 region consumes and overwrites its own two dead
  16-Q blocks.  Dense tail compaction uses 12 Q records, so the complete
  intermediate has exactly 108 Q records inside the existing 1792-byte
  scratch, with four old tail-padding records unused.
- The exact 864-tag consumer route loads and normalizes every source Q once,
  needs at most four live sources in consecutive `v0-v3`, and emits 108 natural
  full-Q stores.  Its source arity is 48 TBL2-equivalent, 44 TBL3-equivalent
  and 16 TBL4 records.  Roots, R0 scale and the
  `2497→2617→21397→4577→ternary` range chain are unchanged.  Terminal
  materialization falls from 1728 instructions to a 216-instruction budget;
  after conservative GPR-parking and route/mask charges the static model still
  predicts at least 1314 fewer instructions.  P28 now owns real symbolic
  allocation, correctness and Pi 5 timing.  Evidence:
  `experiments/gt864-p27-consumer-i16-lane-basis/`.

- Completed P26 without changing production.  Exact loop/call expansion gives
  4583 source instructions for selected Official Inverse+Crepmod3 and 8324 for
  GT fused Inverse-to-ternary.  The matched profiler shells contribute 22/21,
  reproducing P25's exact 4605→8345 and +3740-instruction deficit.
- GT already has 151 fewer `mul/sqrdmulh/mls` instructions.  The dominant
  excess is +864 lane extracts, +788 loads, +1159 stores and +438 scalar
  setup/address/control instructions.  Of GT's 1044 loads, 706 are constants,
  including 448 composite-terminal loads repeated across six main I16 calls
  and the tail.
- P21 proves scatter-only removal cannot close the 280.675-cycle gap; P11's
  store-then-route and P22's copy-only DAG remain rejected.  P27 instead
  searches the inverse9→I16 lane/bank basis for a naturally vector-consumable
  raw-to-ternary ABI before assembly.  Evidence:
  `experiments/gt864-p26-inverse-deficit-audit/`.

### 2026-09-13

- Completed P25 without changing production.  Exact P24 revision
  `d76a8289a8652e156665aff78bee6946183b2923` beats the selected SUPERCOP
  20260831 Official by 1167.750/1440.450/694.525 clean cycles for
  Keygen/Encaps/Decaps across 252 observations each.  Cross-implementation
  exact/tampered and instrumentation-equivalence gates pass; Pi 5 remained
  unthrottled.  The selected Official tree hash remains
  `40a284439eb5fe8dfef77f1a995ebc8dd16182835048d64e959fbcb6e3df0b59`;
  independent upstream-latest provenance is still unverified.
- The largest positive matched boundary is Decaps Inverse-to-ternary at
  +280.675 cycles and +3740 instructions.  Aggregate ToBytes follows at
  +47.000/+174.350/+178.000 cycles for Keygen/Encaps/Decaps.  P26 first aligns
  the Official and GT Inverse work to find an exact new removable DAG; ToBytes
  remains second.  Evidence: `experiments/gt864-p25-official-profile/`.

- Completed and promoted P24 from exact commit archives: P18 baseline
  `32481d08aae9135803379499c68c12b20a3856d4` versus P24 candidate
  `4b7a3b83085045694f8861cea61660d3345816ac`.  Full/Small improve by
  15.906/39.660 cycles and exactly 194 instructions plus six reads per call.
  Across 252 observations, complete Keygen/Encaps/Decaps improve by paired
  medians 147.000/67.325/62.625 cycles and exactly 582/388/388 instructions.
  Manifest, active-symbol/object, 513+513 exact-byte, guard, input-immutability,
  AAPCS/SIMD-wipe, KAT and malformed-rejection gates pass unthrottled on Pi 5.
  P25 is the selected-Official profiler checkpoint.  Evidence:
  `experiments/gt864-p24-p23-production/`.

- Completed P23 without changing production.  The historical P6-D3 threshold
  was rebased because P18 had already surpassed it.  Against current P18, an
  exact globally interned routing graph has 54 sources, 24 rotations and 200
  transpose nodes per top.  A constructive 26-register schedule executes all
  224 routing nodes once and reloads seven evicted sources, reducing complete
  Full/Small calls by exactly 194 instructions and six Q loads with no
  coefficient scratch or vector spill.
- The one-output Slothy control is rejected: it lost 53.813/10.648 Full/Small
  cycles because its fine windows serialized normalization and packing.  The
  retained 18-window, three-output schedule restores cross-output ILP and
  improves P18 by 16.375/46.586 cycles.  Frozen integration improves
  Keygen/Encaps/Decaps by 131.375/81.125/64.500 cycles with exact instruction
  deltas -582/-388/-388.  KAT, malformed transcript, exact bytes, canaries and
  no-spill object gates pass.  P24 is the separate production promotion gate.
  Evidence: `experiments/gt864-p23-tobytes-global-dag/`.

### 2026-09-12

- Completed P22 without changing production.  Two-output SSA butterflies delete
  32 `ORR` copies per main-I16 call, reducing the region from 667 to 635
  instructions.  Exact signed-int16/store-address oracles, 4096 native
  exact/alias/AAPCS/wipe cases, KEM/KAT/malformed tests and no-spill Slothy pass;
  the Cortex-A76 model improves from 166 to 158 cycles/call.
- The scheduled kernel improves the direct six-call boundary by 37.203 paired-
  median cycles and exactly 192 instructions, but this does not cross the real
  consumer boundary: complete Inverse-to-ternary regresses by 5.610 cycles in
  365/366 pairs and Decaps by 21.775 cycles in 173/186 pairs.  The RA-only
  control is worse (+186.407 Inverse, +199.300 Decaps).  P22 is rejected and
  P23 returns to the statically hard-gated ToBytes coordinate-to-wire search.
  Evidence: `experiments/gt864-p22-main-i16-ssa/`.

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
