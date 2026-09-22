# Slothy Driver Template

Use this reference when producing a human-reviewable Slothy driver draft.

The driver is generated support code. It should be easy for the user to review,
edit target model choices, and run externally. Codex should not run Slothy
unless the user explicitly asks in a later step.

## Rule: Generate driver templates, not final optimized code

### When to use

Use after symbolic source, region labels, and kernel contract are complete.

### Preconditions

- `kernel-contract-template.yml` or `assembly-kernel-plan.yml` identifies source
  path, output path, start/end labels, target architecture, target
  microarchitecture, workflow, live-outs, and reserved registers.

### Driver pattern

```python
import slothy
import slothy.targets.aarch64.aarch64_neon as AArch64_Neon

# Select target model here.
# Example:
# import slothy.targets.aarch64.cortex_a72 as Target
# import slothy.targets.aarch64.apple_m1_firestorm as Target

SOURCE = "kernels/<kernel>.sym.S"
OUTPUT = "kernels/<kernel>.opt.S"

s = slothy.Slothy(AArch64_Neon, Target)
s.load_source_from_file(SOURCE)

# Configure reserved registers, live-ins, live-outs, and loop options here.
# Keep this file generated but human-reviewable.

s.optimize(
    start="slothy_start_<kernel_id>",
    end="slothy_end_<kernel_id>",
)
s.write_source_to_file(OUTPUT)
```

The local asset `assets/slothy-driver-template.py` expands this skeleton for
one-pass, RA-then-window-opt, and macro RA/unfold/window-opt workflows.

### Range/correctness requirements

- Driver labels must match symbolic source labels.
- Reserved-register policy must match ABI and kernel contract.
- Workflow must match region size and macro usage.
- Output file paths must not overwrite symbolic source.

### Validation checklist

- Check target model import.
- Check source and output paths.
- Check start/end labels.
- Check reserved registers.
- Check live-outs and `inputs_are_outputs` policy.
- Check whether generated outputs overwrite previous generated artifacts.

### Common mistakes

- Using global Slothy when the repository expects vendored Slothy.
- Forgetting to update target model from placeholder.
- Writing output over symbolic source.
- Using one-pass driver for a medium or macroized region.

## Rule: Keep workflow-specific generated outputs explicit

### When to use

Use when the selected workflow is B or C.

### Preconditions

- `kernel.workflow` is `ra-then-window-opt` or
  `macro-ra-unfold-window-opt`.

### Driver pattern

- Workflow A output: `kernel.opt.S`.
- Workflow B outputs: `kernel.alloc.S`, then `kernel.opt.S`.
- Workflow C outputs: `kernel.alloc.S`, `kernel.real_alloc.S`, then
  `kernel.opt.S`.

### Range/correctness requirements

- `.alloc.S` should preserve instruction order for RA-only passes.
- `.real_alloc.S` should contain unfolded real AArch64 in the region.
- `.opt.S` may reorder instructions but must preserve dependencies.

### Validation checklist

- Compare every generated stage to the previous stage.
- Confirm generated comments are not confused with emitted instructions.
- Confirm final output is assembled and tested before benchmark.

### Common mistakes

- Inspecting only final `.opt.S`.
- Treating synthetic macro timing as final timing.
- Forgetting that exact physical registers may vary across runs.
