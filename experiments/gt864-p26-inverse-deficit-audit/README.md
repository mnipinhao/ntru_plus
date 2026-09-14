# P26 — matched-boundary Inverse deficit audit

P26 is a source- and PMU-reconciled audit of the P25 Decaps boundary:

```text
selected Official poly_invntt_scale + poly_crepmod3
versus
GT gt864_native_inverse_ternary
```

It changes no production code.  `audit.py` expands every fixed loop and GT
helper call, classifies the dynamic instruction stream, and reconciles it with
P25's measured retired instructions.  The two `official-*.s` inputs are exact
copies from the selected SUPERCOP 20260831 tree; their hashes are recorded in
`audit-results.json`.

```sh
python3 audit.py
```

Result: passed.  The +3,740-instruction deficit is dominated by fragmented
materialization and repeated loads, not modular multiplication.  See
[RESULTS.md](RESULTS.md).
