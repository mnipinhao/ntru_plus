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

The bounded allocation question passes. Slothy allocates and schedules the
15-instruction B3 in exactly the nine-register window `v0,v24-v31`, with
spills disabled and no emitted stack or memory instruction. Freeze the
returned assembly and log as evidence, but keep the candidate status at
`investigate`.

The next experiment must expand the boundary to the surrounding NTT9 region.
That is where overlapping B3 live ranges, twist/eta constants, and the other
fifteen live data vectors become real instructions rather than reserved-name
pressure. The N1 model remains a proxy; Pi 5 target attribution and SUPERCOP
remain later gates.
