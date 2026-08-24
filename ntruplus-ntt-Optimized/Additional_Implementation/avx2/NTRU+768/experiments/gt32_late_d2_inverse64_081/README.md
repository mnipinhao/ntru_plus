# GT32-LATE-D2-INVERSE64-081

Architecture-critical executable gate for replacing the selected quartic
`B3 -> inverse32` seam with a persistent quadratic `QBM -> inverse64` seam.
GT Clean and all KEM callers are unchanged.

## Corrected semantic bridge

Gate 080's canonical discrete-log coordinate is not the physical frequency
coordinate consumed by the selected production inverse.  The latter was
recovered from the exact inverse impulse response:

```text
physical Q -> inverse32 k
0,4,2,6,16,20,18,22,8,12,10,14,24,28,26,30,
1,5,3,7,17,21,19,23,9,13,11,15,25,29,27,31
```

Using that coordinate, `omega64=3160`, `omega64^2=1784`, and tile-specific
`mu0`, the six-tile oracle proves 153,600 coefficient identities:

```text
inverse64 plane 0 = [c0[0], mu0*c2[0], ..., c0[31], mu0*c2[31]]
inverse64 plane 1 = [c1[0], mu0*c3[0], ..., c1[31], mu0*c3[31]]
```

The executable test additionally reconstructs the D2 branches with explicit
CRT and feeds the result to the qualified current I0/I1 redeposit.  It matches
the current quartic B3 endpoint before testing inverse64, so QBM and inverse
attribution are independent.

Correctness: 2,136 impulse, structured, and random differential trials pass
modulo q.  Observed absolute output bounds were 1,989 for control and 1,863 for
candidate; these observations do not widen any production contract.

## Implementations adjudicated

V1 paid the full physical-Q routing with generic four-source `vpshufb` masks.
It exposed two real AVX2 lane-local redeposit requirements; both are included
in the candidate rather than repaired by the harness.

V2 is the required mode-preserving mutation.  It recognizes the selected
physical mapping as a fixed 4x4 word transpose per sixteen-Q vector and lowers
naturalization from 172 to 124 instructions.  Correctness remains exact.

## SUPERcop-style directional evidence

The gate uses one fixed ELF, CPU1 pinning, ASLR on, fresh processes, 32 timings
per process, stabilized quartiles, and balanced `C/K/K/C` order over 16 blocks.
The host exposed two exact approximately 1x/5x frequency regimes, so the
two-process block median is retained only for audit.  Both regimes reject the
candidate; the stable 1x cluster is used for magnitude attribution.

```text
                         control      candidate       delta
V1 full seam             ~262.0       ~479.5          +217.5 TSC
V2 full seam             ~261-262     ~464.5          ~+203 TSC
V2 candidate block wins                              0 / 16
```

Component attribution (fresh-process low stable regime):

```text
control B3 -> post-I1             157.25 TSC
candidate D2/QBM                  159.50 TSC   (+2.25)

control inverse32 + normalize      88.00 TSC
candidate route + inverse64       318.50 TSC  (+230.50)
  physical naturalization          51.00
  inverse64 core                  223.50
  coefficient-plane -> TILE4       18.50
```

The full composition recovers some overlap, but not enough to change the
decision.

## Work and code shape

```text
                                control   candidate V2
static instructions                557       1017
memory operands                    153        341
movement-family instructions       122        340
selected text bytes               2428       4435
RSP references / spills              0          0
vector mul instructions            198        160
```

The candidate really removes vector multiplication work, but replaces it with
far more physical routing and a 64-axis inverse.  QBM is only at parity with
the current B3/post-I1 producer; the measured loss is owned by inverse64 and
its required entry/output routing, not by a generic permutation that remains
unoptimized.

## Decision

`CLOSED_FOR_SCOPE` for the current late-SoA input ABI, immediate i16 inverse64,
current AVX2 target, and current TILE4 common endpoint.  The algebraic proof is
retained, but this executable architecture does not proceed to KEM integration.

This does not claim that every possible D2 representation is impossible.  A
future reopen requires a genuinely different consumer contract that removes
the 64-axis routing/output repayment, not another schedule of this seam.
