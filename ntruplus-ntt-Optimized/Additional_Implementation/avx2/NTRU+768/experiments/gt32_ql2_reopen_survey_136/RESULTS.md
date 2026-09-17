# Experiment 136 results

## Headline

All three Gate-135 reopen conditions were investigated.  None currently
supplies enough executable credit to reopen persistent QL2 native BaseMul.
This is not a statement that every future QL2 factorization is impossible.

## 1. Qword-local routing deletion

For a direct quartic dot product, output `k` pairs `a_i` with
`b_(k-i mod 4)`, with lambda weighting on wrapped terms.  Exhausting all
`24 x 24 = 576` asymmetric coefficient orders proves that a fixed A/B qword
layout can make at most one of the four output dots consume the stored B order
directly.  At least three distinct non-native B packets remain.  Reordering
the four coefficients therefore cannot delete the qword-local routing class.

The broader alternatives already have executable evidence:

- Gate 135 D0--D3 uses the arithmetic floor of four `vpmaddwd` diagonals but
  pays `+220.41` port-5/11 uops and `+218.53` core cycles per call.
- Producer-preexpanded diagonals merely materialize a larger ABI; they move
  routing into producer stores and consumer loads.
- The exact rank-7 tensor changes the multiplication class, but Experiment
  059E loses `+237` TSC with its faithful exit and `+398` TSC with its dense
  mixed-scale exit.

Result: the cheap coefficient-order search class is exhausted.  The broader
family remains open only for a genuinely producer-native evaluation basis
whose BaseMul **and** Q24 exit are sparse.  Another D0--D3 schedule is not a
reopen premise.

## 2. Scale absorption

The natural native kernel returns `e=-1`; Gate 135 pays a complete 48-vector
`Mont(R^2)` pass to return to `e=0`.  Removing exactly that pass passes 1,000
scale-equivalence trials.

SUPERcop/libcpucycles, CPU 1, ASLR on, 16 fresh paired launches:

| placement | median TSC delta | 95% bootstrap CI | favorable launches |
|---|---:|---:|---:|
| Normal, natural `e=-1` minus current `e=0` | **-107.67** | `[-109.46,-106.29]` | 16/16 |
| Reversed | **-106.92** | `[-107.52,-105.83]` | 16/16 |

Thus roughly **107 cycles is an optimistic ceiling** for this reopen: it assumes
Q24 absorbs the scale for zero cost.  That is only about 49% of Gate 135's
`+218.12`-cycle loss.  A real endpoint cannot be free: product `e=-1` and
message `e=0` cannot be added as i16 representatives, and multiplication by
`R = -147 mod q` exceeds i16 range at the established bounds.  It requires a
wide mixed-scale reduction or a scaled message producer.  The existing exact
scale-consumer gate already proves that such algebraic fusion retains 48
conversion chains and gives only `-24` static instructions for its concrete
whole edge.

Result: scale absorption is real and sizeable, but it cannot independently
repay native QL2 BaseMul.  It is useful only as part of a new combined DAG that
also removes a substantial part of the routing loss.

## 3. Load-dependency repayment

Experiment 133 estimates L1D-pending cycles per Encap as `3.58` for Official
and `16.76` for QL2: a directional delta of only `13.18`, not a 218-cycle
budget.  As a deliberately impossible upper bound, classify every positive
direct leaf delta as fully removable load debt:

```text
Decode 30 + CBD 25 + r serializer 45 + SOTP 13 + QL2 B3 12.75
= 125.75 cycles
```

Even that over-credit reaches only 57.7% of the required repayment, while
several entries are known arithmetic/serialization/context costs rather than
load stalls.

Result: the current production profile rejects the load-dependency reopen.
It may reopen only with new PEBS/LBR evidence identifying a specific removable
dependency chain worth more than 218 caller cycles.

## Decision

```yaml
GT32-QL2-REOPEN-SURVEY-136:
  routing_reorder: SEARCH_CLASS_EXHAUSTED
  routing_new_factorization: NO_EXECUTABLE_CANDIDATE
  scale_absorption: REAL_BUT_INSUFFICIENT_ALONE
  scale_free_ceiling_tsc: 106.92..107.67
  load_dependency_repayment: REJECTED_BY_MEASURED_UPPER_BOUND
  gate135_reopened: false
  production_modified: false
```

The honest remaining reopen condition is now narrower: present a concrete
combined representation/factorization that removes qword routing and can also
use the 107-cycle scale-finalizer credit.  Without that new DAG, persistent
QL2 native BaseMul remains closed for scope.
