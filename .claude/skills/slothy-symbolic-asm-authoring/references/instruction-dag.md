# Instruction DAG

The instruction DAG is Codex's scheduling intent. Slothy may schedule and
allocate it, but Codex must define the dependencies.

## Requirements

- Name every logical input, output, constant, load, store, and intermediate.
- Record true dependencies, tied operands, destructive operands, and memory
  order constraints.
- Record which operations may commute or be reordered.
- Record range changes after reductions, narrowing, packing, or unpacking.
- Keep load/store offsets public and traceable to the memory contract.

## Authoring Rules

- Select the DAG before symbolic assembly.
- Use symbolic value names that match the DAG nodes when practical.
- Do not add instructions only because they appear scheduler-friendly.
- Do not remove reductions, masks, narrowing, or packing nodes unless the
  contract changes and the user approves.

## Review Checklist

- Every candidate instruction maps to one DAG node or documented scaffolding.
- Every DAG output appears as a candidate live-out or store.
- Every live-out has a path from live-ins/constants.
- Memory dependencies reflect aliasing, pointer post-increments, and stores.
- Tied operands are explicit enough for Slothy target-model support.
