# Decision

Retain this audit as the research control plane before CF5-B.

The current evidence does **not** close any of the six end-to-end principles:
three have strong partial evidence (twist fusion, weighted BaseMul, reduction
placement), one has an internally clean but serializer-incomplete ABI
(layout), and two remain open (alternative GT axis order and inverse internal
liveness).

The next hard gate is `M5A-E2E-AUDIT1`: build an exact NTT9-first boundary and
layout model, without assembly. It must expose the LD3-to-row map, permutation
cost, resulting NTT16 consumer layout, memory-pass count, and register budget.
Reject the axis-order alternative before implementation if it adds a
coefficient memory pass or has no credible static cost path below the retained
NTT16-first design.

CF5-B remains the next implementation gate only after this structural question
has a documented answer. Production and the frozen SUPERCOP package remain
unchanged.
