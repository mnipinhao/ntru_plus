# Learning and transparency protocol

This file defines how each optimization turn will be communicated. The goal is
that the owner can reconstruct the work without trusting an AI summary.

## Four evidence labels

Every important statement is labeled as one of:

- **Source fact** — directly visible in named repository lines or symbols.
- **Derived fact** — follows from shown arithmetic or an executable checker.
- **Measurement** — produced by a named binary, command, host, and result file.
- **Hypothesis** — plausible but not yet proven or measured.

These labels must not be mixed. In particular, a hypothesis is never presented
as a source fact, and a measurement is never presented as a proof.

## Per-turn report

Each implementation turn reports:

1. **Question** — the one bounded issue addressed.
2. **Why now** — its position in the operation DAG and campaign plan.
3. **Current behavior** — caller, callee, input, output, and representation.
4. **Mathematics** — formula, modulus, scale, and index mapping.
5. **Code map** — files, symbols, and changed lines.
6. **Change** — readable pseudocode followed by implementation details.
7. **Validation** — exact commands, oracles, cases, and failures.
8. **Performance** — benchmark contract and results, if correctness passed.
9. **Limits** — what remains unproven or unmeasured.
10. **Decision** — keep, refine, reject, or promote.

## Assembly explanation standard

For every assembly kernel, preserve:

- a mathematical reference function;
- semantic pseudocode;
- a register/lane diagram;
- input/output byte offsets;
- constants with mathematical and encoded values;
- instruction groups mapped back to the pseudocode;
- range after every reduction boundary;
- AAPCS64 clobber and preserved-register list;
- generated source and generation command when applicable.

An optimized schedule may be difficult to read, but it must have a readable
symbolic or source-order parent that implements the same instruction DAG.

## Experiment record

Every candidate directory contains:

```text
README.md                 question, hypothesis, and status
contract.yml              inputs, outputs, ranges, layout, ABI
reference/                readable oracle or relation
candidate/                candidate source
tests/                    stage and integration tests
results/                  curated metadata and summaries
DECISION.md               keep/refine/reject/promote with reasons
```

Raw reproducible outputs may remain ignored, but commands, metadata, hashes,
and concise summaries must be retained.

## Mandatory checkpoints

- **Algebra checkpoint:** before choosing the GT mapping.
- **Representation checkpoint:** before consumers use a new layout.
- **Range checkpoint:** before reduction removal, reordering, or narrowing.
- **Instruction checkpoint:** before Slothy or final scheduling.
- **Correctness checkpoint:** before any performance measurement.
- **Full-path checkpoint:** before promotion discussion.
- **Promotion checkpoint:** separate commit and audit.

## Reading order for the owner

For each completed phase, read in this order:

1. the phase section in `PLAN.md`;
2. the relevant ring/DAG/kernel contract;
3. the readable reference code;
4. the candidate code walkthrough;
5. the test output summary;
6. the benchmark and decision record;
7. only then the optimized assembly.
