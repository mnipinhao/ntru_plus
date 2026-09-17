# Development tiers for NTRU+1152 AArch64

Modelled on [mlkem-native](https://github.com/pq-code-package/mlkem-native)'s
`dev/aarch64_{clean,opt}` split, with one deliberate difference in each
direction.

| tier | what it is |
|---|---|
| [`ntruplus1152_clean`](ntruplus1152_clean) | the arithmetic, as **symbolic-register** assembly emitted by a generator that authors data-flow rather than register allocation |
| [`ntruplus1152_opt`](ntruplus1152_opt) | the same kernels after SLOTHY, **one directory per microarchitecture** |
| `ntruplus-GT-Production/.../NTRU+1152` and the SUPERCOP leaves | what ships |

**Difference from mlkem-native, first:** its `clean` tier is handwritten
assembly with `.req` aliases and macros, so registers are already allocated and
SLOTHY only reorders.  This repository's tradition, established across the
NTRU+864 campaign, is `V<name>` symbolic registers produced by a Python
generator; SLOTHY then does register allocation *and* scheduling, in two passes
(`ra` with `functional_only`, then `timing` with the split heuristic).  That
gives the solver more freedom and keeps the generator readable as data-flow.

**Difference from mlkem-native, second:** it targets a single microarchitecture
(`Arm_Neoverse_N1_experimental`) and `autogen` installs that one result.  Here
each target gets its own `opt` directory, because SUPERCOP selects among sibling
implementations per host: shipping `aarch64-gt1152-a76` and
`aarch64-gt1152-m1` lets the benchmark pick, and both carry the same checksum.

## Layout

```
ntruplus1152_clean/
    generate.py          authors the kernels as data-flow DAGs
    src/*.sym.S          generated symbolic assembly, SLOTHY's input
ntruplus1152_opt/
    Makefile             one rule per (kernel, target)
    cortex_a76/          Pi 5; the only target this repo can measure directly
    neoverse_n1/         mlkem-native's target, for comparison
    apple_m1_firestorm/  the local development host
scripts/
    autogen.py           install one tier and target into a package directory
```

## Which kernels are here, and why only those

Every candidate was measured against its issue floor before being admitted, and
most were rejected:

| kernel | measured | floor | utilisation | admitted |
|---|---:|---:|---:|---|
| `basemul_rinv` | 3,054 | 2,376 | 78% | **yes** |
| `baseinv` numerator | 3,711 | 2,952 | 79% | **yes** |
| `baseinv` finish | 1,095 | 864 | 79% | **yes** |
| `ntt9` (P16) | 484/bank | 450 | 93% | no |
| codec `tobytes_small` (P19) | 836 | 792 | 90% | no |
| codec `frombytes` (P19) | 723 | ~720 | ~100% | no |

The three admitted kernels are the ones still written as NEON intrinsics C, and
they sit at a consistent 78-79% — that consistency is itself the evidence that
the problem is GCC's scheduling rather than the algorithm.  `basemul_rinv` has
the hardest evidence of all: the official implementation reaches 2,551 on an
instruction multiset identical to ours.

## Status

| piece | state |
|---|---|
| `clean` generator and `basemul_rinv.sym.S` | written, **verified** |
| SLOTHY `ra` pass (register allocation) | runs clean, self-check OK |
| SLOTHY `timing` pass (scheduling) | first solve in progress |
| `autogen.py` | written, not yet exercised on a package |
| `baseinv` numerator and finish | not yet written |

The generator is verified through the `ra` stage, whose output *is* assemblable
clean assembly: 4,000 trials x 1,152 coefficients against the shipped C oracle,
inputs on the declared [0,4095] plus the all-4095 and random-extreme cases,
**zero differences at all** — not even a different Montgomery representative —
and `max |out| = 1728` exactly as `normalize_d7` is designed to give.

Register-allocated but unscheduled it runs at **3,155 cycles** against the
intrinsics C's 3,054.  That is the honest baseline the `timing` pass has to
beat, and it is what a symbolic clean tier costs: the DAG order is the
generator's, not a compiler's.

Note one consequence of the symbolic choice: unlike mlkem-native's clean tier,
`*.sym.S` cannot be assembled directly.  The `ra` output stands in for it.
