# P110 — 768's lead was one file, and 864 and 1152 can have it

P109 found 768's contestable remainder 2-6x better than 864's and 1152's, and
traced it to the hashing: identical permutation **counts**, identical outputs,
but GT 768 spending **152.8 ns a permutation against 864's 164.8 and 1152's
164.1**.  `shake256_prefixed` is character-identical in the three trees, so the
wrapper was not it.

## The verification, and the number that gave it away

P109's measurement ran each set in its own binary, so the spread could have been
code layout.  `verify.c` links **all eighteen hash calls into one process** --
three sets, two sides, three calls -- with every symbol renamed per set.  Same
answer:

| set | GT ns/perm | Official ns/perm | ratio |
|---|---:|---:|---:|
| 768 | **152.8** | 187.6 | **0.814** |
| 864 | 164.8 | 176.5 | 0.934 |
| 1152 | 164.1 | 178.0 | 0.922 |

Not layout.  And one figure was impossible: **152.8 is below the 158.33 the bare
permutation measured**, and no wrapper can cost less than nothing.  The bare
figure had been measured with 864's file.

## Three different Keccak permutations

| | instructions | M2 Pro |
|---|---:|---:|
| **GT 768** | **122** | **147.30 ns** |
| GT 864 | 146 | 158.33 |
| GT 1152 | 146 | 158.33 |
| upstream CE `f1600` | — | 158.32 |

All four byte-identical on the same state.  768 carries **mlkem-native's hybrid
scalar/vector routine**; 864 and 1152 carried one written for them.  Recomputed
against 147.3, GT 768's wrapper is **+4.9 ns a permutation** against 864's +6.5
and 1152's +5.8 -- **the three wrappers are equally good and the whole
difference was the permutation.**

## Landed

Same symbol, same AAPCS64 contract including the `d8-d15` save that 864's own
`test_keccak_v84a` asserts (100,003 states, passed).  Copied into both trees,
`97ef2d6b`:

| M2 Pro, ns | before | after | against Official + CE |
|---|---:|---:|---|
| 864 keygen | 4,338 | **4,147** | -4.6% -> **-8.8%** |
| 864 encaps | 4,981 | **4,682** | -5.2% -> **-10.9%** |
| 864 decaps | 4,045 | **3,866** | -2.5% -> **-6.8%** |
| 1152 keygen | 6,797 | **6,524** | -4.5% -> **-8.3%** |
| 1152 encaps | 6,535 | **6,133** | -6.0% -> **-11.8%** |
| 1152 decaps | 5,230 | **4,982** | -4.7% -> **-9.2%** |

Cortex-A76 has no FEAT_SHA3, the file compiles away there, and its numbers are
unchanged to within 6 ns.

## What it cost, and what it says

**Every M2 margin for both sets roughly doubled, from copying one file between
directories in the same repository.**

For comparison, the transform work this session -- P29's paired inverse, the
`ST3` widening and the packed tail normalisation, three landings with Slothy
runs and full gate suites -- moved 864's decapsulation from -1.1% to -2.5%.  The
file copy moved it to -6.8%.

The campaign spent itself on the Good-Thomas transform because that is what the
decomposition is *for*.  The transform is where GT is behind (its kernels are
slower than Official's in five of six measured cases on M2), and the lead came
from the symmetric side all along -- where the three sets were not even carrying
the same code.
