# P38 — Forward/Full-ToBytes arithmetic co-DAG gate

P38 tests whether the three direct-Forward Full-ToBytes call sites can remove,
rather than relocate, the 108 dynamic `SQRDMULH+MLS` normalization pairs found
by P37.

The gate is rejected statically. Exact execution of current production Forward
finds a valid small-input and Keygen-f witness outside `(-q,q)` for every one
of 864 output coordinates. Canonicalizing in a post-pass or before Forward
stores adds the same 216 instructions that Small would remove, while the
existing one-product quotient cannot determine all output quotients.

Production is unchanged; Slothy and Pi 5 are intentionally not run after the
arithmetic gate fails. Reproduce the machine audit on Apple arm64 with:

```sh
python3 audit.py
```

See [RESULTS.md](RESULTS.md) and `audit-results.json`.
