# 068 invariants

The following conditions define the scope of the executable evidence.

- The ring, Good–Thomas decomposition, B3 arithmetic, Montgomery constants and
  Q24 byte format are unchanged.
- The B3/message seam remains `e=0` and uses the 032 selected-executable bounds
  `[20215, 20250, 20285, 20296]`.
- The existing full-signed-int16 `v=9` reducer is used without a new checkpoint.
- Every source word and message word is routed to its exact Q24 consumer slot;
  the mapping is a checked 768-element bijection.
- V1 and V2 never materialize or reload a complete ordinary M-domain sum.
- The only internal B3 scratch is the existing 96-byte raw `c0/c1/c2` state.
- All routing, message addition, reduction and packet formation is charged to
  the candidate endpoint.
- Correctness is canonical 1,152-byte equality, not merely equivalence modulo
  q at an internal checkpoint.
- GT Clean production sources and dispatch are not modified.
- A full Encap benchmark is out of scope after the island loses to 032.
