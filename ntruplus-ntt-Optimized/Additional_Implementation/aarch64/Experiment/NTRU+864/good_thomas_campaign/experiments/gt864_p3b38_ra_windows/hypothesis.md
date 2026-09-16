# P3B38 — optimize-register-pressure

Mode: existing_region_replacement. Baseline P3B37 complete Forward 3518.28 cycles.
Observation: P3B37 locked every vector register during window scheduling.
Hypothesis: a different internal allocation removes false register reuse
dependencies and exposes a better subsequent fixed-register schedule.
Change: functional-only fixed-order RA, then the same small real-instruction
window scheduler. Boundary registers, reserved constants and GPRs remain fixed.
The initial global RA returned UNKNOWN at 30 seconds. The completed attempt
uses split factor 16 for RA as well: local window boundaries stay fixed,
limiting cross-window lifetime freedom. RA then completes in 13.073 seconds.
Expected static effect: same arithmetic, memory accesses and instruction count.
Expected performance effect: target a repeatable >1% complete Forward gain.
Register pressure: allocation may change lifetimes, but no spill is permitted.
Correctness/range: exact instruction DAG and memory addresses must match;
P3B35 range theorem remains applicable without new arithmetic assumptions.
Falsifier: failed exact DAG/ABI checks, spills, or no repeatable full-path gain.
Outcome: no gain; do not adopt the new allocation. Keep experimental evidence
with skill score investigate, not a correctness rejection or global RA
impossibility claim.
No production mutation. Local Slothy execution follows the user's override.
The contract lists physical input names for authoring checks; this is not an
allocator lock. The driver fixes boundary names, not all internal definitions.
