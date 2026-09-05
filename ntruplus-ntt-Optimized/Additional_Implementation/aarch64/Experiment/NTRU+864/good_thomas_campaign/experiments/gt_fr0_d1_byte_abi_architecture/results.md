# D1-P3A results

Status: **PASS as an architecture-selection gate.**

## Exact factorization

- The authoritative 864-entry map remains a bijection with SHA-256
  `11bcb9351c470ca466347cd69f50b40aa23b56f1456556dc5da41a5417fa3c82`.
- Only 144 leaf routes are distinct.  The route is identical across two top
  branches and three cubic components.
- A stock 24-coefficient Official tile does **not** come from one FR0 tile.
  Each of its three vectors uses the same eight lanes drawn from eight FR0
  tiles.
- Per top, the route graph splits into two disconnected 9-output/9-input
  components.  Every node has degree eight, and the one missing edge per node
  is a perfect matching: exactly `K9,9 - matching`.
- The complete polynomial is therefore twelve identical-shape route9 kernels:
  `2 top × 3 component × 2 graph components`.

The ideal memory floor for a route9 implementation is 108 `q` loads and 108
`q` stores: each of the 108 FR0 vectors is read once and each output vector is
written once.  This does not yet count the cross-register routing operations.

## Byte composition

The machine model reproduces all 18 stock 48-coefficient shuffle blocks and
proves `poly_shuffle` and `poly_shuffle2` are inverse permutations.  Composing
FR0 routing with `poly_shuffle2` is bijective and can eliminate the separate
Official temporary/shuffle pass.

The composed mapping is not trivially local: 72 output vectors touch three
FR0 tiles, 36 touch four, and every 48-coefficient packing block touches 16
FR0 tiles.  Therefore a naïve per-tile direct pack is rejected.

Static work removable by successful fusion is one stock shuffle direction:
324 `TRN` instructions plus 216 vector load/store instructions over the full
polynomial, in addition to deleting the scalar compatibility loop.
