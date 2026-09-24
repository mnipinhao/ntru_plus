# P134 — canonical reduction in the full serializer, NTRU+864 and NTRU+1152

`reduce_canon` (full `tobytes`) was Barrett (`sqrdmulh` + `mls`, landing in
(-q, q)) then a sign mask and a second `mls`.  The second half is replaced by
`add` + `umin` (the AVX2 exp002 canonicalisation, already used by GT's small
serializer): four instructions either way, one multiply fewer, which matters
where multiplies own a pipe (A76 V0).

`exhaustive.c`: identical for all 65,536 int16 inputs, and equal to x mod q.

| | M2 keygen / encaps / decaps | A76 keygen / encaps / decaps |
|---|---|---|
| 864 | -7 / -4 / -8 ns | -0.39 / -0.41 / -0.45% |
| 1152 | -11 / -11 / -11 ns | -0.40 / -0.47 / -0.54% |

P129 harness, three interleaved sessions, HEAD against the change.  Encaps
moves although it only serializes with the small path: the compiler keeps one
shared body for both paths.  KAT, M2 + Linux `make check`, TIMECOP pass.
