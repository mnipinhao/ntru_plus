# P44 — phase-aware route-cache borrowing

P44 is complete and is **rejected before symbolic assembly**. Production remains
the P24 Full and Small ToBytes kernels.

## Fixed experiment boundary

The experiment retains P41's A-before-B order constraint and overlapping
Q/S/D stores. It changes only route-register availability:

- `v0-v25` remain the persistent route cache;
- route construction may transiently borrow `v29`, then `v30-v31` in the
  28/29-register controls;
- immediately before every unchanged Full normalization/packing consumer, the
  route root and every retained route value must fit in `v0-v25`;
- no borrowed value may cross a consumer boundary;
- no coefficient scratch, spill or additional memory pass is allowed.

This is stricter and physically meaningful compared with simply running the
old cache simulator at capacity 29. The model is still optimistic because it
does not charge for a physical-register relocation if an eventual coloring
cannot keep every carried value in `v0-v25`; failure here therefore blocks a
real candidate.

## Baseline and hypothesis

The exact P24 Full top region was extracted from production:

| metric per 432-coefficient top | P24 | P41 |
|---|---:|---:|
| route instructions | 285 | 320 |
| coefficient Q loads | 61 | 76 |
| terminal instructions | 162 | 108 |

P44's predeclared gate required both:

```text
route instructions <= 300/top
coefficient loads  <= 61/top
```

Passing that gate would have retained P41's 54 terminal-instruction saving per
top while removing its measured read-pressure problem.

## Search result

The search evaluated 300,000 precedence-preserving mutations: all capacities
26 through 29 under the instruction-first objective, four independent
capacity-27 seeds, and capacities 27 through 29 under a load-first objective.

The useful Pareto points were:

| objective | transient capacity | route instructions/top | loads/top | complete instruction delta vs P24 |
|---|---:|---:|---:|---:|
| instruction-first | 27 | **306** | 70 | -66 |
| load-first | 27 | 311 | **66** | -56 |

The controls were 320/76 at capacity 26, 311/67 at capacity 28 and 314/71 at
capacity 29 under the instruction-first runs. More borrowed registers do not
help monotonically because they must be emptied at every consumer boundary.

Neither Pareto point passes P44:

- the instruction-first point misses by 6 route instructions and 9 loads/top;
- the load-first point misses by 11 route instructions and 5 loads/top.

## Interpretation and decision

P41's excess reads are not caused primarily by a one-register transient peak.
They arise from values that would need to remain cached **across** output
consumers, exactly where Full normalization and packing reclaim `v29-v31`.
Borrowing those registers only inside a route phase cannot preserve that
cross-consumer state.

No `candidate-full.sym.S` was generated, and Slothy was intentionally not run:
the canonical workflow stops before assembly when the static arithmetic/memory
gate fails. P44 is rejected; production is unchanged. The next generic
serializer gate is P45, a true two-record joint packing DAG rather than another
cache-only variant.

Reproducible artifacts:

- `baseline-region.S`
- `baseline-contract.yml`
- `kernel-contract.yml`
- `instruction-dag.yml`
- `search.py`
- `instruction-search-results.json`
- `load-search-results.json`
