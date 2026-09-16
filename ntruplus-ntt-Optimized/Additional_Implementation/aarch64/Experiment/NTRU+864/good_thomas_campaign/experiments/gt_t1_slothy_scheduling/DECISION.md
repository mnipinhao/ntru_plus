# A1-S decision

Reject the generated T1+Slothy schedule. It is correct, allocation-safe and
contract-preserving, but complete Forward is 43.306 Cortex-A76 cycles slower
than the same-binary T1 baseline with identical retired instructions.

Retain T1 bank-major as the active tail architecture and retain its current
hand schedule. Do not reopen scheduling-only work from the same N1 proxy
model. A future Forward candidate needs either a Cortex-A76-specific model or
a changed arithmetic dependency graph with a concrete critical-path/resource
hypothesis; it remains a separate experiment.
