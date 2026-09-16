# D1-P3B5 decision

Reject the R9-A-output-local fusion.  It implemented the wrong output contract:
the root-derived Official transform order without the AArch64 `shuffle2` byte
ordering.  Pi 5 cross-check stopped before PMU at the first tagged mismatch.

Do not repair this body by adding a full Official scratch array; that recreates
P3B4.  Continue under D1-P3B6 with the composed-map input-once schedule.  Keep
this compact source and decision only until the successor is independently
reproducible, then archive or remove the redundant rejected body during campaign
cleanup.
