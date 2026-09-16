# P46 — Full normalization DAG

P46 is complete and **promoted for Full ToBytes only**.  The exact Pi 5
boundary and every full-KEM caller improve.  The Cortex-A76 Slothy proxy moves
in the opposite direction; the user explicitly approved that recorded
broader-full-path tradeoff on 2026-09-16.  Small remains the exact P24 kernel.

## Candidate

P24 canonicalizes each Barrett residual with three instructions:

```asm
sshr mask.8h, x.8h, #15
and  mask.16b, mask.16b, q.16b
add  x.8h, x.8h, mask.8h
```

P46 uses the sign bit as the exact multiplier of `q`:

```asm
ushr bit.8h, x.8h, #15
mla  x.8h, bit.8h, q.8h
```

For a signed 16-bit lane, `ushr #15` is exactly zero or one.  After the
unchanged Algorithm-10 `b=1` reduction the residual is in `[-3291,3291]`, so
adding `q=3457` exactly when the sign bit is one produces the same canonical
value in `[0,3456]`.  Full has 108 such lanes groups per call, hence the
candidate retires exactly 108 fewer instructions.  Small is unchanged.

## Correctness and contract gates

- Exhaustive identity over all 65,536 signed-int16 inputs passes.
- The inherited P23 route/pack oracle passes 516 exact byte-map cases.
- The generated physical region passes symbolic-use checking and AArch64
  assembly; all 18 fixed-allocation Slothy windows are optimal and spill-free.
- The only recorded contract change is the equivalent normalization method.
  Public ABI, FR0 input, exact output bytes, memory accesses, bounds and
  constant-time behavior are unchanged.
- Pi 5 KAT and malformed-ciphertext transcripts pass; the linked objects have
  no Q-register stack traffic.

## Slothy result

The fixed-allocation Cortex-A76 model reports:

| Region | P24 | P46 | Delta |
|---|---:|---:|---:|
| Full top, modeled cycles | 1495 | 1562 | +67 |

This is the same pipeline-pressure warning previously seen for P42: fewer
source instructions do not imply a lower multiply-pipeline schedule cost.
The parser's intermediate `INFEASIBLE` messages are binary-search probes; the
final JSON records 18/18 optimal windows, instruction-multiset preservation
and no spill.

## Pi 5 result

Measurements use `/home/pi/supercop-20260831` on `pi@100.99.191.9`.

| Boundary | P24 cycles | P46 cycles | Paired delta | Instructions delta |
|---|---:|---:|---:|---:|
| Full ToBytes | 1395.125 | 1386.762 | -8.364 | -108 |
| Small control | 985.117 | 985.031 | -0.086 | 0 |
| Keygen | 43124.125 | 43107.875 | -13.500 | -108 |
| Encaps | 44993.825 | 44988.025 | -13.650 | -108 |
| Decaps | 39922.250 | 39915.900 | -5.450 | -108 |

All three full-KEM operation branch counts are unchanged.  The board stayed
unthrottled and ended at 60.4 C.

## Decision

P46 passes algebra, range, allocation, assembly, exact bytes, KAT, malformed
input, object audit and target-silicon performance.  The automatic scorer does
not encode a worse-cycle override, so `candidate-score.yml` and
`promotion-report.yml` explicitly preserve both the `1562 > 1495` proxy result
and the user's approval.  Production contains the exact Pi-tested scheduled
Full source under the existing public symbol; no source instruction or timing
number was altered to manufacture parity.
