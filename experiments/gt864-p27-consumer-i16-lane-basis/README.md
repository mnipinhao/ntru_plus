# P27 — consumer-oriented I16 lane-basis search

P27 is the machine-only layout gate selected by P26.  It searches all 15 ways
to pair the six existing main P8 records `(component, four-row-half)`.  It does
not change production assembly and does not claim measured speed.

The selected layout keeps inverse9 and its P8 writes unchanged.  Three paired
I16 regions consume two existing 16-Q blocks apiece, then overwrite those
already-consumed blocks with full eight-channel output records.  The tail is
compacted from 16 padded Q records to 12 dense Q records.  The resulting 108
records are normalized once and routed to 108 natural Q stores.

Reproduce the exact coordinate, route, range, scale and register-budget gate:

```sh
python3 experiments/gt864-p27-consumer-i16-lane-basis/audit.py
```

`audit-results.json` is the checked compact result.  `RESULTS.md` explains the
selected matching, why pre-I16 top recombination is not a permutation, and the
remaining physical risks for P28.

