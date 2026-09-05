# Decision

Pass D1-P3B3 and select paths independently: retain R9-A plus the stock API for
ToBytes, and retain direct C1 for FromBytes. On Pi5 they measure 1849.450 and
1183.250 cycles respectively. C1 ToBytes loses 15.68% to R9-A despite retiring
25 fewer instructions, and C2 loses both directions; reject those placements.

The Pi5 GCC object contains no vector spill. C1 is wholly stackless; C2 reverse
uses only a GPR ABI save/restore frame. These are experimental byte-boundary
selections, not Production promotion. The next hard gate is a production-shaped
KEM build that replaces only the selected direction at each real call site and
repeats byte-exact valid/tampered correctness plus paired PMU.

Withdraw the P3B2 54-vector impossibility claim. Exact input-once routing
witnesses use 16/14 partial outputs. They keep streaming/factorized routing
available and prevent presenting C1/C2 as an exhaustive architecture choice.

C2 uses public greedy output order but receives no unimplemented vector-reuse
credit. CT checker warnings refer to the compile-time direction selector
`decode`; source indices and loop counts are public. Feature audit is clean.
