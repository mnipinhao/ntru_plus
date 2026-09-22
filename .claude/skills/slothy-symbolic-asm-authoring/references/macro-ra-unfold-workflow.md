# Macro RA / Unfold / Window Optimization Workflow

Use this reference when a symbolic AArch64 Neon region is too large for a simple
one-pass Slothy solve.

Source basis: `mnipinhao/slothy_and_ra` demonstrates three workflows:
allocate+optimize together, allocate first then window-optimize, and macro
RA/unfold/window-optimize using a vendored Slothy checkout.

## Workflow selection summary

| Workflow | Use for | Typical input | Typical outputs |
| --- | --- | --- | --- |
| A: allocate and optimize together | small kernels, simple butterflies, modular multiply micro-kernels | `kernel.sym.S` | `kernel.opt.S` |
| B: allocate first, then window-optimize | medium kernels, 2-4 butterfly fragments, pointwise multiply with reductions | `kernel.sym.S` | `kernel.alloc.S`, `kernel.opt.S` |
| C: macro RA, unfold, then window-optimize | larger repeated structures, multi-layer NTT fragments, repeated matrix-vector accumulation fragments | `kernel.macro_sym.S` | `kernel.alloc.S`, `kernel.real_alloc.S`, `kernel.opt.S` |

Codex writes symbolic sources and driver/config drafts for the selected
workflow. Codex does not run the workflow unless the user explicitly asks later.

Prefer a vendored or local Slothy checkout. `slothy_and_ra` uses
`extern/slothy`; do not assume a globally installed package is the intended
backend.

## Rule: Workflow A, allocate and optimize together

### When to use

Use for small kernels.

### Preconditions

- Region is ideally fewer than 50 instructions.
- Live ranges are simple.
- Solver time is expected to be seconds to minutes.

### Authoring pattern

- Use symbolic vector temporaries.
- Enable allocation and scheduling in one pass.
- Disable spills unless the contract explicitly permits them.
- Expected input: `kernel.sym.S`.
- Expected output: `kernel.opt.S`.

### Range/correctness requirements

- Reordering must preserve memory order and arithmetic dependencies.

### Validation checklist

- Compare symbolic source to `.opt.s`.
- Confirm emitted instructions use concrete registers.
- Confirm instruction order may change.
- Run kernel tests.

### Common mistakes

- Using one-pass solve on a medium region that should be split.
- Allowing spills accidentally.
- Treating exact physical register choices as stable.

## Rule: Workflow B, allocate first then window-optimize

### When to use

Use for medium kernels such as 50 to 150 instructions.

### Preconditions

- One-pass allocation plus scheduling is too slow or fragile.
- Instruction order should first be preserved for audit.

### Authoring pattern

- Pass 1: functional-only register allocation with no reordering.
- Pass 2: schedule the allocated real assembly using split/window heuristic.
- Keep `.alloc.s` and `.opt.s` as distinct generated artifacts.
- Expected input: `kernel.sym.S`.
- Expected outputs: `kernel.alloc.S`, then `kernel.opt.S`.

### Range/correctness requirements

- `.alloc.s` should preserve instruction order while assigning registers.
- `.opt.s` may reorder instructions but must preserve dependencies.

### Validation checklist

- Compare `.sym.S` vs `.alloc.s`: order preserved, concrete registers emitted.
- Compare `.alloc.s` vs `.opt.s`: final schedule changes.
- Treat unused-output warnings as expected only when the driver deliberately
  permits extracted-region dead values.

### Common mistakes

- Running scheduling before allocation on a medium region.
- Mistaking verbose split-heuristic progress for a hang.
- Forgetting to configure live-outs.

## Rule: Workflow C, macro RA then unfold then window-optimize

### When to use

Use for large or repeated kernels where direct allocation on the fully expanded
stream is too expensive.

### Preconditions

- The repeated blocks can be represented as macro-ish pseudo-instructions.
- Macro specs expose all real register constraints.
- Final scheduling will run on unfolded real AArch64 instructions.

### Authoring pattern

- Write macroized symbolic stream.
- Run functional-only synthetic RA.
- Unfold macros without another solver-backed allocation pass.
- Run window optimization on the unfolded real region.
- Keep macro definitions and generated artifacts reproducible.
- Expected input: `kernel.macro_sym.S`.
- Expected outputs: `kernel.alloc.S`, `kernel.real_alloc.S`, then
  `kernel.opt.S`.

### Range/correctness requirements

- Macro specs must expose hidden constraints, such as consecutive destination
  registers for structure loads.
- Placeholder macro timing must not be interpreted as final performance.

### Validation checklist

- Compare symbolic macro source to `.alloc.s`.
- Compare `.alloc.s` to `.real_alloc.s` and check macros unfold in the region.
- Compare `.real_alloc.s` to `.opt.s`.
- Inspect hidden constraints such as consecutive register pairs.

### Common mistakes

- Hiding real register constraints inside macro expansion.
- Interpreting synthetic macro timing as real AArch64 timing.
- Removing `@slothy:no-unfold` from scaffolding macros.

## Driver configuration notes

- Workflow A should set `constraints.functional_only = False`,
  `constraints.allow_reordering = True`, and `constraints.allow_spills = False`.
- Workflow B pass 1 should set `functional_only = True` and
  `allow_reordering = False`; pass 2 should set `functional_only = False`,
  `allow_reordering = True`, `variable_size = True`, and enable split heuristic.
- Workflow C pass 1 should be synthetic functional-only RA; pass 2 should call
  `slothy.unfold(..., macros=True, aliases=False)`; pass 3 should run
  window optimization on real unfolded AArch64.
- `allow_useless_instructions = True` can be appropriate for extracted regions,
  but the report must say why unused-output warnings are expected.
- Concrete register numbers are not stable across solver runs; inspect emitted
  constraints and correctness, not byte-for-byte register choices.
