# M5U-CF2 — FR-ISO2 scaled NTT9 Slothy gate

This experiment turns the four exact M5U-CF1 arithmetic witnesses into
Slothy-sized symbolic assembly regions.  It answers one deliberately narrow
question:

> Can one complete scaled NTT9 block be allocated and scheduled while nine
> vectors belonging to its sibling block remain live and untouchable?

The answer is **yes for each isolated block**.  The four 138/154-instruction
regions all pass remote register allocation, self-check, split-window
scheduling, and emitted-assembly audit without spill.  This does not yet prove
that two independently allocated blocks can be joined without register copies.

## Reproduce

```sh
make static-check
make audit
```

`optimize.py` is the remote Slothy driver.  The checked-in files under
`slothy-output/` are the allocated assembly, scheduled assembly, and complete
logs returned from `pinhao@172.25.166.141:51208`.

Read `REGISTER_FLOW.md` before editing the symbolic regions.  `results.md`
records the evidence and its limits; `DECISION.md` defines the next hard gate.
