# Results

```text
correctness:                         PASS (1000 trials + both aliases)
candidate stack references:         0
Normal candidate-control:           +215.62 cycles
Reversed candidate-control:         +218.12 cycles
PMU core-cycle delta:               +218.53/call
PMU retired-instruction delta:      +318.83/call
PMU port-5/11 delta:                +220.41 uops/call
decision:                            CLOSED_FOR_SCOPE
```

The mandatory e=0 scale repayment was included.  No KEM benchmark was run
because the architecture-critical consumer already exceeds the credible
producer/serializer repayment budget.
