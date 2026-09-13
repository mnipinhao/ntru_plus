# P24 — P23 ToBytes production promotion

P24 compares committed P18 production (`4b7a3b83^`) with the committed P23
three-output schedules (`4b7a3b83`).  It does not copy from the working tree at
benchmark time.  Both packages are created by `git archive` from the recorded
revisions, then validated and timed in an isolated Pi 5 directory under
`/home/pi/supercop-20260831/bench/pinhao`.

The external symbols, FR0 input, canonical wire output, Full/Small range
contracts, disjoint-buffer ABI and public wrapper cleanup policy are unchanged.

P24 passed every promotion gate on `pi@100.99.191.9`.  The exact results are
recorded in [RESULTS.md](RESULTS.md) and `pi-results.json`; production remains
linked through the existing `gt864_p18_tobytes_{full,small}_asm` ABI names.
