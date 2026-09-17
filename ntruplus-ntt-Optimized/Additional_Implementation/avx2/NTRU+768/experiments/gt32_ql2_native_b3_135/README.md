# GT32 QL2-native general BaseMul (135)

This executable gate adjudicates the candidate selected by experiment 134.
Production GT Clean is unchanged.

```text
control:   M x M -> current general B3 -> QL2
candidate: QL2 x QL2 -> qword-local vpmaddwd/REDC16
                     -> mandatory Mont(R^2) -> QL2
```

Neither side is charged a synthetic representation conversion.  The gate
therefore measures the intrinsic consumer cost that a persistent-QL2 Encap
would pay.

## Correctness

The first implementation exposed that the historical AoS lambda table used
TILE4 full-AoS leaf order, not QL2 partial-transpose leaf order.  Gate 135
therefore generates lambda/qinv tables by relabelling production M-order
lambdas to the exact QL2 leaf order.

After that correction:

- 1,000 random products are mod-q equal to current general B3;
- `out == a` and `out == b` both pass;
- the required `e=-1 -> e=0` `Mont(R^2)` finish is present;
- the hand-written AVX2 leaf has zero stack references and zero spills.

## SUPERcop-style result

CPU 1, ASLR on, installed SUPERcop `libcpucycles`, 16 fresh launches,
alternating paired order:

| placement | candidate - control | 95% bootstrap CI | wins |
|---|---:|---:|---:|
| Normal | +215.62 cycles | [+214.11,+215.99] | 0/16 |
| Reversed | +218.12 cycles | [+217.81,+218.59] | 0/16 |

Fixed-process PMU corroboration, normalized per BaseMul call:

| event | candidate - control |
|---|---:|
| core cycles | +218.53 |
| retired instructions | +318.83 |
| port 0 uops | +37.90 |
| port 1 uops | +92.64 |
| port 5/11 uops | **+220.41** |

The loss is not inferred from instruction count.  The executable result and
PMU agree that qword-local dot construction plus output compaction and the
mandatory scale finish produce a real backend-routing/multiply cost.

## Repayment closure

Experiment 134 offered `-432` boundary routes per Encap, but those routes are
not 432 cycles.  Existing directly measured credits give the useful scale:

- persistent-r Forward plus serializer in 101: about `-112` core cycles;
- removing current B3 `M->QL2` output formation: at most the roughly
  `24-cycle` 103 B3 presentation debt;
- even granting the entire roughly `30-cycle` current Decode debt as an
  optimistic h-side credit gives only about `-166` cycles.

That deliberately favorable repayment is still smaller than the measured
`+216..+219` native-B3 loss.  A full KEM caller would therefore not be an
informative next measurement for this lowering.

## Decision

```yaml
GT32-QL2-NATIVE-B3-135:
  correctness: PASS
  zero_spill: PASS
  performance: FAIL
  decision: CLOSED_FOR_SCOPE
  closed_scope:
    - persistent QL2 inputs
    - qword-local D0-D3 vpmaddwd dot construction
    - unsigned REDC16
    - explicit Mont(R^2) e0 repayment
    - current AVX2 target
  production_modified: false
```

This does not close every persistent-QL2 family.  Reopen only with a new
BaseMul factorization that removes the qword-local routing class, absorbs the
`e=0` correction into an operation already required by Q24, or supplies a
measured load-dependency premise large enough to repay more than 218 cycles.
Rescheduling this same 37-instruction loop is not a sufficient premise.

Run `make benchmark` to reproduce.
