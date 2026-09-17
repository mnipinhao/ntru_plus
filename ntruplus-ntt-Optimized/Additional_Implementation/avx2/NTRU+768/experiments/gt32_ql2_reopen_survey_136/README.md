# GT32 QL2 reopen survey (136)

This gate investigates all three explicit reopen conditions left by Gate 135
without modifying GT Clean:

1. remove the qword-local routing operation class;
2. absorb the natural `e=-1 -> e=0` correction into Q24;
3. find a measured load-dependency repayment larger than the 218-cycle native
   QL2 BaseMul loss.

The routing branch exhausts all 576 asymmetric coefficient orders inside a
quartic qword and audits the already executable tensor alternatives.  The
scale branch additionally builds a natural `e=-1` version of the exact Gate
135 kernel and measures the entire removed finalizer, giving an executable
upper bound even before paying for a real mixed-scale Q24.  The load branch
uses the production PMU/LBR evidence from Experiment 133 and deliberately
over-generous upper bounds.

Run:

```sh
make clean
make check
make benchmark
```

See [RESULTS.md](RESULTS.md) for the conclusions and
`generated/reopen-survey.json` for the machine-readable audit.
