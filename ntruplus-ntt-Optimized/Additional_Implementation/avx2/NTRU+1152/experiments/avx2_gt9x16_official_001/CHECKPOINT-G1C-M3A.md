# Checkpoint G1C-M3A: full inverse16 experiment contract

M3A defines the full inverse16 experiment before writing assembly. Its source
of truth is `generated/g1c-m3-inverse16-oracle.json`. It keeps forward
persistent S/D, terminal-coefficient basis, and inverse physical-q split state
as separate dimensions.

## Three-way decomposition

- M3-C0 is the exact full materialized control: BMScale materializes before a
  D1/D2/D4/D8 inverse using the current inter-stage representation.
- M3-C1 links BMScale live results into D1, then materializes before the same
  D2/D4/D8 tail. `C1-C0` asks whether M2's edge credit survives the full caller.
- M3-C2 carries split state through D1/D2/D4/D8 and materializes only the final
  required boundary. `C2-C1` isolates persistent-state routing and scheduling
  credit. `C2-C0` is reported but cannot attribute the source of the win.

All variants must use identical arithmetic, input residency, output address,
compiler flags, and balanced paired scheduling. The static report must compare
stores, reloads, routing families, shifts, Montgomery chains, constant loads,
and peak live YMM. Montgomery-chain count is expected to remain equal.

## Algebraic map

For each of nine physical rows, the oracle derives inverse stages in order
D1, D2, D4, D8 from the adjusted forward twiddles. Every stage covers each of
16 physical q lanes exactly once with eight butterflies, and each local inverse
matrix composes with its forward matrix to `2I mod 3457`. This follows the
current physical-q representation and does not imitate Official's textual
inverse stage order.

## Range gate

The existing BMScale independent envelope is ±13,824. D1 is safe: its sum is
±27,648 and its twisted side remains small. At D2, however, independently
combining two D1 sum streams yields ±55,296, outside signed i16. This is a
failure of the independent-interval proof, not evidence that actual
producer-correlated states overflow.

Therefore no convenience reduction is inserted and M3 assembly is not yet
authorized. The next checkpoint must propagate actual producer-real correlated
register states through D1/D2/D4/D8, record every split stream's extrema and
Montgomery inputs, and obtain a mechanical bound strong enough either to prove
the lazy path or identify the earliest mathematically required reduction.

## Price ledger

F1's +58.5 cycles per forward and F5's -22-cycle BMScale-to-D1 edge are
orthogonal experiment prices. They are not netted before G2 defines a complete
path containing both. The current leading hypothesis is instead F0 persistent
forward → consumer-native arithmetic → F5 split inverse, which pays no F1 debt.

This checkpoint contains no cycle result, SUPERCOP evidence, or production
qualification.
