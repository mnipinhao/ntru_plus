# M5A end-to-end structural audit report

Audit execution: **pass**. This means the frozen evidence is internally
consistent; it does not mean that all six optimization principles pass.

## Pipeline lock

- **CF4** is the executable complete-operation control: CF0 Forward x2,
  direct FR-ISO2 BaseMul, direct FR-ISO2 Inverse. It passed 117/117
  polynomial products, but its cost ledger rejects it against FR-0.
- **CF5-A** is a Forward-only candidate. It passed its producer/consumer
  boundary and correctness gates and estimates 4726 dynamic instructions,
  but it is not yet a code-size-faithful full Forward or a 2F+B+I binary.

## Audit matrix

| Audit | Status | Pass condition | What the evidence says |
| --- | --- | --- | --- |
| GT axis order | **open** | not met | The current order is structurally justified, but the alternative has neither an exact boundary implementation nor end-to-end timing. Therefore axis order is not yet empirically settled. |
| Twist absorption | **partial** | not met | CF5-A proves eight fewer Algorithm-10 mulmods per Forward and removes the separate post-transform stage, but it has not been integrated and timed with BaseMul+Inverse; 64 standalone inverse row corrections remain. |
| Inverse backward liveness | **open** | not met | The polynomial-multiplication API consumes all 864 natural coefficients. Output-level pruning is impossible; only a node-level inverse DAG plus a real downstream serializer contract could reveal dead internal work, and neither exists yet. |
| Weighted BaseMul | **partial** | not met | The complete 288-leaf weight census and isolated specialized-kernel timing pass. The whole-product win does not: CF4 is already +463.162 cycles before inverse correction. |
| Layout/serializer co-design | **partial** | not met | The internal FR-ISO2 boundaries are zero-conversion, but the real SUPERCOP serializer/caller boundary is not linked. Layout co-design cannot be declared complete before that consumer is explicit. |
| Reduction placement | **partial** | not met | Reduction placement has one successful measured result in BaseMul, but no transform-wide placement search or end-to-end timing exists. |

## Quantitative facts exposed by the audit

- CF5-A fuses FR-ISO2 scaling into scaled NTT9 DAGs and deletes eight
  complete Algorithm-10 multiplications per Forward versus CF0. The
  separate post-NTT9 correction stage becomes zero, but the candidate is
  not yet timed end to end.
- The executable CF4 path still pays 208 standalone representation
  correction vector mulmods: `2 * 72` in Forward plus `64` in Inverse.
- BaseMul has exactly 288 cubic leaves: 144 use `Y^3-9`, 144 use
  `Y^3-3`. Both weights are quadratic residues and cheap small public
  constants; the direct kernel deletes 72 widening reductions and saves
  334.194 p50 cycles on the measured Cortex-A76.
- There are zero full-buffer conversions at Forward→BaseMul and
  BaseMul→Inverse. The pipeline still materializes P8+tail at algorithmic
  transform pass boundaries; that is traffic, but not representation-only
  conversion debt.
- All 864 natural polynomial outputs are live in the current API. No
  inverse pruning can be claimed without a node-level DAG and the actual
  serializer's required-output contract.

## Next hard gate

**M5A-E2E-AUDIT1: exact NTT9-first axis/layout model.** Do not write the
large assembly candidate yet. First derive its LD3-to-row map, required
shuffle/transpose and memory traffic, resulting NTT16 input layout, and
register budget. Kill it immediately if it needs another coefficient
memory pass or has no credible static path below NTT16-first.

This is intentionally prior to CF5-B: it answers whether the current axis
choice is a measured design decision or merely inherited structure.
