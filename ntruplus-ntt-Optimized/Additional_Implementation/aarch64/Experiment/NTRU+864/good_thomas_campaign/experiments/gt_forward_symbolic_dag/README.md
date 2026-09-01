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

Run `make check` for the mathematical and artifact gates. The repository has
no local Slothy checkout or virtual environment. A known remote interpreter is
`/home/pinhao/slothy/venv/bin/python`, but no allocation, schedule, cycle, or
code-size result exists until its generated assembly and log are returned and
audited.
