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
implementations per host: shipping `aarch64-gt1152-a76` and `aarch64-gt1152-m1`
would let the benchmark pick, with the same checksum on both.

That second difference is so far **structure without content**: SLOTHY's
`neoverse_n1` and Apple M1 models have no widening-multiply classes, and every
kernel admitted here is built on `smull`/`smlal`.  See
[`ntruplus1152_opt/README.md`](ntruplus1152_opt/README.md); `cortex_a76` is the
only target that can currently be scheduled, and the only one this repository
can measure.

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
| SLOTHY for `cortex_a76` | **done — 3,054 -> 2,744 cycles, installed, all gates green** |
| SLOTHY for `neoverse_n1` and Apple M1 | **blocked on SLOTHY's models**, see below |
| `autogen.py` | written |
| `baseinv` numerator and finish | not yet written |

The generator is verified through the `ra` stage, whose output *is* assemblable
clean assembly: 4,000 trials x 1,152 coefficients against the shipped C oracle,
inputs on the declared [0,4095] plus the all-4095 and random-extreme cases,
**zero differences at all** — not even a different Montgomery representative —
and `max |out| = 1728` exactly as `normalize_d7` is designed to give.

Register-allocated but unscheduled it runs at **3,155 cycles** against the
intrinsics C's 3,054 — the honest baseline a symbolic clean tier starts from,
since the DAG order is the generator's and not a compiler's.  After the `timing`
pass it runs at **2,744**, against the official's 2,551 and a 2,376 floor.

Note one consequence of the symbolic choice: unlike mlkem-native's clean tier,
`*.sym.S` cannot be assembled directly.  The `ra` output stands in for it.
