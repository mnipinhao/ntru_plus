# M5Q decision

Close M5Q as passed.  Keep M5O as the correctness baseline and M5P's rejection
as the performance baseline.

The next experiment is the user-selected register-contract change:

```text
GT core may use v0-v31
+ outermost public poly_ntt wrapper saves/restores d8-d15 once
```

Do not save inside each bank.  AAPCS64 requires preservation of only the low
64 bits, hence `d8-d15`, not eight full q-register stores.  Four `stp d,d` and
four `ldp d,d` add eight dynamic instructions; increasing the existing fixed
frame from 32 to 96 bytes needs no additional stack-adjust instruction.

The next symbolic DAG must exploit the extra registers rather than merely
allocate the unchanged 633 instructions.  First targets are:

1. eliminate the six destructive-B3 `orr` saves in each NTT9 core and the
   held-tail copy where liveness allows: current ceiling 13 copies per bank,
   78 per full Forward;
2. pin reusable q/root/main-stage/bit-reversal constants across component
   banks where table identity permits, instead of reloading them six times;
3. test whether the expanded live set enables a lower-instruction cross-stage
   DAG without stores or a larger memory pass.

Eliminating all 78 current helper copies but adding eight ABI saves gives only
70 net instructions, leaving 727 of the current 797-instruction gap.  Thus the
next hard gate is a feasibility and exact instruction-count gate, not yet an
expectation of beating Official.  It must state and machine-check every removed
instruction before Pi 5 timing.
