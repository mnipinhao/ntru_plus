# M5L results

- Exact address gate: 16 halfword reads at `p8[768+8*t+bank]`; byte stride 16,
  pointer advance 256, no over-read.
- Exact DAG gate: both top residues pass 16 basis vectors and 40,000 seeded
  bound-range random vectors against the frozen scalar Algorithm-10 NTT16.
- Region: 65 real instructions: 16 lane loads, 13 public vector loads, six
  Algorithm-10 triples, eight adds/subtracts, six transposes, two `movi`, and
  two `tbl`.
- Remote: `pinhao@172.25.166.141:51208`, Slothy 0.2.2, checkout
  `d636d638d06b370d1acc5774ca31c9572d3d2e6f`.
- RA: OPTIMAL in 0.916156 seconds, selfcheck OK, no spills.
- Schedule: `split_heuristic_full:OK!`, 16 N1-proxy cycles.
- ABI audit: only `v0-v7,v16-v31` and `x1,x2,x4`; no `v8-v15`, stack,
  store, branch, or spill. Both returned artifacts assemble.
- Artifact SHA-256: allocated
  `39fb1f2e9e70e5770596e71355227268cf767707855138e45cf8bd93f4a2faf3`,
  scheduled
  `a0ecfaa2471bbbfb9284007e031e47994781257d63ef7e8907df3a7c76245399`,
  log `3976d5d10da9c1d88158d48cae68de031ef358a16dbb319d38dee2e9a4268b2b`.

This is a bounded producer sub-gate, not full Forward or benchmark evidence.
