# NTRU+768 BaseMul callsite provenance

This inventory is taken from the unchanged Official `kem.c`.  It separates
operand provenance from the output contract; a layout opportunity is useful
only when both sides of that boundary agree.

| Caller edge | Operand A | Operand B | Next consumer | Reuse | Current mixed private BM applicable? |
|---|---|---|---|---|---|
| `keygen.h` | `g`: CBD/triple -> NTT | `finv`: baseinv(`f`) | `tobytes(pk)` | neither operand is used by another BM | No: requires the general `e=0` serialized-output contract |
| `keygen.hinv` | `f`: CBD/triple -> NTT | `ginv`: baseinv(`g`) | `tobytes(sk)` | neither operand is used by another BM | No: requires the general `e=0` serialized-output contract |
| `encap.c` | `h`: `frombytes(pk)` | `r`: CBD -> NTT | add NTT(`m`) -> `tobytes(ct)` | no BM reuse | No: attractive asymmetric producers, but requires general `e=0` mixed BM |
| `decap.m1` | `c`: `frombytes(ct)` | `f`: `frombytes(sk)` | inverse -> `crepmod3` | original `c` is later modified for `r2` | Yes: this is the current private `e=-1` mixed-BM island |
| `decap.r2` | `c`: decoded `c` minus NTT(`m2`) | `hinv`: `frombytes(sk)` | `tobytes` -> hash/verify | no later BM reuse | No: requires the general `e=0` serialized-output contract |

## Consequences

- There is no transformed operand consumed by two BaseMul calls, so a generic
  AoS+SoA shadow copy has no demonstrated amortization case.
- `decap.m1` is the only existing callsite matching the implemented
  `SoA(e=0) x AoS(e=0) -> lazy AoS(e=-1) -> inverse` contract.
- `encap.c` and `decap.r2` have especially promising asymmetric producer
  provenance, but they need a distinct general-scale mixed kernel and direct
  serialization/layout support.  The private inverse-only symbol must not be
  substituted there.
- The direct private-SoA decoder remains the enabling producer for
  `decap.m1`.  Materializing TILE4 AoS and then transposing it does not count
  as a production solution.

## Selected representation gate

The caller-private coefficient-polymul benchmark compares:

```text
AA: N5-AoS + N5-AoS + AoS/AoS B3
SA: N5-private-SoA + N5-AoS + SoA/AoS mixed BM
SS: N5-private-SoA + N5-private-SoA + SoA/SoA BM + AoS redeposit
```

All three then use the same I1, T9, and `crepmod3`.  This is an arithmetic
caller gate for representation selection; it does not claim that both inputs
of the real `decap.m1` callsite already have equally cheap producers.
