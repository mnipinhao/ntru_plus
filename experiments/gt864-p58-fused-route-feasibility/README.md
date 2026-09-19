# P58 — fused producer/route feasibility for the GT864 inverse

P58 changes no production code.  It is a machine-only feasibility gate for the
design named at the end of P29: emit the natural-order `ST3` inside the paired
I16 producer schedule instead of running `p29_main_route` as a separate pass.

## Why this is reopened

Every earlier store-path redesign (P11, P21, P22, P27–P34) was decided on
Cortex-A76 paired PMU alone.  Measurements on 2026-09-18 show that A76 is the
one host where the output scatter cannot pay off, because the inverse is
mul-port bound there and the 864 `UMOV` + 864 `STRH` occupy otherwise idle
issue slots:

| removing the whole store path | Pi 5 Cortex-A76 | Apple M2 Pro |
|---|---:|---:|
| saving | 207 cyc (4.3%) | 82.7 ns (19.6%) |

P29 rebuilt against current production and re-measured on both hosts:

| | A76 cyc | instructions | IPC | M2 ns |
|---|---:|---:|---:|---:|
| production | 4,819 | 8,304 | 1.723 | 421.9 |
| P29 | 5,024 (+4.3%) | 6,926 (−1,378) | 1.379 | 380.2 (−9.9%) |
| official | 4,743 | 4,861 | 1.024 | 314.5 |

P29's output is byte-identical to production over 20,000 × 864 coefficients.
Its A76 regression is entirely IPC: it retires 1,378 fewer instructions and
still loses, because `p29_main_route` runs as an isolated region at IPC 1.49
while production's standalone `crepmod3_ternary` reaches 2.21.

Isolating the route confirms where the cost sits:

| | A76 | M2 |
|---|---:|---:|
| P29 complete | 5,022 cyc | 380.2 ns |
| P29 without the route pass | 4,436 cyc | 325.5 ns |
| route pass, marginal | **586 cyc / 873 instr → IPC 1.49** | **54.7 ns** |

P29's producers alone already beat production's 4,819.  The whole regression is
that one pass.

## Question this gate answers

Can the route's work be scheduled *inside* a producer region — under the
constraint that a natural output `Q` always needs two producer groups — without
exceeding 32 vector registers, and does Slothy converge on the resulting region?

## Coordinate map

Natural order is `n = top*432 + t*27 + row*3 + component`, and channel
`j = 3*row + component`.  P29's three producer pairs are

| producer | channels |
|---|---|
| P0 = G(0,0)+G(1,0) | 0,3,6,9 ∪ 1,4,7,10 |
| P1 = G(0,1)+G(1,1) | 12,15,18,21 ∪ 13,16,19,22 |
| P2 = G(2,0)+G(2,1) | 2,5,8,11 ∪ 14,17,20,23 |

`ST3#1` (rows 0–3, channels 0–11) needs P0 in full plus P2's low half;
`ST3#2` (rows 4–7, channels 12–23) needs P1 in full plus P2's high half.  P2 is
the shared producer, so the fused order is P2 first, then P0 and P1 each
emitting their own `ST3` as their outputs become final.

## Files

- `pressure.py` — symbolic vector-register pressure of a straight-line Slothy source.
- `profile.py` — pressure histogram and headroom profile.
- `fuse.py`, `fuse2.py` — constructive fusion feasibility under four constant-handling variants.
- `genwindow.py` — emits fused producer+route windows in symbolic form.
- `probe.py` — Slothy convergence probe over window sizes (Cortex-A76 model, full timing schedule).

See [RESULTS.md](RESULTS.md).
