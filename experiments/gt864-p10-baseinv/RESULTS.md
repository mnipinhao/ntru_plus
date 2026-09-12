# P10 — direct-FR0 BaseInv result

## Outcome

P10-A is promoted to production after passing its mathematical, range,
physical-assembly, constant-time, correctness and Pi 5 performance gates.  The
user explicitly approved the successful BaseInv raw-representative contract
change from `|x| <= 1972` to `|x| <= 2550` on 2026-09-12.  The output remains
FR0 modulo 3457 and the complete Keygen consumer chain is machine-closed.

The selected Official source is the captured SUPERCOP tree at
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`; this experiment
does not claim that the capture was independently verified as the latest
upstream revision.

## What changed

The P9 BaseInv converts every input tile from R0 to R1 before constructing the
cubic cofactor.  P10 instead constructs the cofactor directly from R0 inputs:

```text
u   = REDC(b*c)
w   = REDC(c*c)
n0  = REDC(a*a - u*zR)
n1  = REDC(w*zR - a*b)
n2  = REDC(b*b - a*c)
h   = REDC(n2*b + n1*c)
den = REDC(h*zR + n0*a)
```

The cofactor has scale R^-1 and `den` has scale R^-2.  Twelve determinants per
batch chain give final prefix scale `R^(1-3*12) = R^-35 = R^1`, because R has
order 36 modulo q.  A single Algorithm-10 multiplication by R^-2 after the
three-way inversion changes the running inverse to scale R^-1.  Existing
backward recovery then produces every denominator inverse at R^2, and the
three final REDCs produce public R0 coefficients directly.

This removes all per-tile input conversions and the old per-tile finish scale
correction.  The public wrapper hoists q and Montgomery qi into `v30/v31` for
the repeated numerator and finish calls.  The middle prefix/inverse/recover
cores are allowed to clobber volatile vectors, so the wrapper deliberately
reloads the pair before the finish loop.

## Exact range closure

The production-only contract is the already approved KEM definition: BaseInv
is called only on K1 Forward outputs, not arbitrary generic polynomial inputs.
The largest producer bound is 28765.  The machine proof obtains:

| Node | absolute bound |
|---|---:|
| `u`, `w` | 14355 |
| `n0`, `n1` | 14733 |
| `n2` | 26980 |
| `h` | 20038 |
| determinant | 8724 |
| final prefix after step 11 | 1995 |
| globally corrected inverse | 1741 |
| recovered denominator inverse | 1994 |
| raw FR0 finish | 2550 |

All narrowed values fit signed int16.  Every wide expression plus its maximum
Montgomery correction fits signed int32; the tightest remaining margin is
379,354,222.  The downstream D1 BaseMul closure uses the 2550 bound and the
other Forward operand bound 28765.  Its two early REDCs remain within
3967/2848, all three final wide accumulators fit int32, and an exhaustive
Barrett-bucket proof gives output `[-1861,1861]`, still strictly inside
`(-q,q)` for small ToBytes.

The first Pi component run exposed a test-contract bug rather than an assembly
bug: the inherited generic harness generated all signed-int16 values.  Its
first failing sample contained `(-32389,32092,32755)`, outside the K1 bound.
The corrected harness covers the proved cube including +/-28765 and +/-26930,
all 288 injected zero-leaf positions, exact aliasing, canaries, AAPCS and
scratch erasure.  It is not a relaxation of the P10 contract.

## Slothy and physical assembly

The canonical local checkout was `/Users/chenpinhao/slothy`, imported through
the authorized virtual environment.  Each region reached a final OPTIMAL
Cortex-A76 schedule with zero spill:

| Repeated region | P9 model | P10 model | Static instructions |
|---|---:|---:|---:|
| numerator pair, called 18 times | 163 cycles | 123 cycles | 132 |
| finish tile, called 36 times | 41 cycles | 31 cycles | 26 |
| inverse3, called once | 283 cycles | 293 cycles | 164 |
| dynamic model total | 4693 cycles | 3623 cycles | — |

The ten-cycle inverse3 model regression is the one global R^-2 correction; it
is dominated by the repeated numerator/finish savings.  The generic log parser
is not used as proof because it misclassifies intermediate `INFEASIBLE` probes
from Slothy's binary search as final failures.  `slothy-result.json` records the
final OPTIMAL entries, exact imported module paths, hashes and zero-spill
status.

Apple-arm64 physical differential testing passed 65,536 numerator lanes,
65,536 finish lanes and 32,768 inverse3 lanes, including exact in-place alias
and guard edges.

## Pi 5 results

All numbers are medians from six balanced processes pinned to core 3.  The Pi
reported no throttling.  The table below is the final run from the actual
promoted production source.  Full raw observations are in
`production-pi-evidence/*.csv` and the aggregate is
`production-pi-results.json`; the earlier isolated-candidate run remains in
`pi-evidence` and `pi-results.json`.

| Boundary | P9 | P10 | delta |
|---|---:|---:|---:|
| BaseInv success, one call | 5197.422 | 4139.985 | -1057.438 |
| BaseInv failure, one call | 3325.875 | 2628.610 | -697.266 |
| complete Keygen | 45795.250 | 43670.500 | -2124.750 |

The selected Official versus P10 measurement was:

| Boundary | Official | P10 | P10 - Official |
|---|---:|---:|---:|
| BaseInv, two Keygen calls | 8366.875 | 8188.250 | -178.625 |
| complete Keygen | 44309.125 | 43651.625 | -657.500 |
| complete Encaps | 46407.750 | 45356.375 | -1051.375 |
| complete Decaps | 40768.450 | 40899.800 | +131.350 |

Encaps and Decaps do not call BaseInv.  Their P9/P10 deltas were -0.950 and
-10.300 cycles with identical instruction/branch counts, so they are treated
as measurement noise, not a P10 effect.

Correctness evidence: identical 100-case KAT SHA-256
`0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`;
identical 417216-byte malformed transcript SHA-256
`2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`;
and 808 BaseInv component cases for both P9 and P10.

## Decision and next work

P10-A is now the production BaseInv.  Promotion copied the three allocated
leaves and wrapper constant hoists, refreshed the manifest, and passed the
production KAT/component/malformed and paired PMU checks.  P10-B is dropped
because the approved, consumer-closed P10-A contract makes its extra
normalization unnecessary.

After resolving P10, the next measured gap is Decaps.  Compare consistent
boundaries: Official `Inverse + Crepmod3` is 4620.0 cycles while GT's fused
`Inverse_to_ternary` is 5436.975, leaving about 817 cycles.  P11 therefore
targets a smaller joint terminal-Inverse-to-ternary DAG; it must not reopen the
already rejected P6 scratch-only or P3-B half-vector scatter directions.
