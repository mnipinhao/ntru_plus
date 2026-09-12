# P9 — input-once ToBytes routing (promoted)

P9 passes and replaces both production ToBytes entries.  The result is not a
continuation of P6's zero-scratch row materialization.  It reopens the older
P3B6 input-once composed map because P3B6 was rejected by an obsolete absolute
1250-cycle threshold, not by correctness, allocation or a current comparison.

## Exact data flow

For each 432-coefficient top branch, the core loads every one of the 54 FR0 Q
vectors once.  A fixed greedy order has at most sixteen incomplete output
vectors live.  Each input lane is inserted into its exact final eight-
coefficient group; as soon as all eight lanes arrive, that vector is
normalized, packed into twelve bytes and written to its final wire address.
There is no complete routed-row materialization and no coefficient scratch.

The composed `FR0 -> Official shuffle2 -> wire` permutation is a bijection with
SHA-256
`087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270`.
The second top is the same map plus 432 coefficients / 648 bytes.

P9-F accepts arbitrary signed int16 input.  Every eight-coefficient vector uses
the usual `SQRDMULH(x,9); MLS(...,3457)` Barrett step and then negative
correction.  P9-S is a different core, selected only at KEM sites whose
producer closure proves `-3457 < x < 3457`; it contains no Barrett arithmetic
and only conditionally adds q through `CMLT; AND; ADD`.

Both public wrappers preserve `d8-d15`, clear all `v0-v31`, and use no secret-
dependent branch or address.  Input/output remain disjoint at every KEM call.

## Static and target gates

The conservative pre-target estimates were 2812 full and 2596 small dynamic
path instructions, respectively 1249 and 1465 below P6-D3's 4061.  Therefore
both exceed P6-E's required `-829` reopening threshold before scheduling.

GCC 14.2 target audit gives:

| Path | top body | complete dynamic path | delta vs P6-D3 | Barrett/top | spill |
|---|---:|---:|---:|---:|---:|
| P9-F | 1378 | 2809 | -1252 | 54 | none |
| P9-S | 1277 | 2607 | -1454 | 0 | none |

The first two-instruction small correction attempt made GCC create a 32-byte
TBL consecutive-register stack temporary and was rejected before timing.  The
promoted three-instruction correction restores a no-spill allocation while
still deleting all 108 complete-call Barrett pairs.  This is why the promoted
P9-S does not use the superficially shorter lowering.

## Pi 5 same-boundary result

Host `pi@100.99.191.9`, Cortex-A76, GCC 14.2, CPU 3, `ondemand`, 74 samples per
implementation/mode, exact 513-case differential check before every process,
temperature 56.5–62.0 C, `throttled=0x0`.  Workspace:
`/home/pi/supercop-20260831/bench/pinhao/gt864-p9-20260912`.

| Mode | P5 cycles | P9 cycles | delta | instruction delta | read delta | write delta |
|---|---:|---:|---:|---:|---:|---:|
| full | 1766.672 | 1518.164 | -248.508 | -422 | -424 | +30.929 |
| small | 1370.425 | 1173.769 | -196.656 | -389 | -424 | +30.910 |

The `-424` read-event result comfortably passes P6-E's `-101` structural
target.  P9 trades some wider/final store events for eliminating the 432-byte
scratch traffic and repeated route-table reads; cycles, instructions and
branches all improve in both modes.

## Complete KEM result versus frozen P8 production

Six balanced AB/BA processes per isolated substitution and the combined
candidate; each process checks 100 exact cross-version key/ciphertext cases and
100 tampered cases first.

| Candidate | Keygen delta | Encaps delta | Decaps delta |
|---|---:|---:|---:|
| full only | -248.875 | -234.975 | -207.675 |
| small only | -378.875 | -210.975 | -231.000 |
| full + small | **-619.875** | **-415.800** | **-435.925** |

The combined instruction deltas are exactly -1200/-811/-811 and branch deltas
are -157/-107/-107 for Keygen/Encaps/Decaps.  The call ledger closes: Keygen
uses one full plus two small calls; Encaps and Decaps each use one of each.

Mac and Pi complete KEM tests pass.  The 100-case KAT remains
`0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`;
the malformed transcript remains
`2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.

Production contains the exact tested generated cores and public wrappers.
The promoted Pi build is byte-identical to the benchmarked combined candidate
for both core objects, both public-wrapper objects, `gt864_tobytes.o`, and the
complete `libgt864.so` (`4d2d067f...05c5ec16`).  It separately passed the Pi
64-case KEM test and unchanged KAT; see `production-pi-verify.log`.
P10 BaseInv numerator/finish redesign is now next.  Slothy was intentionally
not run: P9 is compiler-allocated C/Neon, the static and target gates already
produced a spill-free physical object, and no symbolic assembly region was
introduced in this gate.
