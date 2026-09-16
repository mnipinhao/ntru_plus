# Results

Status: **CF5-D did not pass the arithmetic gate; no assembly candidate was
created and Slothy was not run.**

## Required budget

CF5-C measured a 351.936-cycle Forward regression for CF5-B versus M5R-D.  Two
Forwards therefore lose 703.873 cycles while the isolated FR-ISO2 BaseMul saves
334.194 cycles.  With zero Inverse penalty, each Forward must recover at least
184.839 cycles.

The 64 additional mulmods in CF5-B occur as eight blocks times eight extra
mulmods.  Using the correlated CF5-C measurement only as a screening density,
recovering 184.839 cycles requires removing at least 34 of those 64 operations.
CF5-D rounded this to a uniform, auditable budget of five removals per block:
at most 21 mulmods rather than 26, or 40 removals per Forward.

## Solver evidence

The inherited exact model has 61 arithmetic nodes.  Its original big-M MILP
contains 379 integer variables and 977 constraints after adding the `<=21`
cost cut.  Four parallel 300-second HiGHS runs all reached the time limit with
no feasible incumbent and no infeasibility certificate.

An independent exact lazy Boolean/modular-potential encoding was then used.
It removes the affine labels from SAT: SAT selects the five add reconciliation
modes and nineteen removable-multiplication flags; a modular union-find checks
the resulting `(A,B)` equalities and returns inconsistent cycles as clauses.
Four parallel 300-second runs again reached the time limit after learning:

| case | learned conflicts | result |
| --- | ---: | --- |
| t0c1 | 1827 | unresolved |
| t0c2 | 1830 | unresolved |
| t1c1 | 1836 | unresolved |
| t1c2 | 1837 | unresolved |

`unresolved` is not an infeasibility proof.  It means CF5-D produced neither
the required `<=21` witness nor a lower-bound certificate within the declared
bounded searches.  The existing 26-mulmod witnesses remain valid upper bounds;
`audit_gate.py` independently re-evaluates their add, internal-multiply, input
twist, and fixed-output costs as exactly 26 for all four cases.  The inherited
finite-field and signed-halfword replay also still passes all four witnesses.

## Decision

The hard gate requires a concrete DAG at or below 21 mulmods for all four
cases.  That condition was not met, so generating assembly or submitting a
569--654 instruction region to Slothy would not be justified.  CF5-D therefore
closes without changing the Forward, BaseMul, Inverse, production link, or any
coefficient memory boundary.

The useful conclusion is narrower than “21 is impossible”: affine rescaling
of the fixed M5R-D topology has not produced a performance-viable FR-ISO2 DAG.
The next arithmetic experiment must change topology (for example, a factored
or matrix-synthesized scaled NTT9), while retaining the same FR-ISO2 leaf ABI,
rather than spending another scheduling round on the 26-mulmod graph.
