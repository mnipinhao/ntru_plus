# U01v3 Stage345 Block01 Regalloc Result

Date: 2026-07-09

Status: first-wave semantic search completed.  No primary R01 ASM was emitted because no candidate is correctness-safe at the semantic-regalloc level yet.

Summary:

```text
R01a delayed-produce: infeasible; requires raw q reload or duplicate Stage12
R01b keep block1 live: plausible, but needs a verified semantic Stage345 block0 DAG emitter
R01c consumer-shaped producer: blocked by overlapping consumer contracts
R01d minimal move bridge: infeasible with current block0 allocation
```

The important result is that the next useful implementation is not another physical register patch.  It is a Stage345 block0 semantic DAG emitter with a register allocator that can be checked before assembly is generated.
