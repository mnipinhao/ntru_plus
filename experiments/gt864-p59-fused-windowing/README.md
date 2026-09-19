# P59 — windowing and precedence strategy for the fused GT864 inverse route

P59 changes no production code.  It follows P58, which established:

- **registers are not the obstacle** — a fused producer+route region needs
  exactly the vector budget the producer alone already needs, provided the
  ternary constants are reloaded per burst instead of held live (the extra loads
  are free; the load ports sit idle);
- **Slothy scalability is the obstacle** — an 81-instruction fused window
  scheduled in about ten minutes, a 131-instruction one did not return in
  twenty-five, and a full fused P0 region is 1,193 instructions.

P59's job is to find out what actually makes those windows hard, and whether
Slothy's own splitting machinery handles them.

## Why this might be routine rather than hard

`split_heuristic_preprocess_naive_interleaving` is documented for exactly this
shape of problem:

> useful if the code to be optimized is comprised of independent computations
> operating on different architectural state; the naive preprocessing will 'zip'
> the different computations prior to applying the core optimization

A fused region is two largely independent computations: the paired-I16 producer
arithmetic and the raw-to-ternary delivery.  That is the intended use.

## Diagnostic first, strategy second

P58's probe left one clue unexplained.  Its log shows

```
Objective: None (any satisfying solution is fine)
Invoking external constraint solver (OR-Tools CP-SAT v9.15.6755) ...
```

so the twenty-five minutes were spent merely finding a *feasible* schedule, not
a good one.  That points at register allocation, not at scheduling.  Two
candidate causes:

1. `allow_spills = False` against a peak pressure of exactly 32;
2. `inputs_are_outputs = True` on a window carved out of the middle of the
   producer, which pins every value crossing either boundary.

`diag.py` varies one knob at a time on the same 131-instruction window.

## Files

- `genwindow.py` — emits fused producer+route windows (variant C, carried from P58).
- `pressure.py` — symbolic vector-register pressure.
- `diag.py` — one-knob-at-a-time Slothy configuration diagnostic.

See [RESULTS.md](RESULTS.md).
