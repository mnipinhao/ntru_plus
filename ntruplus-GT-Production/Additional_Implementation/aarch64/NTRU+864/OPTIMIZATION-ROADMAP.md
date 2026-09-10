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
| P2 | Active | BaseInv two-tile kernel with q/qinv/R constants resident and 18 numerator calls; evaluate SIMD chain-end failure aggregation | Same output and cleanup policy, no secret-dependent branch/address, fewer instructions and BaseInv cycles |
| P3 | Next | Monolithic/stage-fused Decaps inverse | Preserve BaseMul R^-1 to natural-R0 contract; remove avoidable stage calls/scratch/centering only after range closure; improve complete Decaps |
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
