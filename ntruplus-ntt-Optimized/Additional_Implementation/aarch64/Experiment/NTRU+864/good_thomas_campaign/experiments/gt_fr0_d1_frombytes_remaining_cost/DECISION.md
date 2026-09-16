# D1-P3B17 decision

Decision: **retain P3B11 and target structured lane routing.**

P3B11 is already close in retired work (+84 instructions) and removes 35
branches, but remains 144.592 cycles slower than the complete Official native
FromBytes boundary.  The next candidate must replace a repeated lane-move
subgraph with `TRN`/`ZIP`/`EXT`/`TBL` operations without adding scratch or
repeated input loads.  Scheduling-only work is deferred until that DAG exists.
