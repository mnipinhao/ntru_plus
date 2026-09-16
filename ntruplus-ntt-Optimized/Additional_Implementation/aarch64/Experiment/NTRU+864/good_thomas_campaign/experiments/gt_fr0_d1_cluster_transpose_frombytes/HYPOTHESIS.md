# D1-P3B23 local transpose FromBytes hypothesis

Observation: thirteen exact input clusters have two or four sources whose
destination lanes form aligned 32-bit or 64-bit chunks after public source
reordering.  P3B20 paid a separate TBL mask for every destination.

Hypothesis: use `ZIP` for four size-2 clusters and a two-level `TRN` network
for eight size-4 clusters, then insert whole chunks into partial outputs.  Keep
the two unaligned size-4 clusters and one size-6 cluster as scalar lane moves.

The fixed contract is P3B11: exact arbitrary 12-bit values, 54 input groups
loaded once per top, no coefficient scratch, fixed public flow.  Reject on any
byte mismatch, non-ABI spill, or failure to recover 145 cycles per call.
