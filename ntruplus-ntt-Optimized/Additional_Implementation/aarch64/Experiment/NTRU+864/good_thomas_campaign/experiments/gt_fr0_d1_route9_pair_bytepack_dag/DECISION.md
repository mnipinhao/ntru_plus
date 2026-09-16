# D1-P3B16 decision

Decision: **reject complete route9-pair plus byte packing under input-once and
no-scratch constraints.**

Retain P3B6.  The next useful ToBytes search is an exact/bounded optimization
of P3B15's partial-output completion schedule toward at most 26 live outputs,
or a genuinely partial route network measured against the same frontier.  Do
not assemble the 54-vector macro-DAG and do not reintroduce scratch.
