# Decision

Freeze the correlation-safe two-product B3 as the only Forward B3 DAG eligible
for register allocation. Reject any implementation that materializes `2a` or
`3a`, silently returns to the four-product schedule, or changes instruction
order without regenerating the full exact range report.

Use Slothy symbolic-register syntax for authoring. Keep physical allocation
out of the source, forbid spills and `v8-v15`, and model the fifteen other
live-through data vectors by reserving `v1-v23`. The first Slothy question is
strictly whether this 15-instruction region is allocatable and schedulable in
the remaining nine physical registers under the N1 proxy model.

Do not promote this experiment on static checks. A valid next result must
include the returned Slothy assembly and log, a parsed register/spill audit,
and then a larger-region integration test. The N1 model is only a proxy; Pi 5
target attribution and SUPERCOP remain later gates.
