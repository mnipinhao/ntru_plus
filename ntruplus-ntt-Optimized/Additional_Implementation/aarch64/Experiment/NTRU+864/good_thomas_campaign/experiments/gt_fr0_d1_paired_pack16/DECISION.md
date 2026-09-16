# D1-P3B9 decision

Decision: **accept the paired-pack16 primitive for a complete integration
experiment; do not promote it yet.**

Pairing eliminates every packing `TBL`, reduces retired instructions by 316,
and saves 174.300 cycles across the complete ordered 864-coefficient boundary.
This is a real Cortex-A76 gain, not a static-count inference.

P3B6 cannot supply adjacent pairs simultaneously without storage.  The next
candidate must explicitly pay and expose 54 partner store/load round trips per
top-level two-top call, use at most 432 bytes of fixed public scratch, retain
the exact composed byte map, and pass the same arbitrary signed-int16 oracle.
Only the measured complete boundary can replace P3B6.
