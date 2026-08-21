# Results

## 256-launch address factorial

Each process is pinned to logical CPU 1. Each launch reports medians from 1024
measurements per profile. ASLR remains enabled, while the profile page offsets
inside the executable cage remain fixed.

| Profile | Median TSC | Difference from OO | 95% bootstrap CI |
|---|---:|---:|---:|
| OO | 7842 | reference | -- |
| GO | 7838 | -2 | [-2, -2] |
| OG | 7844 | +2 | [+2, +2] |
| GG | 7840 | -2 | [-2, 0] |
| DUP | 7840 | 0 | [0, 0] |

The wrapper/SHAKE factorial interaction is -1 TSC with CI [-2, 0].

The small discrepancy between differences of separately reported absolute
medians and the paired median differences is expected; decisions use paired
launch deltas.

## Interpretation

All effects are at most two TSC, far below the predefined 10--15-cycle action
threshold and two orders of magnitude below the approximately 100-cycle 050
cumulative checkpoint movement.

The same-offset duplicate at different higher virtual-address bits is exactly
neutral. Across 256 ASLR-enabled launches there is no evidence that the tested
Official-like versus GT-like Hash/SHAKE page offsets cause a meaningful complete
hash-path latency difference.

The relocation-free templates use indirect calls to make clone bytes exactly
identical. They preserve the Hash/SHAKE algorithm and common Keccak backend but
are not byte-exact copies of the production relative-call wrappers. This limits
the claim to the controlled address-geometry hypothesis; it does not claim all
possible executable-image interactions are impossible.

## Decision

```text
Hash wrapper address effect:       CLOSED
SHAKE address effect:              CLOSED
wrapper/SHAKE geometry interaction:CLOSED
050 +~100 as actionable Hash debt: REJECTED
```

No offset sweep, Hash rewrite, or production placement rule is justified.
The serializer retains a real, separately observed frontier movement, but the
hash-checkpoint movement is non-component cumulative behavior and should no
longer be used as an optimization budget.

