# D1-P3B10 decision

Decision: **reject the scratch-integrated paired pack.**

The implementation is byte-correct, uses exactly the declared 432-byte public
scratch and has no unexpected coefficient spill.  It removes every packing
`TBL` and 121 retired instructions, but regresses complete ToBytes by 5.725
cycles.  Consequently the P3B9 primitive is useful only when two adjacent
outputs are naturally live together; it is not profitable under P3B6's current
completion order.

Do not combine partner scratch with further local cleanups.  Retain P3B6 as
champion.  The next search must change the vector routing/completion structure
itself or open a separately costed byte-friendly transform-domain ABI; further
instruction deletion around the same completion order is not supported by the
last three Pi 5 gates.
