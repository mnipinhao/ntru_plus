# P16 — P15 full-only ToBytes integration

P16 integrates only the retained P15 full ToBytes schedule into an isolated
production package.  Small ToBytes remains the production P9 implementation.

The change is accepted only if target object identity, KEM/KAT/malformed
correctness and all three paired Keygen/Encaps/Decaps cycle deltas pass on the
Pi 5.  No new Slothy run is involved; the candidate is the exact P15 full
artifact.

Result: accepted and promoted.  See `RESULTS.md`, `results.json`, and
`production-validation.json`.

```sh
python3 run_pi5.py
```
