# D1-P3B20 decision

Decision: **reject clustered TBL; retain P3B11 FromBytes.**

The repeated routing subgraph exists mathematically, but whole-cluster TBL
masks create too much constant and live-state pressure.  It violates the
no-spill gate and regresses cycles.  Reopen only with a smaller local subgraph
whose mask constants are reused in registers and whose object audit is
spill-free before full Pi 5 timing.
