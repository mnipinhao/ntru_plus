# Experiment lifecycle and size policy

The campaign keeps failed ideas reproducible without allowing the working tree
to grow without bound.

## Lifecycle

Every experiment has exactly one registry status:

- `active`: currently allowed to receive implementation work;
- `passed`: its bounded gate passed and its reusable oracle/evidence is frozen;
- `rejected`: the hypothesis failed its declared gate;
- `blocked`: evidence is insufficient and the exact reopen condition is known;
- `superseded`: a named later experiment replaces it;
- `promoted`: copied through a separate Production audit.

At most two experiments may be `active`. Starting a third requires closing or
blocking one of the existing two first.

## Tracked artifact budget

An experiment may contain at most 12 tracked-source artifacts by default. The
normal set is:

```text
README.md
baseline-contract.yml
candidate-contract.yml
iteration.yml
reference source/header
test source
Makefile
results.md
DECISION.md
```

Generated assembly, compiler output, raw benchmark samples, temporary logs,
core dumps, and copied binaries are not source artifacts. Keep them outside the
experiment or ignored; retain only the generation command, hashes, concise
statistics, and decision.

A larger artifact set needs a registry waiver explaining why the experiment
cannot be split into smaller questions.

## Closing and archiving

When an experiment leaves `active`:

1. freeze the exact question and contract;
2. record commands and concise results;
3. write `DECISION.md` with keep/reject/block/promote and reopen conditions;
4. remove disposable generated files;
5. update the registry and scoreboard;
6. do not continue adding candidates to the closed directory—open a new
   experiment with a new bounded question.

Physical relocation into an archive tree is optional. The registry status is
authoritative so links and result provenance do not churn merely for tidiness.

## Isolation

Experiment code remains default-off. The registry gate rejects textual links
from the NTRU+864 Production tree or `stock.mk` to campaign paths or experiment
IDs. Promotion is always a separate, explicit change.
