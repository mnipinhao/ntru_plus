# Pattern Library

Bundled fragments under `assets/patterns/` are reusable symbolic shapes:

- `neon-ntt-2layer-4butterfly.sym.S`
- `neon-ntt-1layer-8butterfly.sym.S`
- `neon-barrett-mul-const.sym.S`
- `neon-montgomery-mul-const.sym.S`
- `neon-twiddle-postinc-load.sym.S`
- `neon-pointwise-mul-4x32.sym.S`
- `neon-row-load-store-layout.sym.S`

## Use Rules

- Treat patterns as examples, not candidates.
- Copy only the shape that matches the active instruction DAG.
- Rename symbolic values to match the active DAG and contract.
- Re-check ranges, constants, lane widths, and memory offsets after copying.
- Never copy a pattern into a candidate `.S` before `kernel-contract.yml` and
  required baseline contracts exist.

## Pattern Review

After adapting a pattern:

- Every symbolic value must have a visible definition.
- Every constant load must match the contract representation.
- Every post-increment must match the baseline region or kernel contract.
- Every store must map to a contract output.
