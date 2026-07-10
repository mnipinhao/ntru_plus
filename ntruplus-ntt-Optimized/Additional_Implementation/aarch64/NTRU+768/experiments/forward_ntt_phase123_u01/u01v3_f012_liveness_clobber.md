# U01v3 F012 Liveness / Clobber Analysis

Status: generated for E3; production default unchanged.

E3 extends the passing E1v2 F01 idea to block012. The new pressure is block2: its live-ins must survive both Stage345 block0 and Stage345 block1 before block2 can consume them.

Block2 handoff choice:

```text
Q16: q7
Q17: q11
Q18: q12
Q19: q13
Q20: q15
Q21: q16
Q22: q21
Q23: q19
```

This choice deliberately avoids `q2/q3/q4` because Stage12 still needs those twiddle registers while all fused outputs are being produced. It is also checked against Stage345 block2's instruction stream: each source register must not be written before the original load site it replaces.

Static contract:

```text
no_spill_allocation_feasible: True
same_as_interference_count: 0
interference_count: 0
spills: 0
raw_q_reloads: 0
duplicate_stage12: False
block2_moves: 7
```

Stage12 uses a tighter three-temp stripe schedule for E3. That matters because by the final stripe, 21 previous block0/block1/block2 outputs are already live, plus `q0/q2/q3/q4` and the current three outputs. A nine-temp Stage12 shape would not fit; the three-temp shape does.
