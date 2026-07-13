---
name: lattice-polymul-core
description: Operational engineering workflow for designing, implementing, or reviewing lattice polynomial multiplication for new polynomial rings and parameter sets, including exploratory ring design, transform choice, coefficient-ring embedding, modular arithmetic, range proofs, and correctness/constant-time validation. Use for new or incomplete algebraic contexts; do not use for existing repo asm cleanup, benchmark-only prototypes, or PMU harness work when the ring and transform contract are already fixed.
---

# Lattice Polynomial Multiplication Core

## Select a mode

State one mode before beginning:

- `design`: Explore or select a ring, parameter set, transform, representation,
  reduction strategy, or implementation family. Treat unresolved algebraic values
  as design variables and record their constraints.
- `implement`: Add or materially change working code after the algebraic and
  representation contracts are fixed. Build from a simple reference relation and
  validate each optimized stage.
- `review`: Reconstruct and audit an existing design or implementation without
  changing it unless the user separately asks for fixes.

Use `design` when the request is exploratory. Do not let an incomplete design
silently enter `implement` mode.

## Apply intake gates by mode

In `design` mode, an unknown modulus, polynomial modulus, root order, or target
platform is not automatically blocking. Record each unknown as a design variable,
state the required constraints, compare viable candidates, and avoid claiming that
an implementation strategy is valid until its preconditions are proven.

In `implement` mode, require the exact coefficient ring/modulus, polynomial
modulus and dimension, multiplication shape, operand ranges, output
representation, and secret/public status before correctness-sensitive code
changes. Require the target platform before platform-specific layout, code, or
benchmark claims.

In `review` mode, treat missing facts as findings. Continue safe source inspection
and contract reconstruction, but do not certify correctness, ranges, or
constant-time behavior until the relevant facts are established.

## Non-goals

- Do not make Kyber, Dilithium, NTRU, NTRU Prime, Saber, or any existing scheme
  the organizing structure.
- Do not provide platform-specific AArch64 Neon or Cortex-M4 tuning here; use a
  platform skill after the core algebraic decision is clear.
- Do not assume a transform or reduction strategy from a scheme name.
- Do not intercept existing implementation work when the ring profile,
  transform, reduction contract, and representation contract are already fixed.

## Cross-skill routing

Read `references/cross-skill-routing.md` when another lattice skill also matches.
For named-scheme planning, start with `lattice-scheme-optimization`, then return
here only for unresolved ring-level decisions.

After the algebraic contract is clear:

- Route AArch64 Armv8-A/Armv9-A Neon kernel planning to
  `aarch64-neon-lattice-polymul`.
- Route Cortex-M4/Armv7E-M kernel planning to `cortex-m4-lattice-polymul`.
- Route Slothy work only after the selected platform skill has produced an
  instruction-selection-level kernel contract.

If the task is an existing repo kernel audit, linked-object path fix,
benchmark-only prototype, PMU harness, or asm cleanup, do not force this skill
unless the requested change could alter algebraic correctness.

## Workflow

1. Read `references/new-ring-intake.md` and select `design`, `implement`, or
   `review` mode.
2. Fill or reconstruct the relevant fields from
   `assets/new-ring-intake-template.md`.
3. Apply the mode-specific intake gates above before choosing or certifying a
   transform, reduction strategy, or layout.
4. Read the smallest relevant reference set:
   `references/transform-decision-tree.md`,
   `references/polynomial-moduli-techniques.md`,
   `references/coefficient-ring-embedding.md`,
   `references/modular-arithmetic-model.md`,
   `references/vectorization-and-permutation-framework.md`,
   `references/range-proof-guidance.md`, or
   `references/correctness-and-constant-time.md`.
5. Treat `references/case-studies/README.md` only as an examples index.
6. Execute the selected mode:
   - In `design`, compare candidate families with explicit algebraic
     preconditions, representation maps, cost assumptions, and proof obligations.
   - In `implement`, establish a simple reference implementation or relation,
     implement incrementally, and test each representation boundary before
     optimizing further.
   - In `review`, reconstruct the target relation and API/internal
     representations, then report violated or unproven preconditions by severity.
7. Use `assets/range-proof-template.md` whenever arithmetic is widened,
   narrowed, lazily reduced, embedded, or switched between rings.
8. Use `assets/benchmark-report-template.md` for performance comparisons; include
   conversions, precomputation, target reduction, and caller workload.

## Validation expectations

Require a simple reference implementation or mathematical reference relation,
boundary-value and randomized differential tests, a range proof, a
representation-map proof, and constant-time review for secret-dependent data.
Inspect generated code when compiler behavior affects correctness or timing.
Never treat benchmark improvement as correctness evidence.
