# Decision

Pass and freeze M5J as the exact NTT16-producer to first-NTT9-consumer
physical ABI. Keep candidate status `investigate`: the result proves
allocation, scheduling, layout, and range closure for one block while the
other block remains live, but it is not a full Forward kernel.

Keep `v16` as an explicit fixed held-tail ABI register. Do not replace it with
an unused symbolic live-out, because that would disappear from the returned
allocation map and could understate pressure. Retain the 16-load public-table
form as a conservative source count; an eight-`ldp` spelling is a later
code-shape refinement, not a correctness prerequisite.

The next hard gate is to consume the held block while all nine first-block
NTT9 outputs remain live. It must preserve zero coefficient loads/stores,
model the fixed `v16` tail as a real second-block input, and pass RA before any
whole-Forward assembly integration.
