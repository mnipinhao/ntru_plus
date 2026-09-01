# M5R decision

Close M5R as a passed hard gate and retain M5R-B as the new experimental GT864
Forward candidate.  Do not promote it to Production: it improves the rejected
M5O baseline but is still 6.1925% slower than Official Forward.

The canonical Slothy scorer says `promote` when M5O alone is treated as the
replacement baseline.  The repo-level decision intentionally remains
experimental candidate because M5O was already rejected by the Official gate.

The experiment answers the original question positively.  Eight additional
registers permit the Pass-2 DAG to delete all thirteen explicit preservation
copies per bank and keep `q`, `roots`, and `bitrev3` live across all six banks.
After the outer `d8-d15` ABI cost, the full path retires 91 fewer instructions
and measures 25.90 fewer cycles without a new coefficient memory boundary.

The next hard gate should target the remaining 706 instructions.  Additional
constant pinning is only worthwhile if a lifetime proof shows that the chosen
NTT16 or NTT9 constants can remain fixed without reducing scheduling quality;
otherwise the largest remaining structural target is the 1,998-instruction
pair of oriented NTT9 blocks identified by M5Q.
