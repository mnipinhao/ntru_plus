# D1-P3B11 input-once FromBytes hypothesis

Observation: the selected P3B4 `c1_from` boundary takes 1183.250 cycles on
Cortex-A76 and constructs each FR0 output q-vector with eight individual lane
loads.  Across the polynomial this is 864 coefficient loads from a 1296-byte
packed stream.  The exact reverse composed-map has an input-once schedule with
at most fourteen partial FR0 output vectors.

Primary bottleneck category: layout/permutation.

Hypothesis: decode every contiguous twelve-byte group exactly once, distribute
its eight coefficients through register lane moves, and store each FR0 q-vector
as soon as its eighth lane arrives.  This should trade repeated byte-addressed
lane loads for 108 sequential decode operations without coefficient scratch.

Exact proposed change: generate a straight-line top-local Neon core for the
inverse of the P3B6 composed map.  Each top performs 54 exact twelve-byte
loads, 54 `unpack8` operations, 432 compile-time lane moves and 54 q-vector
stores.  The same core is called for both 432-coefficient tops.

Expected static effect: replace 864 `LD1 lane` coefficient loads with 108
eight-byte plus 108 four-byte loads, retain exactly 864 lane moves, remove the
C1 address/shift tables from the candidate, and use no coefficient scratch.

Expected performance effect: beat the paired P3B4 `c1_from` control.  The
candidate is only eligible for later full-KEM integration if the cycle gain is
reproducible and its complete FromBytes cost moves materially toward Official.

Expected register-pressure effect: at most fourteen partial output vectors
plus one decoded source and short unpack temporaries.  Any coefficient-vector
spill rejects the candidate before timing.

Correctness or range impact: none.  Every twelve-bit input value in `[0,4095]`
is preserved exactly, including noncanonical encodings.  The map, addresses and
schedule are public compile-time constants.

Falsifying measurement: any mismatch for arbitrary 1296-byte inputs, any
guard-page over-read or output over-write, any coefficient-vector spill, or a
Pi 5 median at or above the paired C1 control.
