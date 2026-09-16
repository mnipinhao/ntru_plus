# D1-P3B0 results

Status: **PASS — emit two independent route9 candidates.**

After relabeling physical Official groups by
`[0,3,6,1,4,7,2,5,8]` and renaming `J_i=I_(8-i)`, the exact rule is:

```text
J_i.lane[l] -> logical output (i + l + 1) mod 9
```

Thus the eight lanes are precisely eight cyclic perfect matchings and output
`i` is the missing edge of row `J_i`.

The source rows can be canonicalized with at most seven `EXT` rotations before
an ordinary 8-by-8 transpose. However, no global source-row order reproduces
all nine Official output lane orders after deleting the missing row. R9-A must
therefore pay a final lane repair; the simplistic claim that one transpose
vector is already every required Official vector is false under the exact ABI.

Static upper bounds per route9, including vector input/output and conservative
constant loads, are 87 instructions for R9-A and 90 for the independent
three-bank TBL R9-B. Across twelve calls both remain far below the measured
roughly 5,207 instructions of the current coordinate bridge, but only Pi 5 can
decide their cycle economics. R9-C is admitted by a multi-metric Pareto gate,
not an instruction-only cutoff; this search found no third concrete
non-dominated network to emit.
