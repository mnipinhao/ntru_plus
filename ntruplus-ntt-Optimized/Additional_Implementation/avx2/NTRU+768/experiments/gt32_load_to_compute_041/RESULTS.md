# Results

## Decision

Load-to-compute is a real optimization axis, but it is consumer-specific.
Reducing retired loads is not itself sufficient.

| Probe | Dynamic exchange | Normal | Reversed | Decision |
|---|---:|---:|---:|---|
| Decode mask 0123 resident | +1 instruction, -13 loads | -7 cycles, 16/16 | -6 cycles, 16/16 | local qualified |
| B3 qinv per-block preload | +12 instructions, -36 loads | -9 cycles, 16/16 | -9 cycles, 16/16 | local qualified |
| Q24 pack-mask resident | +1 instruction, -47 loads | +2 cycles, 0/16 | +3 cycles, 0/16 | closed |
| Q24 pair-factor resident | +1 instruction, -47 loads | -1 cycle, 16/16 | -1 cycle, 15/16 | near-neutral; no promotion |

The Q24 pair-factor result does not pass the cross-method corroboration gate:
region PMU gives a median of about +1.1 core cycles despite approximately
-48.4 retired loads. The pack-mask version gives about +3.3 core cycles and
-47.2 retired loads. Both therefore remain experimental negatives.

B3 does pass cross-method corroboration. Region PMU gives approximately
+12 instructions, -36 retired loads, and -4.7 to -5.6 core cycles per call.
The tighter same-ELF paired harness reports -9 cycles in both placements.

## Mechanism

B3 uses the same qinv vector four times at the start of each of twelve blocks.
One explicit load supplies four register-source multiplies, then the existing
kernel overwrites that register as a Montgomery temporary. This removes load
uops from a multiply-heavy block without adding a long-lived register.

Decode has only one spare YMM. Keeping the most frequent mask resident removes
fourteen memory-source shuffles while preserving the four independent
validity accumulators. Trying to keep all four masks would require changing the
dependency structure and is outside this bounded gate.

Q24 shows why the policy must remain cycle-based. Its constant loads are hot
and overlap well with packet arithmetic. Removing them does not remove either
the vpmaddwd or vpshufb execution work, and the changed active instruction
geometry/scheduling offsets the reduced load pressure.

## Scope

GT Clean production sources were not modified. The two local winners are too
small to claim a full Encap improvement without a fresh same-image caller
gate. They are retained as qualified components for a future composite change;
Q24 constant residency is closed for the current serializer schedule.
