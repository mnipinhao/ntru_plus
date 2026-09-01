# Decision

Do not infer this gate from three isolated M5G runs. The three B3s share roots,
modulus, input lifetimes, nine simultaneous outputs, and the preserved other
column block. Pass only if the returned 45-instruction region assembles and
uses no reserved register, memory, stack, or spill instruction.

The gate passes. Freeze the 45-instruction SSA DAG and returned Slothy
evidence. Do not infer that level 2 fits: the solver uses all fifteen allowed
registers. The next gate must add the four eta/eta-inverse products and three
level-2 B3s with consumer-driven destructive reuse of the nine level-1
outputs, while the other column block remains live.
