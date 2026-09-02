# Hypothesis

The frozen M5R-D NTT16 producer can be separated at the logical
NTT16-to-NTT9 boundary and connected to each CF3 two-block scaled-NTT9
consumer without:

- a coefficient load/store boundary;
- a vector-register copy at the boundary;
- a spill or stack access; or
- changing the producer arithmetic, coefficient loads, or public NTT16 table
  order.

The two tail transforms are not extra live values.  Their final vectors are
exactly `lo_f8_raw` and `hi_f8_raw`, so the boundary contains eighteen NTT16
vectors in total.

This gate deliberately uses two bounded Slothy regions.  It does not ask
Slothy to solve the complete producer-plus-consumer bank as one roughly
650-instruction scheduling problem.  The producer is allocated/scheduled
first; its eighteen physical live-out registers then become fixed physical
live-ins to the matching consumer region.

The hypothesis is falsified by any boundary copy, duplicate/aliased raw
input, spill, coefficient memory traffic, incorrect table advance, failed
arithmetic/layout oracle, or loss of the remaining full-Forward static
instruction advantage over CF0.
