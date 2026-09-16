# Decision

**PASS — use G0 as the authoritative range/scale premise for future M5R-D
FR-0 experiments.**

The historical `8874 -> 24438 -> 2168` chain remains useful only for its older
M5B/M5A source.  It must not be cited as the consumer proof for M5R-D.  The
current closed chain is:

```text
9342 -> M5R-D one-product NTT9 -> 25569
     -> M5C BaseMul/BaseMulAdd -> 2148/2205
     -> M5E-r1 -> maximum lazy halfword 17220
```

G0 also links the exact source components and passes full quotient-ring
differentials, so later layout, fusion, BaseMul, or inverse experiments may use
these bounds as their baseline.  This decision makes no performance or
Production promotion claim.
