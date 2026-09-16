# Decision

**PASS CF5-C as a faithful cost decomposition.  Reject constant-load-only
optimization as the next path.**

The isolated bank sum reproduces 99.12% of the full Forward cycle delta.  The
30-load difference between top0 and top1 does not produce a larger top0 cycle
penalty, while all four cases share sixteen additional Algorithm-10 mulmods.
The top1 consumers are especially important because they fall from roughly
1.024 to 0.969 IPC despite having fewer loads.

Keep FR-ISO2 conditional, but require the next gate to search a genuinely new
scaled-NTT9 arithmetic DAG and a bounded producer/consumer scheduling window.
Do not rerun a monolithic 624/654-instruction Slothy region.  A static screening
candidate should remove multiple mulmods—not only load encodings—and a real Pi
5 full Forward must save at least 184.839 cycles versus CF5-B.  Until then,
M5R-D remains the Forward champion and Production remains Official.
