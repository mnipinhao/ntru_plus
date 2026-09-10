# BaseInv / ToBytes next model — 2026-09-10

Initial hypothesis record. For the subsequent consumer proof, fused numerator,
Slothy allocation and physical Mac test results, see `RESULTS.md`.

Research only. No production change, new allocated assembly, or new Pi timing.
Official source is the captured SUPERCOP 20260831 aarch64 implementation in
`../baseinv-fixed-scale/build/pi-20260910/official-source`; upstream latest status is unverified.

## BaseInv

The finish already shares `den * QINV` across three numerator products. This is
not an unimplemented optimization. The fixed-scale experimental baseline has
114 numerator instructions and 57 finish instructions per eight-leaf tile;
production still has the older 124 / 59 implementation.

### Scale correction

Input coefficients are R0. Numerator converts them to R1; numerators and
denominators stay R1 through the Montgomery arithmetic and batch inversion.
Finish converts the inverse denominator from R1 to R0 once per leaf, then
`REDC(numerator_R1 * inverse_denominator_R0)` produces R0 coefficients.
This amortizes one correction over three components. Deleting it changes the
output scale. Moving it to recovery is not a saving unless recovery actually
absorbs it into an existing operation. A future fused numerator may choose a
different scale ledger, but cannot inherit the existing range proof unchanged.

### Final normalization

GT finishes with six centering instructions per component, 18 per tile and
648 per complete BaseInv. Official finish does not perform this centering.
The fixed-scale proof uses a conservative raw REDC bound of 1972, then centers
to 1728. Removing centering is a credible KEM-only candidate, not yet approved:
all active consumers must accept the larger representatives. Required gate:
trace both Keygen inverse outputs into D1, prove its early/final int32 sums and
output reduction with the enlarged input bound, then check Keygen bytes,
failure paths, aliasing, and cleanup. Modular equivalence alone is insufficient.

### Numerator organization is a larger structural difference

GT readable numerator has 12 variable Montgomery multiplications after its
three input conversions: 3 + 3 + 2 for the numerators, and 4 for denominator.
Official `poly_baseinv_1` fuses wide products/additions before narrowing: seven
vector REDC results per tile, processing two tiles per loop. Its zeta signs
and scales must be included before porting this topology to FR0.
This is not a claim that five reductions can simply be deleted from GT.

GT wrapper calls numerator 36 times and finish 36 times; constants are loaded
inside those cores. Public register preservation happens once, not 72 times.
Two-tile kernels and persistent constants can reduce call/setup overhead, but
require a register-budget check. The field inverse also uses a generic binary
exponentiation loop in the generator; Official uses an addition chain. Treat
that as a separate arithmetic candidate, not a scale-correction improvement.

Recommended order: consumer closure for no-centering finish; then FR0 fused-wide
numerator with an explicit scale/range ledger; then allocation and two-tile
organization. Preserve the fixed-scale candidate as comparator.

## ToBytes: stream the third pair into merge

For one top and one row, a pair produces 24 bytes. The exact output map is

    output[9*k + 3*p + c] = pair[p][3*k + c]
    k=0..7, p=0..2, c=0..2

One pair owns eight disjoint three-byte runs, not a contiguous final region.
Simply replacing its scratch ST3 with a final contiguous store is incorrect.
Fusing three complete pair states would also exceed a naive 32-vector budget.

Bounded candidate: retain pair 0 and 1 scratch; process pair 2 last and feed its
three packed byte-component vectors directly into the existing row merge.
For pair 2, TBL indices change from `3*k+c` to `16*c+k`; low eight lanes of each
component vector are meaningful. Other pairs retain their existing indices.
`check.py` validates all 1296 output byte tags with unique ownership.

Per complete call, this removes 18 scratch ST3 instructions and 36 scratch
loads, avoiding 432 bytes written and 432 bytes read. Scratch allocation can
drop from 656 to 432 bytes. It does NOT remove the merge's 270 TBL, 180 ORR,
270 index loads, or 1296 final output bytes. Pair 2 uses TBL with three source
registers rather than two; consecutive-register constraints and model latency
must be costed. Wipe and pointer setup also change.

This is a mapping proof, not a no-spill proof. Required next gate: joint
pair-2/row-merge symbolic DAG, consume rows early, count peak live vectors and
tuple constraints, then physical allocation. Fail if extra coefficient loads,
spills, or reconstruction copies erase the avoided scratch traffic. Benchmark
complete full/small ToBytes, not just merge. The measured ~380-cycle merge
cannot be subtracted from the current total: most of its work remains.
