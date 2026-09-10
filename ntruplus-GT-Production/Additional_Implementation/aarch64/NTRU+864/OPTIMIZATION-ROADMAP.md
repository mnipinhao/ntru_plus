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
| P3 | Active | Stage-fused Decaps inverse; P3-A constant-resident `center864` promoted | P3-B must preserve BaseMul R^-1 to natural-R0 contract while fusing centering into I16/tail producer stores and removing the separate 1,728-byte pass |
| P4 | Next | Fuse FromBytes legality accumulation into decode/routing | No second 1,728-byte coefficient scan; exact canonical rejection for Encaps and all three Decaps inputs |
| P5 | Next | Reuse KEM temporaries following proven lifetimes | Keygen one `h`; Encaps reuse `ct` for serialized `r`; Decaps reduce seven polynomial temporaries after alias audit; preserve cleanup and failure semantics |
| P6 | Deferred | True zero-scratch ToBytes route + normalization + packing | No extra coefficient loads, no lane ST3, no spill, direct full-vector final stores, complete full/small ToBytes and KEM improvement |

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
