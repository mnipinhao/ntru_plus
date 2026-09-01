# M5L decision

Status: passed as a bounded producer sub-gate; not Production and not a
full-Forward performance claim.

Keep the exact x4-stride gather, the length-2 Algorithm-10 representative
reduction, the three `trn` boundaries, and canonicalizing `tbl` handoff.
Reject immediate `#16` lane-load syntax because it is not encodable.

Next hard gate: prepend this returned two-vector tail producer to a real
sixteen-vector main P8 load/twist/NTT16 producer, then enter M5K while proving
the tail outputs survive without coefficient spills.
