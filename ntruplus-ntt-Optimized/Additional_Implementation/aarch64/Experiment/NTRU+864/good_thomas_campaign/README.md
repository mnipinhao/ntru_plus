# NTRU+864 Good-Thomas campaign

This is the default-off development front door for the NTRU+864 Good-Thomas
campaign. Production remains in `../../NTRU+864/` and does not include this
directory.

Reading order:

1. `PLAN.md` — campaign phases and promotion gates.
2. `LEARNING_PROTOCOL.md` — evidence labels and explanation standard.
3. `ring-profile.yml` — scheme and representation facts.
4. `REFERENCE.md` — authoritative GT C reference and oracle hierarchy.
5. `experiments/README.md` — active experiment registry.
6. `experiments/optimization_scoreboard.md` — decisions and next actions.
7. The selected experiment's contracts, checker, results, and decision.

Run all currently implemented static/correctness gates:

```sh
make check
```

This target does not build or link Production and does not run benchmarks.

Run only the authoritative GT C reference gate:

```sh
make check-reference
```
