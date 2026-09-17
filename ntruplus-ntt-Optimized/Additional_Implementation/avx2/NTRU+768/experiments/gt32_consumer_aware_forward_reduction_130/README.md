# GT32 consumer-aware Forward reduction gate (130)

Experiment 128 rejected its best checkpoint-free NTT32 because its terminal
bound, 17388, exceeded the historical `BM_BOUND=10788`.  Later executable
range audits proved that this was not the selected production contract:
current Forward is conservatively bounded by 18424, current `B3+m` by 20296,
and the selected Q24 reducer is exact over every signed 16-bit input.

This gate reopens that consumer-boundary premise and audits the other bound
inherited from 128. It does not search a new transform. It takes 128's closest
exact network (`mode_bits=00000000100000000000`),
which removes both S2 identity-Montgomery packets in every tile, and propagates
its per-Q bounds through the actual general-B3 quartic formulas, all 192
production lambda entries, the R-squared finalizer, message addition, and the
Q24 signed-word input contract.

The three profiles are:

```text
R0  current r, current m
R1  checkpoint-free r, current m
R2  checkpoint-free r, checkpoint-free m
```

No terminal center, B3 reduction, or Q24 correction is added to the candidate.

## Consumer-bound result

Both consumer-aware candidate profiles are signed-int16 safe:

| profile | max B3 raw | max B3 final | max product+m |
|---|---:|---:|---:|
| R0 production | 10804 | 1872 | 20296 |
| R1 candidate r | 10584 | 1870 | 20294 |
| R2 candidate r+m | 10584 | 1870 | 19258 |

The modular consumer oracle also checks 4096 randomized quartic products and
message additions using deliberately different signed representatives.  All
16384 degree outputs match modulo q.

Thus the stale B3 ceiling was not a valid rejection: once a terminal value
exists, B3 and Q24 accept it without extra work.

## Selected-frontend range result

128 also fixed its NTT32 input bound to 1728. The selected executable
frontend's conservative bound is 5275. Re-propagating the candidate from 5275
gives:

```text
S1  10550
S2  21100
S3  first GS packet pre-add 42200  (>32767)
```

Therefore the current interval proof cannot establish signed-word safety.
This is a proof failure, not an observed counterexample: it ignores
producer-side correlations and is deliberately not wrapped modulo 2^16.

## Executable result

A zero-spill matched ASM lowering was nevertheless built to determine whether
the arithmetic idea has cycle value. It required one physical correction: the
S5 table uses packed qword order `0,2,1,3`, not logical `0,1,2,3`.

- 10000 valid ternary-input differential trials pass through Forward(r/m),
  r-Q24, general B3, and B3+m Q24;
- no candidate stack reference or spill is present;
- static body: 225 instructions / 1004 bytes versus control 237 / 1056;
- dynamic credit: 12 Montgomery chains, about 48 instructions per Forward;
- SUPERCOP cpucycles, pinned same ELF:

| placement | control | candidate | delta | 95% bootstrap CI | wins |
|---|---:|---:|---:|---:|---:|
| normal | 629.94 | 597.23 | -33.00 | [-33.46,-31.54] | 16/16 |
| reversed | 630.44 | 596.75 | -33.33 | [-34.33,-32.19] | 16/16 |

The checkpoint deletion is therefore a real local cycle win, not an
instruction-count guess.

## Decision

Gate 131 subsequently completed the producer-aware proof and found an exactly
reachable ternary pre-add of 34781. Its generated witness wraps under
`vpaddw` and makes this assembly disagree with the control modulo q. The
candidate is therefore closed for the actual Encap input contract. Reopen
only with a different factorization (or a genuinely smaller producer
contract); adding a center/reduction before S3 would repay the work just
deleted and is not this candidate.

GT Clean is not modified.
