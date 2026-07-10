# U01v3 F0123 G3 Model

Status: model-only.  No physical G3 ASM emitted.  Production default unchanged.

Baseline:

```text
G1 = E3/F012 semantic-regalloc + delayed block3 scratch consume
G1 cycles: 2694
G1 instructions: 3743
G1 retained block3 q loads: 24
```

The core issue:

```text
G1 Stage12 computes block3 out3 and stores it to scratch.
Stage345 block3 later reloads Q24..Q31 from that scratch image.
If block3 is regenerated after E3/F012, raw D has already been overwritten by out3.
Avoiding the block3 q load therefore needs either raw reloads or extra prefix storage.
```

Candidate summary:

```text
G3a_delayed_block3_producer_after_E3: status=hard_gate_fail, delta_vs_G1=201, raw_q_reloads=96, risk=high: removes 48 memory ops but adds 96 raw q loads, 9 twiddle loads, and 144 arithmetic instructions
G3b_partial_shared_prefix_t1_t3: status=not_plausible, delta_vs_G1=72, raw_q_reloads=0, risk=high: doubles prefix memory traffic and adds finish arithmetic
G3c_bounded_recompute_no_prefix: status=hard_gate_fail, delta_vs_G1=201, raw_q_reloads=96, risk=high
```

Stage345 block3 direct handoff itself is not the blocker.  Its original destination registers are preclobber-safe, so a producer could hand off to those registers if the producer source contract were cheap enough.

Decision:

```text
emit_physical_asm: false
reason: no G3 candidate passes the hard gate
G3a/G3c: fail no_raw_q_reload and instruction-count gate
G3b: no raw reload, but too much prefix memory traffic and +72 instructions
```

Next meaningful direction:

```text
Keep G1 as the current F0123 sweet spot.
Stop F0123 expansion unless we revisit deeper Phase123 layout/producer order.
```
