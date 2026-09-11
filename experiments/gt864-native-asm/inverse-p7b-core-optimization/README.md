# P7-B — Inverse core optimization before consumer fusion

P7 established that the existing radix-16 CT choice is locally sound; it did
not optimize the complete Inverse NTT.  P7-B therefore freezes the current
public contract and works inside `gt864_inverse_rinv_asm` before P8 is allowed
to fuse raw Inverse output with ternary conversion.

P7-B0 is measurement-only.  It must decompose the production call into the
aggregate inverse9 producer, six main NTT16 calls, the tail NTT16 call,
`center864`, and wrapper/scratch lifecycle on the Pi 5.  Static instruction
counts are retained only as context; they do not select the bottleneck.

P7-B1 will select exactly one measured primary category.  A candidate is not
accepted for scheduling alone: it must delete arithmetic or routing, keep both
transform memory boundaries, preserve R^-1 input through terminal R0 recovery,
stay within the closed int16 range, allocate without spill, and improve both
the complete Inverse and complete Decaps boundaries.  Production remains
unchanged until all correctness, alias, AAPCS, wipe, KAT and Pi 5 gates pass.

