# P91 — why the M2 margins are small, measured rather than inferred

The question: NTRU+864 and NTRU+1152 beat Official by 15-23% on Cortex-A76 and
by 1-6% on M2 Pro with CryptoExtension.  Where does the difference go?

## Two measurement faults found first

**Key generation rejects and retries.**  `do { randombytes(coins); r = gen(...) }
while (r)`.  On one stream the spread between the cheapest and dearest single key
generation is **11x**, 5,708 ns against 64,375.  Which keys a timed batch draws
depends on where in the stream it starts, which depends on how many warm-up
iterations the build managed, which depends on its speed.  Every key-generation
number taken before this is unreliable, including the one that started this
investigation -- an "Official + GT Keccak" build measuring *slower* than
"Official + CE" at 1152.  `rb2.c` reseeds before every timed batch, so all
builds generate the identical sequence of keys.

**The role profiler was silently dropping rows.**  `sample` prints one `???` row
per address for assembly that carries no `.size`, and the parser matched none of
them.  In any profile of a build linking upstream's `CE/f1600.S` that is **46-71%
of the samples**, all of the Keccak permutation, discarded without a word.  The
parser now resolves them by address and refuses to return if under 98% of the
samples are attributed.  Earlier profiles are unaffected -- none of them linked
that file.

## The permutation is identical on M2 and is not on A76

Counted by interposing on the permutation, 200 operations each, identical RNG:

| set | keygen | encap | decap |
|---|---:|---:|---:|
| 768 | 13 | 21 | 12 |
| 864 | 14 | 24 | 14 |
| 1152 | 21.4 | 32 | 19 |

**Official and GT issue exactly the same number, everywhere.**

Cost per permutation, measured directly:

| | Official | GT | |
|---|---:|---:|---|
| M2 Pro, CryptoExtension | 158.2 ns (`CE/f1600.S`) | 158.4 ns (`keccakf1600_v84a.S`) | **identical** |
| Cortex-A76, no CE | 493.1 ns (portable C) | 386.7 ns (`keccakf1600.S`) | **GT 1.27x** |

With FEAT_SHA3 present both sides run the same algorithm on the same
instructions.  Without it, Official has portable C where GT has hand-written
scalar assembly, and that 27% applies to half or more of every operation.  **That
is the whole reason the A76 margins are three to fifteen times the M2 ones**, and
it has nothing to do with the Good-Thomas work.

## What is left to compete over

Permutation time is the count times 158.3 ns and is the same on both sides, so
only the remainder is contestable.  Totals from `perop5.c` -- gated, reseeded,
all six binaries built in one session:

| set/op | perm | share | Official rest | GT rest | GT ahead on rest | margin | **ceiling** | **realised** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 768 keygen | 2058 | 49% | 2106 | 1738 | 17% | -8.8% | -51% | 17% |
| 768 encap | 3324 | 70% | 1431 | 751 | **48%** | -14.3% | -30% | **48%** |
| 768 decap | 1900 | 51% | 1797 | 1237 | 31% | -15.1% | -49% | 31% |
| 864 keygen | 2216 | 49% | 2338 | 2110 | 10% | -5.0% | -51% | 10% |
| 864 encap | 3799 | 72% | 1458 | 1189 | 18% | -5.1% | -28% | 18% |
| **864 decap** | 2216 | 53% | 1927 | 1880 | **2%** | **-1.1%** | -47% | **2%** |
| 1152 keygen | 3388 | 48% | 3735 | 3410 | 9% | -4.6% | -52% | 9% |
| 1152 encap | 5066 | 73% | 1901 | 1477 | 22% | -6.1% | -27% | 22% |
| 1152 decap | 3008 | 55% | 2486 | 2272 | 9% | -3.9% | -45% | 9% |

"Ceiling" is what the margin would be if GT's non-permutation work cost nothing.
Encapsulation cannot exceed -27 to -30% on this machine however good the
arithmetic gets, because the permutation is seventy percent of it.

## So the answer is in two layers

**Every set loses the same thing on M2**: the Keccak advantage that is worth
13-20% of the total on A76 is worth exactly zero here, and the contestable
fraction is only 27-52% to begin with.

**864 and 1152 additionally do less with what is left.**  On the contestable
part 768 is 17-48% ahead of Official, 1152 is 9-22%, and 864 is 2-18%.  **864's
decapsulation is the outlier at 2%** -- 1,880 ns against Official's 1,927, where
768's decapsulation manages 1,237 against 1,797.

## A caution about the next level down

Splitting "rest" further into sponge and arithmetic needs better than sampling.
The profile puts GT's sponge wrapper at 46-109 ns against Official's 163-505, a
real and consistent saving, but it also attributes 2,171 and 2,275 ns to the
same fourteen permutations in two builds -- a 5% disagreement, which on a
2,000 ns bucket is 100 ns.  Any claim about arithmetic at the 50-100 ns level
inside `rest` should be measured by linking, not by sampling.
