# D1-P3B22 result

Status: **rejected by exact static gate; no assembly or PMU run.**

All 27 adjacent serialized q-vector pairs have disjoint eight-input
neighborhoods.  For any input order, an output completes when the last member
of its neighborhood is loaded.  Two outputs can complete on the same step only
if that last input belongs to both neighborhoods; therefore no protocol pair
can be consumed immediately by `pack16`.

The only escapes are partner retention (P3B15/P3B21 spilled), input rereads
(violates the load contract), or scratch (P3B10 lost on Pi 5).  Consequently
there is no pair-local implementation under the fixed conjunction of
input-once, no scratch and no retention.
