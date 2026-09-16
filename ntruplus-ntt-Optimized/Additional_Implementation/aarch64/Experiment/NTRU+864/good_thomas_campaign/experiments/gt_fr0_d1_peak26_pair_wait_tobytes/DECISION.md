# D1-P3B21 decision

Decision: **reject peak-26 pair-wait; retain P3B6 ToBytes.**

The mathematical schedule improves the output frontier, but fails both the
no-spill and cycle gates.  Do not send this C DAG to Slothy: first change the
route/normalize/pack lifetime structure so an object-level live-range model,
including pack temporaries, fits the architectural register budget.
