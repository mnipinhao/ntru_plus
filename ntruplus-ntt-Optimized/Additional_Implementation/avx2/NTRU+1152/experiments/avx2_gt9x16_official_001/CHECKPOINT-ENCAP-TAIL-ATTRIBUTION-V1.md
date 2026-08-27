# ENCAP-TAIL-ATTRIBUTION-V1

## Scope

This checkpoint decomposes the cumulative NTRU+1152 encapsulation tail without
changing production arithmetic or adding attribution-only ASM.  Both sides
start from semantically equivalent resident transformed `r`, `m`, and `h`
states.  Every timed entry independently resets and prepares those states; the
three boundaries are nested executions, not nested warm states:

```text
T0 = resident h projection
T1 = resident h projection + MA2 arithmetic
T2 = resident h projection + MA2 arithmetic + ciphertext serialization
```

The launch-level component estimator is:

```text
H = delta(T0)
M = delta(T1) - delta(T0)
S = delta(T2) - delta(T1)
```

`H + M + S == delta(T2)` is checked within every launch.  Component medians
are used only for ranking; independent medians are not added together.

## Correctness and contract

- The Natural-Q resident-`h` projection is raw-exact against the generated
  1152-cell ownership map.
- T1 outputs serialize byte-exactly against Official.
- Timed GT T2, a separately replayed cumulative production sequence, and
  Official T2 produce identical bytes.
- GT T2 is the frozen scale-4 MA2 path followed by exactly one Direct H1
  `inv4`; the attribution harness does not add a normalization.
- The frozen forward is persistent-AoS + Natural-Q + T0-beta.  The lazy
  Barrett-reduction side candidate is deliberately not included.

## Method

- Class: `supercop-derived-gt9x16-prod3-encap-tail-attribution-v1`.
- Pinned CPU: physical P-core CPU 1.
- Frequency policy: performance governor, turbo disabled.
- Compiler: fixed-common SUPERCOP O3GC recipe.
- 9 fresh launches, 96 observations per label per launch.
- Balanced same-ELF order: Official, GT, GT, Official.
- Controls: normal/reversed placement, ASLR on/off.
- Headline placement: `normal`, predeclared from completed
  `ENCAP-CALLER-ATTRIBUTION-V2`; this campaign did not select its own fastest
  placement.

## Result

Headline (`normal`, ASLR on), GT minus Official:

| boundary/component | median cycles | bootstrap 95% CI | direction |
| --- | ---: | ---: | --- |
| T0 / resident-h projection | +248.15 | [+245.81, +253.50] | GT slower, 9/9 |
| T1 absolute | +386.48 | [+383.79, +389.25] | GT slower, 9/9 |
| MA2 arithmetic (`T1-T0`) | +137.46 | [+135.06, +142.79] | GT slower, 9/9 |
| T2 absolute | +608.94 | [+606.52, +611.19] | GT slower, 9/9 |
| ciphertext serialization (`T2-T1`) | +222.42 | [+218.85, +225.06] | GT slower, 9/9 |

The direct and reconstructed T2 medians are both `+608.9375` cycles and the
maximum launch-level telescoping residual is zero.

All four controls agree.  Absolute T2 debt ranges from `+597.79` to `+609.60`
cycles; every T0/T1/T2 and derived component is positive in 9/9 launches for
every setting.  ASLR-off has one address tuple and ASLR-on has nine for both
placements.

## Decision

The old approximately `+605`-cycle tail bucket is confirmed and explained by
three material costs rather than one hidden outlier:

```text
resident-h projection       about +248 cycles
ciphertext serialization    about +222 cycles
MA2 arithmetic              about +137 cycles
```

Resident-`h` projection is the largest single component, so the next
architecture checkpoint should map the public-key decode/resident-`h`
producer directly to the frozen Natural-Q MA2-native `h` ABI.  The serializer
remains a close second and must not be treated as solved.  No new MA2,
serializer, or forward ASM is authorized by this attribution result alone.

Evidence is stored under
`results/gt9x16-prod3-encap-tail-attribution-v1-intel155h-20260827-002/`.
The failed `-001` attempt produced no retained timing evidence: it selected an
older incomplete campaign implementation missing an included ASM source.  The
successful campaign uses the already-qualified `-exp003` normal/reversed
placement copies from the preceding V2 checkpoint.
