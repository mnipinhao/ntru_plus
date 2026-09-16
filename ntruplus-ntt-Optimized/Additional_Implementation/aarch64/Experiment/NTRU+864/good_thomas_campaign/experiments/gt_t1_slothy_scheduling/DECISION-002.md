# A1-S-002 decision

Do not promote the schedule-only T1 candidate. It is correct, contract-safe,
spill-free, and consistently 8.462 cycles faster at complete Forward, but it
does not meet the predeclared 20-cycle maintenance threshold.

Retain current T1 as the active baseline. Preserve A1-S-002 as evidence that
T1's original physical register allocation is materially better than the
A1-S-001 Slothy allocation, and that scheduling-only has a small positive
Cortex-A76 effect. A future scheduling pass should keep the physical mapping
fixed and needs either a Cortex-A76-specific model or a changed arithmetic DAG
to justify another promotion campaign.
