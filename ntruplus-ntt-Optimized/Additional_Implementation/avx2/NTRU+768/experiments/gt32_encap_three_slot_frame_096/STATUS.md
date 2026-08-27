# Status

```text
correctness:                  PASS
B3 destructive alias:        PASS (095)
frontend/ntt_m exact alias:   PASS
resource shape 4 -> 3:        PASS
production performance:      FAIL
promotion:                    REJECTED
production baseline:         b2a4bea
```

The initial C4/A4/A3 gate found a stable ASLR-off Encap regression of about
394 cycles. Because A3 also requires an in-place frontend ownership change,
A4I was added as a causal control. A4I retains the four-slot/6592-byte frame
without dynamic work while using the exact A3 Forward and B3 dataflow.

The closure result assigns the loss to the frame/remapped absolute stack data
geometry, not to B3 alias or in-place Forward:

```text
ASLR off, Encap
A4-C4      +3.250   CI [-11.75,+8.50]
A4I-A4     -1.750   CI [-11.00,+7.75]
A3-A4I   +402.875   CI [+395.50,+417.25]  0/16 favorable
A3-C4    +408.125   CI [+398.25,+416.50]  0/16 favorable
```

No production file is modified. Do not search field order, padding, or a
single favorable stack placement under this campaign. Gate 095 remains a
reusable exact-alias contract, but the natural 5056-byte three-slot Encap
frame is `CLOSED_FOR_SCOPE`.
