---
name: lattice-scheme-optimization
description: Route and plan scheme-level lattice optimization work for NTRU+, HAETAE, derived NTRU-like schemes, and derived Dilithium-like schemes. Use this skill to turn current scheme and repository facts into a ring profile, operation DAG, platform-neutral kernel requirements, and a platform handoff. For existing NTRU+768 GT production repo work, use ntruplus-gt-kernel-engineering instead.
---

# Lattice Scheme Optimization

## Non-goals

- Do not use this skill for completely new rings with no scheme context; use
  `lattice-polymul-core`.
- Do not use this skill for NTTRU; it is out of scope.
- Do not choose platform instructions, physical registers, Slothy regions, or
  final assembly here.
- Do not intercept asm cleanup, linked-object audits, wrapper fixes, PMU
  harnesses, or benchmark-only prototypes when the scheme/ring/kernel contract
  is already known.

## Cross-skill routing

Read `../lattice-polymul-core/references/cross-skill-routing.md` when another
lattice skill also matches. Use this skill as the scheme-level entry point, then
resolve ring-level unknowns through `lattice-polymul-core` before creating an
operation DAG or kernel requirements.

For existing NTRU+768 GT production work in this workspace, route to
`ntruplus-gt-kernel-engineering` first. Return here only if the request changes
scheme-level correctness obligations.

After scheme and core decisions are fixed:

- Route AArch64 Armv8-A/Armv9-A Neon contracts to
  `aarch64-neon-lattice-polymul`.
- Route Cortex-M4/Armv7E-M contracts to `cortex-m4-lattice-polymul`.
- Route Slothy work to `slothy-symbolic-asm-authoring` only after the selected
  platform skill has produced an instruction-selection-level kernel contract.

## Artifact ownership

This skill owns:

- `ring-profile.yml`: sourced scheme, parameter, ring, range, representation,
  workload, and validation facts.
- `operation-dag.yml`: one hot operation or kernel family decomposed into its
  mathematical and dataflow dependencies.
- `kernel-requirements.yml`: platform-neutral kernel boundaries, invariants,
  memory/security requirements, performance context, and validation oracle.
- The selected platform route and unresolved proof obligations.

The platform skill owns instruction selection, coefficient/table layout,
register classes, ABI/live-in/live-out contracts, reserved registers, and the
platform kernel contract. The Slothy skill owns symbolic source and Slothy
regions after that contract exists.

## Workflow

1. Identify the scheme family, concrete variant, current specification or
   repository revision, and requested optimization scope. State a best-effort
   assumption only when it does not change the ring profile.
2. Read the matching family reference, then the concrete variant reference when
   applicable.
3. Fill `ring-profile.yml` from `assets/ring-profile-template.yml`. Source the
   coefficient ring, polynomial modulus, dimensions, operand ranges,
   representations, hot operations, and validation paths from the current
   specification or repository.
4. Identify unresolved transform, embedding, modular-arithmetic, reduction, or
   range decisions. Route those decisions to `lattice-polymul-core` and update
   the ring profile before continuing.
5. Build `operation-dag.yml` from `assets/operation-dag-template.yml` for one hot
   operation or coherent kernel family. Do not create one giant scheme-wide DAG.
6. Build platform-neutral `kernel-requirements.yml` from
   `assets/kernel-requirements-template.yml`. Preserve scheme semantics,
   representation transitions, ranges, public/secret dataflow, caller context,
   and forbidden changes.
7. Select the target platform route. Give the ring profile, operation DAG, and
   kernel requirements to the platform skill; let that skill produce the
   instruction-selection-level platform contract.
8. If the user requests Slothy, hand the three scheme artifacts plus the
   platform contract to `slothy-symbolic-asm-authoring`. Do not synthesize
   missing instruction, ABI, memory, or reserved-register contracts here.
9. Read a scheme roadmap only for a staged kernel campaign. Choose the first
   kernel from current profiling and caller impact rather than roadmap order
   alone.
10. For a Slothy campaign, apply the relevant checks in
    `references/review-gates/slothy-scheme-review-gates.md` after each artifact
    stage.

## References and assets

- For NTRU+ or derived NTRU-like work, read
  `references/families/ntru-like.md`; for concrete NTRU+, also read
  `references/variants/ntruplus.md`.
- For HAETAE or derived Dilithium-like work, read
  `references/families/dilithium-like.md`; for concrete HAETAE, also read
  `references/variants/haetae.md`.
- Read `references/ring-profile-operation-dag-kernel-requirements.md` for artifact
  boundaries and handoff gates.
- Read `references/roadmaps/ntruplus-kernel-roadmap.md` or
  `references/roadmaps/haetae-kernel-roadmap.md` only for the matching staged
  kernel campaign.
- For completely new ring details, read
  `../lattice-polymul-core/references/new-ring-intake.md`.
- For AArch64 Neon planning, read
  `../aarch64-neon-lattice-polymul/references/armv8-v9-neon-platform-model.md`
  only after the scheme/core artifacts are ready.

## Validation expectations

Produce sourced artifacts with explicit ring and representation contracts,
operand and intermediate ranges, kernel boundaries, target route,
range/correctness obligations, reference functions, tests/KAT paths, and
case-study-only warnings. Never treat a scheme name or roadmap as permission to
skip ring-specific validation.
