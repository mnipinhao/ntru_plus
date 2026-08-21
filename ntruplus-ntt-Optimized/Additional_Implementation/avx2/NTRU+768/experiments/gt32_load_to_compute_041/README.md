# GT32-LOAD-TO-COMPUTE-041

This experiment tests a new optimization axis without modifying GT Clean:
trade additional cheap register loads/instructions for fewer repeated
memory-source constant loads. Core cycles, not instruction count, decide.

The bounded executable probes are:

- Q24-LTC keeps the production M-lazy Q24 arithmetic and packet order. It
  keeps the pack mask in otherwise unused ymm12. The pair factor remains a
  memory operand because q and v stay live through the reducer. Static
  expectation: +1 explicit instruction and -47 loads.
- B3-LTC preloads qinv into ymm13 at each T16 block, uses it for the four
  initial products, then allows the existing Montgomery temporary to overwrite
  it. Static expectation: +12 instructions and -36 loads.

Decode has four mask values and only one free YMM while the four-chain validity
accumulator is live. The bounded probe therefore keeps the most frequent 0123
mask in ymm13: +1 instruction, -13 net loads. It does not alter the accumulator
or transpose schedule. Holding all four masks remains liveness-constrained.

Run make check and then make benchmark. The generated load_map.json records
the audited dynamic classes; benchmark.json records multi-launch
normal/reversed results.

See RESULTS.md for the completed decision. GT Clean production files are
inputs only; every candidate is generated under this experiment directory.
