# D1-P3B10 paired-pack integration hypothesis

Observation: P3B9 saves 174.300 cycles on the complete ordered packing
boundary.  Under the exact P3B6 route, every adjacent output pair completes at
different input steps, requiring one public partner store and reload per pair.

Primary bottleneck category: packing permutation plus bounded scratch traffic.

Hypothesis: eliminating all 108 P3B6 packing `TBL` instructions and replacing
two 12-byte stores by one `ST3` per pair saves more cycles than 54 partner
store/load round trips per complete call.

Exact proposed change: retain P3B6's composed map, 54-load input order, peak-16
partial-output schedule, full signed-int16 normalization and external byte ABI.
When the first member of an adjacent pair completes, store its raw q-vector in
a fixed 432-byte scratch slot.  When its partner completes, reload it,
normalize both, pair-pack, and issue one final `ST3`.

Expected static effect: remove packing `TBL`, reduce final stores, add exactly
27 scratch stores and 27 reloads/top.  Expected performance effect: beat P3B6
1502.443 cycles; `<1250` remains the promotion gate.

Expected register-pressure effect: completed partners leave registers
immediately, preserving P3B6's peak-16 partial frontier.  Pair packing needs one
loaded partner and extra short-lived packing temporaries.  Any compiler-created
coefficient spill outside the declared scratch fails the allocation gate.

Correctness/range impact: none.  Scratch contains raw signed-int16 vectors;
both pair members receive the same P3B6 normalization immediately before byte
packing.  All scratch addresses and pair decisions are compile-time/public.

Falsifying measurement: byte mismatch, guard failure, scratch above 432 bytes,
unexpected spill, failure to emit 54 `ST3` per complete call, or complete
ToBytes not faster than P3B6.
