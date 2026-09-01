# Decision

Pass and freeze M5K as the two-NTT9-block live-through hard gate for one
`(top,component)` bank. Keep status `investigate`: it proves that the complete
consumer side fits all 24 caller-saved Neon registers without coefficient
traffic, but does not include the actual producer loads/NTT16 assembly or full
Forward integration.

Keep the explicit fixed `v16` capture. It makes the long tail lifetime visible
to Slothy and permits safe reuse only after the second block becomes active.
Keep all eighteen outputs as declared region live-outs; otherwise block-one
pressure would be understated.

The next hard gate is the real pass-2 producer-to-consumer bank: add the
coefficient loads and exact NTT16 producer assembly ahead of M5K, derive the
public table-pointer ABI, and prove that the resulting one-bank region still
allocates without coefficient spills before adding repeated-bank control or
FR-0 stores.
