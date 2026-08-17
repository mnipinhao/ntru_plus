# Official Main vs fastest qualified GT32 candidates (2026-08-10)

## Scope

- Official: vendored NTRU+768 AVX2 Official Main in the same benchmark binaries.
- GT32 Decap: production-promoted Q24 GT-unpack, recovered-r GT-pack, and lazy10788 GT-pack; B3/I1/T9 arithmetic remains frozen.
- GT32 Encap: Q24 GT-unpack plus the H1 high-range private-SoA Q24 GT-pack.
- GT32 Keygen: current `gt32-prod` A+B+C+D2 production-shaped candidate using the intrinsic P-SoA BaseInv path.
- Normal and reversed link placements were measured separately.
- TSC numbers are invariant-TSC ticks per operation, not literal core cycles. PMU `cpu_core/cycles` is reported separately.

## Full-operation results

Delta is GT32 minus Official; negative is a GT32 win.

| Operation | Placement | Official TSC | GT32 TSC | Paired TSC delta | Result |
|---|---:|---:|---:|---:|---|
| Decap | Normal | 12008.712 | 12104.286 | +88.168 (+0.734%) | GT32 loses |
| Decap | Reversed | 12050.997 | 12152.996 | +92.043 (+0.764%) | GT32 loses |
| Encap | Normal | 17468.698 | 17523.574 | +70.389 (+0.403%) | GT32 loses |
| Encap | Reversed | 17494.832 | 17535.588 | +57.166 (+0.327%) | GT32 loses |
| Keygen G1 | Normal | 13298.639 | 13313.208 | -14.115 (-0.106%) | Statistical tie |
| Keygen G1 | Reversed | 13226.166 | 13356.377 | +125.527 (+0.949%) | GT32 loses |

## PMU core-cycle results

| Operation | Placement | Official cycles | GT32 cycles | Paired/region delta | Interpretation |
|---|---:|---:|---:|---:|---|
| Decap | Normal | 19366.408 | 19539.730 | +197.518 (+1.020%) | GT32 loses |
| Decap | Reversed | 19459.477 | 19809.078 | +338.281 (+1.738%) | GT32 loses |
| Encap | Normal | 27864.214 | 28120.137 | +255.923 (+0.918%) | GT32 loses |
| Encap | Reversed | 27944.499 | 28429.733 | +485.234 (+1.736%) | GT32 loses |
| Keygen G1 | Normal | 30990.423 | 30979.651 | -34.754 (-0.112%) | CI crosses zero |
| Keygen G1 | Reversed | 30992.937 | 31202.362 | +265.096 (+0.855%) | Stable GT32 loss |

For paired distributions, the median paired delta need not equal the subtraction of the two independently reported medians.

## Where GT32 wins and loses

### Decap

Fresh cumulative PMU attribution (incremental phase deltas):

| Phase | Normal cycles | Reversed cycles | Assessment |
|---|---:|---:|---|
| C1 Decode / GT-unpack | +51.087 | +49.057 | Stable loss; GT boundary still costs more core work than Official decode |
| C2 first BM + inverse + crepmod3 | +56.862 | +65.796 | Stable loss; fewer instructions do not shorten the consumer critical path |
| C3 Forward(m) + sub + general BM + recovered-r pack | -96.688 | -16.418 | GT win, but placement-sensitive magnitude |
| C4 hash_g + SOTP decode + hash_h | +24.411 | -156.674 | Strong placement/runtime interaction; not a stable intrinsic win/loss |
| C5 CBD + NTT + check pack + verify | -6.379 | +12.008 | Approximately parity |
| C6 select + cleanup | +29.584 | -16.743 | Small and placement-sensitive |

GT32 retires about 1527 fewer instructions per full decap, yet uses 198--338 more core cycles. The remaining loss is therefore delivery/critical-path efficiency, especially C1/C2, rather than excess instruction count.

### Encap

Fresh paired TSC phase deltas:

| Phase | Normal TSC | Reversed TSC | Assessment |
|---|---:|---:|---|
| E1 input decode/CBD/SOTP | +11.961 | +11.901 | Small stable loss |
| E2 two Forward NTTs | -120.109 | -120.750 | Largest stable GT32 win |
| E3 general BaseMul | -11.855 | -10.863 | Small stable GT32 win |
| E4a add(m) | -0.655 | -0.120 | Parity |
| E4b serialize r-hat | +22.155 | +26.304 | Stable loss |
| E4c serialize ciphertext (H1) | +20.986 | +26.142 | Stable residual loss after H1 improvement |
| E5 hash/glue | +16.746 | +15.521 | Small stable loss in this binary |

PMU corroborates the structural picture: E2 saves about 190--244 core cycles and E3 saves 29--49, while r-hat serialization costs about 82--102 extra core cycles and ciphertext serialization costs about 19--21. The complete caller still loses 256--485 core cycles because the small boundary debts and caller-level delivery effects outweigh the Forward/BaseMul gains.

### Keygen

G1 is the production-shaped single-attempt candidate. It is not stable across placement:

- Normal: -34.754 core cycles, 95% bootstrap CI [-112.769, +171.340]; statistical tie.
- Reversed: +265.096 core cycles, 95% CI [+132.229, +330.981]; clear GT32 loss.
- GT32 retires 2394--2519 fewer instructions and 407--426 fewer stores.
- GT32 performs 908--930 more loads, consistently.

Fresh cumulative checkpoints show that the two-attempt arithmetic preparation can win, but the later consumer/serialization/hash delivery gives the saving back. The main stable regression appears by C4 (second BM and two secret-key packs): cumulative +66.938 normal and +122.939 reversed core cycles. This is the previously identified integration tax: qualified A+B+C+D2 components do not compose into a placement-stable production keygen.

## Decision

- Official Main remains the production winner/default for all three KEM operations.
- GT32 Forward NTT is a clear kernel win, and GT32 general BaseMul is at least parity/slightly faster in Encap.
- GT-native Q24 boundaries substantially reduce earlier layout debt, but do not yet make full Decap or Encap faster than Official in this fresh run.
- Keygen remains unpromoted because its result changes with link placement and the reversed placement has a statistically clear regression.

## Raw fresh artifacts

- `tile4-official-vs-fastest-gt32-decap-tsc-20260810.json`
- `tile4-official-vs-fastest-gt32-decap-pmu-20260810.json`
- `tile4-official-vs-fastest-gt32-decap-attribution-20260810.json`
- `tile4-official-vs-fastest-gt32-encap-tsc-20260810.json`
- `tile4-official-vs-fastest-gt32-encap-pmu-20260810.json`
- `tile4-official-vs-fastest-gt32-keygen-pmu-20260810.json`
- `tile4-official-vs-fastest-gt32-keygen-cumulative-pmu-20260810.json`
