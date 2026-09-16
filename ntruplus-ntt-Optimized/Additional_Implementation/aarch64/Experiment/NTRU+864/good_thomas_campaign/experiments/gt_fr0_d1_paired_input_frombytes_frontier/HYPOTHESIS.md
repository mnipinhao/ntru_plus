# D1-P3B14 paired-input FromBytes hypothesis

P3B11 decodes one 12-byte serialized q-vector at a time.  This gate asks
whether adjacent q-vector pairs can instead be decoded from 24 bytes with an
`LD3`-style three-vector load and routed directly into FR0, while retaining the
input-once, no-coefficient-scratch and no-spill contracts.

The search constrains every input q-vector to remain adjacent to its serialized
mate.  It measures both an optimistic sequential-routing frontier and the
actual atomic-pair frontier required when all three `LD3` result vectors become
live together.  This is a static feasibility test, not an optimality proof.
