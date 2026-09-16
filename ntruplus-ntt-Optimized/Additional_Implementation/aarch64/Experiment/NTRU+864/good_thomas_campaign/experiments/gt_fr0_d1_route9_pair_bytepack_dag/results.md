# D1-P3B16 result

Status: **the complete-route9-pair/no-scratch macro-DAG is rejected.**

The attractive local identity is exact: within every 48-coefficient
`shuffle2` block, serialized coefficient pairs are `(stream0,stream1)`,
`(stream2,stream3)` and `(stream4,stream5)` with the same source lane, eight
times each.

The lifetime problem occurs one level earlier.  Each input-once route9 stream
produces one vector for each of nine output blocks.  Completing streams in
sequence retains 9, 18, 27, 36, 45 and finally 54 vectors because a complete
48-coefficient block needs all six streams.  Packing one stream pair early does
not solve the frontier.  Its nine blocks contain 216 packed bytes, requiring
at least 14 vector registers even under ideal dense storage.  No serialized
q-vector is complete before all three pair classes arrive.  Two pending pairs
therefore require at least 27 registers; the next route stream alone needs nine
input vectors, already reaching 36 before route temporaries.

Producing one output block at a time avoids retention only by rereading route
inputs: 486 q-vector loads per top rather than 54.  A scratch version adds the
same kind of memory boundary already rejected by P3B10.

This result is scoped to complete route9 primitives and the existing exact
byte order.  It does not prove that a new partial-route network is impossible,
but such a network converges toward the P3B6 partial-output formulation and
must beat its peak/completion schedule directly.
