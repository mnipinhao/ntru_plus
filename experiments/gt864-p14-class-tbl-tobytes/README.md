# P14 — class-local TBL4 ToBytes routing

P14 replaces P9's edge-at-a-time `INS` routing with 15 exact source-
neighborhood classes per 432-coefficient top.  Within one class, eight source
Q vectors remain resident and each completed output Q is formed by two
independent four-register `TBL` operations plus `ORR`, then immediately
normalized, packed and stored.  A maximum-overlap class path needs 64 rather
than 120 source Q loads per top.

This is not the rejected P6 zero-scratch architecture: it preserves P9's
input/output boundary and still does not create coefficient scratch.  It also
does not wait for adjacent output pairs, the infeasible P3B22 condition.
