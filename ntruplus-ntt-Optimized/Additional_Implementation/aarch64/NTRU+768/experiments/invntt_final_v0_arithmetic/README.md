# Inverse final V0 arithmetic study

This experiment tests instruction deletion in the active production rminus1
inverse final path. It does not change production and does not run Slothy.

The proof gate checks two candidates for every final low/high output chain:

1. delete the final Barrett reduction;
2. replace `sqdmulh + srshr + mls` with `sqrdmulh + mls`.

Run:

```sh
python3 experiments/invntt_final_v0_arithmetic/analyze_final_v0.py
```

`result.json` contains the per-site reachable ranges and counterexamples.
`result.md` contains the decision and dynamic instruction accounting.
