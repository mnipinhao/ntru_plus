# Result metadata

Keep compact reviewed summaries here. Raw SUPERCOP data and fixed-ELF launch
logs are reproducible artifacts and should be archived outside Git.

Tracked repository-local diagnostics:

- `ntt16-intel155h-20260820-002/ntt16-diagnostic.json`: Checkpoint C retained
  C reference, C0 leaf/body, C1 leaf, plus the assembly audit. This is not
  SUPERCOP evidence.
- `c2-intel155h-20260820-001/c2-diagnostic.json`: terminal-pair distance-8 and
  complete NTT16 A/B, including chain and packing audit. Diagnostic only.
- `c3-intel155h-20260820-001/c3-diagnostic.json`: one-row pair persistent-S/D
  Official-routing A/B and leaf audit. Diagnostic only.
- `c4-intel155h-20260820-001/c4-diagnostic.json`: nine-row sequential/pipelined
  from-Z and zero-materialization natural-input pair evidence. Diagnostic only.
- `official-stages-intel155h-20260821-001/official-stage-paired.json`: pinned
  Official T0/T3x3/T2x4 stage medians paired with D-A and four C4 pairs.
  Repository-local diagnostic only.
