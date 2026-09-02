# Decision

**PASS M5U-CF1 as a static arithmetic-existence hard gate.**

The exact scaled NTT9 can absorb enough FR-ISO2 scaling to delete one complete
Algorithm-10 multiplication per scaled block relative to CF0.  The four
required `(top,component)` witnesses reproduce the exact output matrices and
pass constant-specific int16 range checks.  This authorizes a separate
symbolic-assembly realization experiment.

Do not promote this candidate or infer a cycle improvement yet.  The solver did
not certify optimality, and 24 fewer arithmetic instructions can be offset by
composite-constant loads, longer live ranges, register spills, or scheduling
stalls.  The next hard gate must materialize all four witness shapes as Slothy
symbolic regions, derive their exact constant-table/load ledger, and prove
all-32-register allocation with no spill and no extra coefficient boundary.
Only after that may it be integrated and measured against CF0 and the two-
Forward 334.194-cycle BaseMul budget.
