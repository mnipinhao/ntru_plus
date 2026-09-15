# P29 — equal-half paired direct full-ST3 route

## Decision

P29 is **rejected for production**.  It is structurally much smaller than
P28-S and slightly improves the isolated complete Inverse, but it still loses
to the committed P13-C/P8 production consumer.  Production is unchanged.

## Data flow

For every `(top,t)`, P29 pairs the six producer groups as
`G00+G10`, `G01+G11`, and `G20+G21`.  The main route loads those three paired
Q records, performs terminal normalization, exposes the upper D halves with
three `EXT` instructions, and issues two full-vector `ST3.4h` stores.  Those
stores emit rows 0--7 directly in natural component-interleaved order.  The
tail kernel normalizes the three useful row-8 lanes and writes exactly six
bytes with one `STR W` plus one `STRH`; it never uses lane `ST3`.

This removes P28-S's complete standalone route network: 216 `TBL2`, 216
mask-Q loads, 108 held-value `ORR`, and 3,456 bytes of masks.  A machine search
also proved why a single-producer direct-Q design is impossible: all 15 group
pairings require at least two producer groups per natural output Q.

## Slothy and object audit

- Tail allocation: 32 bounded windows, 58.351 seconds, no spill.
- Main route allocation: 32 bounded windows, 96.066 seconds, no spill.
- P29 static total: 4,180 executable instructions versus P28-S's 4,369.
- Objects: 3,364 B unchanged paired main, 3,136 B tail, 3,492 B main route.
- Linked route: exactly 64 full-vector `ST3.4h`, zero lane `ST3`.
- Tail and route contain no `sp`-relative access and no route-mask object.

The route setup originally allowed Slothy to reuse `w1`, which would clobber
the public scratch pointer in `x1`.  Declaring `x0`, `x1`, and `x2` as setup
live-outs fixed the contract; the regenerated physical assembly preserves all
three pointers.

## Correctness and security gates

- Tagged coordinate/range audit: exact 864 coordinates; exhaustive raw input
  interval `[-4577,4577]` maps to ternary `{-1,0,1}`.
- Local exact C/assembly oracle: 1,001/1,001 cases.
- Pi 5 KEM: 64 round trips and tampered-ciphertext rejection for production,
  P28-S, and P29.
- KAT SHA-256 for all three:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Malformed transcript SHA-256 for all three:
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
- 4,096 inverse-to-ternary cases pass exact output, in-place aliasing, AAPCS
  preservation, and complete public scratch wipe.
- Fixed public control flow and public-only addresses are preserved.

## Raspberry Pi 5 paired PMU

Environment: Cortex-A76 CPU 3, Linux `6.18.33+rpt-rpi-2712`, `ondemand`,
`get_throttled=0x0`.  Six alternating processes produced 366 paired complete
Inverse samples and 186 paired samples per KEM operation.

### P28-S to P29

| Operation | P28-S median | P29 median | paired cycle delta | instruction delta | P29 wins |
|---|---:|---:|---:|---:|---:|
| Complete Inverse-to-ternary | 4,975.281 | 4,968.125 | **-7.180** | -191 | 281/366 |
| Decaps | 40,166.400 | 40,181.575 | +4.075 | -191 | 77/186 |
| Keygen control | 43,104.500 | 43,107.750 | +1.000 | 0 | 92/186 |
| Encaps control | 45,015.125 | 45,002.600 | -9.150 | 0 | 109/186 |

P29 improves the isolated complete Inverse only marginally.  Its IPC falls
from P28-S's `1.4235` to `1.3871`, so most of the 191-instruction reduction is
lost to the new dependency/store shape.

### Production to P29

| Operation | Production median | P29 median | paired cycle delta | instruction delta | P29 wins |
|---|---:|---:|---:|---:|---:|
| Complete Inverse-to-ternary | 4,891.570 | 4,967.594 | **+76.844** | -1,452 | 0/366 |
| Decaps | 40,078.550 | 40,194.750 | **+108.625** | -1,452 | 0/186 |
| Keygen control | 43,107.750 | 43,143.875 | +21.250 | 0 | 65/186 |
| Encaps control | 44,996.475 | 45,015.775 | +16.575 | 0 | 60/186 |

Production sustains approximately `1.7056` IPC in complete Inverse; P29 only
reaches `1.3872`.  P29 therefore fails both required promotion gates despite
retiring 1,452 fewer instructions and 42 fewer branches.

## Next gate

Do not schedule P29 again and do not optimize only its final stores.  A viable
successor must change the producer/consumer dependency graph enough to recover
production-like issue width while retaining the direct natural-order output.
The next static model should expose the critical path per `(top,t)` and test
whether normalization and the two ST3 records can be pipelined across adjacent
records without retaining P29's three-pair synchronization point.
