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
| P6 | Active | Consumer-oriented zero-scratch ToBytes route + normalization + packing | Remove at least one P6-A frontier lifetime; no extra coefficient loads, no lane ST3, no spill, direct full-vector final stores, complete full/small ToBytes and KEM improvement |
| P6-C | Done | Joint packed-A producer + restore-A/B pack + three-pair merge symbolic DAG | Exact model and physical assembly oracle passed; peaks are 26/32; both Slothy allocations are optimal without spill; all physical TBL2/TBL3 groups are consecutive |
| P6-D | Done | Complete all-nine-row full/small zero-scratch ToBytes kernels | 12 Slothy regions optimal/no-spill; exact 1,296 bytes; 108 coefficient Q loads; zero coefficient scratch; 80 Q + 2 D stores; complete full/small oracle passed |
| P6-E | Next | Same-boundary Pi 5 timing of P6-D3 versus frozen 432-byte-scratch ToBytes | Full and small cycles/instructions/IPC/load/store; specialize small conditional-add-only DAG if shared full normalization loses; only then consider full-KEM integration |

## Fixed facts and non-tasks

- GT already uses three-chain hierarchical BaseInv batch inversion.
- GT already has the BaseMul R^-1 plus matching inverse scale ABI; current
  BaseMul R^-1 is essentially tied with Official.
- Small ToBytes intentionally omits the 108 Barrett reductions only for
  producers proved to lie in `(-q,q)`; full ToBytes keeps normalization.
- Secret/scratch clearing is a policy requirement and is not deleted merely to
  match Official timing.
- Forward is currently faster than the selected Official component and is not
  on this immediate critical path.

## Change log

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
  The 16,752-byte arm64 text performs 108 coefficient Q loads, uses a 176-byte
  public save frame and zero coefficient scratch, keeps TBL groups consecutive,
  and uses neither lane ST3 nor x18.  The executable oracle passed 4,107 full
  signed-int16 cases and 4,096 small-range cases with output canaries.
- Production remains unchanged.  D3-small currently aliases the full Barrett
  DAG, so P6-E must time full and small separately against the frozen scratch
  implementation; a conditional-add-only small specialization is the fallback
  before any production promotion.
