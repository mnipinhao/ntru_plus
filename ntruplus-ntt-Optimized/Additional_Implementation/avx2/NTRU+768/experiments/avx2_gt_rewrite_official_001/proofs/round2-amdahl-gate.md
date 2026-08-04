# Round 2 cycle decomposition and Amdahl gate

The checkpoint caller baseline on CPU 1 is 91,088.810 invariant-TSC cycles
for Official and 186,861.520 for GT.  Stage measurements use the same release
objects, two warmups, twenty forward/reverse samples, and one million calls per
sample.  The deterministic counted KEM triplet executes six forwards, five
BM-A operations (four normal and one scale entry), two base inversions, one
inverse, seven encodes, and four decodes.

| Stage | Median cycles | Calls/triplet | Weighted cycles |
|---|---:|---:|---:|
| forward frontend | 2,779.331 | 6 | 16,675.986 |
| forward B1 including GT-layout store | 4,513.877 | 6 | 27,083.262 |
| BM-A | 3,224.674 | 5 | 16,123.370 |
| baseinv | 820.905 | 2 | 1,641.810 |
| inverse B1 including GT-layout load | 9,695.076 | 1 | 9,695.076 |
| inverse tail | 5,356.300 | 1 | 5,356.300 |
| tobytes | 1,127.040 | 7 | 7,889.280 |
| frombytes | 3,319.791 | 4 | 13,279.164 |

`gt_poly_ntt_canonical` has no standalone canonicalization pass.  Its
reductions are embedded in forward B1, so the decomposition assigns zero to a
separate canonical pass and does not create an unsafe natural-bound variant.

The caller-weighted assembly target is therefore:

```text
C32 = 6 * forward_B1 + inverse_B1
    = 36,778.338 cycles
```

The frozen Round 2 gate requires savings of 95,420 cycles for parity and
99,974 cycles for promotion.  With the freshly measured baseline, reaching
the explicit 92,906/86,530 thresholds would require 93,955.520/100,331.520
cycles respectively.  Even an impossible zero-cycle B1 implementation saves
only 36,778.338 cycles and leaves GT at 150,083.182 cycles.  This zero-cycle
floor is more optimistic than every load/store, arithmetic-uop, or dependency
floor, so a more detailed nonzero floor cannot change the decision.

The PMU run confirms warm-L1 behavior: forward B1 and inverse B1 have about
0.003 and 0.006 L1 load misses per call.  They retire about 21,297 and 32,770
uop slots per call and are primarily backend-bound, but eliminating all of
that work still cannot cross the theoretical gate.

Decision: `stop-amdahl-theoretical-gate-failed`.  No GT assembly symbols,
selectors, execution-order streams, or Official changes are introduced in
Round 2.  B1, BM-A, canonical integration, and `BACKEND=official` remain
frozen.
