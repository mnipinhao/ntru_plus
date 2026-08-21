# Where current GT Clean Encap loses

## Short answer

GT Clean does not lose in Forward NTT or general BaseMul.  Its complete
polynomial island is faster than Official in a same-ELF causal benchmark.

The current production binary loses because several small boundary debts and
a larger non-additive whole-image delivery cost outweigh that island win.

## Fresh production evidence

The formal ASLR-on SUPERcop-style benchmark reports:

```text
Official Encap StQ2   28032.71 cycles
GT Clean Encap StQ2   28277.95 cycles
GT - Official          +245.24 cycles
```

A second fresh-export test executes 20,000 encapsulations per process and
collects region-dominant PMU counts.  Median per call:

| Event | Official | GT Clean | GT - Official |
|---|---:|---:|---:|
| core cycles | 28,552.84 | 28,926.05 | **+359.28** |
| retired instructions | 70,337.13 | 69,682.23 | **-657.61** |
| retired loads | 9,146.21 | 9,909.23 | **+763.08** |
| retired stores | 1,857.97 | 1,778.62 | **-79.42** |

All eight paired PMU blocks show more GT loads, fewer GT instructions and
stores, and more GT core cycles.  The median cycle result agrees
with the independent formal StQ2 result.

This rejects the explanation that GT simply executes more instructions.

## Same-ELF polynomial-island evidence

The controlled same-ELF gate divides polynomial work into:

```text
R1  Decodeq(h)
R2  Forward(r) + Q24(rhat)
R3  Forward(m) + general BaseMul + add(m) + Q24(ciphertext)
R4  complete R1 + R2 + R3 island
```

Current Clean minus Official in the two link orders:

| Region | Normal TSC | Reversed TSC | Interpretation |
|---|---:|---:|---|
| R1 Decode h | +20.51 | +20.56 | proven GT local debt |
| R2 r path | -43.65 | -44.77 | GT winner |
| R3 final polynomial path | -37.17 | -43.44 | GT winner |
| R4 complete island | **-57.27** | **-64.04** | GT polynomial architecture wins |

R4 also saves 78.8--107.6 core cycles and 1,003 retired instructions.
Consequently the approximately +245-cycle full-Encap result cannot be assigned
to N5 Forward or B3 arithmetic.

## Load interpretation

The older region-scoped load closure assigns the GT-minus-Official load deltas:

```text
R1 Decode                  +105 loads
R2 r path                  +224 loads
R3 final polynomial path   +329 loads
sum                        +658 loads
observed R4                +654 loads
```

The closure is exact to four loads.  Therefore those loads are genuine GT
representation work, not hidden harness glue.  But 553 of the 658 summed extra
loads belong to R2/R3, which are faster than Official.  Removing aggregate
loads without regard to dependency shape is not a valid optimization goal.

R1 is the only demonstrated local polynomial component where extra load work
coincides with a cycle loss.

## Remaining small typed-boundary debts

After the selected high-range H1 Q24 path, the last phase attribution measured:

| Phase | Normal TSC | Reversed TSC | status |
|---|---:|---:|---|
| E1 input decode/CBD/SOTP | +12.08 | +11.90 | small stable debt |
| E2 two N5 Forwards | **-115.83** | **-120.45** | frozen winner |
| E3 general B3 | **-13.35** | **-11.95** | frozen winner |
| E4a add(m) | approximately 0 | approximately 0 | neutral |
| E4b serialize rhat | +12.47 | +20.97 | real but bounded |
| E4c H1 ciphertext residual | +15.60 | +22.96 | reduced small debt |
| E5 nominal hash/glue cut | +12.86 | +17.11 | not causal by subtraction alone |

E4b cannot use a sign-only centered pack: real producer values exceed q on the
first tested trial and reach absolute value 12,884.  Moving the same reduction
work to the Forward terminal does not delete it.  E4c has already had its main
approximately 100-core-cycle debt removed by the selected high-range Q24 path.

These visible boundary debts are only tens of cycles and do not add up to the
fresh +245-cycle formal gap.

## What is not a component debt

A causal outside-island test forced both predecessors to call the same physical
`noinline,noclone` shared code.  It found:

```text
middle hash/SOTP glue   +2.86 / -8.44 TSC
common tail             -0.06 / +1.28 TSC
```

There is no stable 50--100-cycle hash, SOTP, copy, clear, or common-tail
penalty.  Adjacent cumulative-prefix subtraction is not a valid component-cost
estimator for this caller.

## Final attribution

```text
Proven local debts:
  - Decode h boundary
  - rhat Q24 reduction/serialization
  - small residual ciphertext Q24 boundary

Proven winners:
  - two N5 Forwards
  - general B3
  - complete polynomial island

Not proven as intrinsic debt:
  - hashes/SOTP shared glue
  - copy/clear tail

Dominant explanation of the formal loss:
  - whole-prefix / whole-image executable delivery
  - relative hot-code geometry and frontend interaction
  - load-heavy GT representation contributes pressure, but aggregate load
    count alone does not predict performance
```

The fresh full loop establishes the production symptom (+359 core cycles,
fewer instructions, more loads).  Existing same-ELF causal gates establish
where it is not coming from.  No current evidence supports reopening N5 or B3
arithmetic.
