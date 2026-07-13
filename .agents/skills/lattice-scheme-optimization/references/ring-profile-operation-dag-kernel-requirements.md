# Ring Profile, Operation DAG, and Kernel Requirements

Use this reference to prepare scheme-owned artifacts before invoking a platform
skill or `slothy-symbolic-asm-authoring`.

## Contents

- Artifact sequence and ownership
- Ring-profile requirements
- Core-decision gate
- Operation-DAG requirements
- Kernel-requirements boundary
- Platform and Slothy handoffs
- NTRU+ and HAETAE focus

## Artifact sequence and ownership

Produce and validate artifacts in this order:

1. `ring-profile.yml`
2. Resolved core polynomial-arithmetic decisions
3. `operation-dag.yml`
4. `kernel-requirements.yml`
5. Target platform route
6. Platform-owned instruction-selection-level kernel contract
7. Optional Slothy handoff

Use these scheme-owned templates:

- `../assets/ring-profile-template.yml`
- `../assets/operation-dag-template.yml`
- `../assets/kernel-requirements-template.yml`

Do not put platform instruction selection, physical-register policy, Slothy
region labels, or final assembly in the three scheme-owned artifacts.

## Ring-profile requirements

### Preconditions

- Identify the scheme family and concrete variant.
- Record the current specification revision or repository commit.
- List missing source facts rather than filling them from memory.

### Required content

- Coefficient ring and exact coefficient modulus.
- Polynomial modulus, degree, and module dimensions when applicable.
- Transform/root conditions and representation conventions.
- Operand, public-constant, intermediate, and output ranges.
- Exact or rounded output semantics.
- Secret/public classification and constant-time requirements.
- Hot operations and caller/reuse context.
- Reference C, constants/tables, tests, KATs, and benchmark paths.
- Candidate target requirements without selecting instructions.

### Validation

- Confirm every numeric fact against the current source.
- Confirm input, internal, and output representations separately.
- Confirm ranges before using storage width as an arithmetic-width argument.
- Confirm source paths exist or mark them as unresolved.

## Core-decision gate

Before building the operation DAG, identify whether any of these remain open:

- Transform family or transform cutoff.
- Coefficient-ring switching or auxiliary embedding.
- Target polynomial reduction.
- Modular multiplication/reduction strategy.
- Range or reconstruction proof.
- Canonical versus bounded output behavior.

Route open decisions through `lattice-polymul-core`. Update the ring profile with
the selected decision, its preconditions, and unresolved proof obligations. Do
not construct downstream artifacts on an assumed transform or representation.

## Operation-DAG requirements

Build one DAG for one hot operation or coherent kernel family. Record:

- Mathematical contract and exact operation shape.
- Input/output representations and coefficient bounds.
- Dependencies and dataflow.
- Public constants, zeta/table ordering, and source.
- Loads, stores, alignment, aliasing, and public-offset requirements.
- Caller consumption and reuse.
- Forbidden semantic changes.
- Reference function and differential-test route.

Do not use one giant DAG for the entire scheme.

## Kernel-requirements boundary

Create one `kernel-requirements.yml` for a candidate kernel boundary. Include:

- Operation and caller context.
- Required inputs, outputs, live values at the semantic level, and reuse.
- Range, representation, constant, memory, and constant-time requirements.
- Portability and target constraints that affect platform selection.
- Expected performance measurement and full-path baseline.
- Reference oracle, boundary tests, differential tests, and KAT route.
- Changes the platform implementation must not make.

Keep the artifact platform-neutral. Do not select instructions, vector lanes,
table layout, symbolic registers, physical registers, ABI registers, or Slothy
region boundaries here.

## Platform handoff

Select a platform skill after the three scheme artifacts pass their gates. Give
that skill the artifacts and ask it to produce the platform-owned kernel
contract, including:

- Instruction selection and data layout.
- Table layout and constants.
- ABI, live-ins, live-outs, and memory contract.
- Register classes and reserved-register constraints.
- Platform-specific range and constant-time arguments.

For AArch64 Neon use `aarch64-neon-lattice-polymul`; for Cortex-M4 use
`cortex-m4-lattice-polymul`. Name another platform route explicitly when neither
applies.

## Slothy handoff

Invoke `slothy-symbolic-asm-authoring` only after the platform contract exists.
The handoff must include:

- `ring-profile.yml`
- `operation-dag.yml`
- `kernel-requirements.yml`
- The platform-owned kernel contract
- Fixed instruction selection, ABI, live-ins/live-outs, memory, constants,
  ranges, reserved registers, and forbidden changes

Slothy authoring may preserve and schedule the contracted instruction DAG; it
must not choose a new high-level algorithm or silently change instruction
selection.

## NTRU+ focus

For a concrete NTRU+ parameter set, source `q`, `f(x)`, degree, transform/root
conditions, coefficient representation, multiplication path, tables, KATs, and
benchmark harness from the current repository. Do not infer classic NTRU, NTRU
Prime, or NTTRU structure from the scheme name.

Include `poly_mul`, NTT/INTT, pointwise products, and encode/decode arithmetic
only when they occur in the selected current path. Use profiling and caller
impact to select the first kernel.

## HAETAE focus

For a concrete HAETAE parameter set, source the ring, `q`, degree, module
dimensions, NTT tables, challenge distribution, decomposition constants,
verification products, tests, and KATs from the current implementation. Do not
import Dilithium constants, packing, table order, or rejection behavior.

Track NTT ranges separately from matrix/vector accumulation and decomposition
ranges. Use full-scheme profiling before treating NTT as the primary bottleneck.

## Common mistakes

- Jumping from a scheme name directly to assembly.
- Treating paper parameters as current repository facts.
- Building a DAG before resolving a transform or representation decision.
- Putting platform instructions or registers in `kernel-requirements.yml`.
- Sending only a function name to a platform or Slothy skill.
- Claiming whole-scheme speedup from a micro-kernel benchmark.
