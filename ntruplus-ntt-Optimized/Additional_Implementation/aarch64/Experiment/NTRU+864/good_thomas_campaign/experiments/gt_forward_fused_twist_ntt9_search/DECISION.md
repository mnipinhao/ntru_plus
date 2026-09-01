# M5S-A decision

Status: **reject**.

The candidate passes algebra, contract, no-spill, linked correctness, and ABI
gates, and it reduces each block from 136 to 128 instructions.  It nevertheless
regresses complete Forward on Pi 5 by 0.754509%.  The paired-load DAG must not
replace M5R-B and remains default-off.

The cyclic-orientation search also proves that this candidate family cannot
remove the four eta corrections.  Reopening Forward fusion requires a genuinely
different arithmetic DAG that removes at least one Algorithm-10 multiplication,
not another encoding of the same 24 mulmods.
