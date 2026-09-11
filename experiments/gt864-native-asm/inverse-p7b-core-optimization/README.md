# P7-B — Inverse core optimization before consumer fusion

P7 established that the existing radix-16 CT choice is locally sound; it did
not optimize the complete Inverse NTT.  P7-B therefore freezes the current
public contract and works inside `gt864_inverse_rinv_asm` before P8 is allowed
to fuse raw Inverse output with ternary conversion.

P7-B0 is measurement-only.  It must decompose the production call into the
aggregate inverse9 producer, six main NTT16 calls, the tail NTT16 call,
`center864`, and wrapper/scratch lifecycle on the Pi 5.  Static instruction
counts are retained only as context; they do not select the bottleneck.

P7-B1 selected the inverse9 constant-materialization DAG.  The production core
used every SIMD register except `v0` and `v5`, while materializing the same
Barrett-Shoup pair `(722,6844)` six times.  `generate_b1.py` keeps that pair in
the two free registers and removes 24 MOV/DUP instructions while adding four at
entry, for a net saving of 20 instructions per call and 240 per complete
Inverse.  It explicitly models V/Q/D/S/H/B names as one register and rewrites a
destructive instruction's sources before ending the destination live interval.
Both details were found by a deliberately failed early correctness candidate.

`optimize_b1.py` is timing-only: it uses `/Users/chenpinhao/slothy`, disables
renaming and spills, and therefore cannot conceal pressure by selecting a new
allocation or stack traffic.  The frozen, tested result is
`candidate.b1.clean.S`; `generate_b1.py` remains the readable DAG generator.
The raw candidate is intentionally retained in the measurements because it
shows that deleting instructions without rescheduling made the kernel slower.

Results are in `RESULTS.md`, `p7b0-results.json`, `p7b1-results.json`, and the
generation/Slothy JSON ledgers.  Raw CSVs and build packages are disposable and
remain under `build/` or the Pi path
`/home/pi/ntruplus-p7b-20260911-ffee627b`.
