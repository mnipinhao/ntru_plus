# M5G: correlation-safe Forward B3 symbolic DAG

This experiment is the hard gate between the readable M5F C schedule and any
Forward register allocation or instruction scheduling. It changes one
oriented radix-3 butterfly from four fixed products to two, proves the exact
destructive instruction DAG over every Forward instantiation, and expresses
that 15-instruction region with Slothy symbolic registers.

The selected algebra is

```text
y0 = a + b + c
y1 = a + rho*b + rho2*c
y2 = (a-y0) + (a-y1) + a
```

The last line is congruent to the usual third radix-3 output because
`1+rho+rho2 = 0 (mod q)`. Its instruction order matters. A tempting
implementation first builds `2a` and `3a`; the full correlation-aware Forward
proof finds magnitude 50448 and 176 unsafe signed-halfword nodes. The selected
destructive order instead forms `a-y0=-b-c` and
`a-y1=-rho*b-rho2*c`. Exhausting the correlated one-variable transfers keeps
every exact DAG node within 28568.

`gt864_forward_b3_two_product.sym.S` contains only `V<name>` registers. It
does not assign physical registers. The remote driver reserves `v1-v23`, so
Slothy sees the exact nine-register window `v0,v24-v31` left by fifteen
live-through data vectors and the ABI prohibition on `v8-v15`. This is a
pressure experiment for one B3 region, not yet a complete Forward kernel.

The remote hard gate used `/home/pinhao/slothy/venv/bin/python` and checkout
revision `d636d638d06b370d1acc5774ca31c9572d3d2e6f`. The first attempt correctly
failed before solving because the driver omitted the three boundary outputs.
After deriving and declaring `outputs=["a","b","c"]`, Slothy 0.2.2 found an
OPTIMAL 24-cycle N1-proxy schedule with 20 stalls and passed its selfcheck.

The emitted instructions use exactly `v0,v24-v31`: all nine available vector
registers, no `v1-v23`, no GPR, no stack, and no memory instruction. The
returned source and log are frozen under `slothy-output/`; `make check` audits
them and assembles the emitted source. This proves the bounded B3 allocation
gate, not complete Forward feasibility or Pi 5 performance.
