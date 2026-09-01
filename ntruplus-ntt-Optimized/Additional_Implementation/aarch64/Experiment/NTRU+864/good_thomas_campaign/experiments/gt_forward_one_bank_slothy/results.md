# M5M results

- Exact DAG: both top residues pass 16 basis plus 20,000 seeded bound-range
  vectors each; main packed NTT16 is exact-equal to scalar Algorithm 10.
- Bounds: sampled main maximum 8523; inherited exhaustive/correlation-aware
  NTT16 maximum 9342 and complete NTT9 maximum 28568.
- Region: 633 real instructions; 144 meaningful coefficient halfwords and 56
  public vectors loaded; zero coefficient stores.
- Remote: Slothy 0.2.2 at checkout
  `d636d638d06b370d1acc5774ca31c9572d3d2e6f` on
  `pinhao@172.25.166.141:51208`.
- RA: OPTIMAL in 143.014540 seconds, selfcheck OK, spills forbidden.
- Schedule: approximately 20-instruction split windows,
  `split_heuristic_full:OK!`, 158 N1-proxy cycles.
- Emitted audit: exactly `v0-v7,v16-v31` and `x0-x5`; fixed `v17/v16` survive
  to their consumers; no `v8-v15`, stack, store, branch, or symbolic leak.
- Both returned assembly artifacts assemble as arm64 objects.
- SHA-256: allocated
  `adc07ce6f5feee890d12dac64d757f64b60fb767e1d02b09730ec1e8f007a608`,
  scheduled
  `fbf03349658111e2a82263c7f67d58c0c28e03592417eb8eba591f814e0bdf28`,
  RA log
  `aa8f0b762836623c712bf3b61ebed57681a1eba21ff7a29862733010c0493def`,
  schedule log
  `47dde5fafb6e268c471bef69b36ed4a9f33f8be818dfc72554729a80d3f80a98`.

This proves bounded one-bank allocation and scheduling feasibility.  It is
not a full Forward correctness, Pi 5 timing, or SUPERCOP result.
