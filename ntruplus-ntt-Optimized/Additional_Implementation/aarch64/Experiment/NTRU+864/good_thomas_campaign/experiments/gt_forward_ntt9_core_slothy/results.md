# Results

The M5I complete-NTT9 hard gate passes:

- 102 real instructions: six B3s and four eta/eta-inverse products;
- exact complete-core maximum magnitude 28568, output union
  `[-28568,28565]`, and zero unsafe signed-halfword nodes;
- RA-only Slothy result OPTIMAL with preserved instruction order and selfcheck
  OK;
- real-instruction split-window scheduling ends in
  `split_heuristic_full:OK!` and reports 25 N1-proxy cycles;
- exact emitted register set `v0-v7,v25-v31`, all fifteen allowed registers;
- zero reserved `v8-v24`, memory, GPR, branch, stack, or spill instructions;
- both allocated and scheduled sources assemble as AArch64 Neon.

For this solver result, the input and output boundary is:

| Role | Register | Role | Register |
| --- | --- | --- | --- |
| `f0` | `v25` | `out0` | `v0` |
| `f1` | `v3` | `out1` | `v25` |
| `f2` | `v6` | `out2` | `v2` |
| `f3` | `v1` | `out3` | `v7` |
| `f4` | `v4` | `out4` | `v29` |
| `f5` | `v5` | `out5` | `v30` |
| `f6` | `v26` | `out6` | `v3` |
| `f7` | `v28` | `out7` | `v26` |
| `f8` | `v30` | `out8` | `v28` |
| `roots` | `v2` | `modq` | `v31` |

This table describes one allocation, not a stable ABI. Its important result is
that outputs reuse dead input/support registers while the other block remains
reserved. The next gate must constrain the NTT16 producer to a compatible
handoff or prove the boundary permutation cost; it must not assume this exact
register numbering for free.

Hashes:

- allocated: `c3ca14f8f5acd7bff48e5bbbcbf147ea7fe8de2fe186fc67b290146ff9ac0750`;
- scheduled: `574467fd8cf699f126fc4fa30d2734f13842134b343640bc7e22f9aa43e91d03`;
- log: `856963b6157e645a317b759f2bbd0c631475f42d8b7d45a6273fd716a567ae62`.

The generic `parse-slothy-log.py` is not authoritative for this split-window
log: it treats the configured timeout and numbers embedded in experiment text
as result signals. The experiment-local checker instead requires both pass
identities, RA OPTIMAL/selfcheck, every window selfcheck, final
`split_heuristic_full:OK!`, explicit live-outs, and no output warnings.
