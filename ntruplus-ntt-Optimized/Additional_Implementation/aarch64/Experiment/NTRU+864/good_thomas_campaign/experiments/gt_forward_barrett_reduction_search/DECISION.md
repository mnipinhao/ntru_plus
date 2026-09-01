# Decision

Select R0 and freeze zero identity reductions for the first Forward assembly.
The sound constant-specific interval maximum is 25569, leaving 7198 of signed
int16 headroom. R0 also minimizes fixed multiplies and the NTT9 register model.

SMT/MILP is not run because it was proposed only to resolve an interval
overflow. R0 is safe even under the interval over-approximation. Reopen solver
work only if a later arithmetic reordering, constant set, or input bound makes
the sound interval exceed int16.
