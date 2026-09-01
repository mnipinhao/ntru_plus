# M5P decision

Reject the current M5O performance hypothesis.  GT is slower than Official by
6.80--6.83% in every complete Pi 5 repetition, despite achieving higher IPC.
The stable 797-instruction excess is the first-order cost signal.

Keep M5O as a correctness-proven experimental transform, but do not proceed to
full-KEM ABBA, SUPERCOP, or Production promotion.  The next hard gate should
decompose dynamic instructions by top split, six-bank control, NTT16, NTT9,
reductions, and stores, then define a concrete instruction-removal target.  In
particular, distinguish unavoidable GT arithmetic from repeated helper setup
and call/control overhead before changing scheduling or layout.

M5P also closes the exact-alias question positively: `out == in` is safe for
the complete M5O wrapper and passed 384 Pi 5 cases with sentinels.  Partial
overlap remains outside the contract.
