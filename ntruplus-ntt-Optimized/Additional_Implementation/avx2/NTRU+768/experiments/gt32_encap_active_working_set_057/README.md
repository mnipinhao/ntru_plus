# GT32-ENCAP-ACTIVE-WORKING-SET-057

This experiment separates active polynomial cardinality from reserved frame
size.  It reuses the correctness-qualified lifetime schedule from experiment
031 and does not modify production Clean GT.

| Profile | Active polynomial states | Reserved scratch | Execution shape |
|---|---:|---:|---|
| A | 5 | 5 polynomials | Current out-of-place frontend landing in `c` |
| B | 4 | 5 polynomials | In-place `r/m` landing; fifth slot reserved but untouched |
| C | 4 | 4 polynomials | Same B hot body with the unused frame storage removed |

A and B enter the same `working_set_057_reserved` symbol and call the same
`encap_body` address.  They have the same stack reservation, selected GT
kernels, call count, and memory-operation count.  B changes only object
liveness: frontend output lands in the final `r` or `m` object, and the dead
`work` object later receives the B3/add result.

C calls the same `encap_body`, but necessarily uses a distinct wrapper in order
to reserve four rather than five polynomial objects.  It is secondary
attribution for the frame-release effect, not as clean a causal comparison as
A versus B.

No producer fusion, B3 fusion, arithmetic change, Q24 change, or new
representation is included.

## Reproduction

```sh
tools/build.sh
build/test_057
tools/run.py \
  --binary build/bench_057 --launches 48 --cpu 1 \
  --output results/working-set-48.json
tools/run_pmu.py \
  --binary build/pmu_057 --blocks 18 --cpu 1 \
  --output results/pmu-balanced-18.json
```

Both runners use balanced mirrored orderings and CPU 1 affinity.  The PMU gate
uses 20,000 full Encap calls per process.
