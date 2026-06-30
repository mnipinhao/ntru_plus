# Slothy Structural Strategy

Date: 2026-06-30

Scope: structural contract and integration safety only.  No Slothy run was
performed, no `.opt.s` candidate was generated, and production defaults were
not changed.

## Current Evidence

Small source-order or local production-window Slothy attempts are no longer
enough promotion evidence.  The current evidence is:

| route | result | conclusion |
| --- | --- | --- |
| InvNTT Stage45 canonical stripes | correctness passed, but the initial small win did not reproduce and the all-four stripe candidate regressed on Pi5 PMU | route stopped |
| generic/rminus1 basemul one-loop | Slothy reported `OPTIMAL` and correctness passed, but Pi5 PMU regressed | source-order one-loop route rejected |
| Forward NTT local-window campaign | final-store solver infeasible; stage12 parser-blocked by internal labels; stage345 candidate segfaulted before correctness output | no correctness-pass candidate |

Main rule:

```text
Small source-order local Slothy windows are no longer enough.
Future Slothy work requires explicit structural contract and safe integration.
```

Slothy model cycles remain useful for diagnostics, but they are not promotion
evidence.  A candidate needs correctness, Pi5 PMU against the correct baseline,
and repeat/non-regression evidence.

## Slothy Input Hygiene Checklist

Every Slothy input region must pass this checklist before running the solver:

1. Region start/end labels exist physically in the input file.
2. The region contains no unsupported internal marker labels.
3. The region contains no unsupported instruction forms.
4. The region contains no branch/call/ret unless explicitly allowed.
5. The region contains no `adr`/`adrp` symbolic address setup unless the parser
   supports it or it is explicitly allowed.
6. Constants/table pointers are either live-in or explicitly materialized
   outside the schedulable region.
7. Reduction chains are intact.
8. Store/layout groups are not cut in half.
9. Instruction count is known.
10. Source equivalence to production or canonical macro expansion is
    documented.

Lightweight preflight helper:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/window_inputs/check_slothy_input_hygiene.py
```

Example:

```sh
python3 ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/window_inputs/check_slothy_input_hygiene.py \
  --file ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/window_inputs/forward_ntt_ntt32_final_store_marked.s \
  --region slothy_start_forward_ntt_ntt32_block0_final_reduce_store:slothy_end_forward_ntt_ntt32_block0_final_reduce_store
```

The helper intentionally stays small.  It catches missing labels, internal
labels, `adr`/`adrp`, branch/call/ret, and reports instruction count.  It does
not replace the real Slothy parser or the kernel-specific live-range contract.

## Materialization Rules

Prefer benchmark-only materialized inputs when production source labels are too
coarse or unsafe:

- Do not add experimental labels to production ASM unless the project already
  treats those labels as non-executed metadata.
- Normalize labels, comments, blank lines, and local marker names when checking
  equivalence.
- Record both production parent instruction count and materialized child
  instruction count.
- If production is cross-scheduled and materialization uses canonical macro
  expansion, state that limitation explicitly.

Materialized inputs are Slothy inputs, not promotion artifacts.  A generated
candidate still needs a benchmark-only integration wrapper and full correctness.

## Benchmark-Only Integration Contract

Each Slothy candidate must document the following before it is wired into a
benchmark-only variant:

1. Live-in vector registers.
2. Live-out vector registers.
3. Live-in scalar registers.
4. Live-out scalar registers.
5. Clobbered registers.
6. Stack/scratch usage.
7. Constant/table pointer usage.
8. Memory reads.
9. Memory writes.
10. In-place aliasing assumptions.
11. ABI wrapper assumptions.
12. Expected output layout.
13. Expected representative/range contract.

For Forward NTT this means the contract must include at least:

- `x0` destination base and row/scatter pointer convention.
- `x4` row base / scratch convention.
- `x10` scatter pointer convention.
- `x12` twiddle/table pointer convention.
- `x14` scatter bound convention.
- `v0` q/reduction constants.
- Exact GT block-major row-bitrev store map.

## Crash-Safe Benchmark Policy

If a candidate benchmark segfaults or exits before correctness output, classify
the campaign as an integration-contract failure.

Rules:

- Do not proceed to PMU interpretation.
- Do not report cycle deltas.
- Do not mark the candidate as current best.
- Do not commit the generated candidate artifact unless it is explicitly needed
  as a minimal diagnostic.
- Stop the local-window campaign and fix the structural contract first.

Correctness output must appear before PMU is considered valid, for example:

```text
correctness,total_mismatches=0
correctness,total_mismatches=0,valid_cases=64
```

## Forward NTT Structural Next Action

Current target state:

```yaml
forward_ntt_production_windows:
  status: needs_structural_strategy
```

Required next action before any new Forward NTT Slothy run:

1. Produce label-clean materialized Forward NTT inputs.
2. Move `adr`/table pointer setup outside schedulable regions or explicitly
   model it as live-in.
3. Define explicit live-in/live-out contracts.
4. Add crash-safe benchmark-only wrappers before rerunning Slothy.
5. Require standalone correctness and KEM/full-path correctness before PMU.

Do not mark Forward NTT as active until these items exist.

## Global Target State

No Slothy target is currently active for immediate local-window scheduling.
Next active Slothy work requires structural/window-contract preparation.

Current statuses:

| target | status |
| --- | --- |
| `forward_ntt_production_windows` | `needs_structural_strategy` |
| `generic_rminus1_basemul` | `needs_new_strategy` |
| `invntt_rminus1_row1_stage45_stripes` | `stopped` |
| `polyinv` | `external_algorithm_first` |
| `encap_residual_hash_copy` | `stopped` |
| `crepmod3` | `stopped` |
